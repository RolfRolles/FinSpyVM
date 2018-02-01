"""The main module for representing X86 instructions and operands.  Generally,
clients will need to import both this module and :mod:`.X86MetaData`."""

from X86MetaData import *
from Pandemic.Util.HashFunctions import binary_hash
from Pandemic.Util.Guarded import *
from X86Internal import *
from Pandemic.Util.ASMFlow import *

HASH_Gd = 1
HASH_Gw = 2
HASH_Gb = 3
HASH_ControlReg = 4
HASH_DebugReg = 5
HASH_MMXReg = 6
HASH_XMMReg = 7
HASH_FPUReg = 8
HASH_SegReg = 9
HASH_Mem16 = 10
HASH_Mem32 = 11
HASH_AP16 = 12
HASH_AP32 = 13
HASH_Id = 14
HASH_Iw = 15
HASH_Ib = 16
HASH_JccTarget = 17

class Gd(GeneralReg):
	"""Class representing 32-bit general registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_Gd,R32Elt,adjust_value)

class Gw(GeneralReg):
	"""Class representing 16-bit general registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_Gw,R16Elt,adjust_value)

class Gb(GeneralReg):
	"""Class representing 8-bit general registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_Gb,R8Elt,adjust_value)	

class ControlReg(Register):
	"""Class representing control registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_ControlReg,CntElt,adjust_value)

class DebugReg(Register):
	"""Class representing debug registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_DebugReg,DbgElt,adjust_value)

class MMXReg(Register):
	"""Class representing MMX registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_MMXReg,MMXElt,adjust_value)

class XMMReg(Register):
	"""Class representing XMM registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_XMMReg,XMMElt,adjust_value)

class FPUReg(Register):
	"""Class representing FPU registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_FPUReg,FPUElt,adjust_value)

class SegReg(Register):
	"""Class representing segment registers."""
	def __init__(self,value,adjust_value=False):
		self.init(value,HASH_SegReg,SegElt,adjust_value)

class Id(Immediate):
	"""Class representing 32-bit immediate constants."""
	def __init__(self,value):
		self.init(HASH_Id,value,0xFFFFFFFF)

class Iw(Immediate):
	"""Class representing 16-bit immediate constants."""
	def __init__(self,value):
		self.init(HASH_Iw,value,0xFFFF)

class Ib(Immediate):
	"""Class representing 8-bit immediate constants."""
	def __init__(self,value):
		self.init(HASH_Ib,value,0xFF)

class AP16(FarTarget):
	"""Class representing 16-bit segment:offset memory locations."""
	def __init__(self,seg,off):
		self.init(HASH_AP16,seg,off,0xFFFF)

class AP32(FarTarget):
	"""Class representing 32-bit segment:offset memory locations."""
	def __init__(self,seg,off):
		self.init(HASH_AP32,seg,off,0xFFFFFFFF)

class JccTarget(Operand):
	"""Class representing jump targets."""
	def __init__(self,taken,nottaken):
		self._taken    = GuardedInteger(taken,0xFFFFFFFF)
		self._nottaken = GuardedInteger(nottaken,0xFFFFFFFF)
		self._hashcode = HASH_JccTarget
	
	def __repr__(self):
		return "JccTarget(%r,%r)" % (self._taken,self._nottaken)

	def __str__(self):
		return "%s" % X86Hexify(self._taken.value)

	def __eq__(self,other):
		return type(self)==type(other) and self._taken.value == other._taken.value and \
		self._nottaken.value == other._nottaken.value

class Mem16(MemExpr):
	"""Class representing 16-bit memory expressions.
	
	:ivar `.R16Elt` BaseReg: The base register, or ``None``.
	:ivar `.R16Elt` IndexReg: The index register, or ``None``.
	"""
	def __init__(self,seg,size,basereg=None,indexreg=None,disp=None,adjust_values=False):
		self.init(HASH_Mem16,seg,size,R16Elt,basereg,indexreg,disp,0xFFFF,adjust_values)
	
	def __eq__(self,other):
		return type(self)==type(other) and self.BaseReg == other.BaseReg and \
		self.IndexReg == other.IndexReg and self.Disp == other.Disp and \
		self.Seg == other.Seg and self.size == other.size
	
	def __call__(self,seg):
		return type(self)(seg,self.size,self.BaseReg,self.IndexReg,self.Disp)

	def DefaultSeg(self):
		"""16-bit memory expressions use ``SS`` by default if the base register is
		``Bp``, and ``DS`` otherwise.
		
		:rtype: :class:`~.SegElt`
		"""
		return SS if self.BaseReg == Bp else DS

	def __repr__(self):
		cn = self.__class__.__name__
		return "%s(%r,%r,%r,%r,%r)" % (cn,self.Seg,self.size,self.BaseReg,self.IndexReg,self.Disp)

	def String(self):
		sb = "%s" % self.BaseReg  if self.BaseReg  != None else ""
		ss = "%s" % self.IndexReg if self.IndexReg != None else ""
		sd = X86Hexify(self.Disp) if self.Disp     != None else ""
		if sb == "" and ss == "" and sd == "": sd = "0"
		return self.MakeString([sb,ss,sd])

class Mem32(MemExpr):
	"""Class representing 32-bit memory expressions.
	
	:ivar `.R32Elt` BaseReg: The base register, or ``None``.
	:ivar `.R32Elt` IndexReg: The index register, or ``None``.
	"""
	def __init__(self,seg,size,basereg=None,indexreg=None,scalefac=0,disp=None,adjust_values=False):
		self.init(HASH_Mem32,seg,size,R32Elt,basereg,indexreg,disp,0xFFFFFFFF,adjust_values)
		self.scalefac = GuardedInteger(scalefac,3)

	@property
	def ScaleFac(self): 
		"""32-bit memory expressions may scale the index register by this value,
		which is in the range of 0-3.  It should be set to ``0`` if there is no 
		scale factor.  Otherwise, it corresponds to multiplying by 
		``1 << ScaleFac``.  That is, a value of ``1``	corresponds to multiplying
		by ``2``; ``2`` corresponds to multiplication by ``4``; and ``3`` denotes
		multiplication by ``8``.
		"""
		return self.scalefac.value
	@ScaleFac.setter
	def ScaleFac(self,value): self.scalefac.value = value
	
	def __eq__(self,other):
		return type(self)==type(other) and self.BaseReg == other.BaseReg and \
		self.IndexReg == other.IndexReg and self.ScaleFac == other.ScaleFac and \
		self.Disp == other.Disp and self.Seg == other.Seg and self.size == other.size

	def __call__(self,seg):
		return type(self)(seg,self.size,self.BaseReg,self.IndexReg,self.ScaleFac,self.Disp)

	def __repr__(self):
		cn = self.__class__.__name__
		return "%s(%r,%r,%r,%r,%r,%r)" % (cn,self.Seg,self.size,self.BaseReg,self.IndexReg,self.ScaleFac,self.Disp)

	def String(self):
		sb = "%s" % self.BaseReg if self.BaseReg != None else ""
		if self.IndexReg != None:
			ss = "%s" % self.IndexReg
			if self.ScaleFac != 0:
				ss = "%s*%d" % (ss,1<<self.ScaleFac)
		else:
			ss = ""
		sd = X86Hexify(self.Disp) if self.Disp != None else ""
		if sb == "" and ss == "" and sd == "": sd = "0"
		return self.MakeString([sb,ss,sd])
			
	def DefaultSeg(self):
		"""32-bit memory expressions use ``SS`` by default if the base register is
		``Ebp`` or ``Esp``, and ``DS`` otherwise.
		
		:rtype: :class:`~.SegElt`
		"""
		return SS if self.BaseReg == Ebp or self.BaseReg == Esp else DS
	
	def HashIndex(self):
		return binary_hash(hash(self.IndexReg),hash(self.ScaleFac),self._hashcode+2)

class Instruction(object):
	"""Class representing X86 instructions.
	
	:ivar `.PF1Elt` prefixes: list of group #1 prefixes
	:ivar `.MnemElt` mnem: mnemonic
	:ivar `.Operand` op1: first operand, or ``None``
	:ivar `.Operand` op2: second operand, or ``None``
	:ivar `.Operand` op3: third operand, or ``None``
	"""
	def NumOps(self):
		"""Return the number of operands (``0-3``) possessed by this instruction.
		
		:rtype: integer
		"""
		if self.op1 == None: return 0
		if self.op2 == None: return 1
		if self.op3 == None: return 2
		return 3

	def AddPrefix(self,pfx):
		"""Add a Group #1 prefix.
		
		:param `.PF1Elt` pfx:
		"""
		self.prefixes.append(pfx)
	
	def GetOp(self,num):
		"""Retrieve an operand by number.
		
		:param integer num: which operand
		:rtype: :class:`~.Operand`
		"""
		if num == 0: return self.op1
		if num == 1: return self.op2
		if num == 2: return self.op3
		print "Instruction::GetOp: num %d out of bounds" % num
		raise IndexError
	
	def __init__(self,prefixes,mnem,op1=None,op2=None,op3=None):
		self.prefixes = prefixes
		if not isinstance(mnem,MnemElt):
			print "Instruction: mnem %s was not of type %s" % (mnem,MnemElt)
			raise TypeError
		self.mnem = mnem
		
		self.op1 = op1
		self.op2 = op2
		self.op3 = op3
	
	def __repr__(self):
		pfx = "" if len(self.prefixes) == 0 else ",".join(map(repr,self.prefixes))
		return "Instruction([%s],%r,%r,%r,%r)" % (pfx,self.mnem,self.op1,self.op2,self.op3)
		
	def MakeString(self,parts,intersperse):
		parts = map(lambda o: "" if o == None else ("%s" % o),parts)
		parts = filter(lambda o: o != "",parts)
		return intersperse.join(parts)

	def __str__(self):
		pfx = "" if len(self.prefixes) == 0 else "["+" ".join(map(str,self.prefixes))+"] "
		opstr = self.MakeString([self.op1,self.op2,self.op3],", ")
		return "%s%s %s" % (pfx,self.mnem,opstr)
		
	def __eq__(self,other):
		return type(self) == type(other) and self.NumOps() == other.NumOps() and \
		set(self.prefixes) == set(other.prefixes) and (self.mnem,self.op1,self.op2,self.op3)\
		== (other.mnem,other.op1,other.op2,other.op3)
							
	def __ne__(self,other):
		return not(self.__eq__(other))
	
	def __hash__(self):
		pfxhash = reduce(lambda a,b: a^hash(b),self.prefixes,0)
		ophash  = reduce(lambda a,b: a^hash(b),map(self.GetOp,xrange(0,3)),0)
		return pfxhash^ophash^hash(self.mnem)

class InvalidInstruction(Exception):
	"""This exception may be thrown during decoding, if an attempt to decode an
	undefined instruction is made, or if an encoded instruction specifies an
	illegal operand.  For example, some operands are encoded in such a way that
	they might specify a register or memory location, but one of those 
	possibilities could be illegal."""
	def __str__(s): return s.__class__.__name__

class X86DecodedInstruction(object):
	"""A class for packaging the results of instruction decoding.  In particular,
	the :class:`Instruction` class does not indicate the address of an 
	instruction, nor its length, nor which addresses to which the instruction may
	transfer control.
	
	:ivar integer ea: the instruction's address
	:ivar `Instruction` instr: the instruction itself
	:ivar integer length: the length of the instruction
	:ivar `.FlowType` flow: the instruction's successor addresses
	"""
	def CreateFlow(self):
		"""Inspect the instruction and its length, and determine which type of
		control flow it exhibits (passes control to the next instruction, returns,
		conditional jump, etc).  For a complete listing of flow types, see the 
		:mod:`ASMFlow` module."""
		mnem = self.instr.mnem
		op0 = self.instr.GetOp(0)
		next_addr = self.ea + self.length
		if op0 != None and isinstance(op0,JccTarget):
			if mnem == Call:
				return FlowCallDirect(op0._taken.value,next_addr)
			if mnem == Jmp:
				return FlowJmpUnconditional(op0._taken.value,next_addr)
			if mnem in [Jo,Jno,Jb,Jae,Jz,Jnz,Jbe,Ja,Js,Jns,Jp,Jnp,Jl,Jge,Jle,Jg,Loopnz,Loopz,Loop,Jcxz,Jecxz]:
				return FlowJmpConditional(op0._taken.value,op0._nottaken.value)
			else:
				print "CreateFlow:  JccTarget with invalid mnenonic %s" % MnemToString[mnem]
				raise ValueError
		elif mnem in [Call,CallF]: return FlowCallIndirect(next_addr)
		elif mnem in [Jmp,JmpF]:   return FlowJmpIndirect()
		elif mnem in [Ret,Retf,Iretd,Iretw]: return FlowReturn()
		else: return FlowOrdinary(next_addr)

	def __init__(self,ea,instr,length,flow=None):
		self.ea = ea
		self.instr = instr
		self.length = length
		self.flow = flow if flow != None else self.CreateFlow()

#if __name__=="__main__":
#	i = Instruction([],Add,Gb(Al),Gb(Cl))
#	print "%s" % i
#	print "%r" % i
