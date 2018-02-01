from Pandemic.X86.X86 import *
from Pandemic.X86.X86MetaData import *
from Pandemic.X86.X86Encoder import X86Encoder
import unittest

class TestX86Encoder(unittest.TestCase):
	enc = X86Encoder()
	
	def do_test(self,instr,bytes):
		encbytes = self.enc.EncodeInstruction(instr)
		error = "%s(%r): expected %s, got %s" % (instr,instr,bytes,encbytes)
		self.assertEqual(bytes,encbytes,error)
		
	# Simple end-to-end test, no special features used
	def test00_Simple(self):
		self.do_test(Instruction([],Nop),[0x90])

	# Native16/SizePrefix encoding method
	def test01_SizePrefix(self):
		self.do_test(Instruction([],Pushaw),[0x66,0x60])
		self.do_test(Instruction([],Pushad),[0x60])

	# Exact operand
	def test02_Exact(self):
		self.do_test(Instruction([],In,Gb(Al),Gw(Dx)),[0xEC])
	
	# ModRMGroup encoding method and RegOrMem_Register
	def test03_ModRMGroup_RegOrMem_Register(self):
		self.do_test(Instruction([],Inc,Gb(Al)),[0xFE,0xC0])

	# GPart operand
	def test04_GPart(self):
		self.do_test(Instruction([],Xor,Gb(Bl),Gb(Al)),[0x30,0xC3])

	# RegOrMem_Mem32 operand
	def test05_RegOrMem_Mem32(self):
		self.do_test(Instruction([],Xor,Mem32(DS,Mb,Eax,None,0,0),Gb(Al)),[0x30,0x00])

	# RegOrMem_Mem16 operand
	def test06_RegOrMem_Mem16(self):
		self.do_test(Instruction([],Xor,Mem16(DS,Mb,Bx,Si,0),Gb(Al)),[0x67,0x30,0x00])

	# Immediate_Ib operand
	def test07_Immediate_Ib(self):
		self.do_test(Instruction([],Int,Ib(2)),[0xCD,0x02])

	# Immediate_Iw operand
	def test08_Immediate_Iw(self):
		self.do_test(Instruction([],Ret,Iw(4)),[0xC2,0x04,0x00])

	# SizePrefix operand
	def test09_SizePrefix(self):
		self.do_test(Instruction([],Xor,Gw(Bx),Gw(Ax)),[0x66,0x31,0xC3])

	# AddrPrefix operand
	def test10_AddrPrefix(self):
		self.do_test(Instruction([],Stosb,Mem16(ES,Mb,Di,None,None)),[0x67,0xAA])
		self.do_test(Instruction([],Stosb,Mem32(ES,Mb,Edi,None,0,None)),[0xAA])

	# ExactSeg operand
	def test11_ExactSeg(self):
		self.do_test(Instruction([],Lodsb,Mem16(DS,Mb,Si,None,None)),[0x67,0xAC])
		self.do_test(Instruction([],Lodsb,Mem32(DS,Mb,Esi,None,0,None)),[0xAC])
		self.do_test(Instruction([],Lodsb,Mem32(FS,Mb,Esi,None,0,None)),[0x64,0xAC])

	# SizePrefix and Immediate_Id operand
	def test12_SizePrefix_Immediate_Id(self):
		self.do_test(Instruction([],Push,Id(0x12345678)),[0x68,0x78,0x56,0x34,0x12])

	# AddrPrefix and Immediate_FarTarget operand
	def test13_AddrPrefix_Immediate_FarTarget(self):
		self.do_test(Instruction([],CallF,AP16(0x1234,0)),[0x67,0x9A,0x00,0x00,0x34,0x12])
		self.do_test(Instruction([],CallF,AP32(0x1234,0)),[0x9A,0x00,0x00,0x00,0x00,0x34,0x12])

	# AddrPrefix and Immediate_MemExpr operand
	def test14_AddrPrefix_Immediate_MemExpr(self):
		self.do_test(Instruction([],Mov,Gb(Al),Mem16(DS,Mb,None,None,0x1234)),[0x67,0xA0,0x34,0x12])
		self.do_test(Instruction([],Mov,Gb(Al),Mem32(DS,Mb,None,None,0,0x12345678)),[0xA0,0x78,0x56,0x34,0x12])