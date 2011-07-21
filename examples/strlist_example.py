#!/usr/bin/python

from pydhcplib.type_strlist import strlist


word = strlist()
print "a0 : ",word

word1 = strlist("azerty")
print "a1 : ",word1

word2 = strlist("qwerty")
print "a2 : ",word2

word3 = strlist([97, 122, 101, 114, 116, 121])
print "a3 : ",word3

if word1 == word2 : print "test 1 : ",word1, "==",word2
else : print "test 1 : " ,word1, "!=",word2

if word1 == word3 : print "test 2 : ", word1, "==",word3
else : print "test 2 : ", word1, "!=",word3



