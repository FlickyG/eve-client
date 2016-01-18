#/bin/python

import sqlite3
import untangle
import json, requests, pprint
import eveSQL.firstGo as firstGo



#Test PSQL connectivity
conn = sqlite3.connect("/home/adam/Documents/eve/native/eve.db")

curr = conn.cursor()



#nowValueJita(34)
x = firstGo.quickValueJita(34)
for y in x.evec_api.quicklook.sell_orders.order:
    print y.price.cdata, y.vol_remain.cdata

print ("### SQL MESS AROUND ###")
print firstGo.getItemId("Tritanium")
print firstGo.getItemName(34)
print firstGo.getRegionID("Catch")
print firstGo.getRegionName(10000014)
print firstGo.getSystemID('Jita')
print firstGo. getSystemName(30000142)

curr.close()
conn.close()
print ("### END OF SQL MESS AROUND ###")



#[{"buy":{"forQuery":{"bid":true,"types":[34],"regions":[],"systems":[30000142],"hours":24,"minq":10001},"volume":12247190000,"wavg":5.906915872130669,"avg":5.776666666666666,"variance":0.4084984126984128,"stdDev":0.6391388055019135,"median":6.01,"fivePercent":6.2056,"max":6.22,"min":3.19,"highToLow":true,"generated":1451850198106},"all":{"forQuery":{"bid":null,"types":[34],"regions":[],"systems":[30000142],"hours":24,"minq":10001},"volume":23125540019,"wavg":6.186607831493425,"avg":6.311372549019604,"variance":0.7708379853902345,"stdDev":0.877973795389267,"median":6.18,"fivePercent":4.484691780821918,"max":12.0,"min":1.19,"highToLow":false,"generated":1451850198036},"sell":{"forQuery":{"bid":false,"types":[34],"regions":[],"systems":[30000142],"hours":24,"minq":10001},"volume":10778350019,"wavg":6.550773157727789,"avg":6.5620909090909105,"variance":0.5057274462809929,"stdDev":0.7111451654064681,"median":6.505,"fivePercent":6.339434900641621,"max":12.0,"min":6.31,"highToLow":false,"generated":1451850198050}}]
























