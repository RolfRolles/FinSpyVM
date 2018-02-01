from Pandemic.X86.X86MetaData import R16Elt
from Pandemic.X86.X86ModRM import ModRM16, modrm_16
from Pandemic.X86.X86ByteStream import StreamObj
from X86Random import rnd_bool
import random
import unittest

student_tests = False

if student_tests:
	num_iterations = 10000
else:
	num_iterations = 100000

# Helper function to generate a random displacement (either None, an 
# 8-bit signed value, or a 16/32-bit value).  choose_none determines
# whether it is acceptable to return None.
def rnd_displ(choose_none,mask):
	i = random.randint(0 if choose_none else 1,2)
	if i == 0: return None
	if i == 1: return mask&(127-random.randint(0,255))
	if i == 2: return random.randint(0,mask)

class TestModRM16(unittest.TestCase):
	def setUp(self):
		# This is useful for deterministic testing.  Otherwise, different memory 
		# expressions will be generated each time we run the tests.  While this is
		# advantageous for testing of the entire framework, the randomness is 
		# likely to confuse and fatigue the student during exercises.
		if student_tests:
			random.seed(0x12345678)
	
	def one_iteration(self):
		# Choose base and scale registers, and displacement
		b,sr = random.choice(modrm_16) if rnd_bool() else (None,None)
		d    = rnd_displ(not (b == None and sr == None),0xFFFF)

		# Make a ModRM16, encode our random choices by parts, and then call 
		# Interpret to get back the constitutent components.
		m = ModRM16()
		m.EncodeFromParts(b,sr,d)
		nb,nsr,nd,_ = m.Interpret()

		# Test to make sure we got back roughly what we put in.
		if nb is not None:
			self.assertIsInstance(nb,R16Elt,"%s(%r) should have been a 16-bit register, not type %s" % (nb,nb,type(nb)))
		self.assertEqual(b, nb, "Chose base register %s, retrieved %s"  % (b, nb))

		if sr is not None:
			self.assertIsInstance(sr,R16Elt,"%s(%r) should have been a 16-bit register, not type %s" % (sr,sr,type(sr)))
		self.assertEqual(sr,nsr,"Chose index register %s, retrieved %s" % (sr,nsr))

		if d is not None:
			if nd is None:
				self.assertTrue(d==0,"Chose displacement %#lx, retrieved None" % d)
			else:
				self.assertEqual(d,nd,"Chose displacement %#lx, retrieved %#lx" % (d,nd))

		elif nd is not None:
			self.assertIsInstance(nd,(int,long),"%s(%r) should have been an integer, not type %s" % (nd,nd,type(nd)))
			self.assertTrue(nd == 0,"Chose no displacement, retrieved %#lx" % nd)

		# GGG must be set in order to encode into bytes.
		m.GGG = 7
		bytes = m.Encode()
		
		# Make a new ModRM16, and populate it by decoding the encoded version of 
		# the previous one.
		m = ModRM16()
		m.Decode(StreamObj(bytes))
		db,dsr,dd,_ = m.Interpret()

		# Ensure that we got back something roughly equal.
		if db is not None:
			self.assertIsInstance(db,R16Elt,"Interpret: %s(%r) should have been a 16-bit register, not type %s" % (db,db,type(db)))
		self.assertEqual(db,nb,  "Decoded base register %s, encoded %s"  % (b, nb))

		if dsr is not None:
			self.assertIsInstance(dsr,R16Elt,"Interpret: %s(%r) should have been a 32-bit register, not type %s" % (dsr,dsr,type(dsr)))
		self.assertEqual(dsr,nsr,"Decoded index register %s, encoded %s" % (sr,nsr))

		if dd is not None:
			if nd is None:
				self.assertTrue(dd==0,"Decoded displacement %#lx, encoded None" % dd)
			else:
				self.assertEqual(dd,nd,"Decoded displacement %#lx, encoded %#lx" % (dd,nd))
		elif nd is not None:
			self.assertIsInstance(nd,(int,long),"Interpret: %s(%r) should have been an integer, not type %s" % (nd,nd,type(nd)))
			self.assertTrue(nd == 0,"Chose no displacement, retrieved %#lx" % nd)

	def test_ModRM16(self):
		for i in xrange(num_iterations):
			self.one_iteration()