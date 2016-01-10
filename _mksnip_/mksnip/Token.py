
import collections
import re


Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])


class Tokens(object):
    """
    Create a new tokens from the given string.
    Tokens is composed of iterable items.
    """

    def __init__(self, string):
        """
        argument string is expected to be code.snip contents such as:

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
            ...
        """
        self.__pos = 0;  # for iterable
        self.__code = string
        self.__tokens = []  # [Token(..), Token(..), ..]

    @property
    def list(self):
        """ Return list of tokens """
        return self.__tokens

    # --- iterable ---

    def __iter__(self):
        """ Return self """
        return self

    def next(self):
        """ Return next token, and increment iterator. """
        try:
            next_val = self.__tokens[self.__pos]
        except IndexError:
            raise StopIteration
        else:
            self.__pos += 1
            return next_val

    def seek(self):
        """ Return next token. """
        return self.__tokens[self.__pos]

    # --- token ---

    def tokenize(self):
        self.__tokens = list(self.tokenize_with_gen())
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
        match_obj = get_token(self.__code)
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
            match_obj = get_token(self.__code, pos)

        if pos != len(self.__code):
            raise RuntimeError('Unexpected character %r on line %d' % (self.__code[pos], line))

        yield Token('EOF', '---EOF---', line, 0)
