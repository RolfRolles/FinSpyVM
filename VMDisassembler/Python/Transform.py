from Pandemic.Util.ExerciseError import ExerciseError

test_map1_expected = [2,4,6]		

# Exercise:  write a definition for mapfn such that the output is
# as above under test_map1_expected.
def test_map1():
	l = [1,2,3]
	def mapfn(i):
		raise ExerciseError("Functional::Map1")
	return map(mapfn,l)

test_map2_expected = [(1,2,3),(4,5,6),(7,8,9)]

# Exercise:  write a definition for mapfn such that the output is 
# as above under test_map2_expected.
def test_map2():
	l = [2,5,8]
	def mapfn(i):
		raise ExerciseError("Functional::Map2")
	return map(mapfn,l)

test_map3_expected = [(1,True),(2,True),(3,True)]

# Exercise:  write a definition for mapfn such that the output is 
# as above under test_map3_expected.
def test_map3():
	l = [1,2,3]
	def mapfn(i):
		raise ExerciseError("Functional::Map3")
	return map(mapfn,l)

test_filter1_expected = [60,61,62,63,64]
	
def raise_exerror(string):
	raise ExerciseError(string)

# Exercise:  write a definition for the lambda function such that
# as above under test_filter1_expected.
def test_filter1():
	# This is a list [0,1,2,3,4,...,99]
	l = range(0,100)
	# expression involving the variable i.
	
	# Exercise: replace the call to raise_exerror in the lambda with some boolean
	# expression involving the variable i.	
	return filter(lambda i: raise_exerror("Functional::Filter1"),l)

test_filter2_expected = [0,1,2,97,98,99]

# Exercise:  write a definition for the lambda function such that
# as above under test_filter2_expected.
def test_filter2():
	l = range(0,100)
	# expression involving the variable i.
	
	# Exercise: replace the call to raise_exerror in the lambda with some boolean
	# expression involving the variable i.	
	return filter(lambda i: raise_exerror("Functional::Filter2"),l)

test_filter3_expected = [(1,True),(3,True)]

# Exercise:  write a definition for the lambda function such that
# the function returns as above under test_filter3_expected.  Remember
# that the integer part of a Const is kept in a field called "int".
def test_filter3():
	l = [(1,True),(2,False),(3,True),(4,False)]
	# expression involving the variable i.
	
	# Exercise: replace the call to raise_exerror in the lambda with some boolean
	# expression involving the variable i.
	return filter(lambda i: raise_exerror("Functional::Filter3"),l)

test_reduce1_expected = 3628800

# Exercise:  multiply all of the integers in the list l.  You will also need
# to set initial_value to something sensible.
def test_reduce1():
	l = xrange(1,11) # [1,...,10]
	def reducefn(a,i):
		raise ExerciseError("Functional::Reduce1")
	initial_value = 0
	return reduce(reducefn,l,initial_value)

test_reduce2_expected = 20

# Exercise:  add all the constants in list l.  The result should evaluate to 
# 20.  How must initial_value be set in order to achieve this sum?
def test_reduce2():
	# [1,2,3,4]
	l = range(1,4)
	def reducefn(a,c):
		raise ExerciseError("Functional::Reduce2")
	initial_value = 1
	return reduce(reducefn,l,initial_value)

test_reduce3_expected = "boom bam kablow blaow"

# Exercise:  set initial_value, and write a lambda function such that the 
# string above is returned.
def test_reduce3():
	l = ["bam","kablow","blaow"]
	def reducefn(e,n):
		raise ExerciseError("Functional::Reduce3")
	initial_value = "replaceme"
	return reduce(reducefn,l,initial_value)

if __name__ == "__main__":
	bFailed = False

	def test_harness(l_tests,string):
		bLocalFailed = False
		for i in xrange(0,len(map_tests)):
			(f,res) = map_tests[i]
			actual = f()
			if res != actual:
				print "%s test #%d failed; expecting %s, got %s" % (string,i+1,res,actual)
				bLocalFailed = True
		return bLocalFailed

	map_tests = [(test_map1,test_map1_expected),(test_map2,test_map2_expected),(test_map3,test_map3_expected)]
	bFailed |= test_harness(map_tests,"Map")

	filter_tests = [(test_filter1,test_filter1_expected),(test_filter2,test_filter2_expected),(test_filter3,test_filter3_expected)]
	bFailed |= test_harness(filter_tests,"Filter")

	reduce_tests = [(test_reduce1,test_reduce1_expected),(test_reduce2,test_reduce2_expected),(test_reduce3,test_reduce3_expected)]
	bFailed |= test_harness(reduce_tests,"Reduce")

	if bFailed:
		print "Tests failed, assignment incomplete!"
	else:
		print "All tests passed, assignment complete!"	

