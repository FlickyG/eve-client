# /bin/python


from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
from django.db.transaction import on_commit
standard_library.install_aliases()
from builtins import str
from builtins import object

import sqlite3, eveapi, requests, requests_cache, time
import untangle
import json, requests, pprint
import tempfile
import pickle
import zlib
import os
from os.path import join, exists


# EVE API Stuff
charKeys = [{"CHAR_KEYID" : 4958524,
            "CHAR_VCODE" :  "njXdwQdNFNlf47TfOAnbNuHP6gX7sJeArgD2AEk1Qpay1tkUagUMyStSriZPQqd0",
            "CHAR_AMASK" : 1073741823,
            }]
# Corp
corpKeys = {"CORP_KEYID" : 1383071,
            "CORP_VCODE" : "m0ecx5e1r8RCMsizNKXyB91HQchkHjJmNJlG8or0xy3VvkpiAJj1J7wXb70lUMm0",
            "CORP_AMASK" : 268435455,
            }

TRADE_SKILLS = ["Accounting", "Broker Relations", "Contracting", "Corporation Contracting",
                  "Customs Code Expertise", "Daytrading", "Margin Trading", "Marketing",
                  "Procurement", "Retail", "Trade", "Tycoon", "Visibility", "Wholesale"]

PROD_SKILLS = ["Advanced Industrial Ship Construction", "Advanced Industry", "Advanced Large Ship Construction",
               "Advanced Mass Production", "Advanced Medium Ship Construction", "Advanced Small Ship Construction",
               "Capital Ship Construction", "Drug Manufacturing", "Industry", "Mass Production", "Outpost Construction",
               "Supply Chain Management"]

SCIENCE_SKILLS = ["Advanced Laboratory Operation", "Amarr Encryption Methods", "Amarr Starship Engineering",
                  "Astronautic Engineering    Intelligence", "Caldari Encryption Methods", "Caldari Starship Engineering",
                  "Defensive Subsystem Technology", "Electromagnetic Physics", "Electronic Engineering", "Electronic Subsystem Technology",
                  "Engineering Subsystem Technology", "Gallente Encryption Methods", "Gallente Starship Engineering", "Graviton Physics",
                  "High Energy Physics", "Hydromagnetic Physics", "Laboratory Operation", "Laser Physics", "Mechanical Engineering",
                  "Metallurgy", "Minmatar Encryption Methods", "Minmatar Starship Engineering", "Molecular Engineering", "Nanite Engineering",
                  "Nuclear Physics", "Offensive Subsystem Technology", "Plasma Physics    ", "Propulsion Subsystem Technology", "Quantum Physics",
                  "Research", "Research Project Management", "Rocket Science", "Science Intelligence", "Scientific Networking", "Sleeper Encryption Methods",
                  "Sleeper Technology", "Takmahl Technology", "Talocan Technology", "Yan Jung Technology"]

REPROC_SKILLS = ["Arkonor Processing", "Astrogeology", "Bistot Processing", "Crokite Processing", "Dark Ochre Processing", "Deep Core Mining",
                 "Gas Cloud Harvesting", "Gneiss Processing", "Hedbergite Processing", "Hemorphite Processing", "Ice Harvesting", "Ice Processing",
                 "Industrial Reconfiguration", "Jaspet Processing", "Kernite Processing", "Mercoxite Processing", "Mining", "Mining Upgrades",
                 "Omber Processing", "Plagioclase Processing", "Pyroxeres Processing", "Reprocessing", "Reprocessing Efficiency", "Salvaging",
                 "Scordite Processing", "Scrapmetal Processing", "Spodumain Processing", "Veldspar Processing"] 
           


# Test PSQL connectivity
conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
curr = conn.cursor()

##########################
# EVE API 
##########################
eveapi.set_user_agent("eveapi.py/1.3")

class MyCacheHandler(object):  # for eve api calls
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
            # print "'%s': retrieving from memory" % path
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

cachedApi = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True))

def getAllCharacters():
    MY_CHARACTERS = {}
    # get the skill tree once, and reuse it for all characters
    skilltree = cachedApi.eve.SkillTree()
    # in case there are multiple accounts, or multiple keys
    for allKeys in charKeys:
        auth = cachedApi.auth(keyID=allKeys["CHAR_KEYID"], vCode=allKeys["CHAR_VCODE"])
        theseCharacters = auth.account.Characters()
        # get names etc for each key set with their keys so we can look them up later
        for theCharacters in theseCharacters.characters:
            # print (theCharacters.name, theCharacters.characterID, theCharacters.corporationName, 
                   # theCharacters.corporationID, allKeys["CHAR_KEYID"], allKeys["CHAR_VCODE"])
            localDict = {"name" : theCharacters.name,
                         "charID" : theCharacters.characterID,
                         "corpName" : theCharacters.corporationName,
                         "corpID" : theCharacters.corporationID,
                         "charKey" : allKeys["CHAR_KEYID"],
                         "charVCode" : allKeys["CHAR_VCODE"]}
            # print (localDict["charVCode"])
            # get the skills for each character
            myCharacterSheet = auth.character(theCharacters.characterID).CharacterSheet()
            # print ("HELLO", myCharacterSheet.name)
            # Now the fun bit starts. We walk the skill tree, and for every group in the
            # tree...
            sp = [0, 250, 1414, 8000, 45255, 256000]
            total_sp = 0
            total_skills = 0
            for g in skilltree.skillGroups:
                skills_trained_in_this_group = False
                # ... iterate over the skills in this group...
                for skill in g.skills:
                    # see if we trained this skill by checking the character sheet object
                    trained = myCharacterSheet.skills.Get(skill.typeID, False)
                    if trained:
                        # yep, we trained this skill.
                        # print the group name if we haven't done so already
                        if not skills_trained_in_this_group:
                            skills_trained_in_this_group = True
                        # and display some info about the skill!
                        total_skills += 1
                        total_sp += trained.skillpoints
                        localDict[skill.typeName] = trained.level
                    else:
                        localDict[skill.typeName] = 0
            # get standings
            theseCharacters = auth.character(theCharacters.characterID).Standings()
            for npcCorp in theseCharacters.characterNPCStandings.NPCCorporations:
                localDict[npcCorp.fromName] = npcCorp.standing
            for npcFactions in theseCharacters.characterNPCStandings.factions:
                localDict[npcFactions.fromName] = npcFactions.standing
            MY_CHARACTERS[theCharacters.name] = localDict
    return MY_CHARACTERS

ALL_CHARS = getAllCharacters()
# get standings
def getStandingName(char, corp):
    if char in ALL_CHARS:
        if corp in ALL_CHARS[char]:
            s = ALL_CHARS[char][corp]
        else:
            print ("corp not in all chars")
            f = factionNameFromCorpName(corp)
            s = ALL_CHARS[char][f]
        return s
    else:
        print ("char not in all chars")
  
def printInterstingSkills(characters):
    for x in characters:
        print (x["name" ])
        for skill in TRADE_SKILLS:
            if (skill in x) and (x[skill] != 0):
                print (">>", skill, x[skill])

def getAllStandings():
    for allKeys in MY_CHARACTERS:
        # print (allKeys["name"])
        auth = cachedApi.auth(keyID=allKeys["charKey"], vCode=allKeys["charVCode"])
        theseCharacters = auth.character(allKeys["charID"]).Standings()
        # for x in theseCharacters.characterNPCStandings.NPCCorporations:
        #    print (x.fromName, x.standing)

####################
# Get Dabase Results
####################
def getItemId(interestingItem):
    # gets the item ID when passed a striong represtning ther item of interes
    query = "SELECT typeID, typeName FROM invTypes WHERE typeName = "
    strr = "\""
    curr.execute(strr.join([query, interestingItem, ""])) 
    x = curr.fetchone()
    y = x[0]
    return y

def getItemName(interestingItem):
    query = "SELECT typeID, typeName FROM invTypes WHERE typeID = "
    strr = "\""
    curr.execute(strr.join([query, str(interestingItem), ""]))     
    x = curr.fetchone()
    return x[1]
def getRegionID(interestingRegion):
    query = "select regionName, regionID from mapRegions where regionName ="
    strr = "\""
    curr.execute(strr.join([query, interestingRegion, ""]))     
    x = curr.fetchone()
    y = x[1]
    return y

def getRegionName(interestingRegion):
    query = "select regionName, regionID from mapRegions where regionID = "
    strr = "\""
    curr.execute(strr.join([query, str(interestingRegion), ""]))     
    x = curr.fetchone()
    y = x[0]
    return y

def getSystemID(interestingSystem):
    query = "select regionID, solarSystemID, solarSystemName from mapSolarSystems where solarSystemName ="
    strr = "\""
    curr.execute(strr.join([query, interestingSystem, ""]))    
    x = curr.fetchone()
    y = x[1]
    return y

def getSystemName(interestingSystem):
    query = "select regionID, solarSystemID, solarSystemName from mapSolarSystems where solarSystemID = "
    strr = "\""
    curr.execute(strr.join([query, str(interestingSystem), ""]))    
    x = curr.fetchone()
    y = x[2]
    return y
'''
inputTypes = []
a = set(curr.execute('SELECT materialTypeID FROM invTypeMaterials').fetchall()) # all the input material types
for b in a: # turn a into a list
    inputTypes.append(b[0])
    

x = curr.execute('SELECT typeID, materialTypeID FROM invTypeMaterials').fetchall() # all manufacturable output
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
def corpFromID(corpID):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT invNames.itemName from invNames "
                 "INNER JOIN crpNPCCorporations ON crpNPCCorporations.corporationID = invNames.itemID "
                 "WHERE crpNPCCorporations.corporationID = {id}".
                 format(id=corpID))
    return (curr.fetchall())  


    
# select faction details from corp name

def factionNameFromCorpName(corp):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT crpNPCCorporations.corporationID, invNames.itemName, "
                 "chrFactions.factionName, chrFactions.factionID FROM chrFactions "
                 "INNER JOIN crpNPCCorporations ON crpNPCCorporations.factionID = chrFactions.factionID "
                 "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                 "WHERE invNames.itemName = \"{cp}\"".
                 format(cp=corp))  # Thukker Mix
    x = curr.fetchall()
    if len(x) == 1:
        return x[0][2]
    else:
        print ("factionNameFromCorpName returned more than 1 result", corp, x)

# select faction from corp id
def factionNameFromCorpID(corp):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT crpNPCCorporations.corporationID, invNames.itemName, chrFactions.factionName, "
                 "chrFactions.factionID FROM chrFactions "
                 "INNER JOIN crpNPCCorporations ON crpNPCCorporations.factionID = chrFactions.factionID "
                 "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                 "WHERE invNames.itemID = {cp}; ".
                 format(cp=corp))  # 1000160
    x = curr.fetchall()
    if len(x) == 1:
        return x[0][2]
    else:
        print ("factionNameFromCorpID returned more than 1 result", corp, x)            

# select all corps for faction name
def corpsFromFactionName(faction):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT crpNPCCorporations.corporationID, invNames.itemName, chrFactions.factionName, "
                 "chrFactions.factionID FROM crpNPCCorporations "
                 "INNER JOIN chrFactions ON chrFactions.factionID = crpNPCCorporations.factionID "
                 "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                 "WHERE chrFactions.factionName = \"{fc}\";".
                format(fc=faction))  # Thukker Tribe
    print (curr.fetchall())

# select all corps for faction ID

def corpsFromFactionid(faction):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT crpNPCCorporations.corporationID, invNames.itemName, chrFactions.factionName, "
                 "chrFactions.factionID FROM crpNPCCorporations "
                 "INNER JOIN chrFactions ON chrFactions.factionID = crpNPCCorporations.factionID "
                 "INNER JOIN invNames ON invNames.itemID = crpNPCCorporations.corporationID "
                 "WHERE chrFactions.factionID = {fc};".
                 format(fc=faction))  # 500015
    return (curr.fetchall())

# find station owner from sytemID

def stationOwnsersFromSystemID(sysID):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT stationID, corporationID, solarSystemID FROM staStations WHERE solarSystemID = {id}".
                 format(id=sysID))
    return (curr.fetchall())

def stationOwnserFromStationID(sysID):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    curr = conn.cursor()
    curr.execute("SELECT stationID, corporationID, solarSystemID FROM staStations WHERE stationID = {id}".
                 format(id=sysID))
    x = curr.fetchall()
    if len(x) == 1:
        return x
    else:
        print ("stationOwnserFromStationID returned more than 1 result", sysID, x)

''' find BP ID from item name
select industryActivityProducts.typeID, (select invTypes.typeName from invTypes where invTypes.typeID =  industryActivityProducts.typeID)
from invTypes
inner join industryActivityProducts
on industryActivityProducts.productTypeID = invTypes.typeID
where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'Anathema')
'''
def findBpIdFromName(itemName):
    curr.execute("SELECT invTypes.typeName " 
                 "FROM invTypes "
                 "INNER JOIN industryActivityProducts "
                 "ON industryActivityProducts.productTypeID = invTypes.typeID "
                 "WHERE industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = \"{nm}\")".
                 format(nm=itemName))
    print (curr.fetchone())

findBpIdFromName("Anathema")


''' find BP NAME from item name
select invTypes.typeName
from invTypes
inner join industryActivityProducts
on industryActivityProducts.productTypeID = invTypes.typeID
where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = 'Anathema')
'''
def findBpNameFromName(itemName):
    curr.execute("SELECT industryActivityProducts.typeID, "
                 "(select invTypes.typeName from invTypes where invTypes.typeID =  industryActivityProducts.typeID) "
                 "from invTypes "
                 "inner join industryActivityProducts "
                 "on industryActivityProducts.productTypeID = invTypes.typeID "
                 "where industryActivityProducts.productTypeID = (SELECT typeID from invTypes where typeName = \"{n}\")".
                 format(n=itemName))
    return curr.fetchone()[0]

''' find BP from item type
select typeID from industryActivityProducts where productTypeID = 969;
'''
def findBpFromID(itemID):
    curr.execute("SELECT typeID FROM industryActivityProducts "
                 "WHERE productTypeID = {id}".
                 format(id=itemID))
    print (curr.fetchone())
    
# findBpFromID(624) 

''' build from blueprint
select invTypes.typeName, industryActivityMaterials.quantity, invTypes.typeID
from invTypes
INNER JOIN industryActivityMaterials
ON  industryActivityMaterials.materialTypeID = invTypes.typeID
WHERE industryActivityMaterials.typeID = 969 AND activityID = 1;
'''
def matsForBp(bpID):
    mats = {}
    curr.execute("SELECT invTypes.typeID, industryActivityMaterials.quantity "
                 "FROM invTypes "
                 "INNER JOIN industryActivityMaterials "
                 "ON  industryActivityMaterials.materialTypeID = invTypes.typeID "
                 "WHERE industryActivityMaterials.typeID = {id} AND activityID = 1".
                 format(id=bpID))
    x = (curr.fetchall())
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


########################
# Eve Market API Calls
########################
# marketStatUrl = "http://api.eve-central.com/api/marketstat/json"
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

requests_cache.install_cache('wait_test')
requests_cache.clear()
s = requests_cache.CachedSession()
s.hooks = {'response': make_throttle_hook(0.1)}
s.get('http://httpbin.org/delay/get')
s.get('http://httpbin.org/delay/get')

def nowValueJita(interestingItem):
    systemID = 30000142
    marketStatUrl = "http://api.eve-central.com/api/marketstat/json?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    # print marketStatUrl
    resp = s.get(url=marketStatUrl)
    # print resp.text
    data = json.loads(resp.text)
    # pprint.pprint(data)
    # print ("They Buy ", data[0]['buy']['max'])
    # print ("They Sell ", data[0]['sell']['min'])
    return data[0]['sell']['min']
        
def nowValue(systemID, interestingItem):
    marketStatUrl = "http://api.eve-central.com/api/marketstat/json?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    resp = s.get(url=marketStatUrl)
    # print resp.text
    data = json.loads(resp.text)
    # pprint.pprint(data)
    # print ("They Buy ", data[0]['buy']['max'])
    # print ("They Sell ", data[0]['sell']['min'])
    return (data[0]['buy']['max'], data[0]['sell']['min'])      

def quickValueJita(interestingItem):
    systemID = 30000142
    marketStatUrl = "http://api.eve-central.com/api/quicklook?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    resp = s.get(url=marketStatUrl)
    obj = untangle.parse(resp.text)
    return obj

def createCorpAssetsTable(assets):
    curr.executescript('drop table if exists corpassets;')
    conn.execute("CREATE TABLE corpassets"
                "(itemid INT PRIMARY KEY  NOT NULL,"
                "locationid     INT    NOT NULL,"
                "typeid    INT    NOT NULL,"
                "quantity    INT    NOT NULL,"
                "flag    INT    NOT NULL,"
                "singleton    INT    NOT NULL"
                ");")
    for x in assets:
        print (x["itemID"])
        '''conn.execute("INSERT INTO corpassets "
                     "(itemid, locationid, typeid, quantity, flags, singleton) "
                     "VALUES (", x["itemID"],", "x['locationID'],", ",x['typeID'],", ",x['quantity']",","
                     ""x['flags']", ",x['singleton']);""
                     )'''
        conn.execute("INSERT INTO corpassets ({ii}, {li}, {ti}, {q}, {f}, {s}) VALUES ({vii}, {vli}, {vti}, {vq}, {vf}, {vs})".
                    format(ii="itemid", li="locationid", ti="typeid", q="quantity", f="flag", s="singleton",
                            vii=x["itemID"], vli=x["locationID"], vti=x["typeID"], vq=x["quantity"], vf=x["flag"], vs=x["singleton"]))
    conn.commit()
    
def getValueCorpAssets():
    total = 0
    curr.execute('SELECT typeid FROM corpassets;')
    for x in curr.fetchall():
        total = total + nowValue(30000142, x[0])[1]
        # print ("fetching",x[0])
        # print (nowValue(30000142, x[0])[1])
    print ("Value of all corp assets if put into iSell orders in Jita:", total)

def findT1Items():
    # select set of primary keys in invTypesMaterials
    # for every row in set
    # if x[1] in x[0]
    pass

print (nowValueJita(34))



# conn.close()
