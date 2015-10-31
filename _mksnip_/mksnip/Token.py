
import collections


Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])


class Tokens(object):
	"""
	Create a new tokens from the given token list.
	Tokens is composed of iterable items.
	"""

	__pos = 0;
	# __elems = [Token(), ...]

	def __init__(self, tokens):
		"""
		argument "tokens" is expected to be Token list such as:
			[Token(..), Token(..), ..]
		"""
		self.__elems = tokens

	@property
	def elems(self):
		return self.__elems

	def __iter__(self):
		""" Return self """
		return self

	def next(self):
		""" Return next token, and increment iterator. """
		try:
			next_val = self.__elems[self.__pos]
		except IndexError:
			raise StopIteration
		else:
			self.__pos += 1
			return next_val

	def seek(self):
		""" Return next token. """
		return self.__elems[self.__pos]
