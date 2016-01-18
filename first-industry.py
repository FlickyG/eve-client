'''
Created on 16 Jan 2016

@author: adam
'''
import sqlite3
import untangle
import json, requests, pprint
#import eveSQL
import eveSQL.firstGo as firstGo
#from docutils.parsers.rst.directives import parts



#Test PSQL connectivity
conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")
curr = conn.cursor()


ALL_CHARS = firstGo.getAllCharacters()



mats =  (firstGo.matsForBp(firstGo.findBpNameFromName("Armor EM Hardener I")))
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



    
def findEStandingBest():
    # b = base standing    
    b = firstGo.getStandingName("Flicky G", "Republic Fleet")
    #s = diplomacy skil
    s = ALL_CHARS["Flicky G"]["Diplomacy"]
    # E = 10 - (10-B) x (1 - 0.04 x S)
    st = 10 - (10 - b) * (1 - 0.04 * s)
    return st

findEStandingBest()

def reprocModuleBest():
    #station equipment
    #station tax
    #scrapmetal skill
    s = ALL_CHARS["Flicky G"]["Scrapmetal Processing"]
    pass


SELECT staStations.reprocessingEfficiency, inNames.itemName FROM staStations
INNER JOIN invNames ON staStations.stationID = invNames.itemID
WHERE staStations.stationsID = 


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