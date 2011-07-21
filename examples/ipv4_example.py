#!/usr/bin/python


from pydhcplib.type_ipv4 import ipv4


address = ipv4()
print "a0 : ",address

address1 = ipv4("192.168.0.1")
print "a1 : ",address1

address2 = ipv4("10.0.0.1")
print "a2 : ",address2

address3 = ipv4([192,168,0,1])
print "a3 : ",address3



if address1 == address2 : print "test 1 : ",address1, "==",address2
else : print "test 1 : " ,address1, "!=",address2

if address1 == address3 : print "test 2 : ", address1, "==",address3
else : print "test 2 : ", address1, "!=",address3



