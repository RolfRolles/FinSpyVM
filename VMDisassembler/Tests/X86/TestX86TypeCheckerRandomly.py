from Pandemic.X86.X86InternalOperand import *
from Pandemic.X86.X86TypeChecker import X86TypeChecker,TypeCheckInfo
from X86Random import X86RandomOperand, rnd_bool
import random
import unittest

num_iterations = 10000

class TestX86TypeCheckerRandomly(unittest.TestCase):
	tc = X86TypeChecker()
	rog = X86RandomOperand()

	def do_test(self,aop,opnd,res,(m,s,a)):
		error = "%s: operand %r(%s) did not match!" % (aop,opnd,opnd)
		self.assertIsNotNone(res,error)
		self.assertIsInstance(res,TypeCheckInfo,"X86TypeChecker(%s,%s) should have returned a TypeCheckInfo object, not type %s" % (aop,opnd,type(res)))
		error = "%s: operand %r(%s) did not report that a size prefix was required!" % (aop,opnd,opnd)
		self.assertFalse(s and res.sizeo == False,error)
		error = "%s: operand %r(%s) did not report that an address prefix was required!" % (aop,opnd,opnd)
		self.assertFalse(a and res.addro == False,error)

	def one_iteration(self):
		m,s,a = rnd_bool(),rnd_bool(),rnd_bool()
		aop = AOTElt(random.randint(0,X86_INTERNAL_OPERAND_LAST))
		opnd = self.rog.gen(aop,(m,s,a))
		res  = self.tc.check(aop,opnd)
		self.do_test(aop,opnd,res,(m,s,a))
		
	def test_Randomly(self):
		for i in xrange(0,num_iterations):
			self.one_iteration()