
import re
import textwrap

from Error import (Error)
from Token import (Token, Tokens)


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
#     :write the snippet in lang-dir/*.sublime-snippet
#   

class Parser(object):
	"""docstring for Parser"""

	def __init__(self, code, filename='input', output_dir='./tmp', make_file=lambda a,b,c,d: None):
		self.__code = code
		self.__filename = filename
		self.__output_dir = output_dir
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
				print('[Finished %s]' % self.__filename)
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
			# # invoke function that make snippet file
			# snippet = Snippet(self.__output_dir)
			# snippet.mkfile(
			# 	filename=('%s.sublime-snippet' % (token.value)), 
			# 	snippet_type=snippet_type, 
			# 	value=token.value, 
			# 	tag=tag
			# )
			self.__make_file(
				('%s.sublime-snippet' % (token.value)),
				snippet_type,
				token.value,
				tag,
			)
		else:
			Error.print_error(Error.message(
				self.__filename, token.line, token.column, 'not snippet: %s' % token.value
			))