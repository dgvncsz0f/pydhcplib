#!/usr/bin/python

from pydhcplib.type_hw_addr import hwmac


address = hwmac()
print "a0 : ",address

address1 = hwmac("ff:11:22:33:44:55")
print "a1 : ",address1

address2 = hwmac("f6.16.26.36.46.56")
print "a2 : ",address2

address3 = hwmac("ff.11-22:33-44.55")
print "a3 : ",address3



if address1 == address2 : print "test 1 : ",address1, "==",address2
else : print "test 1 : " ,address1, "!=",address2

if address1 == address3 : print "test 2 : ", address1, "==",address3
else : print "test 2 : ", address1, "!=",address3



address4 = hwmac([186, 45, 67, 176, 6, 11])
address5 = hwmac("ba:2d:43:b0:06:0c")
    
print "b0 : ", address4,address4.list()
print "b1 : ", address5,address5.list()
