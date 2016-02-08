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
import time
import tempfile
import pickle
import zlib
import os
from os.path import join, exists
import psycopg2, requests, requests_cache

from eveSQL import firstGo
import untangle, json, pprint, logging


logging.basicConfig(filename='eve-first_transactions.log',level=logging.DEBUG)
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


## eve api
auth = api.auth(keyID=CORP_KEYID, vCode=CORP_VCODE)
result2 = auth.account.Characters()
cachedApi = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True))
# postgres for safe keeping of our own data
connQ = psycopg2.connect("dbname='eveclient'  user='adam'")
currQ = connQ.cursor()



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

"""
for x in corpTransactions.transactions:
    print (x)
    
corpJournal = corp.WalletJournal()
for x in corpJournal.entries:
    print (x)
    

"""
corpAssets = corp.AssetList().assets

def populate_corp_assets_table(assets):
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
    currQ.execute("DELETE FROM corpassets")
    for x in assets:
        '''conn.execute("INSERT INTO corpassets "
                     "(itemid, locationid, typeid, quantity, flags, singleton) "
                     "VALUES (", x["itemID"],", "x['locationID'],", ",x['typeID'],", ",x['quantity']",","
                     ""x['flags']", ",x['singleton']);""
                     )'''
        currQ.execute("INSERT INTO corpassets ({ii}, {li}, {ti}, {q}, {f}, {s}) VALUES ({vii}, {vli}, {vti}, {vq}, {vf}, {vs})".
                    format(ii="itemid", li="locationid", ti="typeid", q="quantity", f="flag", s="singleton",
                            vii=x["itemID"], vli=x["locationID"], vti=x["typeID"], vq=x["quantity"], vf=x["flag"], vs=x["singleton"]))
    connQ.commit()
    

def make_throttle_hook(timeout=1.0):  # for eve market api calls
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached
    """
    def hook(response, **kwargs):
        if not getattr(response, 'from_cache', False):
            print ('sleeping')
            time.sleep(timeout)
        return response
    return hook

requests_cache.install_cache(cache_name='wait_test', expires_after = 3600)
requests_cache.clear()
s = requests_cache.CachedSession()
s.hooks = {'response': make_throttle_hook(0.1)}
 
def now_value(systemID, interestingItem):
    marketStatUrl = "http://api.eve-central.com/api/marketstat/json?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    resp = s.get(url=marketStatUrl)
    # print resp.text
    data = json.loads(resp.text)[0]
    #print ("data", data["buy"]["generated"])
    return data
    # pprint.pprint(data)
    # print ("They Buy ", data[0]['buy']['max'])
    # print ("They Sell ", data[0]['sell']['min'])
    
x = now_value(30002510, 7621)


def insert_market_price(data):
    """ insert into the psql table 'marketprices' the data given as an input
    the input data shouls usually be a json lookup on the eve-market API
    """
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
        currQ.execute("INSERT INTO marketprices " 
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
        connQ.rollback()
        logging.debug('Duplicate market data, connQ.execute rolled back!')
    else:
        connQ.commit() 
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
        currQ.execute("INSERT INTO marketprices " 
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
        connQ.rollback()
        logging.debug('Duplicate market data, connQ.execute rolled back!')
    else:
        connQ.commit() 
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
        currQ.execute("INSERT INTO marketprices " 
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
        connQ.rollback()
        logging.debug('Duplicate market data, connQ.execute rolled back!')
    else:
        connQ.commit() 
    



    
"""

#30002053 hek
# 34 tritanium

firstGo.createCorpAssetsTable(corpAssets)
firstGo.getValueCorpAssets()


"""

#get Stored Sell values
def get_stored_sale_price(item, system):
    currQ.execute("SELECT min FROM marketprices WHERE (direction = \'they_sell\' AND "
                  "item = {it} AND system = {sys}) "
                  "ORDER BY generated DESC "
                  "LIMIT 1".
                  format(it = item, sys = system))
    x = currQ.fetchall()[0]
    return float(x[0])

#itemID, locationID, typeID, quantity, flag, singleton
queries = SDEQueries()
markets = EVECrest()

for x in corpAssets:
    #print (x.itemID, queries.get_system_from_station_ID(x.locationID))
    y = now_value(queries.get_system_from_station_ID(x.locationID), x.typeID)
    insert_market_price(y)

# find group and other items in the gorup of 220mm Vulcan AutoCannon I
queries.get_item_id("220mm Vulcan AutoCannon I")
queries.get_market_group_from_type_id(490)
items = queries.getItemsInGroup(575)


systems = []    
systems.append(queries.get_system_id("Hek"))
systems.append(queries.get_system_id("Rens"))


for theSystems in systems:
    for theItems in items:
        markets.get_date_last_entry(theItems, theSystems)
        insert_market_price(now_value(theSystems, theItems))
        
get_stored_sale_price(490, queries.get_system_id("Hek"))


sell_these = []
for theItems in items:
    diff = (get_stored_sale_price(theItems, queries.get_system_id("Hek")) - 
            get_stored_sale_price(theItems, queries.get_system_id("Rens")))
    if (diff > 0):
        #print (queries.get_item_name(theItems), diff, theItems)
        sell_this = [queries.get_item_name(theItems), diff]
        sell_these.append(sell_this)
    else:
        pass
    
sell_these.sort(key=lambda x: x[1], reverse=True)
pprint.pprint(sell_these)
        

        
systems = ["Teonusude", "Gelfiven", "Gulfonodi", "Nakugard", "Tvink", 
           "Lanngisi", "Magiko", "Vullat","Eystur", "Hek", "Lustrevik",
           "Hror", "Otou", "Nakugard", "Uttindar"]

x = queries.find_meta_mods(3)
y = set(x).intersection(set(queries.find_high))


