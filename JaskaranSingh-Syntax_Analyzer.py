import os
class JackAnalyzer(object):   # make class Jack analyzer
    def __init__(self, file_path):
        jack_files = self.parse_files(file_path)   # open jack file 
        for jack_file in jack_files: # Read from jack file
            self.analyze(jack_file)

    def parse_files(self, file_path):
        if '.jack' in file_path:  # check if the file selected is a jack file
            return [file_path]
        else:
            print('You have not selected a jack file')

    def analyze(self, jack_file):
        tokenizer = JackTokenizer(jack_file)  # call jack tokenizer
        ce = CompilationEngine(jack_file)  # call compilation engine
        while tokenizer.has_more_tokens():
            tokenizer.advance()   # call tokenizer advance
            if tokenizer.token_type == 'KEYWORD':  # for keywords
                ce.write_token('keyword', tokenizer.curr_token) # write the keywords
            elif tokenizer.token_type == 'SYMBOL': # for symbol
                ce.write_token('symbol', tokenizer.curr_token) # write the symbol
            elif tokenizer.token_type == 'INT_CONSTANT': # for integer constant
                ce.write_token('integerConstant', str(tokenizer.curr_token)) # write the integer constant
            elif tokenizer.token_type == 'STRING_CONSTANT':  # for string constant
                ce.write_token('stringConstant', tokenizer.curr_token) # write the string constant
            elif tokenizer.token_type == 'IDENTIFIER':   # for identifier
                ce.write_token('identifier', tokenizer.curr_token) # write the identifier
        ce.close() # close the file

class JackTokenizer(object):
    def __init__(self, jack_filename):
        self.jack_filename = jack_filename   # declare variable to filename
        self.jack = self.load_file(self.jack_filename)   # load the file
        self.curr_token = None
        self.token_type = None
        self.keywords = self.keyword_dict()  # form dictionary of keywords
        self.symbols = self.symbol_set()  # form a new set of symbols

    def has_more_tokens(self):
        return self.jack   # return if line has any tokens

    def advance(self):
        next_token = self.jack.popleft() 

        # For Symbol
        if next_token[0] in self.symbols: # if token macthes in symbols
            self.token_type = 'SYMBOL' # declare symbol type
            if len(next_token) >= 2 and next_token[:2] in ['++', '<=', '>=']:   # check for the symbols
                self.curr_token = next_token[:2]
                if next_token[2:]:
                    self.jack.appendleft(next_token[2:])   # append the token in symbol list
            else:
                self.curr_token = next_token[0]  # moves to next token 
                if next_token[1:]:
                    self.jack.appendleft(next_token[1:])
            return

        # For String Constant
        if next_token[0] == '"':  # checks for string
            self.token_type = 'STRING_CONSTANT'  # declare string type
            curr_string = next_token[1:]
            full_string = ''
            while True:
                for i, el in enumerate(curr_string):  
                    if el == '"':  #beginning of string
                        full_string += curr_string[:i]  # concatenation
                        if curr_string[i+1:]:
                            self.jack.appendleft(curr_string[i+1:])   # string continues
                        self.curr_token = full_string.strip()  # removes spaces
                        return
                full_string += curr_string + ' '   # appends it in the full string
                curr_string = self.jack.popleft()

        # FOr Integer Constant
        if self.is_int(next_token[0]):  # checks for integer type
            self.token_type = 'INT_CONSTANT'  # declares interger constant
            int_idx = 0  # integer index
            while self.is_int(next_token[:int_idx+1]):  # checks next token if integer
                int_idx += 1  # counter increases 
            self.curr_token = next_token[:int_idx]
            if next_token[int_idx:]:
                self.jack.appendleft(next_token[int_idx:]) # appends it to integer list
            return

        # Identifier or Keyword
        # need to check for trailing symbol
        self.curr_token = next_token
        for i, el in enumerate(next_token):
            if el in self.symbols:  # checks token in symbols
                self.curr_token = next_token[:i]  # next token
                self.jack.appendleft(next_token[i:])  # appends it to the list
                break
        if self.curr_token in self.keywords: # if it matches in keywords
            self.token_type = 'KEYWORD' # declares it keyword
        else:
            self.token_type = 'IDENTIFIER' # declares it identifier

    def token_type(self):
        return self.token_type  # return token type 

    def key_word(self):
        return self.keywords[self.curr_token] # returns the keywords 

    def symbol(self):
        return self.curr_token # returns the symbol

    def identifier(self):
        return self.curr_token # returns the identifier

    def int_val(self):
        return int(self.curr_token) # returns the integer constant

    def string_val(self):
        return self.curr_token # returns the string constant

    

    def load_file(self, jack_filename):
        with open(jack_filename, 'r') as f:  # open file in read mode
            contents = f.read()
        contents = contents.split('\n') # linewise split
        contents = [l.strip() for l in contents]  # clear spaces 
        contents = [l.split('//')[0] for l in contents] # split comments 
        in_comment = False
        for i, line in enumerate(contents):
            start, end = line[:2], line[-2:]
            if start == '/*':  # checks comments 
                in_comment = True

            if in_comment:
                contents[i] = '' # extract the content of comments

            if start == '*/' or end == '*/':
                in_comment = False # end the comment
        words = []
        for line in contents:
            words.extend(line.split()) # write all the contents in words list
        words = [l for l in words if l]
        return deque(words) # deque words

    def is_int(self, string):  # function for integer value
        try:
            int(string) # convert string to integer type
            return True
        except ValueError: # exception error
            return False

    def keyword_dict(self): # keywords 
        return {'class': 'CLASS', 'constructor': 'CONSTRUCTOR','function': 'FUNCTION','method': 'METHOD',
            'field': 'FIELD', 'static': 'STATIC','var': 'VAR','int': 'INT', 'char': 'CHAR', 'boolean': 'BOOLEAN',
            'void': 'VOID', 'true': 'TRUE', 'false': 'FALSE', 'null': 'NULL', 'this': 'THIS', 'let': 'LET',
            'do': 'DO', 'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'return': 'RETURN'}

    def symbol_set(self):
        return set(['{','}','(',')','[',']','.',',',';','+','-','*','/','&', '|', '<', '>', '=', '~'])  # set of symbols



class CompilationEngine(object): # compilation engine
    def __init__(self, jack_filename):
        newfile = jack_filename[:-4] + 'T.xml'  # new filename
        with open(newfile,'w') as self.xml:
            self.write('<tokens>\n')  # header for xml file
            self.updent() # begin indendation
    def write(self, content):
        self.xml.write(content) # write contents in xml file

    def write_token(self, token_type, token): # replace specific tokens
        token = token.replace('&', '&amp;') 
        token = token.replace('<', '&lt;')
        token = token.replace('>', '&gt;')
        self.write(' ' * self.indent + '<' + token_type.lower() + '> ')# opener syntax
        self.write(token)# write token 
        self.write(' </' + token_type.lower() + '>\n') #closing syntax

    def close(self):
        self.downdent()
        self.write('</tokens>') # write footer
        self.xml.close() # close the file

    def updent(self):
        self.indent += 2 # increment indendation

    def downdent(self):
        self.indent -= 2 # decrement indendation


if __name__ == '__main__':
    import sys
    file_path = 'ExpressionlessSquare.jack'  # filename
    JackAnalyzer(file_path)  # call jackanalyzer
