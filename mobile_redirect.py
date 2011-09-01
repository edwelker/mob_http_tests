#!/usr/bin/env python
#! encoding: utf-8

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
        self.history_test( '/pubmed?term=cat&p$mobile=true', '/m/pubmed/?term=cat')

    #no, order doesn't matter, unless you're testing regular expressions too
    def test_std_search_with_mobile_emulation_queryparams_reversed(self):
        self.history_test('/pubmed?p$mobile=true&term=cat', '/m/pubmed/?term=cat')

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

        self.assertEqual( location, expectedurl)

    def getpage(self, url):
        return requests.get( urljoin(self.baseurl, url) )

    def strip_test_querystringparams(self, location):
        scheme, netloc, path, query, fragment = urlsplit(location)
        qs = parse_qsl(query)
        for x in qs:
            if x[0] == "p$mobile":
                qs.remove(x)
        
        qs = urlencode(qs)

        return urlunsplit((scheme, netloc, path, qs, fragment))



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPubMedMobileRedirect)
    unittest.TextTestRunner(verbosity=2).run(suite)
