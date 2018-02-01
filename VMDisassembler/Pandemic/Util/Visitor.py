"""This module implements two helper classes for implementing the visitor 
design pattern, :class:`~.Visitor.Visitor` and :class:`~.Visitor.Visitor2`.
"""

class Visitor(object):
	"""This class will help us implement visitor-style program analysis 
	algorithms.  It exports one method, :meth:`visit`, which uses Python's type
	introspection functionality to:

	#. Retrieve the class name ``CN`` (as a string) for parameter *x*.
	#. Determine whether the Visitor class has a callable method named ``visit_CN``.
	#. If it does, invoke that method.
	#. If not, invoke :meth:`Visitor.Default`, which defaults to raising an exception.

	To program a visitor-style algorithm which performs different actions for 
	different classes, derive a class from :class:`Visitor`, and declare a method
	called ``visit_CN`` for each class name ``CN`` that you want to handle.  Each
	such method takes one parameter, which shall be an instance of the class 
	indicated by the method's name.  Implement your algorithms for handling each 
	class type within these methods.

	To use your class to perform an analysis on an object *obj*, instantiate an 
	instance of the class derived from :class:`Visitor` (let's say it is held in
	a variable named *v*), and then invoke ``v.visit(obj)``.

	The behaviors of the visitor are configurable:

	* If you want to change the default behavior, override :meth:`Visitor.Default`.
	* If you want to change the names of the methods, override :meth:`Visitor.MakeMethodName`.
	* If you want to change how the method is invoked, override :meth:`Visitor.InvokeMethod`.
	"""
	def MakeMethodName(self,o):
		"""By default, return the string ``visit_CN``, where ``CN`` is *o*'s class
		name.
		
		:param object o: object to inspect
		:rtype: string
		:returns: The name of the method to invoke.
		"""
		return "visit_" + o.__class__.__name__
	
	def InvokeMethod(self,method,o):
		"""By default, simply invoke *method* with *o* as its sole parameter.
		
		:param method method: a method defined on the current class
		:param object o: any object type
		"""
		return method(o)

	def Default(self,method_name):
		"""By default, raise an exception if the method is not present."""
		raise RuntimeError("%s:  No method %s" % (self.__class__.__name__,method_name))

	def visit(self, o):
		"""This is what clients call to invoke the visitor algorithm.  You should
		never override this method."""
		# Retrieve the method name
		method_name = self.MakeMethodName(o)
		
		# Determine whether the current object (self) has a method by that name
		method = getattr(self, method_name, False)

		# If it does not, invoke the default handler.
		if not method: 
			return self.Default(method_name)
		
		# If it does, call InvokeMethod.
		if callable(method):
			return self.InvokeMethod(method,o)
		
		# Otherwise, if the member is present but is not a callable method, that
		# signifies that the progammer has declared a data item or some other non-
		# function thing with that name.  This is a programmer error, so throw
		# an exception.
		else:
			raise TypeError("%s:  %s present, but not callable" % method_name)

class Visitor2(object):
	"""This class implements the same idea as the previous visitor class, except
	that the :meth:`visit` method takes two parameters instead of one.  As 
	before, its behaviors for creating method names, invoking methods, and 
	default actions are configurable -- and you will probably need to use them 
	more often than in standard :class:`~.Visitor.Visitor` classes.  On the plus
	side, you can play some cool tricks with them, as we shall see."""

	def MakeMethodName(self,o1,o2):
		"""Default behavior:  concatenate the class names."""
		return "visit_" + o1.__class__.__name__ + "_" + o2.__class__.__name__
			
	def InvokeMethod(self,method,o1,o2):
		"""Default behavior:  pass both arguments to the method."""
		return method(o1,o2)

	def Default(self,method_name):
		"""Default behavior:  raise an exception."""
		raise RuntimeError("%s:  No method %s" % (self.__class__.__name__,method_name))

	def visit(self, o1,o2):
		"""Never override this method."""
		method_name = self.MakeMethodName(o1,o2)
		method = getattr(self, method_name, False)
		if not method: 
			return self.Default(method_name)
		if callable(method):
			return self.InvokeMethod(method,o1,o2)
		else:
			raise TypeError("%s:  %s present, but not callable" % method_name)
