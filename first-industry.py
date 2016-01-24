'''
Created on 16 Jan 2016

@author: adam
'''
import sqlite3
import untangle
import json, requests, pprint
#import eveSQL
import eveSQL.firstGo as firstGo
from eveSQL.SDEQueries import SDEQueries
#from docutils.parsers.rst.directives import parts



#Test PSQL connectivity
conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
curr = conn.cursor()

queries = SDEQueries()

ALL_CHARS = firstGo.getAllCharacters()



mats =  (queries.matsForBp(queries.findBpNameFromName("Armor EM Hardener I")))
amount = 0 
for key, value in mats.iteritems():
   print (key, value)
   amount = amount + (firstGo.nowValueJita(key) * value)
print (amount)
    
#compare build price againsr recylce price
def reprocOre():
    pass
'''Reprocessing yield: Station Equipment 
x (1 + Refining skill x 0.03) 
x (1 + Refining Efficiency skill x 0.02) 
x (1 + Ore Processing skill x 0.02) )'''
#stationEquipment
#refiningSkill
#refiningEffSkill
#oreProcSkill


firstGo.createCorpAssetsTable(assets)

def getSystemIDFromStation(stationID):
    conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
    ss = conn.cursor()
    ss.execute("SELECT solarSystemID from staStations where stationID = {id}".
                 format(id  = stationID))
    s = ss.fetchone()[0]
    return s


 

def itemPrices():
    total = 0
    curr.execute('SELECT typeid, locationid FROM corpassets;')
    for x in curr.fetchall():    
        theyBuy = firstGo.nowValue(getSystemIDFromStation(x[1]), x[0])[0]
        theySell = firstGo.nowValue(getSystemIDFromStation(x[1]), x[0])[1]
        print (firstGo.getSystemName(getSystemIDFromStation(x[1])), firstGo.getItemName(x[0]), theyBuy, theySell)

#Station Equipment x (1 + Refining skill x 0.03) x (1 + Refining Efficiency skill x 0.02) x (1 + Ore Processing skill x 0.02) )

#[(60004516, 1000047, 30002053), (60005236, 1000055, 30002053), (60005686, 1000057, 30002053), (60011287, 1000111, 30002053), (60015140, 1000182, 30002053)]
#NEW MATH --> Station Equipment x (1 + Refining skill x 0.03) x (1 + Refining Efficiency skill x 0.02) x (1 + Ore Processing skill x 0.02) 




#find blueprints in assets and calculate profite
#compare jita prices against rens prices

'''

# get itemID from BlueprintId
select productTypeID from  industryActivityProducts where typeID = 894;

# reprocess from item ID
select invTypes.typeName, invTypeMaterials.quantity, invTypes.typeID
from invTypes
INNER JOIN invTypeMaterials
ON  invTypeMaterials.materialTypeID = invTypes.typeID
WHERE invTypeMaterials.typeID = 11188;
'''