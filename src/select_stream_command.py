# select_stream_sommand.py

from select_error import SelectError
from select_trace import SlTrace

class SelectStreamCmd:
    DOC_STRING = "DOC_STRING"          # Special command types
    NULL_CMD = "NULL_CMD"
    EOF = "EOF"                         # End of file
    EXECUTE_FILE = "EXECUTE_FILE"       # python file
                                        # execute_file()
                                        # to execute
    
    def __init__(self, name, args=None):
        """
        :args: one or more arguments
        """
        self.name = name.lower()        # case insensitive
        if args is None:
            args = []
        if not isinstance(args, list):
            args = [args]
        self.args = args

    
    def is_type(self, typeck):
        """ Return True iff we are of type
            e.g. is_type(SelectStreamCmd.EOF) checks for EOF
        """
        res = self.name.lower() == typeck.lower()
        return res    
        
    def __str__(self):
        string = self.name
        if self.args:
            for arg in self.args:
                string += ", "
                string += f"{arg}"
        return string

class SelectStreamToken:
    WORD = "WORD"                # Token type
    QSTRING = "QSTRING"
    NUMBER = "NUMBER"
    PUNCT = "PUNCT"
    SEMICOLON = "SEMICOLON"
    PERIOD = "PERIOD"
    EOL = "EOL"                 # End of line
    COMMENT = "COMMENT"             # comment (not passed by get_tok())
    EOF = "EOF"                 # End of file
    
    def __init__(self, type, str=None, doc_string=False, delim=None):
        self.type = type
        self.str = str
        self.doc_string = doc_string    # Python like doc string
        self.delim = delim              # iff quoted

    
    def __str__(self):
        string = self.type
        if self.str is not None:
            string += self.str
        return string
    

    def is_cmd(self):
        return True