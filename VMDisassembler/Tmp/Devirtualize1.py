# Import FinSpy VM object definitions and simplification code
from FinSpyVM import *
from Simplify import Simplify

# This dictionary maps a Jcc type to its 2nd opcode byte
# (first byte for all of them is 0x0F).
JCC_TO_OPCODE_DICT = dict([
("JO", 0x80),("JNO",0x81),("JC", 0x82),("JNC",0x83),
("JZ", 0x84),("JNZ",0x85),("JBE",0x86),("JA", 0x87),
("JS", 0x88),("JNS",0x89),("JP", 0x8A),("JNP",0x8B),
("JL", 0x8C),("JGE",0x8D),("JLE",0x8E),("JG", 0x8F),
])

# Given: insns, a list of FinSpy VM instructions
# Generate and return an array of x86 machine code bytes for the VM program
def RebuildX86(insns):
	# Array of x86 machine code, built instruction-by-instruction
	mcArr  = []
	
	# Bookkeeping: which VM position/key corresponds to which
	# position within the x86 machine code array mcArr above
	locsDict = dict()
	keysDict = dict()
	
	# List of fixups for branch instructions
	locFixups = []
	
	# Iterate through the FinSpy VM instructions
	for i in insns:
		
		# currLen is the current position within mcArr
		currLen = len(mcArr)
		
		# Bookkeeping: memorize the x86 position for the 
		# VM instruction's VM position and VM key 
		locsDict[i.Pos] = currLen
		keysDict[i.Key] = currLen

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

		# Is it X86CALLOUT?
		elif isinstance(i,RawX86Callout):
			
			# We aren't handling this just yet.
			# Emit E8 00 00 00 00 (CALL $+5)
			# Revisit later
			mcArr.append(0xE8)
			mcArr.extend([0x00, 0x00, 0x00, 0x00])

		# These should be the only 4 cases left at this point.
		# If not, something went wrong; bail.
		else:
			print "Can't devirtualize", i
			assert(False)

	# Fixups contain:
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

	return bytearray(mcArr)

# Disassemble and simplify VM bytecode program
newInsns = Simplify(list(bytes_from_file("Tmp/dec.bin")))

# Devirtualize
mcArr = RebuildX86(newInsns)

# Write devirtualized code to file
with open("./Tmp/mc-take1.bin", "wb") as f:
	f.write(mcArr)

