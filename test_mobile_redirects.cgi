#!/home/welkere/env/mobile_test/bin/python

import os, site, sys, cgitb, cgi
cgitb.enable()

print "Content-type: text/plain\n\n"

os.environ['VIRTUAL_ENV'] = '/home/welkere/env/mobile_test'

venv = '/home/welkere/env/mobile_test/bin/activate_this.py'
execfile(venv, dict(__file__=venv))

_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#print _project_dir
sys.path.insert(0, _project_dir)
sys.path.insert(0, '/home/welkere/python/mobile_test/')
sys.path.insert(0, os.path.dirname(_project_dir))

try:
    from mobile_redirect import TestPubMedMobileRedirect
    import unittest

    
    form = cgi.FieldStorage()
    port = form.getvalue('port')
    port = "http://%s.ncbi.nlm.nih.gov" % port

    TestPubMedMobileRedirect.baseurl = port

    print "Using %s as the port (domain) for these tests" % TestPubMedMobileRedirect.baseurl

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPubMedMobileRedirect)
    unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
except:
    print "An error has occured running the mobile_redirect tests"


