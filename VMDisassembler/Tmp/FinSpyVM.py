# Import x86 library stuff
from Pandemic.X86.X86Encoder import X86Encoder
from Pandemic.X86.X86Decoder import X86Decoder
from Pandemic.X86.X86ByteStream import StreamObj
import Pandemic.X86.X86MetaData as XM
import Pandemic.X86.X86 as X86

#
# File constants
# 

# Size of a FinSpy VM instruction
INSN_DESC_SIZE = 0x18

# FinSpy VM instructions are encrypted via XOR, here's the key for this sample
xorVals = [0x1D, 0x59, 0xAD, 0x2A]

# Only the ends of FinSpy VM instructions encrypted; this constant dictates
# how many bytes from the beginning to skip. (Probably fixed and does not
# need to be a constant.)
PREAMBLE_SKIP = 0x4

# The base address for this sample
IMAGEBASE_FIXUP = 0x400000

# Beginning of first function in .text
TEXT_FUNCTION_BEGIN = 0x401340

# End of .text
TEXT_FUNCTION_END = 0x41EFC6

# Convenience function to extract a little-endian WORD from an array
def ExtractWord(arr, pos):
	return arr[pos] | (arr[pos+1] << 8)

# Convenience function to extract a little-endian DWORD from an array
def ExtractDword(arr, pos):
	return ExtractWord(arr,pos) | (ExtractWord(arr, pos+2) << 16)
	
# Convenience function to store a little-endian WORD in an array
def StoreWord(arr, pos, word):
	arr[pos]   = (word >> 0) & 0xFF
	arr[pos+1] = (word >> 8) & 0xFF

# Convenience function to store a little-endian DWORD in an array
def StoreDword(arr, pos, dword):
	StoreWord(arr, pos+0, (dword >>  0) & 0xFFFF)
	StoreWord(arr, pos+2, (dword >> 16) & 0xFFFF)

# This comes in in Phase #4; this dictionary collects all RVAs
# from VM instructions that specify imagebase fixups, so long
# as those RVAs lie in the .text section
from collections import defaultdict
ALL_FIXED_UP_DWORDS = defaultdict(list)

# Apply a fixup to a DWORD in an array. The fixup is
# specified. (Usually the IMAGEBASE_FIXUP, but also used
# for fixing up positions re: devirtualized base address).
# * arr: array
# * FixupPos: position in array where DWORD begins
# * FixupSpecified: amount to adjust
def ApplyFixupSpecified(arr, FixupPos, SpecifiedFixup):
	OriginalDword = ExtractDword(arr, FixupPos)
	FixedDword = OriginalDword + SpecifiedFixup
	StoreDword(arr, FixupPos, FixedDword)
	return FixedDword

# Apply an imagebase fixup to a DWORD in an array.
# arr: array
# FixupPos: position in array where DWORD begins
# InsnPos: VM instruction offset
def ApplyFixup(arr, FixupPos, InsnPos):
	# Python scoping statement
	global ALL_FIXED_UP_DWORDS
	
	# Extract DWORD, fix it up, write it back
	FixedDword = ApplyFixupSpecified(arr, FixupPos, IMAGEBASE_FIXUP)
	
	# If the RVA (now a VA) is in the .text section,
	# log it
	if FixedDword >= TEXT_FUNCTION_BEGIN and FixedDword <= TEXT_FUNCTION_END:
		ALL_FIXED_UP_DWORDS[FixedDword].append(InsnPos)


# Enumerated register numbers, identical to x86 machine code internal ordering
REG_EAX = 0
REG_ECX = 1
REG_EDX = 2
REG_EBX = 3
REG_ESP = 4
REG_EBP = 5
REG_ESI = 6
REG_EDI = 7

# List giving names to register numbers
REG_NAME_PAIRS = [
(REG_EAX, "EAX"),
(REG_ECX, "ECX"),
(REG_EDX, "EDX"),
(REG_EBX, "EBX"),
(REG_ESP, "ESP"),
(REG_EBP, "EBP"),
(REG_ESI, "ESI"),
(REG_EDI, "EDI"),
]

# Dictionary giving names to register numbers
REG_NAME_DICT = dict(REG_NAME_PAIRS)

# Enumerated FinSpy VM instruction types. The ordering is specific to this
# sample. For other samples, you'll need a method to identify the VM handlers
# and map their numbers onto these.
INSN_JL                            = 0x01
INSN_JNC                           = 0x03
INSN_JC                            = 0x04
INSN_JNP                           = 0x05
INSN_JLE                           = 0x08
INSN_JBE                           = 0x0A
INSN_JS                            = 0x0B
INSN_JNO                           = 0x0E
INSN_JNZ                           = 0x10
INSN_JNS                           = 0x11
INSN_JG                            = 0x15
INSN_JP                            = 0x19
INSN_JO                            = 0x1C
INSN_JZ                            = 0x1D
INSN_JA                            = 0x20
INSN_JGE                           = 0x21
INSN_JMP                           = 0x06
                                   
INSN_X86_JUMPOUT                   = 0x00
INSN_RAWX862                       = 0x17
INSN_RAWX863                       = 0x1B
INSN_X86_CALLOUT_RVA               = 0x07
                                   
INSN_LOAD_SCRATCH_FROM_REG32       = 0x16
INSN_ADD_REG_TO_SCRATCH            = 0x02
                                   
INSN_LOAD_SCRATCH_FROM_REG         = 0x0D
INSN_STORE_SCRATCH_TO_REG          = 0x0F
INSN_WRITE_REG_TO_SCRATCH_PTR      = 0x12

INSN_SHL_SCRATCH                   = 0x14
INSN_WRITE_IMM_TO_SCRATCH_PTR      = 0x0C
INSN_LOAD_SCRATCH_FROM_IMM         = 0x18
INSN_WRITE_SCRATCH_TO_IMM_PTR      = 0x1A
INSN_ADD_IMM_TO_SCRATCH            = 0x1F

INSN_LOAD_SCRATCH_FROM_SCRATCH_PTR = 0x09
INSN_PUSH_SCRATCH                  = 0x13
INSN_SET_SCRATCH_TO_ZERO           = 0x1E

# List giving names to the VM instruction constants
INSN_NAME_PAIRS = [
(INSN_JL                           , "JL"),
(INSN_JNC                          , "JNC"),
(INSN_JC                           , "JC"),
(INSN_JNP                          , "JNP"),
(INSN_JLE                          , "JLE"),
(INSN_JBE                          , "JBE"),
(INSN_JS                           , "JS"),
(INSN_JNO                          , "JNO"),
(INSN_JNZ                          , "JNZ"),
(INSN_JNS                          , "JNS"),
(INSN_JG                           , "JG"),
(INSN_JP                           , "JP"),
(INSN_JO                           , "JO"),
(INSN_JZ                           , "JZ"),
(INSN_JA                           , "JA"),
(INSN_JGE                          , "JGE"),
(INSN_JMP                          , "JMP"),

(INSN_X86_JUMPOUT                  , "X86_JUMPOUT"),
(INSN_RAWX862                      , "RAWX862"),
(INSN_RAWX863                      , "RAWX863"),
(INSN_X86_CALLOUT_RVA              , "X86_CALLOUT_RVA"),

(INSN_LOAD_SCRATCH_FROM_REG32      , "LOAD_SCRATCH_FROM_REG32"),
(INSN_ADD_REG_TO_SCRATCH           , "ADD_REG_TO_SCRATCH"),

(INSN_LOAD_SCRATCH_FROM_REG        , "LOAD_SCRATCH_FROM_REG"),
(INSN_STORE_SCRATCH_TO_REG         , "STORE_SCRATCH_TO_REG"),
(INSN_WRITE_REG_TO_SCRATCH_PTR     , "WRITE_REG_TO_SCRATCH_PTR"),

(INSN_SHL_SCRATCH                  , "SHL_SCRATCH"),
(INSN_WRITE_IMM_TO_SCRATCH_PTR     , "WRITE_IMM_TO_SCRATCH_PTR"),
(INSN_LOAD_SCRATCH_FROM_IMM        , "SET_IMM_TO_SCRATCH"),
(INSN_WRITE_SCRATCH_TO_IMM_PTR     , "WRITE_SCRATCH_TO_IMM_PTR"),
(INSN_ADD_IMM_TO_SCRATCH           , "ADD_IMM_TO_SCRATCH"),

(INSN_LOAD_SCRATCH_FROM_SCRATCH_PTR, "LOAD_SCRATCH_FROM_SCRATCH_PTR"),
(INSN_PUSH_SCRATCH                 , "PUSH_SCRATCH"),
(INSN_SET_SCRATCH_TO_ZERO          , "SET_SCRATCH_TO_ZERO"),

]

# Dictionary giving names to the VM instruction constants
INSN_NAME_DICT = dict(INSN_NAME_PAIRS)

# Given an x86 instruction as objects in my x86 library, encode it into
# machine code and return the array of bytes
def EncodeInstruction(insn):
	return X86Encoder().EncodeInstruction(insn)

# Base class for all FinSpy VM instruction types.
class GenericInsn(object):
	# A method for initializing specific subclasses
	def SpecificInit(self):
		pass
	
	# This method performs the basic decoding that is common to all
	# FinSpy VM instructions, namely, extracting the components that
	# are shared among all instruction types. Applying fixups here
	# turned out to be a useful design decision, as it centralizes
	# this functionality to one location, allowing us to easily 
	# monitor fixups (which turns out to be important).
	def Init(self, bytes, pos):
		self.Pos      = pos
		self.Key      = ExtractDword(bytes, 0)
		self.Opcode   = bytes[4]
		self.DataLen  = bytes[5]
		self.Op1Fixup = bytes[6]
		self.Op2Fixup = bytes[7]
		self.Remainder = bytes[8:]
		if self.Op1Fixup:
			ApplyFixup(self.Remainder, self.Op1Fixup & 0x7F, self.Pos)
		if self.Op2Fixup:
			ApplyFixup(self.Remainder, self.Op2Fixup & 0x7F, self.Pos)

	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
	
	# Derived clasess should override this
	def __str__(self):
		return ""
	
# Base class for all FinSpy VM branch instructions.
class ConditionalBranch(GenericInsn):
	
	# Perform decoding common to all branch instructions.
	def SpecificInit(self):
		
		# VMTarget, if non-zero, is treated as a displacement
		# from the current VM instruction's position
		self.VMTarget = ExtractDword(self.Remainder,1)
		self.X86Target = None
		if self.VMTarget == 0:
			self.VMTarget = None
			self.X86Target = ExtractDword(self.Remainder,5) + IMAGEBASE_FIXUP
		else:
			self.VMTarget = (self.Pos + self.VMTarget) & 0xFFFFFFFF
	
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	
	# Print the destination. Also print the fallthrough address if not JMP
	def __str__(self):
		mnem = INSN_NAME_DICT[self.Opcode]
		if self.VMTarget:
			tgt = "VM[%#08lx]" % self.VMTarget
		else:
			# This never happened in practice
			tgt = "X86[%#08lx]" % self.X86Target
		fallthrough = self.Pos + INSN_DESC_SIZE
		fallStr = "(fallthrough VM[%#08lx])" % fallthrough if mnem != "JMP" else ""
		return "%#08lx: %s %s %s" % (self.Pos, mnem, tgt, fallStr)

# This function converts the machine code from Raw X86 instructions into 
# strings for convenience in printing. In reality, none of the Raw X86
# instructions contained more than one instruction, but oh well.
def DecodeMulti(bytes, length):
	d = X86Decoder(StreamObj(bytes))
	start = 0
	insns = []
	while start < length:
		i2container = d.Decode(start)
		insns.append("%s" % i2container.instr)
		start += i2container.length
	return " // ".join(insns)

# This function disassembles the raw machine code for indirect jump instructions,
# changes the instructions therein to indirect call instructions, re-assembles
# them, and returns the new machine code with its textual disassembly.
#
# Input: bytes, an array of machine code for an indirect jump.
# Output: a tuple (string: disassembly, bytes: machine code for indirect call)
def ChangeJumpToCall(bytes):

	# Decode the x86 machine code
	i2container = X86Decoder(StreamObj(bytes)).Decode(0)

	# Fetch the instruction from the decoded bundle
	insn = i2container.instr

	# Ensure it's an indirect jump!
	assert(insn.mnem == XM.Jmp)

	# Change the mnemonic to call
	insn.mnem = XM.Call

	# Return new textual disassembly and machine code
	return (str(insn),EncodeInstruction(insn))

# This class describes "Call Indirect", a/k/a X86JUMPOUT instructions.
class RawX86Jumpout(GenericInsn):
	def SpecificInit(self):
		# Instruction data begins at self.Remainder[4:]
		# Fixup should have been applied during decoding, though technically not mandatory
		self.Instruction = self.Remainder[4:]
		x86,insn = ChangeJumpToCall(self.Instruction)
		self.X86 = x86
		self.Instruction = insn
		self.DataLen = len(insn)
		
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	# Print the disassembly rather than the machine code
	def __str__(self):
		return "%#08lx: X86JUMPOUT %s" % (self.Pos, self.X86)
		
# This class describes "Call Direct" a/k/a "X86CALLOUT" VM instructions.
class RawX86Callout(GenericInsn):
	def SpecificInit(self):
		# RVA begins at self.Remainder[4:]
		self.X86Target = ExtractDword(self.Remainder, 4) + IMAGEBASE_FIXUP
		
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
		
	def __str__(self):
		return "%#08lx: X86CALLOUT %#08lx" % (self.Pos, self.X86Target)

# This class describes "Raw X86" VM instructions.
class RawX86StraightLine(GenericInsn):
	def SpecificInit(self):
		self.X86 = DecodeMulti(self.Remainder, self.DataLen)
	
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	# Print the disassembly instead of the machine code.
	def __str__(self):
		return "%#08lx: X86 %s" % (self.Pos, self.X86)

# This class describes a family of Group #2 instructions whose encoding
# contains a DWORD interpreted as an x86 register number. We perform
# common decoding here, then derive classes for specific instructions
# in this family.
class StackDisp32(GenericInsn):
	def SpecificInit(self):
		self.Disp32 = ExtractDword(self.Remainder, 0)
	
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	
	# Common method for interpreting a register number as
	# a string. Used by __str__ in derived classes.
	def _StackStr(self):
		# This if statement was always taken in practice.
		if self.Disp32 >= 0 and self.Disp32 <= 7:
			return REG_NAME_DICT[self.Disp32]
		
		# This never happened in practice. It would have been
		# bad if it did.
		return "DWORD PTR [ESP+%#08lx*4]" % (((7-self.Disp32)+1) & 0xFFFFFFFF)

# Class describing "MOV SCRATCH, REG32" VM instructions, 32-bit displacement.
class MovScratchDisp32(StackDisp32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	
	def __str__(self):
		return "%#08lx: MOV SCRATCH, %s" % (self.Pos, self._StackStr())
	
# Class describing "ADD SCRATCH, REG32" VM instructions.
class AddScratchDisp32(StackDisp32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	def __str__(self):
		return "%#08lx: ADD SCRATCH, %s" % (self.Pos, self._StackStr())
		
# This class describes a family of Group #2 instructions whose encoding
# contains a BYTE interpreted as an x86 register number. We perform
# common decoding here, then derive classes for specific instructions
# in this family.
class StackDisp8(GenericInsn):
	def SpecificInit(self):
		self.Disp8 = self.Remainder[0]
	
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	# Common method for interpreting a register number as
	# a string. Used by __str__ in derived classes.
	def _StackStr(self):
		# This if statement was always taken in practice.
		if self.Disp8 >= 0 and self.Disp8 <= 7:
			return REG_NAME_DICT[self.Disp8]
		
		# These never happened in practice
		return "DWORD PTR [ESP+%#08lx*4]" % (((7-self.Disp8)+1) & 0xFFFFFFFF)

# Class describing "MOV SCRATCH, REG32" VM instructions, 8-bit displacement.
class MovScratchDisp8(StackDisp8):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	def __str__(self):
		return "%#08lx: MOV SCRATCH, %s" % (self.Pos, self._StackStr())

# Class describing "MOV REG32, SCRATCH" VM instructions, 8-bit displacement.
class MovDisp8Scratch(StackDisp8):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

	def __str__(self):
		return "%#08lx: MOV %s, SCRATCH" % (self.Pos, self._StackStr())

# Class describing "MOV [SCRATCH], REG32" VM instructions, 8-bit displacement.
class MovPScratchDisp8(StackDisp8):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: MOV DWORD PTR [SCRATCH], %s" % (self.Pos, self._StackStr())
	def ADT(self):
		return "Mov(DerefScratch,%s)" % self._OStackStr()

# This class describes a family of Group #2 instructions whose encoding
# contains a DWORD constant value. We perform common decoding here, 
# then derive classes for specific instructions in this family.
class Imm32(GenericInsn):
	def SpecificInit(self):
		self.Imm32 = ExtractDword(self.Remainder, 0)
	
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()

# Class describing "SHL SCRATCH, IMM32" VM instructions.
class ShlScratchImm32(Imm32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: SHL SCRATCH, %#08lx" % (self.Pos, self.Imm32)

# Class describing "MOV [SCRATCH], IMM32" VM instructions.
class MovPScratchImm32(Imm32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: MOV DWORD PTR [SCRATCH], %#08lx" % (self.Pos, self.Imm32)

# Class describing "MOV SCRATCH, IMM32" VM instructions.
class MovScratchImm32(Imm32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: MOV SCRATCH, %#08lx" % (self.Pos, self.Imm32)

# Class describing "MOV [IMM32], SCRATCH" VM instructions.
class MovPImm32Scratch(Imm32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: MOV DWORD PTR [%#08lx], SCRATCH" % (self.Pos, self.Imm32)

# Class describing "ADD SCRATCH, IMM32" VM instructions.
class AddScratchImm32(Imm32):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
		self.SpecificInit()
	def __str__(self):
		return "%#08lx: ADD SCRATCH, %#08lx" % (self.Pos, self.Imm32)

# Class describing "MOV SCRATCH, [SCRATCH]" VM instructions.
class MovScratchPScratch(GenericInsn):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
	def __str__(self):
		return "%#08lx: MOV SCRATCH, DWORD PTR [SCRATCH]" % self.Pos

# Class describing "PUSH SCRATCH" VM instructions.
class PushScratch(GenericInsn):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
	def __str__(self):
		return "%#08lx: PUSH SCRATCH" % self.Pos

# Class describing "MOV SCRATCH, 0" VM instructions.
class MovScratch0(GenericInsn):
	def __init__(self, bytes, pos):
		self.Init(bytes, pos)
	def __str__(self):
		return "%#08lx: MOV SCRATCH, 0" % self.Pos

# Dictionary mapping VM opcode constants to constructors for the correct 
# object type
INSN_CONSTRUCTOR_PAIRS = [
(INSN_JL                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JNC                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JC                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JNP                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JLE                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JBE                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JS                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JNO                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JNZ                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JNS                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JG                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JP                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JO                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JZ                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JA                           , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JGE                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),
(INSN_JMP                          , lambda bytes, pos: ConditionalBranch(bytes, pos)),

(INSN_X86_JUMPOUT                  , lambda bytes, pos: RawX86Jumpout(bytes, pos)),
(INSN_RAWX862                      , lambda bytes, pos: RawX86StraightLine(bytes, pos)),
(INSN_RAWX863                      , lambda bytes, pos: RawX86StraightLine(bytes, pos)),
(INSN_X86_CALLOUT_RVA              , lambda bytes, pos: RawX86Callout(bytes, pos)),

(INSN_LOAD_SCRATCH_FROM_REG32      , lambda bytes, pos: MovScratchDisp32(bytes, pos)),
(INSN_ADD_REG_TO_SCRATCH           , lambda bytes, pos: AddScratchDisp32(bytes, pos)),

(INSN_LOAD_SCRATCH_FROM_REG        , lambda bytes, pos: MovScratchDisp8(bytes, pos)),
(INSN_STORE_SCRATCH_TO_REG         , lambda bytes, pos: MovDisp8Scratch(bytes, pos)),
(INSN_WRITE_REG_TO_SCRATCH_PTR     , lambda bytes, pos: MovPScratchDisp8(bytes, pos)),

(INSN_SHL_SCRATCH                  , lambda bytes, pos: ShlScratchImm32(bytes, pos)),
(INSN_WRITE_IMM_TO_SCRATCH_PTR     , lambda bytes, pos: MovPScratchImm32(bytes, pos)),
(INSN_LOAD_SCRATCH_FROM_IMM        , lambda bytes, pos: MovScratchImm32(bytes, pos)),
(INSN_WRITE_SCRATCH_TO_IMM_PTR     , lambda bytes, pos: MovPImm32Scratch(bytes, pos)),
(INSN_ADD_IMM_TO_SCRATCH           , lambda bytes, pos: AddScratchImm32(bytes, pos)),

(INSN_LOAD_SCRATCH_FROM_SCRATCH_PTR, lambda bytes, pos: MovScratchPScratch(bytes, pos)),
(INSN_PUSH_SCRATCH                 , lambda bytes, pos: PushScratch(bytes, pos)),
(INSN_SET_SCRATCH_TO_ZERO          , lambda bytes, pos: MovScratch0(bytes, pos)),

]

# Dictionary mapping VM opcode constants to constructors
INSN_CONSTRUCTOR_DICT = dict(INSN_CONSTRUCTOR_PAIRS)

# Badly named main disassembler function. Given a filename, read one VM
# instruction's raw bytes at a time, decrypt via XOR, construct the right
# Python object, and yield it. This is a generator which loops over the
# whole file.
def bytes_from_file(filename):
	pos = 0
	with open(filename, "rb") as f:
		while True:
			chunk = f.read(INSN_DESC_SIZE)
			if chunk:
				chunk = map(ord, chunk)
				for i in xrange(PREAMBLE_SKIP,INSN_DESC_SIZE):
					chunk[i] ^= xorVals[i % 4]
				yield INSN_CONSTRUCTOR_DICT[chunk[4]](chunk, pos)
				pos += INSN_DESC_SIZE
			else:
				break
