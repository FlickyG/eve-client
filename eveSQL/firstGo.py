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
import sys


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
conn = sqlite3.connect("/home/adam/workspace1/eve-client/eveSQL/eve.db")
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
        print ("loaction of firt go cache", join(tempfile.gettempdir(), "eveapi"))
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

MY_CHARACTERS = {}

def getAllCharacters():
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
        
    
##############
# Standings, Taxes and REprocessing
##################

def findStandingTax():
    if (5.0 - (0.75 * findEStandingBest())) < 0.0:
        t = 0
        return (1 - t)
    else:
        t = (5.0 - (0.75 * findEStandingBest()))
        return  (1 - t)
    
def findEStandingBest():
    # b = base standing    
    b = getStandingName("Flicky G", "Republic Fleet")
    #s = diplomacy skil
    s = ALL_CHARS["Flicky G"]["Diplomacy"]
    # E = 10 - (10-B) x (1 - 0.04 x S)
    st = 10 - (10 - b) * (1 - 0.04 * s)
    return st

def reprocModuleBest():
    #station equipment
    #station tax
    #scrapmetal skill
    sk = (1 + ALL_CHARS["Flicky G"]["Scrapmetal Processing"] * 0.02)
    e = getReprocModuleE(60004516)
    st = findStandingTax()
    #find correct formula
    return (sk*e*st)

def getReprocModuleE(stationID):
    curr.execute("SELECT staStations.reprocessingEfficiency, invNames.itemName FROM staStations "
                    "INNER JOIN invNames ON staStations.stationID = invNames.itemID "
                    "WHERE staStations.stationID = {id};".
                    format(id = stationID))
    efficiency  = curr.fetchone()[0] 
    return efficiency

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

requests_cache.install_cache('first_go', expires_after = 1)
requests_cache.clear()
s = requests_cache.CachedSession()
s.hooks = {'response': make_throttle_hook(0.1)}


def now_value_jita(interestingItem):
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
        
def now_value(systemID, interestingItem):
    marketStatUrl = "http://api.eve-central.com/api/marketstat/json?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    resp = s.get(url=marketStatUrl)
    # print resp.text
    data = json.loads(resp.text)
    # pprint.pprint(data)
    # print ("They Buy ", data[0]['buy']['max'])
    # print ("They Sell ", data[0]['sell']['min'])
    return (data[0]['buy']['max'], data[0]['sell']['min'])      

def quick_value_jita(interestingItem):
    systemID = 30000142
    marketStatUrl = "http://api.eve-central.com/api/quicklook?usesystem=" + str(systemID) + "&typeid=" + str(interestingItem)
    resp = s.get(url=marketStatUrl)
    obj = untangle.parse(resp.text)
    return obj

def create_corp_asset_table(assets):
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
    
def get_value_corp_assets():
    total = 0
    curr.execute('SELECT typeid FROM corpassets;')
    for x in curr.fetchall():
        total = total + now_value(30000142, x[0])[1]
        # print (nowValue(30000142, x[0])[1])
    print ("Value of all corp assets if put into iSell orders in Jita:", total)

def find_t1_items():
    # select set of primary keys in invTypesMaterials
    # for every row in set
    # if x[1] in x[0]
    pass




def main():
    pass
    #print (now_value_jita(34))


if __name__ == "__main__":
    sys.exit(main())


##########

# Start Processing Data
##########
"""
corp = cachedApi.auth(keyID=1383071, vCode="m0ecx5e1r8RCMsizNKXyB91HQchkHjJmNJlG8or0xy3VvkpiAJj1J7wXb70lUMm0").corporation(98436502)
corpTransactions  = corp.WalletTransactions()
for x in corpTransactions.transactions:
    print (x)
    
corpJournal = corp.WalletJournal()
for x in corpJournal.entries:
    print (x)

corpAssets = corp.AssetList().assets
for x in corpAssets:
    print (x)
    
createCorpAssetsTable(corpAssets)
"""
# conn.close()
