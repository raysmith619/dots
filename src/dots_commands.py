# dots_commands.py
"""
Python command support  for dots game for python file Execution
"""
import sys
import re
import traceback

from select_error import SelectError
from select_trace import SlTrace
###from _ast import arg

dC = None               # Global reference, set by CommandFile
class DotsCommands:
    """ The hook from commands expressed via python command files to 
    the dots frame worker
    """
    @classmethod
    def get_cmds(cls):
        return dC
    
        
    def __init__(self, command_stream, play_control=None, debugging=False):
        """
        :command_stream: link to command input file/stream REQUIRED
        :play_control: link to game commands
        :debugging: True - Just testing no command execution enabled
        """
        global dC                       # Static link to dots commands
        ###if not isinstance(command_stream, select_command_stream.SelectCommandStream):
        ###    raise SelectError(f"DotsCommands requires SelectCommandStream NOT {type(command_stream)}")
        
        self.command_stream = command_stream
        self.play_control = play_control
        self.debugging = debugging
        self.debugging_res = True       # Default debugging
        self.new_file = True
        self.reset()
        self.src_lines = None
        self.pre_comment = None         # Current instruction comments
        self.line_comment = None
        self.re_comment_line = re.compile(r'^\s*#')
        self.re_doc_start = re.compile(r'.*"""')
        self.re_line_comment = re.compile(r'^.*\S.*?(\s*#.*)')
        dC = self                       # set link to dots commands


    def get_src_file_path(self):
        """ Get current source file path
        """
        return self.command_stream.get_src_file_path()


    def set_play_control(self, play_control):
        """ Connect command stream processing to game control
        :play_control:  game control
        """
        self.play_control = play_control


    def set_cmd_stream_proc(self, cmd_stream_proc):
        """ Connect command stream processing to command processing
        
        :play_control:  game control
        """
        self.cmd_stream_proc = cmd_stream_proc


    def reset(self):
        self.src_line_prev = -1
        self.new_file = True
        
    def ck(self, *args, **kwargs):
        """ Check command.
        Executed at beginning of each language command
        Check with hasattr because attribute is only
        created when called with links
        :returns: True if should SKIP rest of this cmd processing
        """
        if dC is None or not hasattr(dC, "command_stream"):
            raise SelectError("Missing required command_stream")
        
        src_lineno = None
        if (self.is_src_lst() or self.is_stx_lst()
                or self.is_step()):
            if self.new_file:
                self.src_line_prev = -1
                with open(self.get_src_file_path()) as f:
                    self.src_lines = f.readlines()
                    self.new_file = False
            """ List portion of source file, after previous(index) to and including
            the line in the source file found in the stack
            """
            ###etype, evalue, tb = sys.exc_info()
            ###tbs = traceback.extract_tb(tb)
            tbs = traceback.extract_stack()
            src_lineno = None       # set if found
            src_tbfr = None         # stack frame for src
            src_tbfr_fun = None     # with called function name
            for tbfr in tbs:         # skip bottom (in dots_commands.py)
                if tbfr.filename == self.get_src_file_path():
                    src_lineno = tbfr.lineno
                    src_tbfr = tbfr
                    src_tbfr_fun = None     # Clear if we get another
                    continue
                if src_tbfr is not None and src_tbfr_fun is None:
                    src_tbfr_fun = tbfr
            if src_lineno is not None:
                """ An attempt to partition text into
                    pre_comment - lines preceding command
                    line_comment - comment, including leading whitespace
                                    on the line of command
                    This is a bit of a hack
                """
                doing_doc_string = False    # collecting multi-line
                pre_comment = None
                line_comment = None
                src_line_index = src_lineno-1
                if src_line_index < self.src_line_prev:
                    self.src_line_prev = src_line_index # looping?
                for idx in range(self.src_line_prev+1, src_line_index+1):
                    if idx >= len(self.src_lines):
                        break
                    lineno = idx + 1
                    src_line = self.src_lines[idx]
                    if doing_doc_string:
                        if self.re_doc_start.match(src_line):   # A HACK ???
                            doing_doc_string = False
                        pre_comment += src_line
                    elif self.re_comment_line.match(src_line):
                        if pre_comment is None:
                            pre_comment = ""
                        pre_comment += src_line
                    elif self.re_doc_start.match(src_line):
                        if pre_comment is None:
                            pre_comment = ""
                        pre_comment += src_line
                        doing_doc_string = True
                    elif self.re_line_comment.match(src_line):
                        m = self.re_line_comment.match(src_line)
                        line_comment = m.group(1)
                    src_line_trim = src_line.rstrip()
                    if self.is_src_lst():
                        SlTrace.lg("   %4d: %s" % (lineno, src_line_trim))
                        self.src_line_prev = idx        # Update as printed
                    self.pre_comment = pre_comment
                    self.line_comment = line_comment
            if self.is_stx_lst():
                if src_tbfr_fun is not None:
                    fun_name = src_tbfr_fun.name
                    fun_str = None
                    for arg in args:
                        if fun_str is None:
                            fun_str = fun_name + "(" + repr(arg)
                        else:
                            fun_str += ", " + repr(arg)
                    if fun_str is None:
                        fun_str = fun_name + "("
                    for kw in kwargs:
                        arg = kwargs[kw]
                        fun_str += ", " + kw + "=" + repr(arg)
                    fun_str += ")"
                    SlTrace.lg(f"         SCMD: {fun_str}")
        
        if self.play_control is None and not self.is_debugging():
            raise SelectError("DotsCommands play_control link is missing")
        
        if self.is_step():
            self.wait_for_step()    # At target, wait for step/continue
            
        if self.is_to_line(cur_lineno=src_lineno):
            self.wait_for_step()   # At target line, wait for step/continue
                     
        if self.is_debugging():
            return True            # Skip action because debugging                return False                # No reason to skip rest, do it

        return False        # No reason not to continue
    
    
    def is_debugging(self):
        """ Check if debugging, if so we can disregard execution
        """
        if self.debugging:
            return True         # Ignore
        
        return self.command_stream.is_debugging()
    
    
    def wait_for_step(self):
        self.command_stream.wait_for_step()
        
        
    def is_step(self):
        return self.command_stream.is_step()
        
        
    def is_to_line(self, cur_lineno=None, src_lines=None):
        if src_lines is None:
            src_lines = self.src_lines
        return self.command_stream.is_to_line(
                cur_lineno=cur_lineno, src_lines=src_lines)
    
    
    def is_src_lst(self):
        """ Are we listing source lines?
        """
        return self.command_stream.is_src_lst()

    def is_stx_lst(self):
        """ Are we listing executing commands?
        """
        return self.command_stream.is_stx_lst()
    
    
    def ck_res(self):
        """ debugging ck return
        """
        return self.debugging_res

    def get_line_comment(self):
        """ Get line comment first call then None
        to avoid double hits
        """
        ret = self.line_comment
        self.line_comment = None
        return ret

    def get_pre_comment(self):
        """ Get comment first call then None
        to avoid double hits
        """
        ret =  self.pre_comment
        self.pre_comment = None       
        return ret

    def set_debugging(self, debugging = True):
        """ Set to debug command language, elimitting
        action requiring full game
        """
        self.debugging = debugging
        DotsCommands.play_control = None    # Suppress ck eror
        
    
    """
    Dots commands
    """
    
    def lg(self, *args, **kwargs):
        self.ck(*args, **kwargs)  # No debugging
        return SlTrace.lg(*args, **kwargs)
    
    def set_playing(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit
        
        return self.cmd_stream_proc.set_playing(*args, **kwargs)

    def enter(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit
        
        return self.cmd_stream_proc.enter()
        
    def mark(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit
        return self.cmd_stream_proc.mark(*args, **kwargs)

    
    def start_game(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit
        
        return self.cmd_stream_proc.start_game(*args, **kwargs)
        
    def select(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit
        return self.cmd_stream_proc.select(*args, **kwargs)
    
    def set_play(self, *args, **kwargs):
        if self.ck(*args, **kwargs):
            return self.ck_res()    # Debugging short circuit

        return self.cmd_stream_proc.set_play(*args, **kwargs)

    def undo(self):
        if self.ck():
            return self.ck_res()    # Debugging short circuit
        
        return self.play_control.undo()

    def redo(self):
        if self.ck():
            return self.ck_res()    # Debugging short circuit
        
        return self.play_control.redo()

    """
    Game State Verification commands
    """
    def game_check(self, *args, **kwargs):
        if self.ck():
            return self.ck_res()    # Debugging short circuit
        
        return self.play_control.game_check(*args, **kwargs)

    def play_move(self, *args, **kwargs):
        if self.ck():
            return self.ck_res()    # Debugging short circuit
        
        return self.play_control.play_move(*args, **kwargs)
    
    
dC = DotsCommands.get_cmds()
"""
language commands
"""

def enter():
    return dC.enter()

def lg(*args, **kwargs):
    return dC.lg(*args, **kwargs)

def mark(*args, **kwargs):
    return dC.mark(*args, **kwargs)
    
def select(*args, **kwargs):
    return dC.select(*args, **kwargs)

def set_playing(*args, **kwargs):
    return dC.set_playing(*args, **kwargs)

def set_play(*args, **kwargs):
    return dC.set_play(*args, **kwargs)

def start_game(*args, **kwargs):
    return dC.start_game(*args, **kwargs)

def undo():
    """ Undo command
    """
    return dC.undo()

def redo():
    """ Redo command
    """
    return dC.redo()

"""
Verification Commands
Testing expected game State
"""
def game_check(*args, **kwargs):
    return dC.game_check(*args, **kwargs)

def play_move(*args, **kwargs):
    return dC.play_move(*args, **kwargs)

