'''
Created on 22 Jan 2016

@author: adam
'''
#!/usr/bin/PYTHON
# 

import unittest
from eveSQL.SDEQueries import SDEQueries



class test_getItemID(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
    
    # getItemID returns integers    
    def test_returns_integer(self):
        self.assertIsInstance(self.queries.getItemID("Anathema"), int)

    # getItemID rejects anyton not Strings
    def test_rejects_strings(self):
        with self.assertRaises(AssertionError):
            self.queries.getItemID(12)
            self.queries.getItemID(-12) # getItemID rejects negative numbersign
            self.queries.getItemID(12.0) # getItemID rejects floats
            self.queries.getItemID(-12.0)# getItemID rejects negative floats
    
    #check doesn't return None
    def test_not_returns_none(self):
        with self.assertRaises(TypeError):
            self.queries.getItemID("Adam")

class test_getItemName(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
    
    # getItemID returns integers    
    def test_returns_string(self):
        print (self.queries.getItemName(13))
        self.assertIsInstance(self.queries.getItemName(13), str)

    # getItemID rejects anyton not Strings
    def test_rejects_strings(self):
        with self.assertRaises(AssertionError):
            self.queries.getItemName("Anathama")
            self.queries.getItemName(-12) # getItemName rejects negative numbersign
            self.queries.getItemName(12.0) # getItemName rejects floats
            self.queries.getItemName(-12.0)# getItemName rejects negative floats

    def test_not_returns_none(self):
        with self.assertRaises(TypeError):
            self.queries.getItemName(60) # first 'missing' itmeID

class test_getRegionID(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_integer(self):
        self.assertIsInstance(self.queries.getRegionID("Molden Heath"), int)
    
    def test_not_return_None(self):
        region = "Jita"
        with self.assertRaises(TypeError):
            self.queries.getRegionID(region)
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getRegionID(12)
            self.queries.getRegionID(-12)
            self.queries.getRegionID(12.0)
            self.queries.getRegionID(-12.0)

class test_getRegionName(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_string(self):
        self.assertIsInstance(self.queries.getRegionName(10000054), str)
    
    def test_not_return_None(self):
        region = "Jita"
        with self.assertRaises(TypeError):
            self.queries.getRegionID(region)
    
    def test_rejects_strings(self):
        region = "Jita"
        with self.assertRaises(AssertionError):
            self.queries.getRegionName("Metropolis")
            self.queries.getRegionName("Adam")
            self.queries.getRegionName("Devoid ")
            

class test_getSystemID(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_int(self):
        self.assertIsInstance(self.queries.getRegionID("Lonetrek"), int)
    
    def test_not_return_None(self):
        region = "Adam"
        with self.assertRaises(TypeError):
            self.queries.getRegionID(region)
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getRegionID(12)
            self.queries.getRegionID(-12)
            self.queries.getRegionID(12.0)
            self.queries.getRegionID(-12.0)

class test_getSystemName(unittest.TestCase):
    
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_string(self):
        self.assertIsInstance(self.queries.getSystemName(30000001), str)

    def test_not_return_None(self):
        region = ""
        with self.assertRaises(TypeError):
            self.queries.getSystemName(30000000)
    
    def test_rejects_strings(self):
        with self.assertRaises(AssertionError):
            self.queries.getSystemName("Jita")
            self.queries.getSystemName("ADam")

class test_getCorpID(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_int(self):
        self.assertIsInstance(self.queries.getCorpID("Amarr Certified News"), int)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpID("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpID(12)
            self.queries.getCorpID(-12)
            self.queries.getCorpID(12.0)
            self.queries.getCorpID(-12.0)

class test_getCorpName(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_str(self):
        self.assertIsInstance(self.queries.getCorpName(1000160), str)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpName("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpName(-12)
            self.queries.getCorpName(12.0)
            self.queries.getCorpName(-12.0)

class test_getFactionNameFromCorpName(unittest.TestCase):
    
    def setUp(self):
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_string(self):
        self.assertIsInstance(self.queries.getFactionNameFromCorpName("Thukker Mix"), str)

    def test_not_return_None(self):
        region = ""
        with self.assertRaises(AssertionError):
            self.queries.getFactionNameFromCorpName("Adam")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getFactionNameFromCorpName(12)
            self.queries.getFactionNameFromCorpName(-12)
            self.queries.getFactionNameFromCorpName(-12.0)
            self.queries.getFactionNameFromCorpName(12.0)

class test_getFactionNameFromCorpID(unittest.TestCase):
    
    def setUp(self):
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_string(self):
        self.assertIsInstance(self.queries.getFactionNameFromCorpID(1000160), str)

    def test_not_return_None(self):
        region = ""
        with self.assertRaises(AssertionError):
            self.queries.getFactionNameFromCorpID(10000000)
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getFactionNameFromCorpID(12)
            self.queries.getFactionNameFromCorpID(-12)
            self.queries.getFactionNameFromCorpID(-12.0)
            self.queries.getFactionNameFromCorpID(12.0)

class test_getCorpsFromFactionName(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getCorpsFromFactionName("Thukker Tribe"), list)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpsFromFactionName("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpsFromFactionName(12)
            self.queries.getCorpsFromFactionName(-12)
            self.queries.getCorpsFromFactionName(12.0)
            self.queries.getCorpsFromFactionName(-12.0)

class test_getCorpsFromFactionID(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getCorpsFromFactionID(500015), list)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpsFromFactionID("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getCorpsFromFactionID(12)
            self.queries.getCorpsFromFactionID(-12)
            self.queries.getCorpsFromFactionID(12.0)
            self.queries.getCorpsFromFactionID(-12.0)

class test_getStationOwnersFromSystemID(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getStationOwnersFromSystemID(30000145), list)
        print (self.queries.getStationOwnersFromSystemID(30000145))
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getStationOwnersFromSystemID("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getStationOwnersFromSystemID(12)
            self.queries.getStationOwnersFromSystemID(-12)
            self.queries.getStationOwnersFromSystemID(12.0)
            self.queries.getStationOwnersFromSystemID(-12.0)

class test_getStationOwnerFromSystemID(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getStationOwnerFromStationID(60000004), int)
        print (self.queries.getStationOwnerFromStationID(60000004))
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getStationOwnerFromStationID("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getStationOwnerFromStationID(12)
            self.queries.getStationOwnerFromStationID(-12)
            self.queries.getStationOwnerFromStationID(12.0)
            self.queries.getStationOwnerFromStationID(-12.0)

class test_getBpIdFromName(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getBpIdFromName("Anathema"), int)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getBpIdFromName("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getBpIdFromName(12)
            self.queries.getBpIdFromName(-12)
            self.queries.getBpIdFromName(12.0)
            self.queries.getBpIdFromName(-12.0)

class test_getBpNameFromName(unittest.TestCase):
    
    def setUp(self):
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_string(self):
        self.assertIsInstance(self.queries.getBpNameFromName("Anathema"), str)

    def test_not_return_None(self):
        region = ""
        with self.assertRaises(AssertionError):
            self.queries.getBpNameFromName("Poo Bum")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getBpNameFromName(12)
            self.queries.getBpNameFromName(-12)
            self.queries.getBpNameFromName(-12.0)
            self.queries.getBpNameFromName(12.0)

class test_getBpFromID(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.getBpFromID(11188), int)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.getBpFromID("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.getBpFromID(12)
            self.queries.getBpFromID(-12)
            self.queries.getBpFromID(12.0)
            self.queries.getBpFromID(-12.0)

class test_matsForBp(unittest.TestCase):
    def setUp(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass

    def test_FOO(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_returns_list(self):
        self.assertIsInstance(self.queries.matsForBp(11189), dict)
    
    def test_not_return_None(self):
        with self.assertRaises(AssertionError):
            self.queries.matsForBp("Lynda Tahri")
    
    def test_rejects_numbers(self):
        with self.assertRaises(AssertionError):
            self.queries.matsForBp(12)
            self.queries.matsForBp(-12)
            self.queries.matsForBp(12.0)
            self.queries.matsForBp(-12.0)

class test_turn_item_name_into_mats(unittest.TestCase):
    def setup(self):
        
        self.queries = SDEQueries()
        
    def tearDown(self):
        pass
        
    def test_1_anathema(self):
        #    Anathema -> itemID -> bpID -> mats
        sdequeries = SDEQueries()
        idee = sdequeries.getItemID("Anathema")
        bp = sdequeries.getBpFromID(idee)
        mats = sdequeries.matsForBp(bp)
        self.assertEqual(idee, 11188, "item id isn't right")
        self.assertEqual(bp, 11189, "item bp id isn't right")


if __name__ == '__main__':
    ''''y = SDEQueries()
    print ("hello >>>", y.getBpNameFromName("Anathema"))'''    
    unittest.main()
    
    

        