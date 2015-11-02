
import os

import Parser


#       | Snippet
#       |   mkfile(..) <----SnippetHelper
#       |                     replace_variable() <----VariableCountUp
#       |                     format()                  cnt
#       |                                               wrap_variable()
#       V
#     :write the snippet in lang-dir/*.sublime-snippet


class DefineSnippet(object):
	"""docstring for DefineSnippet"""
	def __init__(self, lang):
		self.lang = lang

	def snip_constant(self, string):
		pass

	def snip_class_method(self, string):
		pass

	def snip_instance_method(self, string):
		pass

	def snip_private_method(self, string):
		pass

	def snip_define_method(self, string):
		pass
		

import inspect

method_list = [
	func for func,addr in inspect.getmembers(DefineSnippet('ruby'), predicate=inspect.ismethod)
	if func.startswith('snip_')
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

parser = Parser.Parser(statements)#.tokenize()
parser.parse()



# for x in parser:
# 	print(x)

# print(parser.next())
# print(parser.seek())

