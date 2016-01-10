
import os
import sys
import re

import Parser
from Parser import Snippet
import SnippetHelper


#
# Define how to create snippet file
#

class DefineSnippet(object):
    """docstring for DefineSnippet"""
    def __init__(self, lang, classname, dir_path=''):
        self.lang = lang
        self.dir  = dir_path or lang
        self.classname = classname
        self.__init_snip_dir()

    def mkfile(self, snippet):
        if snippet.type == '---constant---':
            self.snip_constant(snippet)
        elif snippet.type == '---instance-method---':
            self.snip_instance_method(snippet)

    def __init_snip_dir(self):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

    def __get_snip_file_path(self, filename):
        return '%s/%s.%s.sublime-snippet' % (self.dir, filename, self.classname)

    def snip_constant(self, snippet):
        path = self.__get_snip_file_path('%s::%s' % (classname, snippet.value))
        if snippet.tag:
            snippet_value = snippet.value
        else:
            snippet_value = '%s::%s' % (classname, snippet.value)

        with open(path, 'w') as f:
            f.write(
                SnippetHelper.format(
                    snippet=snippet_value,
                    trigger=snippet_value,
                    lang=self.lang,
                    desc=self.classname
                )
            )

    def snip_class_method(self, snippet):
        pass

    def snip_instance_method(self, snippet):
        path = self.__get_snip_file_path(snippet.filename)
        snippet_value = SnippetHelper.replace_variable(snippet.value)
        snippet_trigger = SnippetHelper.remove_newline_and_tab(snippet.value)
        if snippet.tag:
            snippet_value = SnippetHelper.remove_parenthesis(snippet_value)

        with open(path, 'w') as f:
            f.write(
                SnippetHelper.format(
                    snippet=snippet_value,
                    trigger=snippet_trigger,
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
                snippet.tag
            )
            self.snip_instance_method(block_snippet) # re-invoke

    def snip_instance_method_with_tag(self, snippet):
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

    def snip_private_method(self, snippet):
        pass

    def snip_define_method(self, snippet):
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



# # convert 'def func' to 'def func $0 end'
# function snippet_def() {
#     local STR=$*
#     STR=$(
#         echo $STR |
#         sed -e 's/$/\\n\\t$0\\nend/'
#     )
#     echo "$STR"
# }


# file_path = 'BasicObject.snip'

# statements = '''
#     ---class-method---
#     new
#     try_convert(obj)
#     ---instance-method---
#     __id__
#     object_id
#     send(sym, args)
#     __send__(sym, args)
#     equal?(other)
#     instance_eval(string)
#     instance_eval { |obj| block }
#     instance_exec(item) { |item| block }
#     ---define-method---
#     method_missing(method, args, block)
#     self.singleton_method_added(id)
#     self.singleton_method_removed(sym)
#     self.singleton_method_undefined(sym)
#     ---EOF---
# '''

langs = {'ruby'}

lang = sys.argv[1]
if not lang in langs:
    print('no such a language: %s' % sys.argv[1])
    exit()

files = sys.argv[2:]
if files == []:
    print('usage: python mksnip.py <lang> <file.snip>')
    exit()


for file_path in files:
    # file_path = '../ruby/BasicObject.snip'
    statements = ''
    try:
        with open(file_path) as f:
            statements = f.read();
    except FileNotFoundError as e:
        print(e)
        continue

    filename = os.path.basename(file_path)
    classname, ext = os.path.splitext(filename)
    snips_dir = 'tmp-%s/' % lang
    lock_file = '.updating'
    lock_file_path = '%s%s' % (snips_dir, lock_file)

    try:
        with open(lock_file_path, 'w') as f:
            f.write('')
    except Exception as e:
        raise e
    else:
        parser = Parser.Parser(
            code=statements,
            filename=filename,
            make_file=DefineSnippet(lang, classname, snips_dir).mkfile
        )
        parser.parse()
    finally:
        last_modified = os.stat(lock_file_path).st_mtime

        for snip_file in os.listdir(snips_dir):
            if snip_file.startswith('.'):
                continue
            last_modified_of_file = os.stat(snips_dir + snip_file).st_mtime

            if last_modified_of_file < last_modified:
                os.remove(snips_dir + snip_file)
                print('\tremove: %s' % snip_file)

        os.remove(lock_file_path)

        print('[Finished updating %s]' % filename)
