
import collections
import re


Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])


class Tokens(object):
	"""docstring for Tokens"""

	__pos = 0;
	# __tokens = [Token(), ...]

	def __init__(self, tokens):
		self.__tokens = tokens

	@property
	def tokens(self):
		return self.__tokens

	def next(self):
		try:
			next_val = self.__tokens[self.__pos]
		except IndexError, e:
			raise StopIteration
		else:
			self.__pos += 1
			return next_val

	def seek(self):
		return self.__tokens[self.__pos]


class Parser(object):
	"""docstring for Parser"""

	# __string = ""
	# __tokens = Tokens( [Token(), ...] )

	def __init__(self, string):
		self.__string = string;

	@property
	def tokens(self):
		return self.__tokens

	def __iter__(self):
		return self

	def next(self):
		return self.__tokens.next()

	def seek(self):
		return self.__tokens.seek()

	def tokenize(self):
		self.__tokens = Tokens(list(self.tokenize_with_gen()))
		return self

	def tokenize_with_gen(self):
		keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
		token_specification = [
			('SKIP',    r'\t+'),          # Skip over spaces and tabs
			('BEGIN',   r'---[-\w]+---'), # Separator
			('NEWLINE', r'\n+'),          # Line endings
			('COMMENT', r'#.*'),          # Comment
			('TAG',     r'!'),
			('SNIPPET', r'.+'),
		]
		tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
		get_token = re.compile(tok_regex).match
		line = 1
		pos = line_start = 0
		match_obj = get_token(self.__string)
		while match_obj is not None:
			typ = match_obj.lastgroup
			if typ == 'NEWLINE':
				line_start = pos
				line += 1
			elif typ != 'SKIP':
				val = match_obj.group(typ)
				if typ == 'ID' and val in keywords:
					typ = val
				yield Token(typ, val, line, match_obj.start() - line_start)
			pos = match_obj.end()
			match_obj = get_token(self.__string, pos)
		if pos != len(self.__string):
			raise RuntimeError('Unexpected character %r on line %d' % (self.__string[pos], line))





statements = '''
	---class-method---
	# new(array)
	new(size) { |i| block }
	# try_convert(obj)
	---instance-method---
	assoc(obj)
	at(index)
	# bsearch { |x| block }
	# clear
	# collect { |e| block }
	# collect
	collect! { |e| block }
	collect!
	combination(n) { |c| block }
	combination(n)
	compact
	compact!
'''

parser = Parser(statements).tokenize()

for x in parser:
	print(x)


