from Pandemic.X86.X86Encoder import X86Encoder
from X86Random import generate_random_instruction
import unittest

num_iterations = 10000

class TestX86EncoderRandomly(unittest.TestCase):
	enc = X86Encoder()

	def one_iteration(self,i):
		instr = generate_random_instruction()
		print i,instr
		bytes = self.enc.EncodeInstruction(instr)
		self.assertIsNotNone(bytes,"%s: couldn't encode!" % instr)

	def test_Randomly(self):
		for i in xrange(num_iterations):
			self.one_iteration(i)