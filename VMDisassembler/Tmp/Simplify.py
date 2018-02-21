# Import all of the FinSpy VM object types
from FinSpyVM import *

# Is the VM instruction "MOV SCRATCH, 0"?
def IsMovScratch0(insn):
	if isinstance(insn,MovScratch0):
		return True
	if isinstance(insn,MovScratchImm32):
		if insn.Imm32 == 0:
			return True
	return False

# Is the VM instruction "MOV SCRATCH, IMM32"?
# Return the IMM32 if so.
def IsMovScratchImm32(insn):
	if isinstance(insn,MovScratch0):
		return 0
	if isinstance(insn,MovScratchImm32):
		return insn.Imm32
	return None

# Is the VM instruction "MOV SCRATCH, REG32"?
# Return the REG32 number if so.
def IsMovScratchReg(insn):
	if isinstance(insn,MovScratchDisp32):
		return insn.Disp32
	if isinstance(insn,MovScratchDisp8):
		return insn.Disp8
	return None

# Is the VM instruction "ADD SCRATCH, REG32"?
# Return the REG32 number if so.
def IsAddScratchReg(insn):
	if isinstance(insn,AddScratchDisp32):
		return insn.Disp32
	return None

# Is the VM instruction "ADD SCRATCH, IMM32"?
# Return the IMM32 if so.
def IsAddScratchImm32(insn):
	if isinstance(insn,AddScratchImm32):
		return insn.Imm32
	return None

# Is the instruction "PUSH SCRATCH"?
def IsPushScratch(insn):
	return isinstance(insn,PushScratch)

# Is the instruction "MOV REG32, SCRATCH"?
def IsMovRegScratch(insn):
	if isinstance(insn,MovDisp8Scratch):
		return insn.Disp8
	return None

# Create a FinSpy VM "Raw X86" instruction with the specified
# VM instruction key and VM instruction position, given the
# Python representation of an x86 instruction in x86Insn.
def MakeRawX86(Pos, Key, x86Insn):
	# Create a FinSpy VM "Raw X86" instruction with dummy
	# content at the correct position (specified by Pos)
	newInsn = RawX86StraightLine([0]*INSN_DESC_SIZE, Pos)

	# Set the key to be the key from the first of the two
	# instructions of the two-instruction matched sequence
	newInsn.Key = Key

	# Encode the x86 instruction into machine code, store
	# the bytes in the FinSpy VM instruction
	newInsn.Remainder = EncodeInstruction(x86Insn)
	
	# Cache the length of the x86 instruction's machine code
	newInsn.DataLen = len(newInsn.Remainder)

	# Cache the textual disassembly for that instruction
	newInsn.X86 = str(x86Insn)
	
	# Return the FinSpy VM instruction just constructed
	return newInsn
	
# Generic function for matching and replacing 2-instruction patterns
def GenericSimplify2(insnArr, fMatchReplace):
	# This function builds a new list of VM instructions by simplifying the 
	# existing list.
	newInsnArr = []

	# Iterate over all instructions in the list.
	insnArrLen = len(insnArr)
	idx = 0	
	while idx < insnArrLen:
		
		# Get the instruction at the current position
		i1 = insnArr[idx]

		# Make sure we don't go off the end by one...
		if idx + 1 < insnArrLen:
			
			# Get the instruction at the next position
			i2 = insnArr[idx+1]
			
			insnReplace = fMatchReplace(i1,i2)
			if insnReplace:
			
				# Add the new VM instruction to the output list.
				newInsnArr.append(insnReplace)	

				# Move forward by two in the original list and continue.
				idx += 2
				continue
		
		# Otherwise, if we are here, the VM instructions did not fit the pattern.
		# So copy the first instruction, and move on to the next one.
		newInsnArr.append(i1)
		idx += 1
	
	# After all is said and done, return the simplified list.
	return newInsnArr

# Find all occurrences of:
# * "MOV SCRATCH, 0" / "MOV SCRATCH, REG32", OR
# * "MOV SCRATCH, 0" / "ADD SCRATCH, REG32"
# Replace them with "MOV SCRATCH, REG32".
def FirstSimplifyInner(i1, i2):
	# If the first VM instruction is "MOV SCRATCH, 0"...
	if IsMovScratch0(i1):
				
		# Check to see if the second instruction is "MOV SCRATCH, REG32". If 
		# this function returns None, it wasn't. If it returns something other
		# than None, then it returns the register number.
		mr = IsMovScratchReg(i2)
				
		# Otherwise, check to see if the instruction was "ADD SCRACH, REG32",
		# and get the register number if it was (or None if it wasn't).
		if mr is None:
			mr = IsAddScratchReg(i2)
				
		# Did one of the two patterns match?
		if mr is not None:
					
			# Yes: make a new VM instruction, namely "MOV SCRATCH, REG32" to 
			# replace the two instruction sequence we just matched. Use the same
			# file offset position from the first instruction in the sequence.
			newInsn = MovScratchDisp8([0]*INSN_DESC_SIZE, i1.Pos)
					
			# Save the register number into the new instruction.
			newInsn.Disp8 = mr
			
			# Use the same VM instruction key as for the first instruction.
			newInsn.Key = i1.Key
			
			# Return the new instruction
			return newInsn
			
	# Pattern didn't match, return None
	return None
	
def FirstSimplify(insnArr):
	return GenericSimplify2(insnArr, FirstSimplifyInner)

# Find all occurrences of:
# * "MOV SCRATCH, REG32" / "PUSH SCRATCH, REG32"
# Replace them with "RawX86(push reg32)".
def SecondSimplifyInner(i1,i2):
	# Is the first instruction "MOV SCRATCH, REG32"?
	mr = IsMovScratchReg(i1)
	if mr is not None:
		# Is the second instruction "PUSH SCRATCH"?
		if IsPushScratch(i2):
			# Create the x86 instruction "push reg32"
			x86Insn = X86.Instruction([], XM.Push, X86.Gd(mr,True))
			
			# Return a VM "Raw x86" instruction
			return MakeRawX86(i1.Pos, i1.Key, x86Insn)
	# Pattern didn't match, return None.
	return None
	
def SecondSimplify(insnArr):
	return GenericSimplify2(insnArr, SecondSimplifyInner)

# Find all occurrences of:
# * "MOV SCRATCH, REG32_2" / "MOV REG32_1, SCRATCH"
# Replace them with "RawX86(mov reg32_1, reg32_2)".
def ThirdSimplifyInner(i1,i2):
	# Is the first instruction "MOV SCRATCH, REG32_2"?
	mr = IsMovScratchReg(i1)
	if mr is not None:
		
		# Is the second instruction "MOV REG32_1, SCRATCH"?
		mw = IsMovRegScratch(i2)
		if mw is not None:
			# Make the x86 instruction "mov reg32_1, reg32_2"
			x86Insn = X86.Instruction([], XM.Mov, X86.Gd(mw,True), X86.Gd(mr,True))
			
			# Return a "Raw X86" VM instruction
			return MakeRawX86(i1.Pos, i1.Key,x86Insn)
	
	# Pattern didn't match, return None
	return None

def ThirdSimplify(insnArr):
	return GenericSimplify2(insnArr, ThirdSimplifyInner)
	
def FourthSimplifyInner(i1,i2):
	# Is the first instruction "MOV SCRATCH, 0"?
	if IsMovScratch0(i1):
		# Is the second instruction:
		# * "MOV SCRATCH, IMM32", OR
		# * "ADD SCRATCH, IMM32"?
		imm = IsMovScratchImm32(i2)
		if imm is None:
			imm = IsAddScratchImm32(i2)
		if imm is not None:
			# If so, replace it with "MOV SCRATCH, IMM32"
			newInsn = MovScratchImm32([0]*INSN_DESC_SIZE, i1.Pos)
			newInsn.Imm32 = imm
			newInsn.Key = i1.Key
			return newInsn
	
	# Pattern didn't match, return None
	return None

	
def FourthSimplify(insnArr):
	return GenericSimplify2(insnArr, FourthSimplifyInner)
		
# Find all occurrences of "MOV SCRATCH, IMM32" / "PUSH SCRATCH"
# Replace them with Raw x86 "PUSH IMM32".
def FifthSimplifyInner(i1,i2):
	# Is the first instruction "MOV SCRATCH, IMM32"?
	imm = IsMovScratchImm32(i1)
	if imm is not None:
		# Is the second instruction "PUSH SCRATCH"?
		if IsPushScratch(i2):
			# Create the x86 instruction "push imm32"
			x86Insn = X86.Instruction([], XM.Push, X86.Id(imm))
			
			# Return a "Raw X86" instruction"
			return MakeRawX86(i1.Pos, i1.Key, x86Insn)

	# Pattern didn't match, return None
	return None
		
def FifthSimplify(insnArr):
	return GenericSimplify2(insnArr, FifthSimplifyInner)

# Get default segment register for a given base register
def DefaultSeg(r):
	return XM.SS if (r == REG_EBP or r == REG_ESP) else XM.DS

# Make a Mem32 object representing a 32-bit memory expression in
# terms of objects in my x86 library.
# * br: base register (number)
# * sr: scale register (number)
# * sf: scale factor (0-3)
# * disp: 32-bit immediate displacement
def MakeMemExpr(br, sr, sf, disp):

	# Get default segment
	if br is not None:
		seg = DefaultSeg(br)
	else:
		seg = DefaultSeg(sr)
	
	# Decide which registers are base/scale registers depending on
	# the parts that were specified by the memory address sequence.
	# Five different cases, none of them interesting.
	if sf is None:
		if br is None:
			if sr is None:
				return X86.Mem32(seg, XM.Md, None, None, 0, disp)
			else:
				return X86.Mem32(seg, XM.Md, XM.R32Elt(sr), None, 0, disp)
		else:
			return X86.Mem32(seg, XM.Md, XM.R32Elt(br), XM.R32Elt(sr), 0, disp)
	else:
		if br is None:
			return X86.Mem32(seg, XM.Md, None, XM.R32Elt(sr), sf, disp)
		else:
			return X86.Mem32(seg, XM.Md, XM.R32Elt(br), XM.R32Elt(sr), sf, disp)

# Given:
# * A list of FinSpy VM instructions in insnArr
# * An index within that list in idx
# 
# Determine if insnArr[idx] contains a memory address sequence.
# If not, return None. If so, create an x86 memory expression
# operand using my x86 library, and return it along with the
# number of instructions in the address sequence.
def DecodeAddressSequence(insnArr, idx):
	# Save position of index within insnArr
	oldIdx = idx
	
	# The first VM instruction in the sequence is usually "MOV SCRATCH, REG32".
	r1 = IsMovScratchReg(insnArr[idx])

	# Was it?
	if r1 is not None:

		# Yes, it was, so increment the current index
		idx += 1

		# Is the next VM instruction "SHL REG, [1/2/3]"?
		if isinstance(insnArr[idx],ShlScratchImm32):
			# Yes, copy the scale factor
			scaleFac = insnArr[idx].Imm32
			assert(scaleFac == 1 or scaleFac == 2 or scaleFac == 3)
			# Increment the current index
			idx += 1
		
		# Otherwise, there is no scale factor
		else:
			scaleFac = None

		# Is the next VM instruction "ADD SCRATCH, REG32"?
		r2 = IsAddScratchReg(insnArr[idx])
		if r2 is not None:
			# Yes, increment the current index
			idx += 1

		# Is the next VM instruction "ADD SCRATCH, IMM32"?
		disp32 = IsAddScratchImm32(insnArr[idx])
		if disp32 is not None:
			# Yes, increment the current index
			idx += 1
		
		# Make a memory expression from the parts, and return the length
		# of the memory address sequence
		return (idx-oldIdx, MakeMemExpr(r2, r1, scaleFac, disp32))
	
	# The second possibility is that the memory expression is a raw address.
	imm = IsMovScratchImm32(insnArr[idx])
	# Was it?
	if imm is not None:
		# Yes: make a memory expression from the address, and return the
		# length of the memory address sequence (namely, 1).
		return (1, MakeMemExpr(None,None,None,imm))

	# If we are here, neither of the memory address patterns matched, so 
	# signal match failure.
	return None

# Given:
# * A list of FinSpy VM instructions in insnArr
# * An index within that list in idx
# * A Mem32 memory expression in memExpr
# 
# Determine if insnArr[idx] contains a memory access sequence.
# If not, return None. If so, determine the accesss type, and
# create an x86 instruction using the memory address in memExpr.
#
# Return a tuple containing:
# * The number of VM instructions in the access pattern
# * The new x86 instruction
# Or None if the pattern didn't match.
def DecodeAccessSequence(insnArr, idx, memExpr):

	# Save position of index within insnArr
	oldIdx = idx

	# Case #1: "MOV [SCRATCH], REG32"
	if isinstance(insnArr[idx], MovPScratchDisp8):
		# mov [addrInfo], reg32 <- reg32 comes from insnArr[idx]
		return (1,X86.Instruction([], XM.Mov, memExpr, X86.Gd(insnArr[idx].Disp8, True)))
	
	# Case #2: "MOV [SCRATCH], IMM32"
	elif isinstance(insnArr[idx], MovPScratchImm32):
		# mov [addrInfo], imm32
		return (1,X86.Instruction([], XM.Mov, memExpr, X86.Id(insnArr[idx].Imm32)))
	
	# Remaining two cases all begin with "MOV SCRATCH, [SCRATCH]"
	elif isinstance(insnArr[idx], MovScratchPScratch):
		idx += 1
		
		# Case #3: "PUSH SCRATCH"
		if IsPushScratch(insnArr[idx]):
			# push [memExpr]
			return (2,X86.Instruction([], XM.Push, memExpr))
		else:
			# Case #4: "MOV REG32, SCRATCH"
			mr = IsMovRegScratch(insnArr[idx])
			if mr is not None:
				# mov reg32, [memExpr]
				return (2,X86.Instruction([], XM.Mov, X86.Gd(mr,True), memExpr))
			else:
				assert(False)
	
	else:
		# Case #5: "MOV REG, SCRATCH"
		mr = IsMovRegScratch(insnArr[idx])
		if mr is not None:
			# lea reg32, [memExpr]
			return (1,X86.Instruction([], XM.Lea, X86.Gd(mr,True), memExpr))
	
	# No patterns matched
	return None
		
# Find all memory address patterns followed by memory access patterns.
# Replace them with Raw X86 instructions for the corresponding 
# pre-virtualized x86 instructions.
def SixthSimplify(insnArr):
	insnArrLen = len(insnArr)
	newInsnArr = []
	idx = 0
	while idx < insnArrLen:
		dec = DecodeAddressSequence(insnArr, idx)
		if dec is not None:
			lenAddr,memExpr = dec
			acc = DecodeAccessSequence(insnArr, idx+lenAddr, memExpr)
			if acc is not None:
				lenAcc,insn = acc
				#for i in insnArr[idx:idx+lenAddr+lenAcc]:
				#	print i
				#print memExpr
				#print insn
				newInsnArr.append(MakeRawX86(insnArr[idx].Pos, insnArr[idx].Key, insn))
				idx += lenAddr + lenAcc
				continue
		newInsnArr.append(insnArr[idx])
		idx += 1
	return newInsnArr

# Apply all simplifications just discussed.
def Simplify(insns):
	newInsns = FirstSimplify(insns)
	newInsns = SecondSimplify(newInsns)
	newInsns = ThirdSimplify(newInsns)
	newInsns = FourthSimplify(newInsns)
	newInsns = FifthSimplify(newInsns)
	newInsns = SixthSimplify(newInsns)
	return newInsns