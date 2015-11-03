
import os
import sys
import re

import Parser
from Parser import Snippet
import SnippetHelper


#       | CreateSnippet
#       |   mkfile(..) <----SnippetHelper
#       |                     replace_variable() <----VariableCountUp
#       |                     format()                  cnt
#       |                                               wrap_variable()
#       V
#     :write the snippet in lang-dir/*.sublime-snippet


class DefineSnippet(object):
	"""docstring for DefineSnippet"""
	def __init__(self, lang, classname, dir_path=''):
		self.lang = lang
		self.dir  = dir_path or lang
		self.classname = classname
		self.__init_snip_dir()

	def __init_snip_dir(self):
		if not os.path.exists(self.dir):
			os.mkdir(self.dir)

	def __get_snip_file_path(self, filename):
		return '%s/%s.%s.sublime-snippet' % (self.dir, filename, self.classname)

	def snip_constant(self, filename, snippet):
		path = self.__get_snip_file_path('%s::%s' % (classname, filename))

	def snip_class_method(self, filename, snippet):
		pass

	def snip_instance_method(self, snippet, tag=''):
		path = self.__get_snip_file_path(snippet.filename)
		with open(path, 'w') as f:
			f.write(
				SnippetHelper.format(
					snippet=SnippetHelper.replace_variable(snippet.value), 
					trigger=SnippetHelper.remove_newline_and_tab(snippet.value), 
					lang=self.lang, 
					desc=self.classname
				)
			)

		match_proc = re.compile(r"\bblock\b\s*\}")
		if match_proc.search(path):
			block_snippet = Snippet(
				self.__filename_proc_to_block(snippet.filename),
				snippet.type,
				self.__snip_proc_to_block(snippet.value),
				tag
			)
			self.snip_instance_method(block_snippet)

	def snip_instance_method_with_tag(self, filename, snippet):
		path = self.__get_snip_file_path(filename)
		with open(path, 'w') as f:
			f.write(
				SnippetHelper.format(
					snippet=SnippetHelper.remove_parenthesis( SnippetHelper.replace_variable(snippet) ), 
					trigger=SnippetHelper.remove_newline_and_tab(snippet), 
					lang=self.lang, 
					desc=self.classname
				)
			)

	def snip_private_method(self, filename, snippet):
		pass

	def snip_define_method(self, filename, snippet):
		pass

	@staticmethod
	def __snip_proc_to_block(snippet):
		snippet = re.compile(r'(?<= )\{(?= ?block)').sub("do\n\t", snippet)
		snippet = re.compile(r'(?<= )\{').sub("do", snippet)
		snippet = re.compile(r'(?<=\|) ').sub("\n\t", snippet)
		snippet = re.compile(r' \}').sub("\nend", snippet)
		return snippet

	@staticmethod
	def __filename_proc_to_block(filename):
		filename = re.compile(r'(?<= )\{').sub('do', filename)
		filename = re.compile(r'\bblock\b').sub('..', filename)
		filename = re.compile(r'(?<= )\}').sub('end', filename)
		return filename
		

class CreateSnippet(object):
	"""docstring for CreateSnippet"""

	def __init__(self, define):
		self.__define_snippet = define
		self.dir = define.dir

	# def mkfile(self, filename, snippet_type, value, tag=''):
	# 	if snippet_type == '---constant---':
	# 		self.__define_snippet.snip_constant(filename, value)
	# 	elif snippet_type == '---class-method---':
	# 		self.__define_snippet.snip_class_method(filename, value)
	# 	elif snippet_type == '---instance-method---' and not tag:
	# 		self.__define_snippet.snip_instance_method(filename, value)
	# 	elif snippet_type == '---instance-method---' and tag:
	# 		self.__define_snippet.snip_instance_method_with_tag(filename, value)
	# 	elif snippet_type == '---private-method---':
	# 		self.__define_snippet.snip_private_method(filename, value)
	# 	elif snippet_type == '---define-method---':
	# 		self.__define_snippet.snip_define_method(filename, value)

	def mkfile(self, snippet):
		if snippet.type == '---instance-method---':
			self.__define_snippet.snip_instance_method(snippet)

		

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


# file_path = 'BasicObject.snip'

# statements = '''
# 	---class-method---
# 	new
# 	try_convert(obj)
# 	---instance-method---
# 	__id__
# 	object_id
# 	send(sym, args)
# 	__send__(sym, args)
# 	equal?(other)
# 	instance_eval(string)
# 	instance_eval { |obj| block }
# 	instance_exec(item) { |item| block }
# 	---define-method---
# 	method_missing(method, args, block)
# 	self.singleton_method_added(id)
# 	self.singleton_method_removed(sym)
# 	self.singleton_method_undefined(sym)
# 	---EOF---
# '''

langs = {'ruby'}

files = sys.argv[2:]
if files == []:
	print('usage: python mksnip.py <lang> <file.snip>')
	exit()

lang = sys.argv[1]
if not lang in langs:
	print('no such a language: %s' % sys.argv[1])
	exit()

for file_path in files:
	# file_path = '../ruby/BasicObject.snip'
	statements = ''
	try:
		with open(file_path, 'r') as f:
			statements = f.read();
	except FileNotFoundError as e:
		print(e)
		continue
	
	filename = os.path.basename(file_path)
	classname, ext = os.path.splitext(filename)

	parser = Parser.Parser(
		code=statements,
		filename=filename,
		make_file=CreateSnippet(DefineSnippet(lang, classname, 'tmp-%s/' % lang)).mkfile
	)

	parser.parse()



