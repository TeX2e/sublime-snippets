
import os
import re
import Parser
import textwrap


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
		filename = re.sub(r'(?=\.sublime-snippet)', '.%s' % (self.classname), filename)
		path = '%s/%s' % (self.dir, filename)
		return path

	def snip_constant(self, filename, code):
		pass

	def snip_class_method(self, filename, code):
		pass

	def snip_instance_method(self, filename, code):
		path = self.__get_snip_file_path(filename)
		with open(path, 'w') as f:
			f.write(
				SnippetHelper.format(
					snippet=SnippetHelper.replace_variable(code), 
					trigger=code, 
					lang=self.lang, 
					desc=classname
				)
			)

	def snip_private_method(self, filename, code):
		pass

	def snip_define_method(self, filename, code):
		pass
		

# import inspect

# method_list = [
# 	(func,addr) for func,addr in inspect.getmembers(DefineSnippet('ruby', 'tmp'), predicate=inspect.ismethod)
# 	if func.startswith('snip_')
# ]
# print(method_list)


class CreateSnippet(object):
	"""docstring for CreateSnippet"""

	def __init__(self, define):
		self.__define_snippet = define
		self.dir = define.dir

	def mkfile(self, filename, snippet_type, value, tag=''):
		if snippet_type == '---constant---':
			self.__define_snippet.snip_constant(filename, value)
		elif snippet_type == '---class-method---':
			self.__define_snippet.snip_class_method(filename, value)
		elif snippet_type == '---instance-method---':
			self.__define_snippet.snip_instance_method(filename, value)
		elif snippet_type == '---private-method---':
			self.__define_snippet.snip_private_method(filename, value)
		elif snippet_type == '---define-method---':
			self.__define_snippet.snip_define_method(filename, value)

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
	def format(snippet, trigger, lang, desc):
		abstract_snippet = '''
			<snippet>
				<content><![CDATA[
			{snippet}
			]]></content>
				<tabTrigger>{trigger}</tabTrigger>
				<scope>source.{lang}</scope>
				<description>{desc}</description>
			</snippet>
		'''
		concrete_snippet = textwrap.dedent(
			abstract_snippet.format(
				snippet=snippet, 
				trigger=trigger, 
				lang=lang,
				desc=desc
			)
		)
		return concrete_snippet


class VariableCountUp(object):
	"""docstring for VariableCountUp"""
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


# filename = 'BasicObject.snip'

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

file_path = '../ruby/BasicObject.snip'

statements = ''
with open(file_path, 'r') as f:
	statements = f.read();

filename = os.path.basename(file_path)
classname, ext = os.path.splitext(filename)

parser = Parser.Parser(
	code=statements,
	filename=filename,
	make_file=CreateSnippet(DefineSnippet('ruby', classname, 'tmp/')).mkfile
)

parser.parse()



