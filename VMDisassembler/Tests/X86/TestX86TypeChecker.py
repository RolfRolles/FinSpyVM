from Pandemic.X86.X86 import *
from Pandemic.X86.X86MetaData import *
from Pandemic.X86.X86InternalOperand import *
from Pandemic.X86.X86TypeChecker import X86TypeChecker, MATCHES, SizePFX, AddrPFX, SegPFX, TypeCheckInfo
import unittest

num_iterations = 10000

m = MATCHES()
sn = SizePFX(False)
sy = SizePFX(True)
an = AddrPFX(False)
ay = AddrPFX(True)
ansfs = TypeCheckInfo(addro=False,sego=FS)
aysfs = TypeCheckInfo(addro=True,sego=FS)

class TestX86TypeChecker(unittest.TestCase):
	tc = X86TypeChecker()
	def do_test(self,aop,possibility_list):
		for (possibility,result) in possibility_list:
			res = self.tc.check(aop,possibility)
			if result is not None:
				self.assertIsNotNone(res,"%s: should have matched %s" % (aop,possibility))
			else:
				self.assertIsNone(result,"%s: should not have matched %s" % (aop,possibility))
			if res is not None:
				self.assertIsInstance(res,TypeCheckInfo,"X86TypeChecker(%s,%s) should have returned a TypeCheckInfo object, not type %s" % (aop,possibility,type(res)))
				error = "%s %s: size override should have been %s, was %s" % (aop,possibility,result.sizeo,res.sizeo)
				self.assertEqual(res.sizeo,result.sizeo)
				error = "%s %s: address override should have been %s, was %s" % (aop,possibility,result.addro,res.addro)
				self.assertEqual(res.addro,result.addro)
				error = "%s %s: segment override should have been %s, was %s" % (aop,possibility,result.sego,res.sego)
				self.assertEqual(res.sego,result.sego)
	
	# Exact operand type
	def test00_Exact(self):
		self.do_test(OAX,[(Gw(Ax),m),(Gw(Cx),None),(Gb(Al),None),(Gd(Eax),None),
		(FPUReg(ST0),None),(MMXReg(MM1),None),(XMMReg(XMM2),None),
		(SegReg(FS),None),(ControlReg(CR0),None),(DebugReg(DR0),None),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Ib(0),None),(Iw(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])

	# GPart operand type
	def test01_GPart(self):
		self.do_test(OGb,[(Gb(Al),m),(Gb(Dl),m),(Gw(Cx),None),(Gd(Eax),None),
		(FPUReg(ST0),None),(MMXReg(MM1),None),(XMMReg(XMM2),None),
		(SegReg(FS),None),(ControlReg(CR0),None),(DebugReg(DR0),None),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Ib(0),None),(Iw(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])
	
	# ImmEnc(Immediate) operand type
	def test02_ImmEnc_Immediate(self):
		self.do_test(OIw,[(Iw(5),m),(Gb(Al),None),(Gb(Dl),None),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Gw(Cx),None),(Gd(Eax),None),(FPUReg(ST0),None),(MMXReg(MM1),None),
		(XMMReg(XMM2),None),(SegReg(FS),None),(ControlReg(CR0),None),
		(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])

	# ImmEnc(JccTarget) operand type
	def test03_ImmEnc_JccTarget(self):
		self.do_test(OJz,[(JccTarget(0,0),m),(Iw(5),None),(Gb(Al),None),(Gb(Dl),None),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Gw(Cx),None),(Gd(Eax),None),(FPUReg(ST0),None),(MMXReg(MM1),None),
		(XMMReg(XMM2),None),(SegReg(FS),None),(ControlReg(CR0),None),
		(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None)])

	# SizePrefix(y,n) operand type
	def test04_SizePrefix(self):
		self.do_test(OGv,[(Gw(Cx),sy),(Gd(Eax),sn),(Mem16(SS,Mb,None,None,0),None),
		(Mem32(SS,Mb,None,None,0,0),None),(Mem16(SS,Mb,Bx,None,0),None),
		(Mem32(SS,Mb,Eax,None,0,0),None),(Mem32(SS,Mb,None,Ebx,0,0),None),
		(Mem32(SS,Mb,Ecx,Ebx,0,0),None),(Iw(5),None),(Gb(Al),None),(Gb(Dl),None),
		(FPUReg(ST0),None),(MMXReg(MM1),None),
		(XMMReg(XMM2),None),(SegReg(FS),None),(ControlReg(CR0),None),
		(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])

	# AddrPrefix(y,n) operand type
	def test05_AddrPrefix(self):
		self.do_test(OYb,[(Mem16(ES,Mb,Di,None,None),ay),(Mem32(ES,Mb,Edi,None,0,None),an),
		(Mem16(FS,Mb,Si,None,None),None),(Mem32(FS,Mb,Esi,None,0,None),None),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Mem16(SS,Mb,Bx,None,0),None),(Mem32(SS,Mb,Eax,None,0,0),None),
		(Mem32(SS,Mb,None,Ebx,0,0),None),(Mem32(SS,Mb,Ecx,Ebx,0,0),None),
		(Iw(5),None),(Gb(Al),None),(Gb(Dl),None),(FPUReg(ST0),None),
		(MMXReg(MM1),None),(XMMReg(XMM2),None),(SegReg(FS),None),
		(ControlReg(CR0),None),(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),
		(AP16(0,0),None),(AP32(0,0),None),(JccTarget(0,0),None)])

	# RegOrMem operand type
	def test06_RegOrMem(self):
		self.do_test(OEb,[(Gb(Al),m),(Gb(Dl),m),(Mem16(DS,Mb,None,None,0),ay),
		(Mem32(DS,Mb,None,None,0,0),an),(Gw(Cx),None),(Gd(Eax),None),
		(FPUReg(ST0),None),(MMXReg(MM1),None),(XMMReg(XMM2),None),
		(SegReg(FS),None),(ControlReg(CR0),None),(DebugReg(DR0),None),	
		(Ib(0),None),(Iw(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])

	# ImmEnc(MemExpr) operand type
	def test07_ImmEnc_MemExpr(self):
		self.do_test(OOb,[(Mem16(DS,Mb,None,None,0),ay),(Mem32(DS,Mb,None,None,0,0),an),
		(Mem16(SS,Mb,Bx,None,0),None),(Mem32(SS,Mb,Eax,None,0,0),None),
		(Mem32(SS,Mb,None,Ebx,0,0),None),(Mem32(SS,Mb,Ecx,Ebx,0,0),None),
		(Iw(5),None),(Gb(Al),None),(Gb(Dl),None),
		(Gw(Cx),None),(Gd(Eax),None),(FPUReg(ST0),None),(MMXReg(MM1),None),
		(XMMReg(XMM2),None),(SegReg(FS),None),(ControlReg(CR0),None),
		(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),(AP16(0,0),None),
		(AP32(0,0),None),(JccTarget(0,0),None)])

	# ExactSeg operand type
	def test08_ExactSeg(self):
		self.do_test(OXb,[(Mem16(DS,Mb,Si,None,None),ay),(Mem32(DS,Mb,Esi,None,0,None),an),
		(Mem16(FS,Mb,Si,None,None),aysfs),(Mem32(FS,Mb,Esi,None,0,None),ansfs),
		(Mem16(SS,Mb,None,None,0),None),(Mem32(SS,Mb,None,None,0,0),None),
		(Mem16(SS,Mb,Bx,None,0),None),(Mem32(SS,Mb,Eax,None,0,0),None),
		(Mem32(SS,Mb,None,Ebx,0,0),None),(Mem32(SS,Mb,Ecx,Ebx,0,0),None),
		(Iw(5),None),(Gb(Al),None),(Gb(Dl),None),(FPUReg(ST0),None),
		(MMXReg(MM1),None),(XMMReg(XMM2),None),(SegReg(FS),None),
		(ControlReg(CR0),None),(DebugReg(DR0),None),(Ib(0),None),(Id(0),None),
		(AP16(0,0),None),(AP32(0,0),None),(JccTarget(0,0),None)])