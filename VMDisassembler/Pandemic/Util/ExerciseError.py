class ExerciseError(Exception):
	"""This error is thrown for functionality to be implemented in exercises."""
	def __init__(self,str):
		""":param str Error string describing incomplete exercise.
		:type str str"""
		self.str = str
	def __str__(self): 
		return self.str
