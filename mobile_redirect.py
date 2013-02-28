#!/usr/bin/env python
# encoding: utf-8
"""
Tests for PubMed Mobile redirect.

Eddie Welker, Aug 31, 2011
"""

import requests
from urlparse import urljoin, parse_qsl, urlsplit, urlunsplit
import unittest
import re
from urllib import urlencode, unquote

class TestPubMedMobileRedirect(unittest.TestCase):

    baseurl = 'http://dev.ncbi.nlm.nih.gov/'
    mob_cookie = dict(ncbi_mmode='mob')
    std_cookie = dict(ncbi_mmode='std')

    def test_std_homepage_no_emulation(self):
        page = self.getpage('/pubmed')
        self.assertEqual(page.status_code, 200)

    #all of these assume no cookie
    def test_std_homepage_with_mobile_emulation(self):
        self.history_test( '/pubmed?p$mobile=true',  '/m/pubmed/') 

    def test_std_abstract_with_mobile_emulation(self):
        self.history_test( '/pubmed/17328369?p$mobile=true', '/m/pubmed/17328369/')

    def test_std_search_with_mobile_emulation(self):
        self.history_test( '/pubmed?term=breast+cancer&p$mobile=true', '/m/pubmed/?term=breast+cancer')

    #no, order doesn't matter, unless you're testing regular expressions too
    def test_std_search_with_mobile_emulation_queryparams_reversed(self):
        self.history_test('/pubmed?p$mobile=true&term=breast+cancer', '/m/pubmed/?term=breast+cancer')

    def test_two_word_search_with_mobile_emulation(self):
        self.history_test('/pubmed?p$mobile=true&term=heart%20attack', '/m/pubmed/?term=heart+attack')

    def test_two_word_search_encoded_with_mobile_emulation(self):
        self.history_test('/pubmed?p$mobile=true&term=brca1%20brca2', '/m/pubmed/?term=brca1+brca2')

    def test_three_word_search_with_mobile_emulation(self):
        self.history_test('/pubmed?p$mobile=true&term=asprin%20heart%20attack', '/m/pubmed/?term=asprin+heart+attack')

    def test_three_word_search_encoded_with_mobile_emulation(self):
        self.history_test('/pubmed?p$mobile=true&term=breast%20cancer%20brca1', '/m/pubmed/?term=breast+cancer+brca1')

    def test_std_link_with_mobile_emulation(self):
        self.history_test( '/pubmed?cmd=link&linkname=pubmed_pubmed&uid=18590863&p$mobile=true', '/m/pubmed/18590863/related/')

    #now test them with a cookie
    def test_std_homepage_with_mobile_cookie(self):
        self.history_test('/pubmed?p$mobile=true', '/m/pubmed/', self.mob_cookie)

    def test_std_abstract_with_mobile_cookie(self):
        self.history_test('/pubmed/18066186?p$mobile=true', '/m/pubmed/18066186/', self.mob_cookie)

    def test_std_search_with_mobile_cookie(self):
        self.history_test('/pubmed/?term=shostakovich&p$mobile=true', '/m/pubmed/?term=shostakovich', self.mob_cookie)

    def test_std_link_with_mobile_cookie(self):
        self.history_test('/pubmed/?cmd=link&linkname=pubmed_pubmed&uid=123456&p$mobile=true', '/m/pubmed/123456/related/', self.mob_cookie)

    #these tests are only good when a cookie is issued along with them... can't have param w/o cookie
    def test_std_homepage_with_standard_flag(self):
        self.history_test( '/pubmed?p$mobile=true&ncbi_mmode=std', '/pubmed', self.mob_cookie)

    def test_std_serach_with_std_flag(self):
        self.history_test( '/pubmed?term=whale&p$mobile=true&ncbi_mmode=std', '/pubmed?term=whale', self.mob_cookie)

    def test_std_abstract_with_std_flag(self):
        self.history_test('/pubmed/18590863?ncbi_mmode=std&p$mobile=true', '/pubmed/18590863', self.mob_cookie)

    def test_std_link_with_std_flag(self):
        self.history_test('/pubmed?cmd=link&ncbi_mmode=std&linkname=pubmed_pubmed&p$mobile=true&uid=17328369',
                            '/pubmed?cmd=link&linkname=pubmed_pubmed&uid=17328369',
                            self.mob_cookie)



    def test_std_homepage_with_standard_flag_and_cookie(self):
        loc = '/pubmed?p$mobile=true&ncbi_mmode=std'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_serach_with_std_flag_and_cookie(self):
        loc = '/pubmed?term=whale&p$mobile=true&ncbi_mmode=std'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_abstract_with_std_flag_and_cookie(self):
        loc = '/pubmed/18590863?ncbi_mmode=std&p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_link_with_std_flag_and_cookie(self):
        loc = '/pubmed?cmd=link&ncbi_mmode=std&linkname=pubmed_pubmed&p$mobile=true&uid=17328369'
        self.routing_rule_test(loc, self.std_cookie)


    def test_std_homepage_with_standard_cookie(self):
        loc = '/pubmed?p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_serach_with_std_cookie(self):
        loc = '/pubmed?term=whale&p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_abstract_with_std_cookie(self):
        loc = '/pubmed/18590863?p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_std_link_with_std_cookie(self):
        loc = '/pubmed?cmd=link&linkname=pubmed_pubmed&p$mobile=true&uid=17328369'
        self.routing_rule_test(loc, self.std_cookie)




#test mobile urls with standard cookie
    def test_mob_homepage_with_std_cookie(self):
        loc = '/m/pubmed/?p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_mob_abstract_with_std_cookie(self):
        loc = '/m/pubmed/18066186/?p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def est_mob_search_with_std_cookie(self):
        loc = '/m/pubmed/?term=shostakovich&p$mobile=true'
        self.routing_rule_test(loc, self.std_cookie)

    def test_mob_link_with_std_cookie(self):
        loc = '/m/pubmed/123456/related/'
        self.routing_rule_test(loc, self.std_cookie)



#test mobile urls with mobile cookie
    def test_mob_homepage_with_mobile_cookie(self):
        loc = '/m/pubmed/?p$mobile=true'
        self.routing_rule_test(loc, self.mob_cookie)

    def test_mob_abstract_with_mobile_cookie(self):
        loc = '/m/pubmed/18066186/?p$mobile=true'
        self.routing_rule_test(loc, self.mob_cookie)

    def test_mob_search_with_mobile_cookie(self):
        loc = '/m/pubmed/?term=breast+cancer&p$mobile=true'
        self.routing_rule_test(loc, self.mob_cookie)

    def test_mob_link_with_mobile_cookie(self):
        loc = '/m/pubmed/123456/related/'
        self.routing_rule_test(loc, self.mob_cookie)

#mobile urls with no cookie
    def test_mob_homepage(self):
        loc = '/m/pubmed/?p$mobile=true'
        self.routing_rule_test(loc, None)

    def test_mob_abstract(self):
        loc = '/m/pubmed/18066186/?p$mobile=true'
        self.routing_rule_test(loc, None)

    def test_mob_search(self):
        loc = '/m/pubmed/?term=breast%20cancer&p$mobile=true'
        self.routing_rule_test(loc, None)

    def test_mob_link(self):
        loc = '/m/pubmed/123456/related/'
        self.routing_rule_test(loc, None)





    #class helper methods
    def history_test(self, inurl, expectedurl, cookies=None ):
        """Tests to see if the incoming url results in the expected url, as well as making sure there is a 303 redirect inbetween"""
        if cookies:
            page = requests.get( urljoin(self.baseurl, inurl), cookies=cookies)
        else:
            page = self.getpage( inurl )
        history = page.history[0]
        self.assertIsNotNone(history) #there should be a redirect, so there should be history
        self.assertEqual(history.status_code, 303)
        location = history.headers.get('location')
    
        if re.search( r'p\$mobile\=true', location):
            location = self.strip_test_querystringparams(location)

        if re.search( r'ncbi.nlm.nih.gov', location):
            location = self.strip_host(location)

        self.assertEqual( location, expectedurl)

    def routing_rule_test(self, loc, cookie):
        page = self.getpage(loc, cookie)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(self.strip_host(page.url), loc)

    def getpage(self, url, cookies=None):
        return requests.get( urljoin(self.baseurl, url), cookies=cookies )

    def strip_test_querystringparams(self, location):
        scheme, netloc, path, query, fragment = urlsplit(location)
        qs = parse_qsl(query)
        for x in qs:
            if x[0] == "p$mobile":
                qs.remove(x)
        
        qs = urlencode(qs)
        return urlunsplit((scheme, netloc, path, qs, fragment))

    def strip_host(self, location):
        s, n, p, q, f = urlsplit(location)
        s = n = ''
        return urlunsplit((s, n, p, q, f))


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPubMedMobileRedirect)
    unittest.TextTestRunner(verbosity=2).run(suite)
