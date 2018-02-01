from Pandemic.X86.X86 import *
from Pandemic.X86.X86MetaData import *
from Pandemic.X86.X86ByteStream import StreamObj
from Pandemic.X86.X86Decoder import X86Decoder
import unittest

class TestX86Decoder(unittest.TestCase):
	err1 = "X86Decoder.Decode should have returned an X86DecodedInstruction object, not "
	err2 = "X86DecodedInstruction.instr field should have been an Instruction object, not "
	def do_test(self,instr,bytes):
		decoder = X86Decoder(StreamObj(bytes))
		i2container = decoder.Decode(0)
		self.assertIsInstance(i2container,X86DecodedInstruction,self.err1+repr(i2container))
		i2 = i2container.instr
		self.assertIsInstance(i2,Instruction,self.err2+repr(i2))
		error = "%s: expected %s(%r), got %s(%r)" % (bytes,instr,instr,i2,i2)
		self.assertEqual(instr,i2,error)
		
	# Direct decoding method, no special features used
	def test00_Direct(self):
		self.do_test(Instruction([],Nop),[0x90])

	# PREDOpSize decoder entry method
	def test01_PREDOpSize(self):
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

	# PredMOD decoding method
	def test07_PredMOD(self):
		self.do_test(Instruction([],Sldt,Mem32(DS,Mw,Eax,None,0,0)),[0x0F,0x00,0x00])
		self.do_test(Instruction([],Sldt,Gd(Eax)),[0x0F,0x00,0xC0])

	# RMGroup decoding method
	def test08_RMGroup(self):
		self.do_test(Instruction([],Vmcall),[0x0F,0x01,0xC1])

	# Immediate_Ib operand
	def test09_Immediate_Ib(self):
		self.do_test(Instruction([],Int,Ib(2)),[0xCD,0x02])

	# Immediate_Iw operand
	def test10_Immediate_Iw(self):
		self.do_test(Instruction([],Ret,Iw(4)),[0xC2,0x04,0x00])

	# SizePrefix operand
	def test11_SizePrefix(self):
		self.do_test(Instruction([],Xor,Gw(Bx),Gw(Ax)),[0x66,0x31,0xC3])

	# AddrPrefix operand
	def test12_AddrPrefix(self):
		self.do_test(Instruction([],Stosb,Mem16(ES,Mb,Di,None,None)),[0x67,0xAA])
		self.do_test(Instruction([],Stosb,Mem32(ES,Mb,Edi,None,0,None)),[0xAA])

	# ExactSeg operand
	def test13_ExactSeg(self):
		self.do_test(Instruction([],Lodsb,Mem16(DS,Mb,Si,None,None)),[0x67,0xAC])
		self.do_test(Instruction([],Lodsb,Mem32(DS,Mb,Esi,None,0,None)),[0xAC])
		self.do_test(Instruction([],Lodsb,Mem32(FS,Mb,Esi,None,0,None)),[0x64,0xAC])

	# SizePrefix and Immediate_Id operand
	def test14_SizePrefix_Immediate_Id(self):
		self.do_test(Instruction([],Push,Id(0x12345678)),[0x68,0x78,0x56,0x34,0x12])

	# AddrPrefix and Immediate_FarTarget operand
	def test15_AddrPrefix_Immediate_FarTarget(self):
		self.do_test(Instruction([],CallF,AP16(0x1234,0)),[0x67,0x9A,0x00,0x00,0x34,0x12])
		self.do_test(Instruction([],CallF,AP32(0x1234,0)),[0x9A,0x00,0x00,0x00,0x00,0x34,0x12])

	# AddrPrefix and Immediate_MemExpr operand
	def test16_AddrPrefix_Immediate_MemExpr(self):
		self.do_test(Instruction([],Mov,Gb(Al),Mem16(DS,Mb,None,None,0x1234)),[0x67,0xA0,0x34,0x12])
		self.do_test(Instruction([],Mov,Gb(Al),Mem32(DS,Mb,None,None,0,0x12345678)),[0xA0,0x78,0x56,0x34,0x12])