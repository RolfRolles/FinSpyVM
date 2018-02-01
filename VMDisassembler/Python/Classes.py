# A basic class, deriving from "object".  This is necessary to use new-style 
# classes.
class Basic(object):
	# It defines one method, DoSomething.
	def DoSomething(self,i):
		return 10+i

if __name__=="__main__":
	# Create a Basic object.  It takes no parameters, so use ().
	b = Basic()
	
	# This should print 15.
	print b.DoSomething(5)

# This class stores a piece of data in a class member called "data".
# Note that we have renamed the method parameter more commonly called "self" 
# to "s".
class HasData(object):
	def Store(s,v):    
		s.data = v         
	def Retrieve(s):   
		return s.data      
		
if __name__=="__main__":
	# Create a HasData object.  It takes no parameters, so use ().
	h = HasData()
	
	# Store 5 in its data member.
	h.Store(5)
	
	# This should print 5.
	print h.Retrieve()
	
	# This should also print 5.
	print h.data

# A base class to illustrate inheritance.
class Base(object):
	def Interface(self):
		self.InternalFunction()
	def InternalFunction(self):
		print "Base"
		
# Derives from Base, above.
class Derived(Base):
	def InternalFunction(self):
		print "Derived"

# Derives from Derived, and thus also Base.
class Derived2(Derived):
	# This method was not present in the original class.
	def OriginalInternal(self):
		# Syntax for calling a method in a base class, rather than an overridden
		# method.
		Base.InternalFunction(self)

if __name__=="__main__":
	b = Base()
	# Prints "Base"
	b.Interface()
	
	d = Derived()
	# Prints "Derived"
	d.Interface()
	# Prints "Base"
	Base.Interface(d)

	d2 = Derived2()
	# Prints "Base"
	d2.OriginalInternal()

class Construct(object):
	# This example has a constructor, the __init__ function.  This is called when
	# the object is created.  Note in the block below that you can create a 
	# Construct object like Construct(0,0).
	def __init__(self,a,b):
		self.a = a
		self.b = b

if __name__=="__main__":
	# Pass the correct number of arguments to the constructor.
	c = Construct(1,2)

	# Prints 1,2
	print c.a,c.b

# This class illustrates how to make ==, !=, str(), repr(), and hash()
# work properly for your custom classes.
class A(object):
	def __init__(s,i): s.i = i
	def __repr__(s):   return "A(%d)" % s.i
	def __str__(s):    return str(s.i)
	def __hash__(s):   return hash(s.i)
	def __ne__(s,o):   return not s==o
	def __eq__(s,o):   return type(s)==type(o) and s.i == o.i
	
if __name__=="__main__":
	# Create two instances
	a = A(1)
	b = A(1)
	
	# Prints "True"
	print (a == b)

	# Prints "True" 
	print (hash(a) == hash(b))

	# Create a dictionary
	d = dict()
	d[a] = "a"
	d[b] = "b"
	
	# Prints "1"
	print len(d.items())
	
	# Representation-print d, sensibly:  "{A(1): 'b'}"
	print repr(d)

	# String-print a, sensibly:  "1"
	print a

# This class illustrates what happens if you don't override those functions.
class A(object):
	def __init__(s,i): s.i = i

if __name__=="__main__":
	# Create two instances
	a = A(1)
	b = A(1)
	
	# Prints "False"
	print (a == b)

	# Prints "False" 
	print (hash(a) == hash(b))

	# Create a dictionary
	d = dict()
	d[a] = "a"
	d[b] = "b"
	
	# Prints "2"
	print len(d.items())
	
	# Representation-print d, inanely
	print repr(d)

	# String-print a, inanely
	print a

# This class uses "properties" to control access to its variables.
class Word(object):
	# Property decorator.
	@property
	# This is the getter. The name of the method is the name of the property.
	def i(self): return self._i

	# Property decorator.
	@i.setter
	# This is the setter. The name of the method is the name of the property.
	# It performs masking.
	def i(self,i): self._i = i & 0xFFFF

	# The constructor invokes the setter.
	def __init__(self,i): self.i = i

if __name__=="__main__":
	w = Word(0x12345678)
	# Prints "0x5678"
	print hex(w.i)
	
	w.i = 0x88888888
	# Prints "0x8888L"
	print hex(w.i)
