import itertools

test_product1_expected = set([('a', 'd'),('a', 'e'),('a', 'f'),('b', 'd'),('b', 'e'),('b', 'f'),('c', 'd'),('c', 'e'),('c', 'f')])

# Exercise:  use itertools.product to return an iterator that produces the values
# shown above under test_product1_expected (though not necessarily in order).
def test_product1():
	raise NotImplementedError("test_product1")
	return itertools.product(None)

test_product2_expected = set([(1, 2, 3),(1, 2, 4),(1, 3, 3),(1, 3, 4),(2, 2, 3),(2, 2, 4),(2, 3, 3),(2, 3, 4)])

# Exercise:  use itertools.product to return an iterator that produces the values
# shown above under test_product2_expected (though not necessarily in order).
def test_product2():
	raise NotImplementedError("test_product2")
	return itertools.product(None)

test_ifilter1_expected = set([(1, 2, 3),(1, 2, 4),(1, 3, 3),(1, 3, 4),(2, 3, 3),(2, 3, 4)])

# Exercise: use either itertools.ifilter or itertools.ifilterfalse to remove those
# tuples from test_product2_expected where the first and second components are the
# same.  Remember:  ifilter keeps values when its filter function returns True;
# ifilterfalse keeps values when its filter function returns False.
def test_ifilter1():
	g = test_product2()
	def filterfn((a,b,c)):
		raise NotImplementedError("test_ifilter1")
	return itertools.ifilter(filterfn,g)

test_imap1_expected = set(['ad','ae','af','bd','be','bf','cd','ce','cf'])

# Exercise: use either itertools.imap or itertools.starmap to concatenate those
# tuples from test_product1_expected into one string per tuple, where the 
# string's first character is the first element of the tuple, and its second
# character is the second element of the tuple.
def test_imap1():
	g = test_product1()
	def mapfn((a,b)):
		raise NotImplementedError("test_imap1")
	return itertools.imap(mapfn,g)

if __name__ == "__main__":
	bFailed = False

	def test_harness(l_tests,string):
		bLocalFailed = False
		for i in xrange(0,len(l_tests)):
			(f,res) = l_tests[i]
			actual = set(f())
			if res != actual:
				print "%s test #%d failed; expecting %s, got %s" % (string,i+1,res,actual)
				bLocalFailed = True
		return bLocalFailed

	product_tests = [(test_product1,test_product1_expected),(test_product2,test_product2_expected)]
	bFailed |= test_harness(product_tests,"Product")
	
	filter_tests = [(test_ifilter1,test_ifilter1_expected)]
	bFailed |= test_harness(filter_tests,"IFilter")

	map_tests = [(test_imap1,test_imap1_expected)]
	bFailed |= test_harness(map_tests,"IMap")

	if bFailed:
		print "Tests failed, assignment incomplete!"
	else:
		print "All tests passed, assignment complete!"	

