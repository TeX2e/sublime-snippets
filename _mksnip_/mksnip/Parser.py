
import collections

from Error import (Error)
from Token import (Token, Tokens)


Snippet = collections.namedtuple('Snippet', ['filename', 'type', 'value', 'tag'])

# reading:
#   A <---- B   :  A depends on B
#   PascalCase  :  class name
#   snake_case  :  method or field
# 
# flow:
# 
#     Parser
#       |
#       | __init__(code, file_name)
#       | tokens <----Tokens
#       |               tokenize() <----Token
#       V
#     parser.tokens (tokenized result set in parser.tokens)
#       |
#       | parse() <----Error
#       |   groups()
#       |   group()
#       |   snips()
#       |   snip() <----make_file()
#       V
#   

class Parser(object):
	"""
	Parser initializer is this:

		Parser(
			code,      # parserable string
			filename,  # for error output
			make_file  # mkfile should be callable
		)

	mkfile has the process how to create snippet file with specific arguments
	"""

	def __init__(self, code, filename='input', 
			make_file=(lambda filename, snippet_type, value, tag: None) ):
		self.__code = code
		self.__filename = filename
		self.__tokens = Tokens(self.__code).tokenize()
		self.__make_file = make_file

	# --- iterable ---

	def __iter__(self):
		return self.__tokens

	def next(self):
		return self.__tokens.next()

	def seek(self):
		return self.__tokens.seek()

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
			next_token = self.__tokens.seek()
			if next_token.typ == 'BEGIN':
				self.group()
			elif next_token.typ == 'EOF':
				print('[Finished parsing %s]' % self.__filename)
				break
			else:
				Error.print_error(Error.message(
					self.__filename, next_token.line, next_token.column, 
					'not separator: %s' % next_token.value
				))
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
			Error.print_error(Error.message(
				self.__filename, token.line, token.column, 'invalid separator: %s' % token.value
			))

	def snips(self, snippet_type):
		while True:
			next_token = self.__tokens.seek()
			if next_token.typ == 'SNIPPET':
				self.snip(snippet_type)
			elif next_token.typ == 'TAG':
				self.__tokens.next()
				self.snip(snippet_type, 'TAG')
			else:
				break

	def snip(self, snippet_type, tag=''):
		token = self.__tokens.next()
		if token.typ == 'SNIPPET':
			print('snippet: (%s) %s %s' % (snippet_type, token.value, tag))
			self.__make_file(
				# filename=('%s.sublime-snippet' % (token.value)),
				# snippet_type=snippet_type,
				# value=token.value,
				# tag=tag,
				Snippet(token.value, snippet_type, token.value, tag)
			)
		else:
			Error.print_error(Error.message(
				self.__filename, token.line, token.column, 'not snippet: %s' % token.value
			))

