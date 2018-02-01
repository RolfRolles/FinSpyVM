"""This module implements "guarded" integers.  They are a fixed size, and are
always truncated to that size upon creation or modification.  As such, they are
similar to how integers normally behave in a language like C.  Implementing 
them this way allows us to represent things that are larger or smaller than
standard C types.  For example, we can represent a 3-bit integer, or a 9-bit
integer.
"""

class GuardedInteger(object):
	"""Guarded integers are always masked to some number of bits, allowing us to
	represent things like 8 and 16-bit integers without littering the code with
	expressions like ``x & 0xFF`` or ``x & 0xFFFFFFFF``.
	
	:ivar integer mask:  A bit-pattern reflecting the legal values of the 
	integer.  For example, an 8-bit value will use a *mask* of ``0xFF``.
	"""
	def __init__(self,val,mask):
		self.mask = mask
		self.value = val
		
	@property
	def value(self):
		"""The integer value itself.  Implemented as a class property.  When the
		client writes code like ``g.value = 0x1234``, the constant will 
		automatically be truncated to the size of the integer."""
		return self._value
	def value(self,val):
		self._value = None if val == None else val & self.mask
	
	def __hash__(self,value):
		return hash(self.value)
	
	def __repr__(self):
		return "%r" % self.value

	def __str__(self):
		return "%s" % self.value
