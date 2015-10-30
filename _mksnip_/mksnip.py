
import collections
import re


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
		except IndexError, e:
			raise StopIteration
		else:
			self.__pos += 1
			return next_val

	def seek(self):
		return self.__elems[self.__pos]


class Parser(object):
	"""docstring for Parser"""

	# __string = ""
	# __tokens = Tokens( [Token(), ...] )

	def __init__(self, string):
		self.__string = string;

	@property
	def tokens(self):
		return self.__tokens

	# --- iterable ---

	def __iter__(self):
		return self.__tokens

	def next(self):
		return self.__tokens.next()

	def seek(self):
		return self.__tokens.seek()

	# --- take token ---

	def tokenize(self):
		self.__tokens = Tokens(list(self.tokenize_with_gen()))
		return self

	def tokenize_with_gen(self):
		keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
		token_specification = [
			('SKIP',    r'\t+|#.*'),      # Skip tabs and Comments
			('BEGIN',   r'---[-\w]+---'), # Separator
			('NEWLINE', r'\n+'),          # Line endings
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

		yield Token('EOF', '---EOF---', line, 0)

	# --- parse ---

	# BNF:
	#   groups ::= Empty | group groups
	#   group  ::= begin snips
	#   snips  ::= Empty | snip snips
	#   snip   ::= tag str | str
	# 
	#   tag    ::= '!'
	#   str    ::= .*
	# 
	def parse(self):
		self.groups()
		return self

	def groups(self):
		while True:
			if self.__tokens.seek().typ == 'BEGIN':
				self.group()
			elif self.__tokens.seek().typ == 'EOF':
				print('eof')
				break
			else:
				print('no separator')
				break

	def group(self):
		token = self.__tokens.next()

		snippet_types = {
			'---constant---', '---class-method---', '---instance-method---', 
			'---private-method---', '---define-method---'
		}
		if token.value in snippet_types:
			self.snips(token.value)
		elif token.value == '---EOF---':
			print('eof')
		else:
			print('no separator')

	def snips(self, snippet_type):
		while self.__tokens.seek().typ == 'SNIPPET':
			self.snip(snippet_type)

	def snip(self, snippet_type):
		token = self.__tokens.next()
		if token.typ == 'SNIPPET':
			print("snippet: " + token.value)
		else:
			print(token)
		



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
parser.parse()

# for x in parser:
# 	print(x)

# print(parser.next())
# print(parser.seek())

