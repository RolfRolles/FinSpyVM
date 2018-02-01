"""This module simulates C-style enumerations."""

class EnumElt(object):
	"""This is the base class for all enumeration elements.  In actuality, each
	enumeration shall correspond to a class derived from this one, and each 
	enumeration element shall be an object of that type."""
	def __init__(self,value):
		if value > self._l:
			print "%s: value %d too large (%d)" % (self.__class__.__name__, value, self._l)
		self._locked = False
		self._value = value
		self._locked = True
	def __call__(self,value): 
		"""This method returns a new enumeration element of the same type, 
		corresponding to the integer *value*.
		
		:param integer value: integer for which to create an :class:`EnumElt`
		:rtype: :class:`EnumElt`
		"""
		return type(self)(value)
	
	def IntValue(self):       
		"""This method returns the integer corresponding to a particular 
		enumeration element.
		
		:rtype: integer
		"""
		return self._value

	# This is pretty stupid -- we try to prevent the user from modifying the 
	# integer value associated with an enumeration element.  Except, in so doing,
	# we lose the ability to modify any data within the object.  So we keep 
	# another variable called _locked that determines whether variables can be
	# written.  It's dumb; don't think too hard about it.
	def __setattr__(self,name,value):
		if self._locked:
			print "Trying to assign %r.%s = %s" % (self,name,value)
			raise RuntimeError
		super(EnumElt, self).__setattr__(name, value)

	# Boring class methods follow
	def __eq__(self,other):
		return type(self) == type(other) and self._value == other._value
	def __ne__(self,other):   return not(self == other)
	def __str__(self):        return self._strdict[self._value]
	def __repr__(self):       return self._reprdict[self._value]
	def __hash__(self):       return hash(self._value)

def enum(name,names,reprs,sequential):
	"""Create a new type derived from :class:`EnumElt`, whose type name is the
	parameter *name* suffixed with the string "Elt".  Then, create instances of
	that class for each string in *sequential*, whose Python-level string shall
	be the corresponding element in *names*, and whose Python-level 
	representation shall be the corresponding element in *reprs*.  I.e., all 
	three of the mentioned lists must have the same length.
	
	:param string name: the name of the enumeration.
	:param string names: a list of names for the enumeration elements, i.e., 
		the values returned by a call to ``str``.
	:param string reprs: a list of representations for the enumeration elements,
		i.e., the values returned by a call to ``repr``.
	:param string sequential:  a list of strings, in order, corresponding to the
		variable names of the elements.
	:rtype: ( `type` , :class:`EnumElt` list )
	"""
	l = len(sequential)
	ToString = { k:v for (k,v) in zip(range(l),names) }
	Reprs    = { k:v for (k,v) in zip(range(l),reprs) }
	elttype  = type(name+"Elt",(EnumElt,),{'_locked':False,'_strdict':ToString,'_reprdict':Reprs,'_l':l})
	elements = map(elttype,range(l))
	return (elttype,elements)

def enum_strfn(name, strfn, reprs):
	"""This function specializes :func:`enum`.  Use it when the Python ``str``
	strings for the enumeration elements are related to the representation 
	strings (in *reprs* ).  *strfn* is responsible for producing the ``str``
	string, given the representation string.

	:param string name: the name of the enumeration.
	:param function strfn: a function that, given the representation string of
		an enumeration element, creates its Python-level ``str`` string.
	:param string reprs:  a list of strings, in order, corresponding to the
		Python-level ``repr`` strings for the elements.
	:rtype: ( `type` , :class:`EnumElt` list )
	"""
	names    = map(strfn,reprs)
	return enum(name,names,reprs,reprs)

def enum_upper(name,sequential): 
	"""A further-specialized version of :func:`enum_strfn`, used when the ``str``
	strings for the enumeration elements are the upper-case versions of the 
	representation strings in *sequential* .

	:param string name: the name of the enumeration.
	:param string sequential:  a list of strings, in order, corresponding to the
		Python-level ``repr`` strings for the elements.
	"""
	return enum_strfn(name,str.upper,sequential)

def enum_lower(name,sequential): 
	"""A further-specialized version of :func:`enum_strfn`, used when the ``str``
	strings for the enumeration elements are the lower-case versions of the 
	representation strings in *sequential* .

	:param string name: the name of the enumeration.
	:param string sequential:  a list of strings, in order, corresponding to the
		Python-level ``repr`` strings for the elements.
	"""
	return enum_strfn(name,str.lower,sequential)	

def enum_specialstr(name,sequential):
	"""This function specializes :func:`enum`.  *sequential* is a list of pairs
	of strings, the first being the representation string, the second being the
	``str`` string.

	:param string name: the name of the enumeration.
	:param string sequential:  a list of strings, in order, corresponding to the
		Python-level ``repr`` strings for the elements.
	:rtype: ( `type` , :class:`EnumElt` list )
	"""
	names = map(lambda (a,b): b,sequential)
	reprs = map(lambda (a,b): a,sequential)
	return enum(name,names,reprs,sequential)