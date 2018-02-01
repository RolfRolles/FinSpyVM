#!/usr/bin/python
import sys
from Pandemic.X86.X86Parser import parser

if(len(sys.argv) != 2):
	print "Usage: %s \"instruction to validate\"" % sys.argv[0]
	sys.exit()

res = parser.Parse(sys.argv[1])
print res, "(%r) was valid" % res