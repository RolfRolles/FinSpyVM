"""Classes for representing :class:`ModRM16` and :class:`ModRM32` memory
expressions.  Also contains functionality to decode a ModRM expression, given
a stream of bytes (as in :class:`.X86ByteStream.StreamObj`), and to produce an
encoded ModRM expression given the constituent parts of a memory expression.
"""

from X86MetaData import *
from X86 import *
from X86ByteStream import StreamObj
from Pandemic.Util.ExerciseError import ExerciseError

def sign_extend_8_16(b8): 
	"""Sign-extend an 8-bit integer to a 16-bit one."""
	return b8 if b8 & 0x80 == 0 else b8 | 0xFF00
def sign_extend_8_32(b8): 
	"""Sign-extend an 8-bit integer to a 32-bit one."""
	return b8 if b8 & 0x80 == 0 else b8 | 0xFFFFFF00
def little_endian_bytes(imm,n):
	"""Return a list of *n* 8-bit integers from the bytes of *imm*"""
	return map(lambda i: imm >> i*8 & 0xFF,xrange(n))

#: The register values specified by the :attr:`~.RM` field of a 
#: :class:`~.ModRM16` object.
modrm_16 = [(Bx,Si),(Bx,Di),(Bp,Si),(Bp,Di),(Si,None),(Di,None),(Bp,None),(Bx,None)]

class ModRM16(object):
	"""Describes a ModRM/16 object."""

	def init(self,mask,mod=None,ggg=None,rm=None,disp=None,dispsize=0):
		self._mod      = GuardedInteger(mod,3)
		self._ggg      = GuardedInteger(ggg,7)
		self._rm       = GuardedInteger(rm ,7)
		self._disp     = GuardedInteger(disp,mask)
		self._dispsize = dispsize
	
	def __init__(self,mod=None,ggg=None,rm=None,disp=None,dispsize=0):
		self.init(0xFFFF,mod,ggg,rm,disp,dispsize)
	
	@property
	def MOD(self): 
		"""The ModRM's top 2 bits."""
		return self._mod.value
	@MOD.setter
	def MOD(self,val):
		self._mod.value = val
	
	@property
	def GGG(self): 
		"""The ModRM's middle 3 bits."""
		return self._ggg.value
	@GGG.setter
	def GGG(self,val):
		self._ggg.value = val

	@property
	def RM(self): 
		"""The ModRM's low 3 bits."""
		return self._rm.value
	@RM.setter
	def RM(self,val):
		self._rm.value = val

	@property
	def Disp(self): 
		"""The ModRM memory expression's displacement, an integer."""
		return self._disp.value
	@Disp.setter
	def Disp(self,val):
		self._disp.value = val
	
	@property
	def DispSize(self):
		"""The ModRM memory expression's displacement size in bytes (0, 1, or 2 
		for :class:`ModRM16`; 0, 1, or 4 for :class:`ModRM32`)."""
		return self._dispsize
	@DispSize.setter
	def DispSize(self,val):
		self._dispsize = val
	
	def Decode(self,stream):
		"""Pull the fields of the ModR/M-16 apart, and consume a displacement if 
		specified.  Set the internal state of the object accordingly.  This is the
		"preliminary" decoding phase, after which the *stream* object is no longer
		necessary.  To actually obtain the parts of the memory expression specified
		by the ModRM, call :meth:`.Interpret`.
		
		:param `.X86ByteStream` stream: byte stream from which to consume bytes
		:raises: :exc:`~.X86.InvalidInstruction` if *stream* consumed 16 or more bytes
		"""
		# Decode ModR/M 16 byte
		b = stream.Byte()
		self.MOD,self.GGG,self.RM = b>>6&3,b>>3&7,b&7
		
		# The size of the displacement is generally specified by the mod.
		Disp,immsize = None,self.MOD
		
		# This special case specifies an address only, with no registers.
		if self.MOD == 0 and self.RM == 6: immsize = 2		
		
		# Decode the immediate, if one was specified.
		if immsize == 2: Disp = stream.Word() 
		if immsize == 1: Disp = sign_extend_8_16(stream.Byte())
		
		# Store the information about the displacement.
		self.Disp     = Disp
		self.DispSize = immsize
	
	def Interpret(self):
		"""For a :class:`.ModRM16` object whose :attr:`.MOD` field is not ``3`` 
		(i.e., the :class:`.ModRM16` object specifies a memory location and not a 
		register), examine the fields of the object and return a 4-tuple describing
		the 16-bit memory expression.
		
		:rtype: (:class:`~.R16Elt`, :class:`~.R16Elt`, integer, integer)
		:returns: A 4-tuple containing a base register, index register, integer
			displacement, and displacement size in bytes.  The register components
			may be ``None``; the displacement may be ``0`` or ``None``.
		:raises: assertion failure if :attr:`MOD` is ``3``.
		"""
		
		# We're interpreting memory expressions here, not registers.
		assert(self.MOD != 3)
	
		# Return a 4-tuple:  (basereg,indexreg,disp,dispsize)
		# m.Disp and m.DispSize will be set identically for any case, so we pull 
		# that logic out into this helper function.
		def ModRM16WithDisp(basereg,indexreg):
			return (basereg,indexreg,self.Disp,self.DispSize)
	
		# Handle the special case of an offset specified directly, i.e., with no
		# base or index register.
		if self.MOD == 0 and self.RM == 6: 
			# Hint: call ModRM16WithDisp.  What should the parameters be?
			# raise ExerciseError("ModRM16::Interpret: Offset-only special case")
			return ModRM16WithDisp(None,None)
		
		# Otherwise, the base and index registers are specified by m.RM.
	
		# Hint: ultimately, you will return the result of calling ModRM16WithDisp.
		# You will need to use the proper registers as specified by m.RM.
		# Take a look at the declaration of the data item named modrm_16.
		# raise ExerciseError("ModRM16::Interpret: General case")
		return ModRM16WithDisp(*(modrm_16[self.RM]))
	
	# This function is here to allow us to encode SIB bytes in the 32-bit case
	# (that class is derived from this one).
	def EncodeAdditional(self,b):
		"""Encode something between the ModRM and displacement.  Not used in the
		:class:`ModRM16` class, but overridden in the :class:`ModRM32` class.
		
		:param b: ModRM byte as a list
		:type b: integer list
		:rtype: integer list
		"""
		return b
	
	# Glue the bitfields together and append a displacement if necessary.
	def Encode(self):
		"""Concatenate the fields :attr:`MOD`, :attr:`GGG`, and :attr:`RM` together
		to form the ModRM-16 byte.  If a displacement is present, turn it into
		a list of little-endian bytes.
		
		:rtype: integer list
		"""
		b = [self.MOD << 6 | self.GGG << 3 | self.RM]
		b = self.EncodeAdditional(b)
		if self.Disp == None: return b
		return b + little_endian_bytes(self.Disp,self.DispSize)

	def EncodeFromParts(self,BaseReg,IndexReg,Disp):
		"""Given base and index registers, and an integer displacement, set the
		internal state to the corresponding integer values.  We must interpret the
		arguments and determine which special cases apply, if any.
		
		:param `.R16Elt` BaseReg: base register (or ``None``)
		:param `.R16Elt` IndexReg: index register (or ``None``)
		:param integer Disp: displacement (may be ``0`` or ``None``)
		:raises Exception: if *BaseReg* and *IndexReg* are an illegal register pair
		"""
		# Helper function:  set the MOD and displacement information.
		def SetModDisp(mod,disp,dispsize): 
			self.MOD,self.Disp,self.DispSize=mod,disp,dispsize
		
		# Is it the case where only an offset is specified?  If so, set MOD=0,RM=6,
		# and the displacement Disp with size 2.  Then, return.
		if BaseReg == None and IndexReg == None:
			# raise ExerciseError("ModRM16::EncodeFromParts: Displacement only")
			self.RM   = 6
			SetModDisp(0,Disp if Disp is not None else 0,2)
			return
		
		had_Disp = False
		# A displacement was not specified.  Set MOD to 0.  We may change it later
		# for [Bp], whose encoding mandates a displacement.
		if Disp == None or Disp == 0:
			# raise ExerciseError("ModRM16::EncodeFromParts: No displacement")
			self.MOD = 0
			
		# A displacement was specified, so set the displacement information.
		else:
			had_Disp = True
			# Check if the displacement can be encoded in 8 bits.  Set the MOD and
			# displacement information.
			# raise ExerciseError("ModRM16::EncodeFromParts: Displacement")
			mod,dispsize = (1,1) if Disp >= 0xFF80 or Disp < 0x80 else (2,2)
			SetModDisp(mod,Disp,dispsize)
		
		# A base register of Bp requires a displacement.  If no displacement has
		# already been specified, set the MOD and displacement information for a
		# 1-byte displacement 0.
		if BaseReg == Bp and not had_Disp:
			# raise ExerciseError("ModRM16::EncodeFromParts: Bp, no displacement")
			SetModDisp(1,0,1)
		
		# Set self.RM to the position of the base/index register pair within the list 
		# modrm_16.  This will throw an exception if the register combination is
		# invalid.
		try:
			# raise ExerciseError("ModRM16::EncodeFromParts: Set RM")
			self.RM = modrm_16.index((BaseReg,IndexReg))
		except e:
			print "Invalid ModRM/16 register pair"
			raise IndexError

	
class SIBBase(object):
	"""This class is only meaningful for 32-bit memory expressions encoded via 
	ModRM, and only if a SIB (Scale-Index-Base) byte is required."""
	def init(self,ss=None,idx=None,base=None,disp=None):
		self._ss   = GuardedInteger(ss  ,3)
		self._idx  = GuardedInteger(idx ,7)
		self._base = GuardedInteger(base,7)
	
	def __init__(self,ss_=None,idx_=None,base_=None):
		self.init(ss_,idx_,base_)

	@property
	def SCALE(self): 
		"""The top two bits of a SIB are the scale factor.
		* 0: 1
		* 1: 2
		* 2: 4
		* 3: 8"""
		return self._ss.value
	@SCALE.setter
	def SCALE(self,val):
		self._ss.value = val
	
	@property
	def INDEX(self): 
		"""The middle three bits of a SIB are the index register."""
		return self._idx.value
	@INDEX.setter
	def INDEX(self,val):
		self._idx.value = val

	@property
	def BASE(self): 
		"""The middle three bits of a SIB are the base register."""
		return self._base.value
	@BASE.setter
	def BASE(self,val):
		self._base.value = val

	def Encode(self):
		"""Concatenate the fields :attr:`SCALE`, :attr:`INDEX`, and :attr:`BASE` 
		together to form the ModRM-16 byte.  If a displacement is present, turn it
		into a list of little-endian bytes.
		
		:rtype: integer list
		"""
		return [self.SCALE << 6 | self.INDEX << 3 | self.BASE]

class ModRM32(ModRM16):
	def __init__(self,mod=None,ggg=None,rm=None,sf=None,idx=None,base=None,disp=None,dispsize=0):
		self.init(0xFFFFFFFF,mod,ggg,rm,disp,dispsize)
		
		if (sf is not None or idx is not None or base is not None):
			self._sib = SIBBase(sf,idx,base)
		else:
			self._sib = None
	
	@property
	def SIB(self):
		"""An optional Scale-Index-Byte (SIB) :class:`SIBBase` object."""
		if self._sib == None:
			self._sib = SIBBase()
		return self._sib
	@SIB.setter
	def SIB(self,val):
		self._sib = val

	def EncodeAdditional(self,b):
		"""If a :class:`SIBBase` SIB was required, append its encoding to the
		parameter *b*.  Otherwise, return *b* as-is.
		
		:param b: ModRM byte as a list
		:type b: integer list
		:rtype: integer list
		"""
		return b if self._sib == None else b + self.SIB.Encode()
	
	def Decode(self,stream):
		"""Pull the fields of the ModR/M-32 apart, and consume a displacement if 
		specified.  Set the internal state of the object accordingly.  This is the
		"preliminary" decoding phase, after which the *stream* object is no longer
		necessary.  To actually obtain the parts of the memory expression specified
		by the ModRM, call :meth:`.Interpret`.
		
		:param `.X86ByteStream` stream: byte stream from which to consume bytes
		:raises: :exc:`~.X86.InvalidInstruction` if *stream* consumed 16 or more bytes
		"""
		# Optional parts set to None
		ss,idx,base,disp = None,None,None,None
		
		# Decode ModR/M 32 byte
		b = stream.Byte()
		mod,ggg,rm = b>>6&3,b>>3&7,b&7
		
		# Default immediate size in bytes; special cases can change it.
		immsize = 0 if mod == 0 else 1 if mod == 1 else 4 if mod == 2 else 0
		
		# Special case:  no register is used; only a DWORD displacement.
		if mod == 0 and rm == 5: immsize = 4
		
		# SIB is present:
		if mod != 3 and rm == 4:
			
			# Decode SIB byte
			b = stream.Byte()
			ss,idx,base = b>>6&3,b>>3&7,b&7
			
			# Special case:  mod == 0 and base == EBP -> [idx*ss+dword]
			if mod == 0 and base == 5: immsize = 4
		
		# Decode any immediates that were specified
		if immsize == 1: disp = sign_extend_8_32(stream.Byte())
		if immsize == 4: disp = stream.Dword()
		
		# Set the parts within the ModRM32 object self
		self.MOD      = mod
		self.GGG      = ggg
		self.RM       = rm
		self.Disp     = disp
		self.DispSize = immsize
		if ss is not None:
			self.SIB.SCALE = ss
			self.SIB.INDEX = idx
			self.SIB.BASE  = base
		
	def Interpret(self):
		"""For a :class:`.ModRM32` object whose :attr:`.MOD` field is not 3 (i.e.,
		the :class:`.ModRM32` object specifies a memory location and not a 
		register), examine the fields of the object and return a 5-tuple describing
		the 32-bit memory expression.
		
		:rtype: (:class:`~.R32Elt`, :class:`~.R32Elt`,integer,integer,integer)
		:returns: A 5-tuple containing a base register, index register, scale 
			factor, integer displacement, and displacement size in bytes. The 
			register components may be ``None``; the displacement may be ``None``.
		:raises: assertion failure if :attr:`MOD` is ``3``.
		"""
		# We're interpreting memory expressions here, not registers.
		assert(self.MOD != 3)
  	
		# Adjust a 32-bit register from a number [0,7] to a 32-bit register enum.
		def AdjustReg32(n): return R32Elt(n)
		
		# Return a 5-tuple:  (basereg,indexreg,scalefac,disp,dispsize)
		# self.Disp and self.DispSize will be set identically for any case, so 
		# we pull that logic out into this helper function.
		def ModRM32WithDisp(basereg,indexreg,scalefac):
			return (basereg,indexreg,scalefac,self.Disp,self.DispSize)
  	
		# Is it the case that the expression is just a DWORD?
		if self.MOD == 0 and self.RM == 5: 
			# raise ExerciseError("ModRM32::Interpret: Displacement only")
			return ModRM32WithDisp(None,None,0)
		
		# Check to see if a SIB is specified.  If not, no index register is used.
		if self.RM != 4: 
			# raise ExerciseError("ModRM32::Interpret: No SIB")
			return ModRM32WithDisp(AdjustReg32(self.RM),None,0)
		
		# Set IndexReg and ScaleFac to empty at first.
		IndexReg,ScaleFac = None,0
		
		# Is it the case that an index register is present (i.e., SIB.IDX is not 
		# ESP)?  If so, set IndexReg with the adjusted register and set ScaleFac
		# to the SIB's SS field.
		if self.SIB.INDEX != 4:
			# raise ExerciseError("ModRM32::Interpret: Index/Scale")
			IndexReg,ScaleFac = AdjustReg32(self.SIB.INDEX),self.SIB.SCALE
		
		# Is it the case where MOD == 0 and BASE == 5?  In this case, there is no 
		# base register.  Call ModRM32WithDisp and return its value.
		if self.MOD == 0 and self.SIB.BASE == 5:
			# raise ExerciseError("ModRM32::Interpret: No base register")
			return ModRM32WithDisp(None,IndexReg,ScaleFac)
  	
		# The full SIB case applies.  We had a base register (in SIB.SREG), an index
		# (in IndexReg) and scale factor (in ScaleFac).
		#raise ExerciseError("ModRM32::Interpret: SIB general case")
		return ModRM32WithDisp(AdjustReg32(self.SIB.BASE),IndexReg,ScaleFac)

	def EncodeFromParts(self,BaseReg,IndexReg,ScaleFac,Disp):
		"""Given base and index registers, a scale factor, and an integer 
		displacement, set the internal state to the corresponding integer values.
		We must interpret the arguments and determine which special cases apply, if
		any.
		
		:param `.R32Elt` BaseReg: base register (or ``None``)
		:param `.R32Elt` IndexReg: index register (or ``None``)
		:param integer ScaleFac: scale factor (``0-3``)
		:param integer Disp: displacement (may be ``0`` or ``None``)
		"""
		def SetModDisp(mod,disp,dispsize): 
			self.MOD,self.Disp,self.DispSize=mod,disp,dispsize
		
		# Is it the case where only an offset is specified?  If so, set MOD=0,RM=5,
		# and the displacement Disp with size 4, and return.
		if BaseReg == None and IndexReg == None:
			#raise ExerciseError("ModRM32::EncodeFromParts: Displacement only")
			self.RM   = 5
			SetModDisp(0,0 if Disp is None else Disp,4)
			return
		
		had_Disp = False
	
		# A displacement was not specified.  Set MOD to 0.  We may need to change it
		# if some encoding mandates a displacement.
		if Disp == None or Disp == 0:
			#raise ExerciseError("ModRM32::EncodeFromParts: No displacement")
			self.MOD = 0
			
		# A displacement was specified.
		else:
			had_Disp = True
			# Check if the displacement can be encoded in 8 bits.
			#raise ExerciseError("ModRM32::EncodeFromParts: Displacement")
			mod,dispsize = (1,1) if Disp >= 0xFFFFFF80 or Disp < 0x80 else (2,4)
			SetModDisp(mod,Disp,dispsize)
			
		# Special case:  base register of EBP requires a displacement.  Create a byte
		# 0 if a displacement was not specified.
		if BaseReg == Ebp and not had_Disp:
			#raise ExerciseError("ModRM32::EncodeFromParts: EBP, no displacement")
			SetModDisp(1,0,1)
	
		# Was the index register not present (i.e., no SIB byte required)?
		if IndexReg is None:
			
			# Special case:  a SIB byte is required if ESP is the base register.
			# Create a 
			if BaseReg == Esp:
				#raise ExerciseError("ModRM32::EncodeFromParts: ESP base register")
				self.SIB.SCALE = 0
				self.SIB.INDEX = Esp.IntValue()
				self.SIB.BASE  = Esp.IntValue()
	
			# No special case:  put the register number into the RM field.
			#raise ExerciseError("ModRM32::EncodeFromParts: Set RM")
			self.RM = BaseReg.IntValue()
			return
		
		# From here on, we handle the SIB byte.
		self.RM = Esp.IntValue()
	
		# If there's no base register, we require a DWORD displacement and MOD=0.
		if BaseReg == None:
			#raise ExerciseError("ModRM32::EncodeFromParts: No base register")
			self.SIB.BASE = Ebp.IntValue()
			SetModDisp(0,Disp if Disp is not None else 0,4)
	
		# Otherwise, store the base register index into the SREG field of the SIB.
		else:
			#raise ExerciseError("ModRM32::EncodeFromParts: Base register")
			self.SIB.BASE = BaseReg.IntValue()
	
		# Set the ScaleFac and adjust IndexReg.
		#raise ExerciseError("ModRM32::EncodeFromParts: Scale/Index")
		self.SIB.SCALE = ScaleFac
		self.SIB.INDEX = IndexReg.IntValue()