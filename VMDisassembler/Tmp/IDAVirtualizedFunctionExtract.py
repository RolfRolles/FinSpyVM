from idaapi import *
import idc

# Ranges for addresses within the program
PROG_BEGIN = 0x00400000
PROG_END   = 0x00420FFF

# Where the VM interpreter begins
VM_INTERPRETER_ADDRESS = 0x00401950

# Number of instructions to process when walking forward from a virtualized
# function start address looking for PUSH REG32 pair
MAX_NUM_PROLOG_INSTRUCTIONS = 20

# Number of instructions to process when walking backwards from a jump to
# the VM entrypoint looking for PUSH IMM32.
MAX_NUM_OBFUSCATED_JMP_INSTRUCTIONS = 5

# Given an address that references the VM dispatcher, extract
# the VM instruction key pushed beforehand, and the names of
# the two registers used for junk obfuscation. Return a tuple
# with all information just described.
def ExtractKey(vmXref):
	currEa = vmXref
	Key = None
	
	# Walk backwards from the VM cross-reference up to a 
	# specified number of instructions.
	for _ in xrange(MAX_NUM_OBFUSCATED_JMP_INSTRUCTIONS):
		
		# Is the instruction "PUSH DWORD"?
		if idc.GetMnem(currEa) == "push" and idc.GetOpType(currEa, 0) == o_imm:
			
			# Extract the key, exit loop
			Key = idc.GetOperandValue(currEa, 0)
			break
		
		# Otherwise, move backwards by one instruction
		else:
			currEa = idc.PrevHead(currEa, 0)
	
	# After looping, did we find a key?
	if Key:
		# Extract the first operands of the two subsequent instructions
		prevEa1 = idc.PrevHead(currEa,  0)
		prevEa2 = idc.PrevHead(prevEa1, 0)
		
		# Were they push instructions?
		if idc.GetMnem(prevEa1) == "pop" and idc.GetMnem(prevEa2) == "pop":
			# Return the information we just collected
			return (vmXref,Key,idc.GetOpnd(prevEa1,0),idc.GetOpnd(prevEa2,0))
		
		# If not, be noisy about the error
		else:
			print "%#lx: found key %#lx, but not POP reg32, inspect manually" % (vmXref, Key)
			return (vmXref,Key,"","")
	
	# Key not found, be noisy
	else:
		print "%#lx: couldn't locate key within %d instructions, inspect manually" % (xref,MAX_NUM_OBFUSCATED_JMP_INSTRUCTIONS)
		return None

# Apply the function above to all references to the VM interpreter.
def ExtractKeys(vmDispatcher):
	keyList = []
	for xref in [x for x in XrefsTo(vmDispatcher, idaapi.XREF_FAR) if x.iscode]:
		ret = ExtractKey(xref.frm)
		if ret: keyList.append(ret)
	return keyList

# Extract information from all references to the VM
locKey = ExtractKeys(VM_INTERPRETER_ADDRESS)

# Sort that information by the address of the reference to the VM interpreter
sLocKey = sorted(locKey, key=lambda x: x[0])

# Given:
# * ea, the address of a virtualized function
# Find the entry in sLocKey whose VM entry branch 
# location is the closest one greater than ea
# Ouput:
# The tuple of information for the next VM entry
# instruction following ea
def LookupKey(ea):
	global sLocKey
	for i in xrange(len(sLocKey)):
		if sLocKey[i][0] < ea:
			continue
		return sLocKey[i]
	return sLocKey[i-1]

# Given the address of a virtualized function, look up the VM key and
# register information. Return a new tuple with the virtualized function
# start address in place of the address that jumps to the VM interpreter.
def CollateCalloutTarget(tgt):
	assocData = LookupKey(tgt)
	return (tgt, assocData[1], assocData[2], assocData[3])

# Apply the function above to all virtualized function addresses.
def CollateCalloutTargets(targets):
	return map(CollateCalloutTarget, targets)

# Given:
# * CallOut, the target of a function call
# * Key, the VM Instruction key DWORD pushed
# * Reg1, the name of the first obfuscation register
# * Reg2, the name of the second obfuscation register
# Extract the prologue bytes and return them.
def ExtractPrologue(CallOut, Key, Reg1, Reg2):
	
	# Ensure we have two register names.
	if Reg1 == "" or Reg2 == "":
		return (Key, CallOut, [])
	
	currEa = CallOut
	
	# Walk forwards from the call target.
	for i in xrange(MAX_NUM_PROLOG_INSTRUCTIONS):
		
		# Look for PUSH of first obfuscation register.
		if idc.GetMnem(currEa) == "push" and idc.GetOpnd(currEa, 0) == Reg1:
			nextEa = idc.NextHead(currEa, currEa+16)

			# Look for PUSH of second obfuscation register.
			if idc.GetMnem(nextEa) == "push" and idc.GetOpnd(nextEa, 0) == Reg2:
				thirdEa = idc.NextHead(nextEa, nextEa+16)

				# Sanity check: first junk instruction is "mov reg2, address"
				if idc.GetMnem(thirdEa) == "mov" and idc.GetOpnd(thirdEa, 0) == Reg2:
					destAddr = idc.GetOperandValue(thirdEa, 1)
					
					# Was "address" legal?
					if destAddr <= PROG_END and destAddr >= PROG_BEGIN:
						return (Key, CallOut, [ idc.Byte(CallOut + j) for j in xrange(currEa-CallOut) ])
					
					# If not, be noisy
					else:
						print "# 0x%08lx/0x%08lx: found push %s / push %s, not followed by mov %s, address" % (CallOut, currEa, Reg1, Reg2, Reg2)
						pass

		# Move forward by one instruction
		currEa = idc.NextHead(currEa, currEa+16)

	# If we didn't find the two PUSH instructions within some
	# specified number, be noisy.
	print "# 0x%08lx: did not find push %s / push %s sequence within %d instructions" % (CallOut, Reg1, Reg2, MAX_NUM_PROLOG_INSTRUCTIONS)
	return (Key, CallOut, [])
  
# Extract the prologues from all virtualized functions.
def GetPrologues(calloutTargets):
	return map(lambda data: ExtractPrologue(*data),CollateCalloutTargets(calloutTargets))

# This is the output from ExtractCalloutTargets for our sample.
cot = [4221442, 4200220, 4230663, 4229136, 4233745, 4230164, 4226581, 4221974, 4199959, 4199454, 4214303, 4200481, 4228274, 4236862, 4230719, 4230222, 4220499, 4229207, 4225624, 4224602, 4230927, 4223585, 4234338, 4226661, 4200550, 4233831, 4200046, 4212336, 4221556, 4199614, 4228730, 4235388, 4228380, 4238976, 4199360, 4199534, 4233879, 4212376, 4223134, 4226207, 4231335, 4215465, 4200619, 4232881, 4227250, 4238964, 4230334, 4224706, 4200133, 4239047, 4216008, 4226761, 4229836, 4223694, 4229333, 4223192, 4234972, 4221670, 4231911, 4200688, 4235051, 4229380, 4228875, 4230412, 4199694, 4226831, 4223257, 4227356, 4230443, 4229932, 4229427, 4200757, 4228416, 4212551, 4230987, 4214604, 4227408, 4226899, 4219220, 4223317, 4221272, 4230493, 4227936, 4199778, 4200293, 4232551, 4199280, 4213622, 4214647, 4228478, 4199232, 4230028, 4230543, 4221334, 4235674, 4223906, 4223395, 4199858, 4226996, 4200373, 4220344, 4229279, 4233205, 4227520, 4213698, 4234184, 4221386, 4230606, 4230110, 4228583, 4223476, 4227061, 4234231]

# Print the prologue information nicely.
for prologueInfo in GetPrologues(cot):
	Key = prologueInfo[0]
	FuncEa = prologueInfo[1]
	prologue = prologueInfo[2]
	print "(%#lx, %#lx, %s)," % (Key, FuncEa, prologue)