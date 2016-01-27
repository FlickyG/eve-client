'''
Created on 22 Jan 2016

@author: adam
'''
import sqlite3, sys

class SDEQueries(object):
    def __init__(self):
        self.conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
        self.curr = self.conn.cursor()

    def getItemID(self, interestingItem):
        """ reurns the item ID when passed a string represtning ther item's Name
            
        """
        # Check input is a string
        try:
            assert type(interestingItem) is type(""), "requires a string"
        except:
            print ("you passed getItemID something that wasn't a string")
            raise
            sys.exit(0)
        query = "SELECT typeID, typeName FROM invTypes WHERE typeName = "
        strr = "\""
        self.curr.execute(strr.join([query, interestingItem, ""])) 
        x = self.curr.fetchone()
        print ("x", x)
        #check database doesn't return a none type
        try:
            assert x[0] != type(None)
        except:
            print ("getItemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0)           
        y = x[0]
        return y
    
    def getItemName(self, interestingItem):
        """ Returns the item's Name when passed it's integer representation
        """
        # Check input is a string
        try:
            assert type(interestingItem) is int, "requires a integer"
            assert interestingItem > 0, "requires a integer"
        except:
            print ("you passed getItemName something that wasn't an int")
            raise
            sys.exit(0)
        query = "SELECT typeID, typeName FROM invTypes WHERE typeID = "
        strr = "\""
        self.curr.execute(strr.join([query, str(interestingItem), ""]))     
        x = self.curr.fetchone()
        try:
            assert x[1] != type(None)
        except:
            print ("getItemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0)   
        return x[1].encode('ascii', 'ignore')
    
    def getRegionID(self, interestingRegion):
        ''' Returns the Region ID when given the string representation
        '''
        # check input is a string
        try:
            assert type(interestingRegion) is type(""), "requires a string"
        except:
            print ("you passed getRegionID somethig that wasn't a string")
            raise 
            sys.exit(0)
        self.curr.execute("select regionName, regionID from mapRegions where regionName = \"{id}\"".
                           format(id = str(interestingRegion)))
        x = self.curr.fetchone()
        print (x)
        try:
            assert x[1] != type(None), "requires not a none type"
        except:
            print("getRegionID couldn't find what you were looking for and returned a NoneType")
            raise
        y = x[1] 
        return y
    
    def getRegionName(self, interestingRegion):
        ''' Returns Region Name when given a numerical ID
        '''
        #Check input is a int
        try:
            assert type(interestingRegion) is int, "requires a string"
        except:
            print ("getRegionName requires an int")
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
            print ("getRegionName returned a non type") 
            raise
            sys.exit(0)
        return y
    
    def getSystemID(self, interestingSystem):
        ''' Returns system id as an integer when passed the region name as a string
        '''
        #check input is a string
        try:
            assert type(interestingSystem) is type(""), "requires a string"
        except:
            print ("you passed getSystemID something that wasn't a string")
            raise
            sys.exit(0)
        query = "select regionID, solarSystemID, solarSystemName from mapSolarSystems where solarSystemName ="
        strr = "\""
        self.curr.execute(strr.join([query, interestingSystem, ""]))    
        x = self.curr.fetchone()
        try:
            assert x != type(None), "should not return a none"
        except:
            print ("getSystemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        y = x[1]
        return y
    
    def getSystemName(self, interestingSystem):
        ''' Returns system name as a string when passed the system id as an integer
        '''
        try:
            assert type(interestingSystem) is int, "requires a int"
        except:
            print ("you passed getSystemName something that wasn't a integer")
            raise
        query = "select regionID, solarSystemID, solarSystemName from mapSolarSystems where solarSystemID = "
        strr = "\""
        self.curr.execute(strr.join([query, str(interestingSystem), ""]))    
        x = self.curr.fetchone()[2].encode('ascii', 'ignore')
        try:
            print ("x is", x)
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
    # get corp name from corp id
    def getCorpID(self, corpID):
        try:
            assert type(corpID) is type(""), "requires a string"
        except:
            print ("you passed getSystemID something that wasn't a string")
            raise
            sys.exit(0)
        self.curr.execute("SELECT invNames.itemID from invNames "
                     "INNER JOIN crpNPCCorporations ON crpNPCCorporations.corporationID = invNames.itemID "
                     "WHERE invNames.itemName = \"{id}\"".
                     format(id=corpID))
        x = self.curr.fetchone()
        try:
            print ("x is ", x, type(x))
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("getSystemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0]

    def getCorpName(self, corpID):
        try:
            assert type(corpID) is int, "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
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
            print ("getSystemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")
    
        
    # select faction details from corp name
    
    def getFactionNameFromCorpName(self, corp):
        try:
            assert type(corp) is type(""), "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
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
            print ("x is ", type(x), x)
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("getSystemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")
    
    # select faction from corp id
    def getFactionNameFromCorpID(self, corpID):
        try:
            assert type(corpID) is int, "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
            raise
            sys.exit(0)
        self.curr.execute("SELECT chrFactions.factionName "
                     "FROM chrFactions "
                     "INNER JOIN crpNPCCorporations ON crpNPCCorporations.factionID = chrFactions.factionID "
                     "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE invNames.itemID = {cp}; ".
                     format(cp=corpID))  # 1000160
        x = self.curr.fetchone()
        try:
            print ("x is ", x, type(x))
            assert type(x) != type(None), "corpID should not return a none"
        except:
            print ("getSystemID didn't find what you were looking for and returned a None")
            raise
            sys.exit(0) 
        return x[0].encode("ascii", "ignore")      
    #chrFactions.factionID => for facrtionID      
    
    # select all corps for faction name
    def getCorpsFromFactionName(self, faction):
        try:
            assert type(faction) is str, "requires a string"
        except:
            print ("you passed getSystemID something that wasn't a string")
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
            print ("getCorpsFromFactionName should return a list")
            raise
            sys.exit(0)
        return x
            
    
    # select all corps for faction ID
    
    def getCorpsFromFactionID(self, faction):
        try:
            assert type(faction) is int, "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
            raise
        self.curr.execute("SELECT crpNPCCorporations.corporationID "
                     "FROM crpNPCCorporations "
                     "INNER JOIN chrFactions ON chrFactions.factionID = crpNPCCorporations.factionID "
                     "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                     "WHERE chrFactions.factionID = {fc};".
                     format(fc=faction))  # 500015
        x = self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
            assert type(x) is list, "requires a list"
            assert len(x) > 0, "list must have length > 0"
        except:
            print ("getCorpsFromFactionID should return a list")
            raise
            sys.exit(0)
        return x
    
    # find station owner from sytemID
    
    def getStationOwnersFromSystemID(self, sysID):
        try:
            assert type(sysID) is int, "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
            raise
        self.curr.execute("SELECT corporationID FROM staStations WHERE solarSystemID = {id}".
                     format(id=sysID))
        x =self.curr.fetchall()
        try:
            assert type(x) != type(None), "Requires a list not a none"
            assert type(x) is list, "requires a list"
            assert len(x) > 0, "list must have length > 0"
        except:
            print ("getStationOwnersFromSystemID returned something unexpected")
            raise
            sys.exit(0)
        return x
        
    
    def getStationOwnerFromStationID(self, sysID):
        try:
            assert type(sysID) is int, "requires a int"
        except:
            print ("you passed getSystemID something that wasn't a int")
            raise
        self.curr.execute("SELECT corporationID FROM staStations WHERE stationID = {id}".
                     format(id=sysID))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a int not a none"
        except:
            print ("getStationOwnerFromStationID returned something unexpected")
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
    def getBpIdFromName(self, itemName):
        try:
            assert type(itemName) is str, "requires a str"
        except:
            print ("you passed getBpIDFromName something that wasn't a string")
            raise
        self.curr.execute("SELECT invTypes.typeID " 
                     "FROM invTypes "
                     "INNER JOIN industryActivityProducts "
                     "ON industryActivityProducts.productTypeID = invTypes.typeID "
                     "WHERE industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = \"{nm}\")".
                     format(nm=itemName))
        x = self.curr.fetchone()
        try:
            assert type(x) != type(None), "Requires a int not a none"
        except:
            print ("getBpIdFromName returned something unexpected")
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
    def getBpNameFromName(self, itemName):
        try:
            assert type(itemName) is str, "requires a str"
        except:
            print ("you passed getBpIDFromName something that wasn't a string")
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
            print ("getBpNameFromName returned something unexpected")
            raise
            sys.exit(0)
        return x[0].encode("ascii", "ignore")
    
    ''' find BP from item type
    select typeID from industryActivityProducts where productTypeID = 969;
    '''
    def getBpFromID(self, itemID):
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
    def matsForBp(self, bpID):
        try:
            assert type(bpID) is int, "requires a int"
        except:
            print ("you passed matsForBp something that wasn't a int")
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
            print ("matsForBp returned something unexpected")
            raise
            sys.exit(0)
        for y in x:
            mats[y[0]] = y[1]
        return mats
    
    # station services from station id
    '''
    SELECT staServices.serviceName from staServices
    INNER JOIN staOperationServices ON staOperationServices.serviceID = staServices.serviceID 
    INNER JOIN staStations ON staStations.operationID = staOperationServices.operationID
    WHERE staStations.stationID = 60004516
    '''
    def getAllMarketGroups(self):
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
                    for x in items:
                        print ("*", x[1])
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
                        for x in items:
                            print ("*", x[1])
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
                            for x in items:
                                print ("*", x[1])
        return marketRoot

                
        




queries = SDEQueries()
x = queries.getAllMarketGroups()

'''
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
'''