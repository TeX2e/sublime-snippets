
import os
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
#       |   snip() <----Snippet
#       |                 mkfile(..) <----SnippetHelper
#       |                                   replace_variable() <----VariableCountUp
#       |                                   format()                  cnt
#       |                                                             wrap_variable()
#       V
#     :write the snippet in lang-dir/*.sublime-snippet
#     


class Parser(object):
	"""docstring for Parser"""

	def __init__(self, string, filename='input', output_dir='./tmp'):
		self.__code = string
		self.__filename = filename
		self.__output_dir = output_dir
		self.__tokens = Tokens(self.__code).tokenize()

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
			# invoke function that make snippet file
			snippet = Snippet(self.__output_dir)
			snippet.mkfile(
				filename=('%s.sublime-snippet' % (token.value)), 
				snippet_type=snippet_type, 
				value=token.value, 
				tag=tag
			)
		else:
			Error.print_error(Error.message(
				self.__filename, token.line, token.column, 'not snippet: %s' % token.value
			))
		

class DefineSnippet(object):
	"""docstring for DefineSnippet"""
	def __init__(self, lang):
		self.lang = lang

	def snip_constant():
		pass

	def snip_class_method():
		pass

	def snip_instance_method():
		pass

	def snip_private_method():
		pass

	def snip_define_method():
		pass
		

import inspect

method_list = [
	func[0] for func in inspect.getmembers(DefineSnippet('ruby'), predicate=inspect.ismethod)
	if func[0].startswith('snip_')
]
print(method_list)


class Snippet(object):
	"""docstring for Snippet"""

	def __init__(self, dir_path):
		self.dir = '../tmp'

	def mkfile(self, filename, snippet_type, value, tag=''):
		if not os.path.exists(self.dir):
			os.mkdir(self.dir)

		filename = re.sub(r'(?=\.sublime-snippet)', '.%s' % os.path.basename(self.dir), filename)

		path = '%s/%s' % (self.dir, filename)
		with open(path, 'w') as f:
			f.write(
				SnippetHelper.format(
					snippet=value, trigger=value, desc=os.path.basename(self.dir)
				)
			)


class SnippetHelper(object):
	@staticmethod
	def replace_variable(snippet_str):
		count_up = VariableCountUp()
		
		return re.sub(
			r'([a-zA-Z_][a-z_=0-9]*)(?=[,)\|])', 
			count_up.wrap_variable,
			snippet_str
		)

	@staticmethod
	def format(snippet, trigger, desc):
		abstract_snippet = '''
			<snippet>
				<content><![CDATA[
			{snippet}
			]]></content>
				<tabTrigger>{trigger}</tabTrigger>
				<scope>source.ruby</scope>
				<description>{desc}</description>
			</snippet>
		'''
		concrete_snippet = textwrap.dedent(
			abstract_snippet.format(
				snippet=SnippetHelper.replace_variable(snippet), 
				trigger=trigger, 
				desc=desc)
		)
		return concrete_snippet


class VariableCountUp(object):
	"""docstring for SnippetHelper"""
	def __init__(self):
		self.cnt = 1

	def wrap_variable(self, match_obj):
		snippet_str = '${%d:%s}' % (self.cnt, match_obj.group())
		self.cnt += 1
		return snippet_str
		

# # convert { block } to 'do block end'
# function snippet_block() {
# 	local STR=$*
# 	STR=$(
# 		echo $STR | 
# 		sed -e 's/ { \$/ do\\n\\t$/' |  # { ${2:block} -> do\\n\\t${2:block}
# 		sed -e 's/ {/ do/' |      # { -> do
# 		sed -e 's/| /|\\n\\t/' |  # | -> |\n\t
# 		sed -e 's/ }/\\nend/' |   # } -> \n end
# 		sed -e 's/\t\${[1-9]:block}/\t${0:block}/' | # do ${2:block} -> do ${0:block}
# 		sed -e 's/\t\${[1-9]:bool}/\t${0:bool}/'     # do ${2:bool} -> do ${0:bool}
# 	)
# 	echo "$STR"
# }
# 
# # convert 'def func' to 'def func $0 end'
# function snippet_def() {
# 	local STR=$*
# 	STR=$(
# 		echo $STR | 
# 		sed -e 's/$/\\n\\t$0\\nend/'
# 	)
# 	echo "$STR"
# }


statements = '''
	---class-method---
	new
	try_convert(obj)
	---instance-method---
	__id__
	object_id
	send(sym, args)
	__send__(sym, args)
	equal?(other)
	instance_eval(string)
	instance_eval { |obj| block }
	instance_exec(item) { |item| block }
	---define-method---
	method_missing(method, args, block)
	self.singleton_method_added(id)
	self.singleton_method_removed(sym)
	self.singleton_method_undefined(sym)
	---EOF---
'''

parser = Parser(statements)#.tokenize()
parser.parse()



# for x in parser:
# 	print(x)

# print(parser.next())
# print(parser.seek())

