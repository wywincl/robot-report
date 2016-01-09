# from xml.dom.minidom import parse
import xml.dom.minidom as dom

__author__ = 'john.wang'


def gen_report(output="output.xml"):
    # use minidom parse xml file
    domtree = dom.parse(output)
    collection = domtree.documentElement

    tests = collection.getElementsByTagName("test")

    test_lists = []
    for test in tests:
        # print ".... Test ...."
        suite = test.parentNode
        status = test.getElementsByTagName("status")
        # print [s.getAttribute("status") for s in status]
        # if test.hasAttribute("name"):
        #     print "Name: %s " % test.getAttribute("name")
        #     print "Status: %s" % status[1].getAttribute("status")
        #     print "Suite: %s\n" % suite.getAttribute("source")
        test_lists.append([suite.getAttribute("source"), test.getAttribute("name"), status[len(status)-1].getAttribute("status")])

    return test_lists

if __name__ == "__main__":
    l1 = gen_report("output.xml")
    l2 = gen_report("output1.xml")
    # for i in l1:
    #     if i[2] == u"FAIL":
    #         print i
    #
    # for i in l2:
    #     if i[2] == u"FAIL":
    #         print i
    i = 0
    while i < len(l1):
        if l1[i][2] == u"FAIL" or l1[i][2] != l2[i][2]:
            print "".join(l1[i]), l2[i]
        i += 1

