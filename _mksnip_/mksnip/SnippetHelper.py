
import re
import textwrap

# class SnippetHelper:

def replace_variable(snippet):
    count_up = _VariableCountUp()

    snippet = re.compile(r'([a-zA-Z_][a-z_=0-9]*)(?=[,)\|])').sub(
        count_up.wrap_variable,
        snippet
    )
    snippet = re.compile(r'\bblock\b').sub('${0:block}', snippet)
    return snippet

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
    abstract_snippet = textwrap.dedent(abstract_snippet)
    concrete_snippet = abstract_snippet.format(
        snippet=snippet,
        trigger=trigger,
        lang=lang,
        desc=desc
    )
    return concrete_snippet

def remove_newline_and_tab(string):
    return re.compile(r'[\n\t]+').sub(' ', string)

def remove_parenthesis(string):
    string = re.sub(r'\(', ' ', string)
    string = re.sub(r'\)', '',  string)
    return string



class _VariableCountUp(object):
    """docstring for VariableCountUp"""
    def __init__(self):
        self.cnt = 1

    def wrap_variable(self, match_obj):
        snippet_str = '${%d:%s}' % (self.cnt, match_obj.group())
        self.cnt += 1
        return snippet_str
