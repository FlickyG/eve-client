#!/home/adam/.virtualenvs/eve-tools/bin/python

'''
Created on 10 Jan 2016

@author: adam
'''
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
from eveSQL.SDEQueries import SDEQueries
from eveSQL.EVECrest import EVECrest
standard_library.install_aliases()
from builtins import str
from builtins import object

import eveapi
import time, datetime
import tempfile
import pickle
import zlib
import os
from os.path import join, exists
import psycopg2, requests, requests_cache
#for debuggin
import code
#for pretty printing of dictionary
from prettytable import PrettyTable
# another apptoach to pretty printing
from tabulate import tabulate

#from eveSQL import firstGo
import untangle, json, pprint, logging
print ("###### NAME ####", __name__)
logger = logging.getLogger(__name__)


#logging.basicConfig(filename='eve-first_transactions.log',level=logging.DEBUG)
#Row(name:Flicky G,characterID:859818750,corporationName:Flicky G Corporation,corporationID:98436502,allianceID:0,allianceName:,factionID:0,factionName:)

#'EVE API Stuff
CHAR_KEYID = 4958524
CHAR_VCODE = "njXdwQdNFNlf47TfOAnbNuHP6gX7sJeArgD2AEk1Qpay1tkUagUMyStSriZPQqd0"
CHAR_AMASK = 1073741823


#Corp
CORP_KEYID = 1383071
CORP_VCODE = "m0ecx5e1r8RCMsizNKXyB91HQchkHjJmNJlG8or0xy3VvkpiAJj1J7wXb70lUMm0"
CORP_AMASK = 268435455


eveapi.set_user_agent("eveapi.py/1.3")
api = eveapi.EVEAPIConnection()


class MyCacheHandler(object):
    # Note: this is an example handler to demonstrate how to use them.
    # a -real- handler should probably be thread-safe and handle errors
    # properly (and perhaps use a better hashing scheme).

    def __init__(self, debug=False):
        self.debug = debug
        self.count = 0
        self.cache = {}
        self.tempdir = join(tempfile.gettempdir(), "eveapi")
        if not exists(self.tempdir):
            os.makedirs(self.tempdir)

    def log(self, what):
        if self.debug:
            print("[%d] %s" % (self.count, what))

    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(list(params.items()))))

        self.count += 1  # for logging

        # see if we have the requested page cached...
        cached = self.cache.get(key, None)
        if cached:
            cacheFile = None
            #print "'%s': retrieving from memory" % path
        else:
            # it wasn't cached in memory, but it might be on disk.
            cacheFile = join(self.tempdir, str(key) + ".cache")
            if exists(cacheFile):
                self.log("%s: retrieving from disk" % path)
                f = open(cacheFile, "rb")
                cached = self.cache[key] = pickle.loads(zlib.decompress(f.read()))
                f.close()

        if cached:
            # check if the cached doc is fresh enough
            if time.time() < cached[0]:
                self.log("%s: returning cached document" % path)
                return cached[1]  # return the cached XML doc

            # it's stale. purge it.
            self.log("%s: cache expired, purging!" % path)
            del self.cache[key]
            if cacheFile:
                os.remove(cacheFile)

        self.log("%s: not cached, fetching from server..." % path)
        # we didn't get a cache hit so return None to indicate that the data
        # should be requested from the server.
        return None

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        key = hash((host, path, frozenset(list(params.items()))))

        cachedFor = obj.cachedUntil - obj.currentTime
        if cachedFor:
            self.log("%s: cached (%d seconds)" % (path, cachedFor))

            cachedUntil = time.time() + cachedFor

            # store in memory
            cached = self.cache[key] = (cachedUntil, doc)

            # store in cache folder
            cacheFile = join(self.tempdir, str(key) + ".cache")
            f = open(cacheFile, "wb")
            f.write(zlib.compress(pickle.dumps(cached, -1)))
            f.close()


class MarketQuestions(object):
    
    def __init__(self):
        self.connQ = psycopg2.connect("dbname='eveclient'  user='adam'")
        self.currQ = self.connQ.cursor()
        expire_after = datetime.timedelta(hours = 6)
        self.s = requests_cache.CachedSession(cache_name="first_transaction_cache", expire_after=expire_after)
        self.s.hooks = {'response': self.make_throttle_hook(0.1)}
    
        self.queries = SDEQueries()
        self.markets = EVECrest()

    def populate_corp_assets_table(self, assets):
        #curr.executescript('drop table if exists corpassets;')    
        """currQ.execute("CREATE TABLE corpassets "
                    "(itemid INT PRIMARY KEY  NOT NULL,"
                    "locationid     INT    NOT NULL,"
                    "typeid    INT    NOT NULL,"
                    "quantity    INT    NOT NULL,"
                    "flag    INT    NOT NULL,"
                    "singleton    INT    NOT NULL"
                    ");")
        """
        self.currQ.execute("DELETE FROM corpassets")
        for x in assets:
            '''conn.execute("INSERT INTO corpassets "
                         "(itemid, locationid, typeid, quantity, flags, singleton) "
                         "VALUES (", x["itemID"],", "x['locationID'],", ",x['typeID'],", ",x['quantity']",","
                         ""x['flags']", ",x['singleton']);""
                         )'''
            self.currQ.execute("INSERT INTO corpassets ({ii}, {li}, {ti}, {q}, {f}, {s}) VALUES ({vii}, {vli}, {vti}, {vq}, {vf}, {vs})".
                        format(ii="itemid", li="locationid", ti="typeid", q="quantity", f="flag", s="singleton",
                                vii=x["itemID"], vli=x["locationID"], vti=x["typeID"], vq=x["quantity"], vf=x["flag"], vs=x["singleton"]))
        self.connQ.commit()
        
    def make_throttle_hook(self, timeout=1.0):  # for eve market api calls
        logger.debug("HELLO LOGGER")
        """
        Returns a response hook function which sleeps for `timeout` seconds if
        response is not cached
        """
        def hook(response, **kwargs):
            if not getattr(response, 'from_cache', False):
                # ('sleeping')
                time.sleep(timeout)
            return response
        return hook
    
    def now_value(self, systemID, interestingItem):
        marketStatUrl = "http://api.eve-central.com/api/marketstat/json?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
        resp = self.s.get(url=marketStatUrl)
        # print resp.text
        data = json.loads(resp.text)[0]
        #print ("data", data["buy"]["generated"])
        return data
        # pprint.pprint(data)
        # print ("They Buy ", data[0]['buy']['max'])
        # print ("They Sell ", data[0]['sell']['min'])
        
    def insert_market_price(self, data):
        logger.debug("HELLO LOGGER")
        """ insert into the psql table 'marketprices' the data given as an input
        the input data shouls usually be a json lookup on the eve-central API
        """
        logger.debug("attempting to insert_market_price {dt}".
                     format(dt = data))
        # buy orders - wehere we sell an item
        x = data["buy"]
        if x["forQuery"]["regions"]:
            pass
        else:
            x["forQuery"]["regions"].append(0)
        
        if x["forQuery"]["systems"]:
            pass
        else:
            x["forQuery"]["systems"].append(0)
        try:
            self.currQ.execute("INSERT INTO marketprices " 
                        "(direction, " 
                        "item, "
                        "region, "
                        "system, "
                        "avg, "
                        "fivepercent, "
                        "generated, "
                        "hightolow, "
                        "max, "
                        "median, "
                        "min, "
                        "stddev, "
                        "variance, "
                        "volume, "
                        "wavg, "
                        "source) "
                        "VALUES ( "
                        "{dir}, " 
                        "{itm}, "
                        "{rgn}, "
                        "{sys}, "
                        "{avg}, "
                        "{pcn}, "
                        "{gnr}, "
                        "{htl}, "
                        "{max}, "
                        "{mdn}, "
                        "{min}, "
                        "{dev}, "
                        "{vrn}, "
                        "{vol}, "
                        "{wvg}, "
                        "{src})".
                        format(
                        dir = "'they_buy'", 
                        itm = x["forQuery"]["types"][0],
                        rgn = x["forQuery"]["regions"][0],
                        sys = x["forQuery"]["systems"][0],
                        avg = x["avg"],
                        pcn = x["fivePercent"],
                        gnr = x["generated"],
                        htl = x["highToLow"],
                        max = x["max"],
                        mdn = x["median"],
                        min = x["min"],
                        dev = x["stdDev"],
                        vrn = x["variance"],
                        vol = x["volume"],
                        wvg = x["wavg"], 
                        src = "'eve-market'")
                        )
        except psycopg2.IntegrityError:
            self.connQ.rollback()
            logger.debug('Duplicate market data, connQ.execute rolled back!')
        else:
            self.connQ.commit() 
        #sell orders, where we buy something from them
        x = data["sell"]
        if x["forQuery"]["regions"]:
            pass
        else:
            x["forQuery"]["regions"].append(0)
        
        if x["forQuery"]["systems"]:
            pass
        else:
            x["forQuery"]["systems"].append(0)
        try:
            self.currQ.execute("INSERT INTO marketprices " 
                        "(direction, " 
                        "item, "
                        "region, "
                        "system, "
                        "avg, "
                        "fivepercent, "
                        "generated, "
                        "hightolow, "
                        "max, "
                        "median, "
                        "min, "
                        "stddev, "
                        "variance, "
                        "volume, "
                        "wavg, "
                        "source) "
                        "VALUES ( "
                        "{dir}, " 
                        "{itm}, "
                        "{rgn}, "
                        "{sys}, "
                        "{avg}, "
                        "{pcn}, "
                        "{gnr}, "
                        "{htl}, "
                        "{max}, "
                        "{mdn}, "
                        "{min}, "
                        "{dev}, "
                        "{vrn}, "
                        "{vol}, "
                        "{wvg}, "
                        "{src})".
                        format(
                        dir = "'they_sell'", 
                        itm = x["forQuery"]["types"][0],
                        rgn = x["forQuery"]["regions"][0],
                        sys = x["forQuery"]["systems"][0],
                        avg = x["avg"],
                        pcn = x["fivePercent"],
                        gnr = x["generated"],
                        htl = x["highToLow"],
                        max = x["max"],
                        mdn = x["median"],
                        min = x["min"],
                        dev = x["stdDev"],
                        vrn = x["variance"],
                        vol = x["volume"],
                        wvg = x["wavg"], 
                        src = "'eve-market'")
                        )
        except psycopg2.IntegrityError:
            self.connQ.rollback()
            logger.debug('Duplicate market data, connQ.execute rolled back!')
        else:
            self.connQ.commit() 
        #all orders - given as an average of both
        x = data["all"]
        if x["forQuery"]["regions"]:
            pass
        else:
            x["forQuery"]["regions"].append(0)
        
        if x["forQuery"]["systems"]:
            pass
        else:
            x["forQuery"]["systems"].append(0)
        try:
            self.currQ.execute("INSERT INTO marketprices " 
                        "(direction, " 
                        "item, "
                        "region, "
                        "system, "
                        "avg, "
                        "fivepercent, "
                        "generated, "
                        "hightolow, "
                        "max, "
                        "median, "
                        "min, "
                        "stddev, "
                        "variance, "
                        "volume, "
                        "wavg, "
                        "source) "
                        "VALUES ( "
                        "{dir}, " 
                        "{itm}, "
                        "{rgn}, "
                        "{sys}, "
                        "{avg}, "
                        "{pcn}, "
                        "{gnr}, "
                        "{htl}, "
                        "{max}, "
                        "{mdn}, "
                        "{min}, "
                        "{dev}, "
                        "{vrn}, "
                        "{vol}, "
                        "{wvg}, "
                        "{src})".
                        format(
                        dir = "'they_all'", 
                        itm = x["forQuery"]["types"][0],
                        rgn = x["forQuery"]["regions"][0],
                        sys = x["forQuery"]["systems"][0],
                        avg = x["avg"],
                        pcn = x["fivePercent"],
                        gnr = x["generated"],
                        htl = x["highToLow"],
                        max = x["max"],
                        mdn = x["median"],
                        min = x["min"],
                        dev = x["stdDev"],
                        vrn = x["variance"],
                        vol = x["volume"],
                        wvg = x["wavg"], 
                        src = "'eve-market'")
                        )
        except psycopg2.IntegrityError:
            self.connQ.rollback()
            logger.debug('Duplicate market data, connQ.execute rolled back!')
        else:
            self.connQ.commit() 
        
    #get Stored Sell values
    def get_stored_sale_price(self, item, system):
        logger.debug("HELLO LOGGER")
        self.currQ.execute("SELECT min FROM marketprices WHERE (direction = \'they_sell\' AND "
                      "item = {it} AND system = {sys}) "
                      "ORDER BY generated DESC "
                      "LIMIT 1".
                      format(it = item, sys = system))
        #print ("item {id} system {sys}".format(id = item, sys = system))
        #print ("db returns.. {db}".format(db = self.currQ.fetchone()[0]))
        x = self.currQ.fetchone()
        return (round(x[0], 2))
    
    #itemID, locationID, typeID, quantity, flag, singleto
    def find_cheapest(self, item):
        logger.debug("HELLO LOGGER")
        hubs = ["Rens", "Jita", "Amarr"]
        cheapest_location = None
        cheapest_price = -1
        for hub in hubs:
            #self.now_value(hub, item)
            try:
                if (cheapest_price == -1) and (self.get_stored_sale_price(item, self.queries.get_system_id(hub)) > 0):
                    #print ("cheapest price = -1")
                    cheapest_location = hub
                    cheapest_price = self.get_stored_sale_price(item, self.queries.get_system_id(hub))
                elif self.get_stored_sale_price(item, self.queries.get_system_id(hub)) < cheapest_price:
                    cheapest_location = hub
                    cheapest_price = self.get_stored_sale_price(item, self.queries.get_system_id(hub))
            except:
                self.insert_market_price(self.now_value(self.queries.get_system_id(hub), item))
                self.get_stored_sale_price(item, self.queries.get_system_id(hub))
        return (cheapest_location, cheapest_price)
             
        
    def get_none_sold_dict(self, items, system):
        logger.debug("HELLO LOGGER")
        these_arent_sold = []
        for item in items:
            if self.get_stored_sale_price(item, system) == 0:
                these_arent_sold.append(item)
        return these_arent_sold
    
    def get_profit_on_items(self, items, from_system, to_system):
        profit_from_item = {}
        for item in items:
            profit = ([self.get_stored_sale_price(item, self.queries.get_system_id(from_system)),
                       self.get_stored_sale_price(item, self.queries.get_system_id(to_system)),
                       (round(self.get_stored_sale_price(item, self.queries.get_system_id(to_system)) - 
                              self.get_stored_sale_price(item, self.queries.get_system_id(from_system)), 2))])
            profit_from_item[self.queries.get_item_name(item)] = profit
        return profit_from_item

    #find items which are cheaper in hek than they are in rens
    def cheaper_between_two_locations(self, items, location1 = "Hek", location2 = "Rens"):
        sell_these = []
        for theItems in items:
            diff = (self.get_stored_sale_price(theItems, self.queries.get_system_id(location1)) - 
                    self.get_stored_sale_price(theItems, self.queries.get_system_id(location2)))
            if (diff > 0):
                #print (queries.get_item_name(theItems), diff, theItems)
                sell_this = [self.queries.get_item_name(theItems), round(diff, 2)]
                sell_these.append(sell_this)
            else:
                pass
        headers = ["item", "profit"]
        sell_these.sort(key=lambda x: x[1], reverse=True)
        return headers, sell_these
    

    # finds items unsold in a system and finds the price in two other hubs
    def unsold_prices_elsewhere(self, items, location = "Lustrevik", location1 = "Jita", location2 = "Rens"):
        sell_these = self.get_none_sold_dict(items, self.queries.get_system_id(location))
        sell_these = self.get_profit_on_items(sell_these, location1, location2)
        sell_these.sorted(sell_these.items(), key=lambda e: e[1][2], reverse = True)
        text = [[aa, bb, cc, dd] for aa, (bb, cc, dd) in sell_these]
        headers = ["item", "from price", "to price", "profit"]
        print (tabulate(text, headers, tablefmt = "simple", numalign= "right", floatfmt = ".2f"))

def main():
    # setup logging functions
    import logging.config
    logging.config.fileConfig('/home/adam/workspace1/eve-client/eve_client_logging.conf')
    # your program code  
    #logging.basicConfig(filename='first_transactions.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    #logging.info('Starting up first_transactions main()')
    trans = MarketQuestions()
    ## eve api
    auth = api.auth(keyID=CORP_KEYID, vCode=CORP_VCODE)
    result2 = auth.account.Characters()
    cachedApi = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True)) 
    # Now the best way to iterate over the characters on your account and show
    # the isk balance is probably this way:
    """
    for character in result2.characters:
        if  "Flicky G" == character.name:
            wallet = auth.corp.AccountBalance(characterID=character.characterID)
            for x in wallet.accounts:
                print (x)
    """         
    corp = cachedApi.auth(keyID=1383071, vCode="m0ecx5e1r8RCMsizNKXyB91HQchkHjJmNJlG8or0xy3VvkpiAJj1J7wXb70lUMm0").corporation(98436502)
    corpTransactions  = corp.WalletTransactions()
    x = trans.now_value(30002510, 7621)
    corpAssets = corp.AssetList().assets
    """
    for x in corpTransactions.transactions:
        print (x)
        
    corpJournal = corp.WalletJournal()
    for x in corpJournal.entries:
        print (x)
        

    """
    #requests_cache.install_cache(cache_name='first_transactions', expires_after = 1)
    #requests_cache.clear()
    
    """
    for x in corpAssets:
        #print (x.itemID, queries.get_system_from_station_ID(x.locationID))
        y = trans.now_value(trans.queries.get_system_from_station_ID(x.locationID), x.typeID)
        trans.insert_market_price(y)
    
    # find group and other items in the gorup of 220mm Vulcan AutoCannon I
    #trans.queries.get_item_id("220mm Vulcan AutoCannon I")
    #trans.queries.get_market_group_from_type_id(490)
    #items = trans.queries.get_items_in_group(575)
    
    
    systems = []    
    systems.append(trans.queries.get_system_id("Hek"))
    systems.append(trans.queries.get_system_id("Rens"))
    """
    
    
    """
    for theSystems in systems:
        for theItems in items:
            markets.get_date_last_entry(theItems, theSystems)
            insert_market_price(now_value(theSystems, theItems))
            
    get_stored_sale_price(490, queries.get_system_id("Hek"))
    """
    

    """            
    groups = ["Afterburneres", ""]
            
    systems = ["Lustrevik", "Teonusude", "Gelfiven", "Gulfonodi", "Nakugard", "Tvink", 
               "Lanngisi", "Magiko", "Vullat","Eystur", "Hek", 
               "Hror", "Otou", "Nakugard", "Uttindar"]

    """
    
    systems = ["Hek", "Rens"]
    
    x = trans.queries.find_meta_mods(4)
    y = set(x).intersection(set(trans.queries.find_high_slots()))
    
    """
    for system in systems:
        for item in y:
            print (trans.markets.get_date_last_entry(item, trans.queries.get_region_id_from_system(trans.queries.get_system_id(system))))
            trans.insert_market_price(trans.now_value(trans.queries.get_system_id(system), item))
            print (trans.get_stored_sale_price(item, trans.queries.get_system_id(system)))
    """
    
    headers, text = trans.cheaper_between_two_locations(y)
    print (tabulate(text, headers, tablefmt = "simple", numalign= "right", floatfmt = ".2f"))

    trans.unsold_prices_elsewhere(y)

if __name__ == '__main__':
    main()