# Import FinSpy VM object definitions and simplification code
from FinSpyVM import *
from Simplify import Simplify

# Get the virtualized function data generated from function extraction scripts
from VirtualizedFunctionData import *

# This dictionary maps a Jcc type to its 2nd opcode byte
# (first byte for all of them is 0x0F).
JCC_TO_OPCODE_DICT = dict([
("JO", 0x80),("JNO",0x81),("JC", 0x82),("JNC",0x83),
("JZ", 0x84),("JNZ",0x85),("JBE",0x86),("JA", 0x87),
("JS", 0x88),("JNS",0x89),("JP", 0x8A),("JNP",0x8B),
("JL", 0x8C),("JGE",0x8D),("JLE",0x8E),("JG", 0x8F),
])

# This dictionary maps a VM key to its prologue bytes, if any
KEY_TO_PROLOGUE_BYTES_DICT = { x[0]:x[2] for x in KEY_TO_X86_VMENTRY_AND_PROLOGUE_BYTES_TUPLES }

# This dictionary maps a virtualized function start address to its VM key
X86_VMENTRY_TO_KEY_DICT    = { x[1]:x[0] for x in KEY_TO_X86_VMENTRY_AND_PROLOGUE_BYTES_TUPLES }

# Given: insns, a list of FinSpy VM instructions
# Generate and return an array of x86 machine code bytes for the VM program
def RebuildX86(insns, newImageBase):
	# Array of x86 machine code, built instruction-by-instruction
	mcArr  = []
	
	# Bookkeeping: which VM position/key corresponds to which
	# position within the x86 machine code array mcArr above
	locsDict = dict()
	keysDict = dict()
	
	# List of fixups for branch instructions
	locFixups = []
	
	# List of fixups for virtualized function calls
	keyFixups = []
	
	# List of fixups for non-virtualized function calls
	binaryRelativeFixups = []

	# Iterate through the FinSpy VM instructions
	for i in insns:
		
		# currLen is the current position within mcArr
		currLen = len(mcArr)
		
		# Bookkeeping: memorize the x86 position for the 
		# VM instruction's VM position and VM key 
		locsDict[i.Pos] = currLen
		keysDict[i.Key] = currLen

		# New: length of prologue instructions inserted before
		# devirtualized FinSpy VM instruction. Only obtains a
		# non-zero value if this instruction corresponds to the
		# beginning of a virtualized function.	
		prologueLen = 0
		
		# New: is this VM instruction the beginning of a 
		# virtualized function?
		if i.Key in KEY_TO_PROLOGUE_BYTES_DICT:
		
			# Get the prologue bytes that should be inserted
			# before this VM instruction.
			prologueBytes = KEY_TO_PROLOGUE_BYTES_DICT[i.Key]
			
			# Increase the length of the instruction.
			prologueLen += len(prologueBytes)
			
			# Copy the raw x86 machine code for the prologue
			# into the mcArr array before devirtualizing the
			# instruction.
			mcArr.extend(prologueBytes)

		# Is it "Raw X86" or "X86JUMPOUT"? Just emit the
		# raw x86 machine code if so
		if isinstance(i,RawX86StraightLine):
			mcArr.extend(i.Remainder[0:i.DataLen])
		elif isinstance(i,RawX86Jumpout):
			mcArr.extend(i.Instruction[0:i.DataLen])

		# Is it a branch instruction?
		elif isinstance(i, ConditionalBranch):

			# Get the name of the branch
			jccName = INSN_NAME_DICT[i.Opcode]

			# Is this an unconditional jump?
			if jccName == "JMP":

				# Emit 0xE9 (x86 JMP disp32)
				mcArr.append(0xE9)

				# Opcode is 1 byte
				dispPos = 1

			# Otherwise, it's a conditional jump
			else:
				# Conditional jumps begin with 0x0F
				mcArr.append(0x0F)
				
				# Second byte is specific to the condition code
				mcArr.append(JCC_TO_OPCODE_DICT[jccName])

				# Opcode is 2 bytes
				dispPos = 2

			# Emit the displacement DWORD (0 for now)
			mcArr.extend([0x00, 0x00, 0x00, 0x00])

			# Emit a fixup: the JMP displacement targets
			# the VM location specified by i.VMTarget
			locFixups.append((i.Pos,dispPos,i.VMTarget))

		# Is this an "X86CALLOUT" ("Direct Call")?
		elif isinstance(i,RawX86Callout):
			
			# New: emit 0xE8 (x86 CALL disp32)
			mcArr.append(0xE8)
			
			# Was the target a non-virtualized function?
			if i.X86Target in NOT_VIRTUALIZED:
				
				# Emit a fixup from to the raw target
				binaryRelativeFixups.append((i.Pos,prologueLen+1,i.X86Target))
				
			# Otherwise, the target was virtualized
			else:
				# Emit a fixup to the devirtualized function body
				# specified by the key of the destination
				keyFixups.append((i.Pos,prologueLen+1,i.X86Target))


			# Write the dummy destination DWORD in the x86 CALL
			# instruction that we just generated. This will be 
			# fixed-up later.
			mcArr.extend([0x00, 0x00, 0x00, 0x00])
		
		# These should be the only 4 cases left at this point.
		# If not, something went wrong; bail.
		else:
			print "Can't devirtualize", i
			assert(False)

	# Process branch fixups. They contain:
	# * srcBegin: beginning of devirtualized branch instruction
	# * srcFixup: distance into devirtualized branch instruction
	#             where displacement DWORD is located
	# * dst:      the position within the VM program where the
	#             branch destination is located
	for srcBegin, srcFixup, dst in locFixups:
		# Find the machine code address for the source
		mcSrc = locsDict[srcBegin]
		# Find the machine code address for te destination
		mcDst = locsDict[dst]
		# Set the displacement DWORD within x86 branch instruction
		StoreDword(mcArr, mcSrc+srcFixup, mcDst-(mcSrc+srcFixup+4))

	# Process virtualized function call fixups, which contain:
	# * srcBegin: beginning of devirtualized CALL instruction
	# * srcFixup: distance into devirtualized CALL instruction
	#             where displacement DWORD is located
	# * dst:      the X86CALLOUT target address
	for srcBegin, srcFixup, dst in keyFixups:

		# Find the machine code address for the source
		mcSrc = locsDict[srcBegin]

		# Lookup the x86 address of the target in the information
		# we extracted for virtualized functions. Extract the key 
		# given the function's starting address.
		klDst = X86_VMENTRY_TO_KEY_DICT[dst]
	
		# Find the machine code address for the destination
		mcDst = keysDict[klDst]

		# Set the displacement DWORD within x86 CALL instruction
		StoreDword(mcArr, mcSrc+srcFixup, mcDst-(mcSrc+srcFixup+4))

	# Process non-virtualized call fixups. Same contents as above.
	for srcBegin, srcFixup, dst in binaryRelativeFixups:

		# Find the machine code address for the source
		mcSrc = locsDict[srcBegin]
	
		# Compute the distance between the end of the x86
		# CALL instruction (at the address at which it will
		# be stored when inserted back into the binary) and
		# the raw x86 address of the X86CALLOUT target
		fixup = dst-(newImageBase+mcSrc+srcFixup+4)
	
		# Set the displacement DWORD within x86 CALL instruction
		StoreDword(mcArr, mcSrc+srcFixup, fixup)

	# Now we replace the function pointers to virtualized functions
	# with the addresses of the devirtualized function bodies.
	#
	# The positions in posList might correspond to VM instructions
	# that were eliminated through simplification. However, we still
	# expect that the VM instruction into which the referencing
	# VM instruction was merged still contains the reference to the
	# virtualized function. So, we look for the previous instruction
	# that was devirtualized, and the next instruction that was
	# devirtualized. Their positions in mcArr give us a region to 
	# search for the dword value.
	#
	# dword: the virtual address of a virtualized function
	# posList: the list of VM instruction positions 
	# referencing the value of dword.
	for dword, posList in []:#ALL_FIXED_UP_DWORDS.items():
	
		# dwArr is the dword we're looking for, as bytes.
		dwArr = [0]*4
		StoreDword(dwArr, 0, dword)
		
		# For each position referencing dword:
		for pos in posList:
		
			# Set the low and high offset within the
			# devirtualized blob to None
			lowPos,highPos = None,None
		
			# posSearchLow is the backwards iterator
			posSearchLow = pos
		
			# Continue while we haven't located a prior
			# instruction with a devirtualization offset
			while not lowPos:
			
				#print "Low: searching pos %#lx" % posSearchLow
				# Does posSearchLow correspond to a 
				# devirtualized instruction? I.e., not
				# something eliminated by a pattern
				# substitution.
				if posSearchLow in locsDict:

					# Yes: get the position and quit
					lowPos = locsDict[posSearchLow]

				else:
					# No: move to the previous instruction
					posSearchLow -= INSN_DESC_SIZE

			# Now search for the next higher VM position
			# with a devirtualization offset
			posSearchHigh = pos+INSN_DESC_SIZE


			# Continue while we haven't located a later
			# instruction with a devirtualization offset
			while not highPos:

				#print "High: searching pos %#lx" % posSearchHigh

				# Does posSearchLow correspond to a 
				# devirtualized instruction? I.e., not
				# something eliminated by a pattern
				# substitution.
				if posSearchHigh in locsDict:
			
					# Yes: get the position and quit
					highPos = locsDict[posSearchHigh]
				else:
					# No: move to the next instruction
					posSearchHigh += INSN_DESC_SIZE


			#print "Nearest: mcArr[%lx..%lx] = %s, decArr[%lx..%lx]" % (lowPos, highPos, mcArr[lowPos:highPos], posSearchLow, posSearchHigh)

			# After the code above, we now have:
			# lowPos: the beginning of the next-lower devirtualized instruction
			# highPos: the beginning of the next-higher devirtualized instruction
			# We now byte-search the array between those positions looking for
			# the value of dword.
			
			# Haven't yet found it.
			bFound = False
			
			# Search through mcArr at the positions specified above
			for i in xrange(lowPos,highPos):
				
				# Say we have found it
				bFoundInner = True
				
				# Byte-for-byte comparison
				for j in xrange(len(dwArr)):
					if mcArr[i+j] != dwArr[j]:
						bFoundInner = False
						break
					else:
						#print "Position %lx matched position %d (%lx)" % (i+j, j, dwArr[j])
						pass

				# Did we find dword within the specified region?
				if bFoundInner:
					#print "Found dword %08lx at position %d" % (dword, i)

					# Retrieve the key corresponding to the VM entrypoint @ dword
					# Retrieve the position of the key within mcArr from that
					# Replace the VM Entrypoint dword in the instruction with the mcArr position
					StoreDword(mcArr, i, keysDict[X86_VMENTRY_TO_KEY_DICT[dword]])
					ApplyFixupSpecified(mcArr, i, newImageBase)

					# Mark that we have replaced the DWORD
					bFound = True
					break
			
			# After searching and replacing.
			if not bFound:
				#print "Did not find dword %08lx in [%d,%d]" % (dword, lowPos, highPos)
				pass
	
	# Return the raw byte array.
	return bytearray(mcArr)

# Disassemble and simplify VM bytecode program
newInsns = Simplify([ x for x in bytes_from_file("Tmp/dec.bin") ])

# Devirtualize, new base address is 0x500000
mcArr = RebuildX86(newInsns, 0x500000)

# Write devirtualized code to file
with open("./Tmp/mc-take2.bin", "wb") as f:
	f.write(mcArr)
