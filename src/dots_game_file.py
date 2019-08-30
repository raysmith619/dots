# dots_game_file.py
"""
Support for the saving and loading of dots game results
    Columns ==>                        Rows--+
    1    2    3    4    5    6               :
    +----+----+----+----+----+          1    V

    +----+----+----+----+----+          2

    +----+----+----+----+----+          3

    +----+----+----+----+----+          4

    +----+----+----+----+----+          5
    
    +----+----+----+----+----+          6
    
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
    # file_name
    # date
    
    game(name=game_type_name,
        date=date_time_stamp,
        nrow=number_of_rows
        ncol=number_of_columns
        nplayer=number_of_players # default: 2
        date=date_time_stamp
        )
    moves((player,row,col)[,        # multi row supported
      (player,row,col)]*
      )
    results((player,nsquare)[, (player,nsquare)]*)
    
    """
import re
import os
from pathlib import Path
from datetime import date


from select_trace import SlTrace
from select_error import SelectError
    
class DotsGameFile:
    
    def __init__(self, file_dir=r"..\gmres", file_prefix="dotsgame",
                 file_ext="gmres"):
        """ Setup games file output
        :file_dir: file directory default=..\gmres
        :file_prefix: file prefix default: dotsgame
        :file_ext: file extension default: gmres
        """
        self.file_dir = file_dir
        self.file_prefix = file_prefix 
        self.file_ext = file_ext 
        self.moves = []
        self.open_output()
    
    
    def open_output(self, file_name=None):
        """ Open games file output
        :file_name:  output file name, base name if not absolute
        """
        if file_name is None:
            file_name = self.file_prefix 
            if not file_name.endswith("_"):
                file_name += "_"
            file_name += SlTrace.getTs()
        if not re.match(file_name, r"^.*\.[^.]+$"):
            file_name += "." + self.file_ext
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        self.file_path = file_name
        path = Path(file_name)
        if path.is_file():
            raise SelectError("gamesfile: %s already exists" % (file_name))
        
        try:
            self.fout= open(self.file_path, "w")
        except Exception as ex:
            SlTrace.lg("open_output(%s) failed: %s" %
                       (self.file_path, str(ex)))
            raise SelectError("No games files")
        print("# %s" % self.file_path, file=self.fout)
        today = date.today()
        d2 = today.strftime("%B %d, %Y")
        print("# On: %s\n" % d2, file=self.fout)
        print("", file=self.fout)
        
    
    def start_game(self, game_name="dots", nplayer=2, nrow=None, ncol=None):
        """ Start producing game resultStep
        :game_name: game name default: dots
        :nplayer: Number of players default: 2
        :nrow: number of rows REQUIRED 
        :ncol: number of columns REQUIRED 
        """
        if game_name is not None:
            self.game_name = game_name
        if nplayer is not None:
            self.nplayer = nplayer
        if nrow is not None:
            self.nrow = nrow
        if ncol is not None:
            self.ncol = ncol
        self.move_no = 0              # Track number of moves
        self.moves = []             # Collect move tuples (player, row, col)
        self.game_ts = SlTrace.getTs()
        
    
    def next_move(self, player=None, row=None, col=None):
        """ Store next move tuple
        :player: player number 1,2,...
        :row: row number 1,2,... from left
        :col: col number 1,2,... from top
        """
        self.move_no += 1
        if player is None:
            raise SelectError("Missing player on move %d" % self.move_no)

        if row is None:
            raise SelectError("Missing row on move %d" % self.move_no)

        if col is None:
            raise SelectError("Missing col on move %d" % self.move_no)
        
        self.moves.append((player,row,col))


    def end_game(self, results=[]):
        """ Process whole game
        :results: list of reslt tuples (player, nsquare)
        """
        if len(self.moves) == 0:
            return              # No moves - no game
        
        print("game(name=%s, nplayer=%s, nrow=%d, ncol=%d, nmoves=%d, ts=%s)"
              % (self.game_name, self.nplayer, self.nrow, self.ncol,
                 len(self.moves), self.game_ts), 
              file=self.fout)
        max_line_len = 70
        line_str = "moves("            
        for i in range(len(self.moves)):
            move = self.moves[i]
            if i > 0:
                move_str = ", "
            else:
                move_str = ""
            move_str += "(%d,%d,%d)" % (move[0], move[1], move[2])
            if len(line_str) + len(move_str) + 1 > max_line_len:
                print(line_str, file=self.fout)
                line_str = ""
            line_str += move_str
            if i >= len(self.moves)-1:
                line_str += ")"   # extra line separation
                print(line_str, file=self.fout)
                
        print("results(", end="", file=self.fout)
        for result in results:
            print("(%d,%d)" % (result[0], result[1]), end="", file=self.fout)
        print(")\n", file=self.fout)


    def end_file(self):
        """ Close results file
        """
        if self.fout is not None:
            self.fout.close()
            SlTrace.lg("Closeing results file %s" % self.file_path)
            self.fout = None
 
 
    def load_game_file(self, file_name=None):
        """ load file bames
        :file_name: path to file
        """
        

    def load_game_files(self, file_pat=None):
        """ Load games
        :file_pat:  Additional filter (rex) pattern default: All
        """
        for root, dirs, files in os.walk(self.file_dir):
            for file in files:
                if file_pat is not None and not re.match(file_pat, file):
                    continue
                file_name = os.path.join(root, file)
                self.load_game_file(file_name) 


            
    
    """
    Process 
    """
    def procFilePyPlus(self, file_name, preamble=None):
        """ Process python code file, with prefix text
        :preamble: text string placed before file contents
                    default: self.preamble (newline appended if none
        :inFile: input file name
        """
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        path = Path(file_name)
        if not path.is_file():
            self.error("inFile({} was not found".format(file_name))
            return False
        compile_str = ""
        if preamble is None:
            preamble = self.preamble
        if not preamble.endswith("\n"):
            preamble += "\n"
        compile_str = preamble
        try:
            fin = open(inPath)
            compile_str += fin.read()
        except Exception as ex:
            SlTrace.lg("input file %s failed %s" % (file_name, str(ex)))
            return False
        
        try:
            code = compile(f.read(), inPath, 'exec')
        except Exception as e:
            tbstr = traceback.extract_stack()
            SlTrace.lg("Compile Error in %s\n    %s)"
                    % (inPath, str(e)))
            return False
        try:
            exec(code)
        except Exception as e:
            etype, evalue, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            SlTrace.lg("Execution Error in %s\n%s)"
                    % (inPath, str(e)))
            inner_cmds = False
            for tbfr in tbs:         # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                    inner_cmds = True
                    SlTrace.lg("    --------------------")         # show bottom (in dots_commands.py)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            return False
        return True
                
                    
if __name__ == "__main__":
    rF = DotsGameFile(file_dir=r"..\test_gmres")
    rF.start_game(game_name="test1", nplayer=2, nrow=7, ncol=7)
    rF.next_move(1,2,2)
    rF.next_move(2,2,3)
    rF.next_move(1,3,4)
    rF.next_move(2,3,4)
    rF.end_game([(1,2), (2,5)])
    
    rF.start_game(game_name="test2", nplayer=2, nrow=5, ncol=7)
    rF.next_move(1,2,3)
    rF.next_move(2,2,4)
    rF.next_move(1,3,5)
    rF.next_move(2,3,6)
    rF.end_game([(1,2), (2,5)])
    rF.end_file()        