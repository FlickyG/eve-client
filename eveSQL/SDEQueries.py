'''
Created on 22 Jan 2016

@author: adam
'''
import sqlite3, sys, datetime

import logging


from sqlite3 import OperationalError


class SDEQueries(object):
    """ Handles SQL calls to the Eve Online SDE held locally on this machine.
        You may need to repoint the location of the sqlite3.connect statement
        TDO - error hanfdling on this and option for CLI input
    """
    #self.logging.basicConfig(filename='eve-first_transactions.log',level=logging.DEBUG)
    
    def __init__(self):
        try:
            location1 = "/home/adam/Documents/eve/native/eve.db"
            self.conn = sqlite3.connect(location1)
            self.curr = self.conn.cursor()
        except sqlite3.OperationalError as e:
            print ("couldn't open the data base at %s %s" % (location1, e) )
        try:
            location2 = "/Users/adam.green/eve.db"
            self.conn = sqlite3.connect("/Users/adam.green/Documents/personal-workspace/eve-project/sqlite-latest.sqlite")
            self.curr = self.conn.cursor()
        except sqlite3.OperationalError:
            print ("couldn't open the data base at %s" % (location2) )
        try:
            location2 = "/Users/adam.green/eve.db"
            self.conn = sqlite3.connect("/Users/adam.green/Documents/personal-workspace/eve-project/sqlite-latest.sqlite")
            self.curr = self.conn.cursor()
        except sqlite3.OperationalError:
            print ("couldn't open the data base at %s" % (location2) )


    def get_item_id(self, interestingItem):
        """ returns the item ID when passed a string represtning ther item's Name
            
        """
        #logging.warning(str(datetime.datetime.now()), "hello this is a warning")
        # Check input is a string
        try:
            assert type(interestingItem) is type(""), "requires a string"
        except:
            print ("you passed get_item_id something that wasn't a string {id}".
                   format(id = interestingItem))
            raise
            sys.exit(0)
        query = "SELECT typeID, typeName FROM invTypes WHERE typeName = "
        strr = "\""
        self.curr.execute(strr.join([query, interestingItem, ""])) 
        x = self.curr.fetchone()
        #check database doesn't return a none type
        try:
            assert x[0] != type(None)
        except:
            print ("get_item_id didn't find what you were looking for and returned a None")
            raise
            sys.exit(0)           
        y = x[0]
        return y
    
    def get_item_name(self, interestingItem):
        """ Returns the item's Name when passed it's integer representation
        """
        # Check input is a string
        try:
            assert type(interestingItem) is int, "requires a integer"
            assert interestingItem > 0, "requires a integer"
        except:
            print ("you passed get_item_name something that wasn't an int")
            raise
            sys.exit(0)
        query = "SELECT typeID, typeName FROM invTypes WHERE typeID = "
        strr = "\""
        self.curr.execute(strr.join([query, str(interestingItem), ""]))     
        x = self.curr.fetchone()
        try:
            assert x[1] != type(None)
        except:
            print ("get_item_name didn't find what you were looking for and returned"
                   " a None",
                   interestingItem)
            raise
            sys.exit(0)   
        return x[1].encode('ascii', 'ignore')
    
    def get_region_id(self, interestingRegion):
        ''' Returns the Region ID when given the string representation
        '''
        # check input is a string
        try:
            assert type(interestingRegion) is type(""), "requires a string"
        except:
            print ("you passed get_region_id somethig that wasn't a string")
            raise 
            sys.exit(0)
        self.curr.execute("SELECT regionName, regionID FROM mapRegions" 
                            " WHERE regionName = \"{id}\"".
                           format(id = str(interestingRegion)))
        x = self.curr.fetchone()
        # Check output makes sense
        try:
            assert x[1] != type(None), "requires not a none type"
        except:
            print("get_region_id couldn't find what you were looking for and "
                  "returned a NoneType")
            raise
        y = x[1] 
        return y
    
    def get_region_id_from_system(self, system):
        ''' Returns the Region ID when given the string representation
        '''
        # check input is a string
        try:
            assert type(system) is int, "requires a int"
        except:
            print ("you passed get_region_if_from_system somethig that wasn't a string")
            raise 
            sys.exit(0)
        self.curr.execute("SELECT regionID FROM mapSolarSystems" 
                            " WHERE solarSystemID = \"{id}\"".
                           format(id = str(system)))
        x = self.curr.fetchone()
        # Check output makes sense
        try:
            assert x[0] != type(None), "requires not a none type"
        except:
            print("get_region_if_from_system couldn't find what you were looking for and "
                  "returned a NoneType")
            raise
        y = x[0] 
        return y
    
    def get_region_name(self, interestingRegion):
        ''' Returns Region Name when given a numerical ID
        '''
        #Check input is a int
        try:
            assert type(interestingRegion) is int, "requires a string"
        except:
            print ("get_region_name requires an int")
            raise
            sys.exit(0)
        query = "select regionName, regionID from mapRegions where regionID = "
        strr = "\""
        self.curr.execute(strr.join([query, str(interestingRegion), ""]))     
        x = self.curr.fetchone()
        y = x[0].encode('ascii', 'ignore')
        try:
            assert type(y) is str, "requires string"
            assert type(y) != type(None), "returned none"
        except:
            print ("type in regionName", x[0])
            print ("get_region_name returned a non type") 
            raise
            sys.exit(0)
        return y
    
    def get_system_id(self, interestingSystem):
        ''' Returns system id as an integer when passed the region name as a string
        '''
        #check input is a string
        try:
            assert type(interestingSystem) is type(""), "requires a string"
        except:
            print ("you passed get_system_id something that wasn't a string")
            raise
            sys.exit(0)
        query = "select regionID, solarSystemID, solarSystemName "\
                " FROM mapSolarSystems WHERE solarSystemName ="
        strr = "\""
        self.curr.execute(strr.join([query, interestingSystem, ""]))    
        x = self.curr.fetchone()
        try:
            assert x != type(None), "should not return a none"
        except:
            print ("get_system_id didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        y = x[1]
        return y

    
    def get_system_from_station_ID(self, stationID):
        ''' Returns system id as an integer when passed a station ID
        '''
        #check input is a string
        try:
            assert type(stationID) is int, "requires a int"
        except:
            print ("you passed get_system_from_station_ID something that wasn't a int")
            raise
            sys.exit(0)
        query = "select solarSystemID from staStations where stationsID = {id}".format(id = stationID) 
        self.curr.execute("select solarSystemID from staStations where stationID = {id}".format(id = stationID))    
        x = self.curr.fetchone()
        try:
            assert x != type(None), "should not return a none"
        except:
            print ("get_system_from_station_ID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        y = x[0]
        return y

    def get_station_name_from_station_id(self, stationID):
        ''' Returns system id as an integer when passed a station ID
        '''
        #check input is a string
        try:
            assert type(stationID) is int, "requires a int"
        except:
            print ("you passed get_station_name_from_station_ID something that wasn't a int")
            raise
            sys.exit(0)
        self.curr.execute("select stationName from staStations where stationID = {id}".format(id = stationID))    
        x = self.curr.fetchone()
        try:
            assert x != type(None), "should not return a none"
        except:
            print ("get_station_name_from_station_ID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        y = x[0]
        return y
    
    def get_stations_from_system_id(self, systemID):
        ''' Returns a list of stations as an integer list  when passed a system ID
        '''
        #check input is a string
        try:
            assert type(systemID) is int, "requires a int"
        except:
            print ("you passed get_stations_from_system_ID something that wasn't a int")
            raise
            sys.exit(0) 
        self.curr.execute("select stationID from staStations where solarSystemID = {id}".format(id = systemID))    
        x = self.curr.fetchall()
        try:
            assert x != type(None), "should not return a none"
        except:
            print ("stations_from_system_ID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return (i[0] for i in x)   
    
    def get_system_name(self, interestingSystem):
        ''' Returns system name as a string when passed the system id as an integer
        '''
        try:
            assert type(interestingSystem) is int, "requires a int"
        except:
            print ("you passed get_system_name something that wasn't a integer")
            raise
        query = "select regionID, solarSystemID, solarSystemName from mapSolarSystems where solarSystemID = "
        strr = "\""
        self.curr.execute(strr.join([query, str(interestingSystem), ""]))    
        x = self.curr.fetchone()[2].encode('ascii', 'ignore')
        try:
            assert x != type(None), "requires  the databse to return somethign that isn't a non type"
            assert type(x) == str, "requires string"
        except:
            print ("the data base retruend a none type")
            raise
        return x
    '''
    inputTypes = []
    a = set(self.curr.execute('SELECT materialTypeID FROM invTypeMaterials').fetchall()) # all the input material types
    for b in a: # turn a into a list
        inputTypes.append(b[0])
        
    
    x = self.curr.execute('SELECT typeID, materialTypeID FROM invTypeMaterials').fetchall() # all manufacturable output
    for y in x:
        if y[0] not in inputTypes:
            print (y[0], "not in inputType", getItemName(y[0]))
        else: # y[1] is made only of un-manufactuable parts
            pass
    
    
    
    
        sqlite> SELECT * FROM invTypeMaterials WHERE typeID = 24698;
        
       
    
    #find BP from item type
    select typeID from industryActivityProducts where productTypeID = 11188;
    
    #find BP ID from item name
    select industryActivityProducts.typeID, (select invTypes.typeName from invTypes where invTypes.typeID =  industryActivityProducts.typeID)
    from invTypes
    inner join industryActivityProducts
    on industryActivityProducts.productTypeID = invTypes.typeID
    where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'EMP M')
    
    #find BP NAME from item name
    select invTypes.typeName
    from invTypes
    inner join industryActivityProducts
    on industryActivityProducts.productTypeID = invTypes.typeID
    where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'Anathema')
    
    ###
    #build from blueprint
    select invTypes.typeName, industryActivityMaterials.quantity, invTypes.typeID
    from invTypes
    INNER JOIN industryActivityMaterials
    ON  industryActivityMaterials.materialTypeID = invTypes.typeID
    WHERE industryActivityMaterials.typeID = 11189 AND activityID = 1;
    
    
    # get itemID from BlueprintId
    select productTypeID from  industryActivityProducts where typeID = 894;
    
    # reprocess from item ID
    select invTypes.typeName, invTypeMaterials.quantity, invTypes.typeID
    from invTypes
    INNER JOIN invTypeMaterials
    ON  invTypeMaterials.materialTypeID = invTypes.typeID
    WHERE invTypeMaterials.typeID = 11188;
    
    
    
    
    '''
    
    def get_corp_id(self, corpID):
        """ Returns an integer corresponding to the corporations ID when passed
            a string representation of that corporation.
            E.G. getCorpID("Acme Corp") returns 123456
            """
        try:
            assert type(corpID) is type(""), "requires a string"
        except:
            print ("you passed get_corp_id something that wasn't a string")
            raise
            sys.exit(0)
        self.curr.execute("SELECT invNames.itemID from invNames "
                     "INNER JOIN crpNPCCorporations ON crpNPCCorporations.corporationID = invNames.itemID "
                     "WHERE invNames.itemName = \"{id}\"".
                     format(id=corpID))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("get_corp_id didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0]

    def get_corp_name(self, corpID):
        """ Returns the string representation of a corp when passed the 
            corporation ID integer
            E.G. get_corp_name(123456) returns "Acme Corp"
        """
        try:
            assert type(corpID) is int, "requires a int"
        except:
            print ("you passed get_corp_name something that wasn't a int")
            raise
            sys.exit(0)
        self.curr.execute("SELECT invNames.itemName from invNames "
                     "INNER JOIN crpNPCCorporations ON crpNPCCorporations.corporationID = invNames.itemID "
                     "WHERE crpNPCCorporations.corporationID = \"{id}\"".
                     format(id=corpID))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("get_corp_name didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")
        
    def get_faction_name_from_corp_name(self, corp):
        """ Returns the string representation of a Faction when passed the 
            string representation of a member corp 
            E.G. get_faction_name_from_corp_name("Thukker Mix") returns "Thukker Tribe"
        """
        try:
            assert type(corp) is type(""), "requires a int"
        except:
            print ("you passed get_faction_name_from_corp_name something that wasn't a int")
            raise
            sys.exit(0)
        self.curr.execute("SELECT chrFactions.factionName "
                          "FROM chrFactions "
                     "INNER JOIN crpNPCCorporations ON crpNPCCorporations.factionID = chrFactions.factionID "
                     "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE invNames.itemName = \"{cp}\"".
                     format(cp=corp))  # Thukker Mix
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("get_faction_name_from_corp_name didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")
    
    # select faction from corp id
    def get_faction_name_from_corp_id(self, corpID):
        """ Returns the string representation of a Faction when passed the 
            integer representation of a member corp 
            E.G. get_faction_name_from_corp_id(654321) returns "Thukker Tribe"
        """
        try:
            assert type(corpID) is int, "requires a int"
        except:
            print ("you passed getFactionNameFromCorpID something that wasn't a int")
            raise
            sys.exit(0)
        self.curr.execute("SELECT chrFactions.factionName "
                     "FROM chrFactions "
                     "INNER JOIN crpNPCCorporations "
                     "ON crpNPCCorporations.factionID = chrFactions.factionID "
                     "INNER JOIN invNames "
                     "ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE invNames.itemID = {cp}; ".
                     format(cp=corpID))  # 1000160
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("get_faction_name_from_corp_id didn't find what you were looking for and "
                   "returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")      
    #chrFactions.factionID => for facrtionID      
    
    # select all corps for faction name
    def get_corps_from_faction_name(self, faction):
        """ Returns a list of integer corporation IDs when passed the string
            string representation of a Faction 
            E.G. get_corps_from_faction_name("Thukker Tribe") returns [123456, 1234567]
        """        
        try:
            assert type(faction) is str, "requires a string"
        except:
            print ("you passed get_corps_from_faction_name something that wasn't a string")
            raise
        self.curr.execute("SELECT crpNPCCorporations.corporationID FROM crpNPCCorporations "
                     "INNER JOIN chrFactions ON chrFactions.factionID = crpNPCCorporations.factionID "
                     "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE chrFactions.factionName = \"{fc}\";".
                    format(fc=faction))  # Thukker Tribe
        x = self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
            assert type(x) is list, "requires a list"
            assert len(x) > 0, "list must have length > 0"
        except:
            print ("get_corps_from_faction_name should return a list")
            raise
            sys.exit(0)
        return x
    
    def get_corps_from_faction_id(self, faction):
        """ Returns a list of integer corporation IDs when passed the string
            string representation of a Faction 
            E.G. get_corps_from_faction_id(987654) returns [123456, 1234567]
        """
        try:
            assert type(faction) is int, "requires a int"
        except:
            print ("you passed get_corps_from_faction_id something that wasn't a int")
            raise
        self.curr.execute("SELECT crpNPCCorporations.corporationID "
                     "FROM crpNPCCorporations "
                     "INNER JOIN chrFactions "
                     "ON chrFactions.factionID = crpNPCCorporations.factionID "
                     "INNER JOIN invNames "
                     "ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE chrFactions.factionID = {fc};".
                     format(fc=faction))  # 500015
        x = self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
            assert type(x) is list, "requires a list"
            assert len(x) > 0, "list must have length > 0"
        except:
            print ("get_corps_from_faction_id should return a list")
            raise
            sys.exit(0)
        return x

    def get_station_owners_from_system_id(self, sysID):
        """ Returns a integer list of all the corporation which own a station in
            the solar system, when the solarsystem is given as a int
            E.G. get_station_owners_from_system_id(30001) returns [123456, 1234567]
            """
        try:
            assert type(sysID) is int, "requires an int"
        except:
            print ("you passed get_station_owners_from_system_id something that wasn't a int")
            raise
        self.curr.execute("SELECT corporationID FROM staStations "
                        "WHERE solarSystemID = {id}".
                     format(id=sysID))
        x =self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
            assert type(x) is list, "requires a list"
            assert len(x) > 0, "list must have length > 0"
        except:
            print ("get_station_owners_from_system_id returned something unexpected")
            raise
            sys.exit(0)
        return x
        
    
    def get_station_owner_from_station_id(self, sysID):
        """ Returns a single integer for the corporation which owns  the station
            given by the station ID, which is also a int
            E.G. get_station_owner_from_station_id(9998789) returns 123456
            """        
        try:
            assert type(sysID) is int, "requires a int"
        except:
            print ("you passed get_station_owner_from_station_id something that wasn't a int")
            raise
        self.curr.execute("SELECT corporationID FROM staStations WHERE stationID = {id}".
                     format(id=sysID))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a int not a none"
        except:
            print ("get_station_owner_from_station_id returned something unexpected")
            raise
            sys.exit(0)
        return x[0]
    
    ''' find BP ID from item name
    select industryActivityProducts.typeID, (select invTypes.typeName from invTypes where invTypes.typeID =  industryActivityProducts.typeID)
    from invTypes
    inner join industryActivityProducts
    on industryActivityProducts.productTypeID = invTypes.typeID
    where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'Anathema')
    '''
    def get_bp_id_from_name(self, itemName):
        try:
            assert type(itemName) is str, "requires a str"
        except:
            print ("you passed get_bp_id_from_name something that wasn't a string")
            raise
        self.curr.execute("SELECT invTypes.typeID " 
                     "FROM invTypes "
                     "INNER JOIN industryActivityProducts "
                     "ON industryActivityProducts.productTypeID = invTypes.typeID "
                     "WHERE industryActivityProducts.productTypeID = "
                     "(SELECT typeID from invTypes where typeName = \"{nm}\")".
                     format(nm=itemName))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a int not a none"
        except:
            print ("get_bp_id_from_name returned something unexpected")
            raise
            sys.exit(0)
        return x[0]
    
   
    
    ''' find BP NAME from item name
    select invTypes.typeName
    from invTypes
    inner join industryActivityProducts
    on industryActivityProducts.productTypeID = invTypes.typeID
    where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'Anathema')
    '''
    def get_bp_name_from_name(self, itemName):
        """ Returns the item id of the blue print of the item's name you passed
            it.  You pass it the item's name, it works out which blue print it
            is made from and returns the item ID for the blueprint            
            EG: get_bp_name_from_name("Punisher") returns 578 
        """
        try:
            assert type(itemName) is str, "requires a str"
        except:
            print ("you passed get_bp_name_from_name something that wasn't a string")
            raise
        self.curr.execute("SELECT "
                     "(select invTypes.typeName from invTypes where invTypes.typeID =  industryActivityProducts.typeID) "
                     "from invTypes "
                     "inner join industryActivityProducts "
                     "on industryActivityProducts.productTypeID = invTypes.typeID "
                     "where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = \"{n}\")".
                     format(n=itemName))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a str not a none"
        except:
            print ("get_bp_name_from_name returned something unexpected")
            raise
            sys.exit(0)
        return x[0].encode("ascii", "ignore")
    
    ''' find BP from item type
    select typeID from industryActivityProducts where productTypeID = 969;
    '''
    def getBpFromID(self, itemID):
        """ Returns the item ID for the blue print of the item of interest. 
            Accepts a integer as the items type id
        """
        try:
            assert type(itemID) is int, "requires a int"
        except:
            print ("you passed getBpFromID something that wasn't a int")
            raise
        self.curr.execute("SELECT typeID FROM industryActivityProducts "
                     "WHERE productTypeID = {id}".
                     format(id=itemID))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a str not a none"
        except:
            print ("getBpFromID returned something unexpected")
            raise
            sys.exit(0)
        return x[0]
        
    # findBpFromID(624) 
    
    ''' build from blueprint
    select invTypes.typeName, industryActivityMaterials.quantity, invTypes.typeID
    from invTypes
    INNER JOIN industryActivityMaterials
    ON  industryActivityMaterials.materialTypeID = invTypes.typeID
    WHERE industryActivityMaterials.typeID = 969 AND activityID = 1;
    '''
    def mats_for_bp(self, bpID):
        """ Returns a dictionary of the materials required to build the item
            given in the blue print IDs output.
        """
        try:
            assert type(bpID) is int, "requires a int"
        except:
            print ("you passed mats_for_bp something that wasn't a int")
            raise
        mats = {}
        self.curr.execute("SELECT invTypes.typeID, industryActivityMaterials.quantity "
                     "FROM invTypes "
                     "INNER JOIN industryActivityMaterials "
                     "ON  industryActivityMaterials.materialTypeID = invTypes.typeID "
                     "WHERE industryActivityMaterials.typeID = {id} AND activityID = 1".
                     format(id=bpID))
        x = (self.curr.fetchall())
        try:
            assert type(x) != type(None), "Requires a str not a none"
        except:
            print ("mats_for_bp returned something unexpected")
            raise
            sys.exit(0)
        for y in x:
            mats[y[0]] = y[1]
        return mats
    
    def get_reproc_output(self, itemID):
        """returns a dictionary of the materials obtained when recycling a module etc
            Accepts a integer, as the itemID as input
        """
        try:
            assert type(itemID) is int, "get_reproc_output accepts only integers"
        except:
            print ("you passed get_reproc_output something unexpected") 
        mats = {}
        self.curr.execute("SELECT materialTypeID, quantity "
                          "from invTypeMaterials "
                          "where typeID = {id}".
                          format(id = itemID))
        x = self.curr.fetchall()
        mats = {}
        try:
            assert type(x) != type(None), "Requires a list not a none"
        except:
            print ("get_reproc_output returned something unexpected")
            raise
            sys.exit(0)
        for keys, values in x:
            mats[keys] = values
        return mats        
    # station services from station id
   
    def print_items_in_group(self, id):
        """ prints all the items in the market group, when passed the market 
            group as an integer.  Does not search recursively for sub-groups
        """
        print (">", id)
        self.curr.execute("SELECT typeID, typeName FROM invTypes "
                            "WHERE marketGroupID = {id}".
                            format(id = id))
        items = self.curr.fetchall()
        for x in items:
            print ("*", x[1])
   
    def get_root_market_groups(self):
        """ returns a list of group ids which correspond to the root martket
             groups.  These groups have no parent and are the top of the market
             view in-game.  Requires no input
        """
        values = []
        self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                     "WHERE parentGroupID is Null "
                     "ORDER BY marketGroupName")
        marketRoot = self.curr.fetchall()
        return [i[0] for i in marketRoot]
    
    def get_childs_from_market_group_id(self, id="Null"):
        """ Returns as a list all of the child groups within the market group 
            id passed to this function.  Also prints the recursive lookup of the
            child groups and the items contained within them.  
        """
        self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
            "WHERE parentGroupID = {id} "
            "ORDER BY marketGroupName".
            format(id = id))
        parents = self.curr.fetchall()
        for x in parents:
            print (x)
            self.print_items_in_group(x[0])
            self.get_childs_from_market_group_id(x[0])
    
    def get_market_group_from_type_id(self, id):
        """ when passed a item id as an int returns as an integer the market
            group this item belongs to.
        """
        self.curr.execute("SELECT marketGroupID from invTypes WHERE typeID = {id}".
                          format(id = id))
        group = self.curr.fetchone()
        return group[0]

    def get_items_in_group(self, group):
        """ returns a list of integers corresponging to the item IDs of the
        items in the given market group
        """
        self.curr.execute("SELECT typeID FROM invTypes "
                        "WHERE marketGroupID = {grp}".format(grp = group))
        results = self.curr.fetchall()
        return [i[0] for i in results]
    
    
    '''
    SELECT staServices.serviceName from staServices
    INNER JOIN staOperationServices ON staOperationServices.serviceID = staServices.serviceID 
    INNER JOIN staStations ON staStations.operationID = staOperationServices.operationID
    WHERE staStations.stationID = 60004516
    '''
    def get_all_market_groups(self):
        """ prints the whole market and returns the root market groups.  These
            are the market groups which have no parents.
        """
        self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                     "WHERE parentGroupID is Null "
                     "ORDER BY marketGroupName")
        marketRoot = self.curr.fetchall()
        for catagories in marketRoot:
            print (catagories[1])
            self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                "WHERE parentGroupID = {id} "
                "ORDER BY marketGroupName".
                format(id = catagories[0]))            
            catagories = self.curr.fetchall()
            for subCatagories in catagories:
                print (">", subCatagories[1])
                self.curr.execute("SELECT typeID, typeName FROM invTypes "
                                  "WHERE marketGroupID = {id}".
                                  format(id = subCatagories[0]))
                items = self.curr.fetchall()
                for x in items:
                    print ("*", x[1])
                self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                "WHERE parentGroupID = {id} "
                "ORDER BY marketGroupName".
                format(id = subCatagories[0]))
                groups = self.curr.fetchall()
                for subGroup in groups:
                    print (">>", subGroup[1])
                    self.curr.execute("SELECT typeID, typeName FROM invTypes "
                                      "WHERE marketGroupID = {id}".
                                      format(id = subGroup[0]))
                    items = self.curr.fetchall()
                    #for x in items:
                        #print ("*", x[1])
                    self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                                      "WHERE parentGroupID = {id} "
                                      "ORDER BY marketGroupName".
                                      format(id = subGroup[0]))
                    x = self.curr.fetchall()
                    for xx in x:
                        print (">>>", xx[1])
                        self.curr.execute("SELECT typeID, typeName FROM invTypes "
                                          "WHERE marketGroupID = {id}".
                                          format(id = xx[0]))
                        items = self.curr.fetchall()
                        #for x in items:
                           # print ("*", x[1])
                        self.curr.execute("SELECT marketGroupID, marketGroupName from invMarketGroups "
                                      "WHERE parentGroupID = {id} "
                                      "ORDER BY marketGroupName".
                                      format(id = xx[0]))
                        y = self.curr.fetchall()
                        for yy in y:
                            print (">>>>", yy[1])
                            self.curr.execute("SELECT typeID, typeName FROM invTypes "
                                             "WHERE marketGroupID = {id}".
                                             format(id = xx[0]))
                            items = self.curr.fetchall()
                            #for x in items:
                                #print ("*", x[1])
        return marketRoot
    
    def purge_inv_types(self):
        """ prints the id and name for all items in the invTypes table
        """
        location1 = "/home/adam/Documents/eve/native/eve.db"
        conn = sqlite3.connect(location1)
        curr = conn.cursor()
        curr.execute("SELECT typeID, typeName FROM invTypes")
        x = curr.fetchall()
        for y in x:
            print (y)
            
    def find_low_slots(self):
        """ returns a list of integers corresponding to the itemID of all the 
            modules which are fitted to ships in low slots
        """
        self.curr.execute("SELECT dgmTypeEffects.typeID "
                          "FROM dgmTypeEffects "
                          "JOIN dgmEffects " 
                          "ON dgmTypeEffects.effectID = dgmEffects.effectID "
                          "WHERE dgmTypeEffects.effectID = 11")
        x = self.curr.fetchall()
        return [i[0] for i in x]


    def find_mid_slots(self):
        """ returns a list of integers corresponding to the itemID of all the 
            modules which are fitted to ships in medium slots
        """
        self.curr.execute("SELECT dgmTypeEffects.typeID "
                          "FROM dgmTypeEffects "
                          "JOIN dgmEffects " 
                          "ON dgmTypeEffects.effectID = dgmEffects.effectID "
                          "WHERE dgmTypeEffects.effectID = 13")
        x = self.curr.fetchall()
        return [i[0] for i in x]             
        
    def find_high_slots(self):
        """ returns a list of integers corresponding to the itemID of all the 
            modules which are fitted to ships in high slots
        """
        self.curr.execute("SELECT dgmTypeEffects.typeID "
                          "FROM dgmTypeEffects "
                          "JOIN dgmEffects " 
                          "ON dgmTypeEffects.effectID = dgmEffects.effectID "
                          "WHERE dgmTypeEffects.effectID = 12")
        x = self.curr.fetchall()
        return [i[0] for i in x]
            
    def find_slot_size(self, id):
        """ prints the fitting size (low, med, high)of a module when passed the
            itemID as an int
        """
        self.curr.execute("SELECT dgmTypeEffects.effectID "
                          "FROM dgmTypeEffects "
                          "WHERE dgmTypeEffects.typeID = {id} "
                          "AND "
                          "(dgmTypeEffects.effectID = 11 OR dgmTypeEffects.effectID = 12 "
                          "OR dgmTypeEffects.effectID = 13)".
                          format(id = id))
        x = self.curr.fetchall()
        for y in x:
            print (y[0])
            
    def find_meta_mods(self, metalevel):
        """ returns a list of integers corresponding to the item IDs of items
            with the meta level
        """
        self.curr.execute("SELECT invTypes.typeID "
        "FROM invTypes "
        "JOIN dgmTypeAttributes "
        "ON invTypes.typeID = dgmTypeAttributes.typeID "
        "WHERE (dgmTypeAttributes.attributeID = 633 AND dgmTypeAttributes.valueInt = {lvl})".
        format(lvl = metalevel))
        x = self.curr.fetchall()
        return [i[0] for i in x]

    def print_meta3_mods(self):
        """ prints all meta3 mods, irrespective of their size
        """
        queries = SDEQueries()
        #queries.find_slot_size(1952)
        highmods = set(queries.find_high_slots())
        meta3mods = set(queries.find_meta_mods(3))
        results = highmods.intersection(meta3mods)
        for x in results:
            print (queries.get_item_name(x))
        print ("#####")
        midmods = set(queries.find_mid_slots())
        results = midmods.intersection(meta3mods)
        for x in results:
            print (queries.get_item_name(x))
        print ("####")
        lowmods = set(queries.find_low_slots())
        results = lowmods.intersection(meta3mods)
        for x in results:
            print (queries.get_item_name(x))       

    def find_agents(self, systemID):
        """ returns a list of agent details for a given system when the system
            ID is a int
        """
        try:
            assert type(systemID) is int, "find_level_3_agents accepts only integers"
        except:
            print ("you passed find_level_3_agents something unexpected") 
        stations = self.get_stations_from_system_id(systemID)
        self.curr.execute("SELECT agentID, staStations.solarSystemID , agtAgents.divisionID, locationID, level, agentTypeId "
                          "FROM agtAgents "
                          "JOIN crpNPCDivisions "
                          "ON agtAgents.divisionID = crpNPCDivisions.divisionID "
                          "JOIN staStations "
                          "ON agtAgents.locationID = staStations.stationID "
                          "WHERE staStations.solarsystemID = {id} ".
                          format(id = systemID))
        agents = self.curr.fetchall()
        try:
            assert type(agents) != type(None), "Requires a list not a none"
        except:
            print ("find_agents returned something unexpected")
            raise
            sys.exit(0)
        return agents
    
    def find_high_level_agents(self, systemID):
        """ returns a list of details for all the agents when given a siystem ID
            as a int.  Where agents are level 3 and above and combat related
        """
        try:
            assert type(systemID) is int, "find_level_3_agents accepts only integers"
        except:
            print ("you passed find_level_3_agents something unexpected") 
        stations = self.get_stations_from_system_id(systemID)
        self.curr.execute("SELECT agentID, staStations.solarSystemID , agtAgents.divisionID, locationID, level, quality "
                          "FROM agtAgents "
                          "JOIN crpNPCDivisions "
                          "ON agtAgents.divisionID = crpNPCDivisions.divisionID "
                          "JOIN staStations "
                          "ON agtAgents.locationID = staStations.stationID "
                          "WHERE (staStations.solarsystemID = {id} "
                          "AND level > 2 "
                          "AND (agtAgents.divisionID = 24 OR agtAgents.divisionID =  28 OR agtAgents.divisionID =  29))".
                          format(id = systemID))
        agents = self.curr.fetchall()
        try:
            assert type(agents) != type(None), "Requires a list not a none"
        except:
            print ("find_agents returned something unexpected")
            raise
            sys.exit(0)
        return agents
        
        
        
    def get_division_name(self, divID):
        """ returns a sting corresponding to the name of the NPCs coporation
            name
        """
        try:
            assert type(divID) is int, "get_division_name accepts only integers"
        except:
            print ("you passed get_division_name something unexpected")         
        self.curr.execute("SELECT divisionName FROM crpNPCDivisions "
                          "WHERE divisionID = {id}".
                          format(id = divID))
        x = self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
        except:
            print ("get_division_name returned something unexpected")
            raise
            sys.exit(0)
        print (x)                    
        return x[0][0]

    def print_high_agents_by_system(self, systemID):
        """ prints a list of details for all the agents above level 3
            who are combat related
        """
        x = self.find_high_level_agents(self.get_system_id(systemID))
        for y in x:
            print (
                   y[0],
                   self.get_system_name(y[1]),
                   self.get_division_name(y[2]),
                   self.get_station_name_from_station_id(y[3]),
                   y[4],
                   y[5]
                   )

def main():
    queries = SDEQueries()
    #queries.find_slot_size(1952)
    stations = queries.get_stations_from_system_id(30002385)
    queries.print_high_agents_by_system("Teonusude")
    queries.print_high_agents_by_system("Gelfiven")
    queries.print_high_agents_by_system("Gulfonodi")
    queries.print_high_agents_by_system("Nakugard")
    queries.print_high_agents_by_system("Tvink")
    queries.print_high_agents_by_system("Lanngisi")
    queries.print_high_agents_by_system("Magiko")
    queries.print_high_agents_by_system("Vullat")
    queries.print_high_agents_by_system("Eystur")
    queries.print_high_agents_by_system("Hek")
    queries.print_high_agents_by_system("Lustrevik")
    queries.print_high_agents_by_system("Hror")
    queries.print_high_agents_by_system("Otou")
    queries.print_high_agents_by_system("Nakugard")
    queries.print_high_agents_by_system("Uttindar")
    
    

    
    
    
    #queries.find_slot_size(1952)



if __name__ == "__main__":
    sys.exit(main())

#queries = SDEQueries()

#x = queries.get_all_market_groups()

#queries = SDEQueries()
#queries.get_item_id("Anathema")
#x = queries.get_all_market_groups()






"""
queries.get_all_market_groups()

print (queries.getBpFromID(451))

x = queries.getItemID("Alumel Gravimetric ECCM Sensor Array I")
print (x)

print (queries.getReprocOutput(x))

"""
   

#x = queries.get_all_market_groups()


#x = queries.get_all_market_groups()



"""
print (queries.getItemName(13))
print (queries.getItemID(queries.getItemName(13)))

print (queries.findBpIdFromName("Anathema"))

print ()

print (queries.corpsFromFactionid(500015))

for x in queries.corpsFromFactionid(500015):
    print (x)
    
print ()

for x in queries.corpsFromFactionid(500015):
    print (queries.corpFromID(x[0]))
"""