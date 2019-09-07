from __future__ import print_function
# from xml.dom.minidom import parse
import xml.dom.minidom as dom

__author__ = 'john.wang'

# use minidom parse xml file
DOMTree = dom.parse("output.xml")
collection = DOMTree.documentElement

tests = collection.getElementsByTagName("test")

for test in tests:
    print(".... Test ....")
    suite = test.parentNode
    status = test.getElementsByTagName("status")
    print([i.getAttribute("status") for i in status])
    if test.hasAttribute("name"):
        print("Name: %s " % test.getAttribute("name"))
        print("Status: %s" % status[1].getAttribute("status"))
        print("Suite: %s\n" % suite.getAttribute("source"))
