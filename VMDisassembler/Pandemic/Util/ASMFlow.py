"""This module implements a generic class hierarchy for describing 
assembly-language control tranfer behaviors.  For example:

* ``nop`` simply transfers control to the next instruction
* ``jmp`` transfers control to some fixed location
* ``ret`` returns

This module contains a collection of classes, each deriving from 
:class:`FlowType`, to describe all possible varieties of control flow.
"""
class FlowType(object):
	def get_successors(self):
		"""Get the addresses of all possible following instructions.
		
		:rtype: ( integer list, integer list )
		:returns: A pair of lists:  those addresses referenced by jumps or normal
			execution, and those addresses that are the targets of call instructions.
		"""
		pass

class FlowOrdinary(FlowType):
	"""Used for most instructions, which only pass execution to the next 
	instruction."""
	def __init__(self,passthrough):
		self.passthrough = passthrough
	def get_successors(self):
		return ([self.passthrough],[])

class FlowCallDirect(FlowType):
	"""Direct calls target an address, and also implicitly reference a return 
  address."""
	def __init__(self,target,retaddr):
		self.target = target
		self.retaddr = retaddr
	
	def get_successors(self):
		return ([self.retaddr],[self.target])

class FlowJmpUnconditional(FlowType):
	"""Unconditional direct jumps only target one address."""
	def __init__(self,target,retaddr):
		self.target = target
	
	def get_successors(self):
		return ([self.target],[])

class FlowJmpConditional(FlowType):
	"""Conditional jumps can target two addresses."""
	def __init__(self,target,fallthrough):
		self.target = target
		self.fallthrough = fallthrough
	
	def get_successors(self):
		return ([self.target,self.fallthrough],[])

class FlowCallIndirect(FlowType):
	"""The destinations of indirect calls are unknown, but the return address 
	is known."""
	def __init__(self,fallthrough):
		self.retaddr = fallthrough
	
	def get_successors(self):
		return ([self.fallthrough],[])

class FlowJmpIndirect(FlowType):
	"""The destinations of indirect jumps are unknown."""
	def get_successors(self):
		return ([],[])

class FlowReturn(FlowType):
	"""Return statements are considered to have no outgoing references."""
	def get_successors(self):
		return ([],[])

