
import collections


Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])


class Tokens(object):
	"""docstring for Tokens"""

	__pos = 0;
	# __elems = [Token(), ...]

	def __init__(self, tokens):
		self.__elems = tokens

	@property
	def elems(self):
		return self.__elems

	def __iter__(self):
		return self

	def next(self):
		try:
			next_val = self.__elems[self.__pos]
		except IndexError:
			raise StopIteration
		else:
			self.__pos += 1
			return next_val

	def seek(self):
		return self.__elems[self.__pos]
