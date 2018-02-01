"""This module provides the class :class:`X86Decoder` to decode X86 machine 
code.  For flexibility, this class consumes bytes from an 
:class:`X86ByteStream.StreamObj`.  Owing to this design decision, we can obtain
the bytes from any source, as long as we can implement the :class:`.StreamObj`
interface around that byte source.  For example, we could use IDA's 
``get_byte()``, map a PE file into a flat memory view and index into that, use
a debugger's capabilities to read from memory, etc.
"""

from X86 import *
from X86ByteStream import StreamObj
import X86DecodeTable
from X86ModRM import ModRM16, ModRM32, sign_extend_8_16, sign_extend_8_32, modrm_16
from X86InternalOperandDescriptions import *
from Pandemic.Util.Visitor import Visitor
from Pandemic.Util.ExerciseError import ExerciseError
	
class X86Decoder(Visitor):
	def Reset(self):
		"""Reset the variables held in the decoder."""
		self.group1pfx = []
		self.sizepfx = False
		self.addrpfx = False
		self.segpfx  = None
		self._modrm  = None
		
	def __init__(self,stream):
		"""Set the stream object (from whence the bytes are consumed) and reset the
		state."""
		self.Stream = stream
		self.Reset()
	
	def GetSegment(self):
		"""Get the segment to use for a memory expression.  If there is a segment
		prefix, use that.  If there is no ModRM, use ``DS``.  If there is a ModRM,
		inspect the base register and use either ``DS`` or ``SS`` accordingly.
		
		:rtype: :class:`~.SegElt`
		"""
		if self.segpfx != None: return self.segpfx
		if self._modrm == None: return DS

		# For 32-bit, use SS if base register is Esp or Ebp, otherwise DS.
		if isinstance(self._modrm,ModRM32):
			basereg,i,s,d,ds = self._modrm.Interpret() 
			if basereg == Ebp or basereg == Esp:
				return SS

		# For 16-bit, use SS if base register is Bp, otherwise DS.
		elif isinstance(self._modrm,ModRM16):
			basereg,i,d,s = self._modrm.Interpret() 
			if basereg == Bp: 
				return SS

		return DS

	def DecodePrefixes(self):
		"""Consume all of the prefixes before the instruction stem, and update the
		class variables accordingly.  When we consume a non-prefix byte, we stop
		and return it.
		
		:rtype: integer
		"""
		while True:
			b = self.Stream.Byte()
			if   b == 0xF0: self.group1pfx.append(LOCK)
			elif b == 0xF2: self.group1pfx.append(REPNE)
			elif b == 0xF3: self.group1pfx.append(REP)
			elif b == 0x2E: self.segpfx = CS
			elif b == 0x36: self.segpfx = SS
			elif b == 0x3E: self.segpfx = DS
			elif b == 0x26: self.segpfx = ES
			elif b == 0x64: self.segpfx = FS
			elif b == 0x65: self.segpfx = GS
			elif b == 0x66: self.sizepfx = True
			elif b == 0x67: self.addrpfx = True
			else:           return b
		
	def DecodeStem(self,first_byte):
		"""Given the first byte of the stem (as read by DecodePrefixes above), examine
		it and any subsequent escape bytes to determine the stem.
		
		:param integer first_byte:
		:rtype: integer
		:returns: A stem number from ``0x000-0x3FF``.
		"""
		if first_byte != 0x0F: return first_byte
		second_byte = self.Stream.Byte()
		if   second_byte == 0x38: return 0x200 | self.Stream.Byte()
		elif second_byte == 0x3A: return 0x300 | self.Stream.Byte()
		return 0x100 | second_byte

	@property
	def ModRM(self):
		"""As in :class:`~.X86Encoder.X86Encoder`, the use of class properties 
		makes ModRM accesses very slick.  We don't have to explicitly store a table
		describing which stems need a ModRM, like most other disassemblers.  
		Instead, we simply wait until some part of the code touches the ModRM 
		property for the first time.  At that point, we parse the ModRM (depending
		upon the address-size prefix) and store it within the object.
		"""
		if self._modrm is None:
			if self.addrpfx: self._modrm = ModRM16()
			else:            self._modrm = ModRM32()
			self._modrm.Decode(self.Stream)
		return self._modrm
	
	def Decode(self,ea):
		"""The main interface to the decoder functionality.
		
		:param integer ea: The address from which to decode
		:rtype: :class:`X86DecodedInstruction`
		"""		
		# Reset the state of the class.
		self.Reset()
		
		# Set the position within the stream.
		self.Stream.SetPos(ea)
		
		# Consume prefixes and update prefix-related variables; consume stem.
		stem = self.DecodeStem(self.DecodePrefixes())
		
		# Find the entry for that stem in the decoding table.
		entry = X86DecodeTable.decoding_table[stem]
		
		# Get the mnemonic and abstract operand type, if no exception is thrown.
		mnem,oplist = entry.decode(self)
		
		# Decode each operand using the visitor methods below.
		ops = map(lambda o: self.visit(AOTtoAOTDL[o.IntValue()]),oplist)
		
		# Create an Instruction object.
		instr = Instruction(self.group1pfx,mnem,*ops)
		
		# Look at the stream position to calculate length.
		final_ea = self.Stream.Pos()
		
		# Return the instruction with its address and length.
		return X86DecodedInstruction(ea,instr,final_ea-ea)
	
	def MakeMethodName(self,enc):
		"""We override this method from the :class:`~.Visitor.Visitor` class to
		simplify the design.  We segregate the :class:`.ImmEnc`, 
		:class:`.RegOrMem`, and :class:`.SignedImm` encodings by their type so as
		to choose a specialized :meth:`visit_` method.
		
		:param `.X86AOTDL` enc:
		:rtype: string
		"""
		if isinstance(enc,ImmEnc):
			op = enc.archetype
			if isinstance(op,MemExpr):   return "visit_Immediate_MemExpr"
			if isinstance(op,FarTarget): return "visit_Immediate_FarTarget"
			return "visit_Immediate_%s" % op.__class__.__name__

		# We have to special-case SegReg, since there are only 6 segment registers.
		# We unify the logic for all other register types, as there are 8 possible
		# registers for each other register type.
		if isinstance(enc,GPart):
			op = enc.archetype
			if isinstance(op,SegReg):
				return "visit_GPart_SegReg"

		if isinstance(enc,RegOrMem):
			suffix = "Register" if self.ModRM.MOD == 3 else "MemExpr"
			return "visit_RegOrMem_%s" % suffix
		
		if isinstance(enc,SignedImm): 
			return "visit_SignExtImm_%s" % enc.archetype.__class__.__name__

		return "visit_" + enc.__class__.__name__

	def visit_Exact(self,i):      
		"""For Exact operand types, return *i*'s *value* field directly.
		
		:param `.Exact` i:
		:rtype: :class:`~.Operand`
		"""
		#raise ExerciseError("X86Decoder::visit_Exact")
		return i.value
	
	def visit_ExactSeg(self,i): 
		"""For ExactSeg operand types, return *i*'s *value* field directly if there
		was no segment override, or a copy of *value* with the overridden segment
		if there was.
		
		:param `.ExactSeg` i:
		:rtype: :class:`~.MemExpr`
		"""
		#raise ExerciseError("X86Decoder::visit_ExactSeg")
		return i.value if not self.segpfx else i.value(self.segpfx)

	def visit_GPart(self,g):         
		"""For GPart operand types, return a register with the same type as *g*'s
		*archetype* field, whose register number is the ModRM :attr:`.GGG` field.
		
		:param `.GPart` g:
		:rtype: :class:`~.Register`
		"""
		#raise ExerciseError("X86Decoder::visit_GPart")
		return g.archetype(self.ModRM.GGG)
	
	def visit_GPart_SegReg(self,g):         
		"""For GPart operand types describing segment registers, check to see that
		the register number is in bound (``0-5``).  If not, raise an 
		:exc:`~.InvalidInstruction` exception.  Otherwise, return the segment 
		register numbered by ModRM :attr:`.GGG` field.
		
		:param `.GPart` g:
		:rtype: :class:`~.Register`
		:raises: :exc:`~.InvalidInstruction` if GGG is out of bounds.
		"""
		#raise ExerciseError("X86Decoder::visit_GPart")
		if self.ModRM.GGG > 5:
			raise InvalidInstruction()
		return g.archetype(self.ModRM.GGG)

	def visit_RegOrMem_Register(self,m): 
		"""For RegOrMem when a register is specified, create a new register of the
		type held in *m*'s reg field.
		
		:raises: :exc:`.InvalidInstruction` if *m*'s *reg* field is ``None``, i.e.
			register values are illegal for this abstract operand type.
		
		:param `.RegOrMem` m:
		:rtype: :class:`~.Register`
		"""
		if m.reg is None: 
			#raise ExerciseError("X86Decoder::visit_RegOrMem_Register:None")
			raise InvalidInstruction()
		#raise ExerciseError("X86Decoder::visit_RegOrMem_Register:Default")
		return m.reg(self.ModRM.RM)

	# For ModRM when a memory is specified, create a Mem16 or Mem32 object 
	# depending upon address size, using the information from the ModRM.
	def visit_RegOrMem_MemExpr(self,m):
		"""For RegOrMem when memory is specified, create a :class:`Mem16` or 
		:class:`Mem32` object depending upon address size, using the information
		from :attr:`X86Decoder.ModRM`.
		
		:raises: :exc:`.InvalidInstruction` if *m*'s *mem* field is ``None``, i.e.
			memory locations are illegal for this abstract operand type.
		
		:param `.RegOrMem` m:
		:rtype: :class:`~.MemExpr`
		"""
		if m.mem is None: 
			#raise ExerciseError("X86Decoder::visit_RegOrMem_MemExpr:None")
			raise InvalidInstruction()
		else:
			seg = self.GetSegment()
			
			# Decode a 16-bit ModRM
			if self.addrpfx: 
				#raise ExerciseError("X86Decoder::visit_RegOrMem_MemExpr:Mem16")
				br,sr,disp,_ = self.ModRM.Interpret()
				return Mem16(seg,m.mem,br,sr,disp)
			 
			# Decode a 32-bit ModRM
			#raise ExerciseError("X86Decoder::visit_RegOrMem_MemExpr:Mem32")
			br,sr,sf,disp,_ = self.ModRM.Interpret()
			return Mem32(seg,m.mem,br,sr,sf,disp)

	def visit_Immediate_Ib(self,i):  
		"""Read a byte from the stream, and return it as an immediate.
		
		:param `.ImmEnc` i:
		:rtype: :class:`.Ib`
		"""
		#raise ExerciseError("X86Decoder::visit_Immediate_Ib")
		return Ib(self.Stream.Byte()) 

	def visit_Immediate_Iw(self,i):  
		"""Read a word from the stream, and return it as an immediate.
		
		:param `.ImmEnc` i:
		:rtype: :class:`.Iw`
		"""
		#raise ExerciseError("X86Decoder::visit_Immediate_Iw")
		return Iw(self.Stream.Word()) 

	def visit_Immediate_Id(self,i):  
		"""Read a dword from the stream, and return it as an immediate.
		
		:param `.ImmEnc` i:
		:rtype: :class:`.Id`
		"""
		#raise ExerciseError("X86Decoder::visit_Immediate_Id")
		return Id(self.Stream.Dword()) 

	def visit_Immediate_MemExpr(self,i):
		"""Create a :class:`Mem16` or :class:`Mem32` depending upon the address
		size prefix.  The memory expression consists of only a displacement and
		no base or index registers, using a word or dword read from the stream,
		respectively.
		
		:param `.ImmEnc` i:
		:rtype: :class:`.MemExpr`
		"""
		seg,size = self.GetSegment(),i.archetype.size
		if self.addrpfx: return Mem16(seg,size,None,None,self.Stream.Word())
		else:            return Mem32(seg,size,None,None,0,self.Stream.Dword())

	def visit_Immediate_FarTarget(self,i):
		"""Create a :class:`AP16` or :class:`AP32` depending upon the address
		size prefix.
		
		:param `.ImmEnc` i:
		:rtype: :class:`.FarTarget`
		"""
		if self.addrpfx: 
			#raise ExerciseError("X86Decoder::visit_Immediate_FarTarget:AP16")
			off = self.Stream.Word()
			return AP16(self.Stream.Word(),off)
		else:
			#raise ExerciseError("X86Decoder::visit_Immediate_FarTarget:AP32")
			off = self.Stream.Dword()
			return AP32(self.Stream.Word(),off)

	def visit_SignExtImm_Iw(self,i): 
		"""Read a byte from the steam and sign-extend it to a word.
		
		:param `.SignedImm` i:
		:rtype: :class:`.Iw`
		"""
		#raise ExerciseError("X86Decoder::visit_SignExtImm_Iw")
		return Iw(sign_extend_8_16(self.Stream.Byte()))

	def visit_SignExtImm_Id(self,i): 
		"""Read a byte from the steam and sign-extend it to a dword.
		
		:param `.SignedImm` i:
		:rtype: :class:`.Id`
		"""
		#raise ExerciseError("X86Decoder::visit_SignExtImm_Id")
		return Id(sign_extend_8_32(self.Stream.Byte()))	
	
	def visit_SizePrefix(self,z):     
		"""Depending upon the operand size prefix, call :meth:`visit` on either 
		*z*'s *yes* or *no* member.
		
		:param `.SizePrefix` z:
		:rtype: :class:`.Operand`
		"""
		#raise ExerciseError("X86Decoder::visit_SizePrefix")
		return self.visit(z.yes if self.sizepfx else z.no)

	def visit_AddrPrefix(self,a):    
		"""Depending upon the address size prefix, call :meth:`visit` on either 
		*z*'s *yes* or *no* member.
		
		:param `.AddrPrefix` a:
		:rtype: :class:`.Operand`
		"""
		#raise ExerciseError("X86Decoder::visit_AddrPrefix")
		return self.visit(a.yes if self.addrpfx else a.no)

	def oJCommon(self,x): 
		"""Common method for decoding jumps.  Calculate the target of the jump, and
		then truncate to 16-bits if there was an address size prefix.
		
		:param integer x: displacement from the end of the current instruction
		:rtype: :class:`.JccTarget`
		"""
		ea = self.Stream.Pos()
		x = x + ea
		if self.addrpfx: x = x&0xFFFF
		return JccTarget(x,ea)
	
	def visit_Immediate_JccTarget(self,j):
		"""Read a dword-sized displacement (or word-sized if there was an address
		prefix) and call :meth:`oJCommon`.
		
		:param `.ImmEnc` j:
		:rtype: :class:`.JccTarget`
		"""
		if self.addrpfx: return self.oJCommon(self.Stream.Word())
		else:            return self.oJCommon(self.Stream.Dword())
		
	def visit_SignExtImm_JccTarget(self,i):
		"""Read a byte-sized displacement, sign-extend it to a dword, and call
		:meth:`oJCommon`.
		
		:param `.SignedImm` i:
		:rtype: :class:`.JccTarget`
		"""
		return self.oJCommon(sign_extend_8_32(self.Stream.Byte()))
