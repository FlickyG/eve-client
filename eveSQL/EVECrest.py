'''
Created on 30 Jan 2016

@author: adam
'''

import pycrest, pprint, psycopg2, time, datetime
from requests.exceptions import ConnectionError
from pip._vendor.requests.packages.urllib3.exceptions import ProtocolError
import requests, sys
import logging


eve = pycrest.EVE()
eve()
logger = logging.getLogger(__name__)
#logger.propagate = False
print ("EVE CREST logger handlers", logger.handle)

def getByAttrVal(objlist, attr, val):
    ''' Searches list of dicts for a dict with dict[attr] == val '''
    matches = [getattr(obj, attr) == val for obj in objlist]
    index = matches.index(True)  # find first match, raise ValueError if not found
    return objlist[index]

def getAllItems(page):
    ''' Fetch data from all pages '''
    ret = page().items
    while hasattr(page(), 'next'):
        page = page().next()
        ret.extend(page().items)
    return ret

#region = getByAttrVal(eve.regions().items, 'name', 'Catch')

#item = getByAttrVal(getAllItems(eve.itemTypes), 'name', 'Tritanium').href
#getAllItems(region().marketSellOrders(type=item))

#market = getByAttrVal(eve.prices(), 'name', 'Tritanium', 'Catch')


#pprint.pprint(eve)

#10000042 metro
#490 22omm vulcan
#history = eve.get('https://public-crest.eveonline.com/market/10000042/types/34/history/')
#pprint.pprint(history)

#get date of last entry in table
#if date older than two days ago, get history
# for each entry in history older than today's date and younger than the last entry
#    enter data into database
# 

class EVECrest(object):
    def __init__(self):
        self.connQ = psycopg2.connect("dbname='eveclient'  user='adam'")
        self.currQ = self.connQ.cursor()

    def fetch_market_history(self, typeid, regionid):
        """ Contact the Eve Crest API and pulls down 13 months of market data.
            This is the same info as contained in the market data screen in-game.
        """
        logger.debug("entering_market_history type = {id} region = {rg}".format(id = typeid, rg = regionid))
        try: # crest api is flaky
            data = eve.get("https://public-crest.eveonline.com/market/{rg}/types/{id}/history/".
                       format(rg = regionid, id = typeid))
            return data
        except ConnectionError as e:
            # to-do - needs to handle 404 errors too
            logger.debug("")
            try:
                if e.args[0].args[1].errno == 104:
                    #print ("eve crest connection reset by peer {ti}, {name}".
                           #format(ti = typeid, name = regionid))
                    self.fetch_market_history(typeid, regionid) # retry for ever
                else:
                    pass
            except Exception as f: #we wrongly assumed it was a reset connection error
                try:
                    if "BadStatusLine" in e.args[0][1]:
                        #print ("pycrest encountered bad status line {ti}, {name}".
                           #format(ti = typeid, name = regionid))
                        self.fetch_market_history(typeid, regionid) # retry for ever
                    else:
                        pass                  
                        #return f # ion which case we aren't sure what the rror is
                except:
                    raise
                    #return e 
    
    def enter_market_history(self, type, region, data):
        """ Inserts into the database the market data given as 'data'.  'Data'
            should be a list and is derived from the EVE Crest API.  The list
            contains the same data a single day's info on the market data screen
            in-game.
            If no items are bought or sold, then the price info from the 
            previous day is carried over.
        """
        try:
            self.currQ.execute("INSERT INTO markethistory ("
                          "type, "
                          "region, " 
                          "avg, "
                          "date, "
                          "high, "
                          "low, "
                          "ordercount,"
                          "volume) "
                          "VALUES ( "
                          "{typ}, "
                          "{rgn}, " 
                          "{avg}, "
                          "\'{dte}\', "
                          "{hgh}, "
                          "{low}, "
                          "{cnt}, "
                          "{vlm}) ".
                          format(
                                 typ = type,
                                 rgn = region,
                                 avg = data["avgPrice"],
                                 dte = data["date"].split("T")[0],
                                 hgh = data["highPrice"],
                                 low = data["lowPrice"],
                                 cnt = data["orderCount"],
                                 vlm = data["volume"]                           
                                 )
                          )
            self.connQ.commit()
        except psycopg2.IntegrityError:
            self.connQ.rollback()


    def get_date_last_entry(self, id, regionid):
        logger.info("entering get_date_last_entry id =  {id} region = {region}".format(id = id, region = regionid))
        self.currQ.execute("SELECT date FROM markethistory "
                      "WHERE (type = {it} AND region = {region}) "
                      "ORDER BY date DESC "
                      "LIMIT 1".
                      format(it = id, region = regionid))
        data = self.currQ.fetchone()
        """ If the database is empty, it may be because we've never pulled this
            data down. It may also be because there is no data to pull, such as
            capital ships in high sec
        """
        try:
            assert data[0] != type(None)
        except TypeError:
            logger.debug("Initial lookup in psql revelas no data in the psql db for this item!")
            try:
                temp_results = self.fetch_market_history(id, regionid)
                x = temp_results["items"]
                #need to handle this better whern the connection is reset by peer, in which case the temp_results are none
            except TypeError as e:
                logger.debug("Exit 101, returning None TypeError and e", e)
                return ("None")
            except pycrest.errors.APIException as e:
                if "Got unexpected status code from server: 404" in e:
                    logger.debug("successfully caught 404, retrying item = {id} ".format(id= id))
                    self.get_date_last_entry(id, regionid)
                logger.debug("Exit 102, 404 detected? returning None e = {e}, id {id}, regionid = {regionid}".
                                format(e = e, id = id, regionid = regionid))
                return ("None")
            if len(x) == 0:
                # here we catch the case of capital ships in high sec mentioned above
                #print ("there is no market data for this item", id)
                logger.debug("this item isn't on the market eg, capitals in high sec, returing None id = {id}, regionid = {rg}".
                             format(id = id, rg = regionid))
                return None
            else: #here we pull down data we haven't seen before
                for datapoint in x:
                    self.enter_market_history(id, regionid, datapoint)
                logger.debug("data found, recursing")
                return self.get_date_last_entry(id, regionid)
        # below is business as usual - get any missing day's info
        last_date = data[0]
        # server side data is updated each day at midnight
        if datetime.date.today() - last_date < datetime.timedelta(days = 2): # if the data is up to date
            return last_date # NORMAL OPERATION
        else: # our data is not up to date
            try:
                # fetch data from crest api
                x = self.fetch_market_history(id, regionid)["items"]
            except:
                logger.debug("Exit 103 second attempt to fetch_mnarket_data failef - returning the data from psql we have")
                return (last_date)  # crest api is flakey - if we can't contact the server now, return the last entry.  Any data is better than none
            """  if the item hasn't traded since our last update, then there is no data to pass
                this may cause an infinite loop if not caught
            """
            data_found  = False # use this to prevent infinite loop
            for datapoint in x:
                #print ("type of datapoint", type(datetime.datetime.strptime(datapoint["date"].split("T")[0], "%Y-%m-%d").date()))
                # skip market entries if the data is before the last date seen in the database
                if (datetime.datetime.strptime(datapoint["date"].split("T")[0], "%Y-%m-%d").date()
                    > last_date):
                    data_found = True # we do have data but it might not be useful
                    #print ("entering data")
                    self.enter_market_history(id, regionid, datapoint)
                else:
                    pass # we already have this data
            if data_found:
                return self.get_date_last_entry(id, regionid)
            else:
                logger.debug("the item is being sold, but not on the dates we're interested in, returning most recent date")
                return last_date # in the case where the item has no current market orders, return the last data one was seen.

def main():
    pass
    #molden heath 10000028 
    #crest = EVECrest()
    #x = crest.get_date_last_entry(489, 10000042)
    #return (x) #nothing to do if you call this directly


if __name__ == "__main__":
    exit(main())

        
        
        
"""        
        get_date_last_entry(id, regionid)


def test(id, regionid):
    self.currQ.execute("SELECT * FROM markethistory "
                  "WHERE (type = {it} AND region = {region}) "
                  "ORDER BY date DESC "
                  "LIMIT 1".
                  format(it = id, region = regionid))
    data = self.currQ.fetchall()
    return data

""" 
        


