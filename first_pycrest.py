'''
Created on 30 Jan 2016

@author: adam
'''

import pycrest, pprint


eve = pycrest.EVE()
eve()

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


pprint.pprint(eve)

#10000042 metro
#490 22omm vulcan
history = eve.get('https://public-crest.eveonline.com/market/10000042/types/490/history/')
pprint.pprint(history)