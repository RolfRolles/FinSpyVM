"""To simplify the boilerplate involved with hashing in our classes, i.e.,
implementing the ``__hash__`` method, this module provides binary and unary 
hash functions whose behavior is modified through a parameter, which is 
basically a salt.  For a given concrete class, this parameter is known as its
"hash code"."""

import random

def rol(bits,value,amt):
	"""Implementation of standard rotate left."""
	bitmask = bits-1
	amt = amt & bitmask
	return (bitmask & (value << amt)) | (bitmask & (value >> (bits-amt)))

def ror(bits,value,amt):
	"""Implementation of standard rotate right."""
	bitmask = bits-1
	amt = amt & bitmask
	return (bitmask & (value >> amt)) | (bitmask & (value << (bits-amt)))

# An array of random numbers.
random_numbers = map(lambda e: random.randint(0,0xFFFFFFFF),xrange(0,64))

def unary_hash(x,n):
	"""Unary hash of a value *x*, implemented by XORing against a list of random
	integers.  To provide salt, use the *n* parameter (the hash code) to decide 
	which random number to XOR against.
	
	:param integer x: value to hash.
	:param integer n: salt / hash code.
	:rtype: integer
	"""
	if n > len(random_numbers):
		n %= len(random_numbers)
	return x ^ random_numbers[n]

# Eight different ways of combining two hashes.
BinaryHashFunctions = [
(lambda x,y: rol(32,x,13) ^ ror(32,y,7)),
(lambda x,y: rol(32,x,7)  - ror(32,y,13)),
(lambda x,y: rol(32,x,5)  + ror(32,y,9)),
(lambda x,y: rol(32,x,9)  ^ ror(32,y,5)),
(lambda x,y: rol(32,x^y-2,5)),
(lambda x,y: ror(32,x+y,5)),
(lambda x,y: rol(32,x-y+5,13)),
(lambda x,y: ror(32,x+y-7,13))]

def binary_hash(x,y,n):
	"""Binary hash.  Use ``n&7`` to determine one of eight possible binary hash
	functions, and then XOR with the *n*th random integer for good measure.  
	Note that I have no idea what I am doing nor what constitutes a "good 
	measure".

	:param integer x: first value to hash.
	:param integer y: second value to hash.
	:param integer n: salt / hash code.
	:rtype: integer
	"""
	idx = n
	if n < 0 or n > len(random_numbers):
		idx = abs(n) % len(random_numbers)
	hashres = BinaryHashFunctions[n & 7](x,y) # Truncate n to 0..7
	return hashres ^ random_numbers[idx]
