# dots_game_load.py
"""
Support for the loading of dots game results
See dots_game_file.py for game and file layout
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
     """
import sys, traceback
import re
import os
from pathlib import Path
from datetime import date

from select_trace import SlTrace
from select_error import SelectError
from dots_results_commands import version,game,moves,results,SkipFile

class DotsGame:

    def __init__(self, name=None, nplayer=2, nrow=None, ncol=None, nmove=None, ts=None):
        self.name = name
        self.nplayer = nplayer
        self.nrow = nrow
        self.ncol = ncol
        self.nmove = nmove
        self.ts = ts
        self.game_moves = []
        self.results = []
        self.games = []
        
        
class DotsGameLoad:
    """ The hook from commands expressed via python command files to 
    the frame worker
    Make it an "ALL CLASS" to ease access via file based calls
    """
    
        
    def __init__(self, file_dir=None, file_prefix="dotsgame",
                 nrow=None,
                 ncol=None,
                 file_ext="gmres",
                 test_file=None):
        """ Setup games file output
        :commands: command processor
        :file_dir: file directory default=..\gmres
        :ncol: if present, restrict games to ncol default: load all
        :nrow: if present, restrict games to nrow default: ncol
                Assume, for restriction, all games in file are the same nrow,ncol
        :file_prefix: file prefix default: dotsgame
        :file_ext: file extension default: gmres
        :test_file: if present, just load this file
        """
        if file_dir is None:
            file_dir = r"..\gmres"
        if nrow is not None or ncol is not None:
            if nrow is None:        # If only is present set the other to same
                nrow = ncol
            if ncol is None:
                ncol = nrow
        self.nrow = nrow
        self.ncol = ncol
            
        self.file_dir = file_dir
        self.file_prefix = file_prefix 
        self.file_ext = file_ext
        self.test_file = test_file
        self.nfile = 0
        self.games = []
        self.loader = None
        self.nfgame = 0         # Number games in file
    
    
    def load_game_file(self, file_name=None):
        """ load game results
        :file_name: path to file
        """
        self.skip_file = False      # True if skipping rest of file
        self.cur_gm = None
        self.nfgame = 0         # Number of games in file
        if self.procFilePyPlus(file_name=file_name):
            self.nfile += 1  # Count if successful
        else:
            self.nfile_error += 1
        
        sum_str = " - skipped"
        if self.cur_gm is not None:
            sum_str = ("     ngame=%d nrow=%d ncol=%d"
                % (self.nfgame, self.cur_gm.nrow, self.cur_gm.ncol))
        SlTrace.lg("End loading file %s%s" % (file_name, sum_str))
            
        
    
    def load_game_files(self, file_pat=None):
        """ Load games
        :file_pat:  Additional filter (rex) pattern default: All
        """
        self.games = []
        self.nfile = 0  # Number of files loaded
        self.nfile_error = 0  # Number of file errors
        self.ngame = 0  # Number of games loaded
        self.ngame_error = 0  # Number pf game errors

        if self.test_file is not None:
            SlTrace.lg("Loading only test file: %s" % self.test_file)
            self.load_game_file(file_name=self.test_file) 
            SlTrace.lg("End loading %d files" % self.nfile)
            return
        
        SlTrace.lg("Files loaded from directory: {}".format(self.file_dir))
        for root, _, files in os.walk(self.file_dir):
            for file in files:
                if file_pat is not None and not re.match(file_pat, file):
                    continue
                file_name = os.path.join(root, file)
                self.load_game_file(file_name=file_name) 
        SlTrace.lg("End loading %d files" % self.nfile)
    
    
    
    def get_num_files(self):
        """ Get number of results files loaded
        """
        return self.nfile
        
           
    
    def get_num_games(self):
        """ Get number of games loaded
        """
        return len(self.games)
    
    """
    Process command file 
    """

    
    def procFilePyPlus(self, file_name=None):
        """ Process python code file, with prefix text
        :inFile: input file name
        """
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        path = Path(file_name)
        if not path.is_file():
            SlTrace.lg("file_name {} was not found".format(file_name))
            return False
        
        compile_str = r"""
"""
        try:
            fin = open(file_name)
            compile_str += fin.read()
            fin.close()
        except Exception as ex:
            SlTrace.lg("input file %s failed %s" % (file_name, str(ex)))
            return False
                
        try:
            exec(compile_str)
        except SkipFile as e:
            SlTrace.lg("    Skipping file", "SkipFile")
            return True
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            SlTrace.lg("Error while executing text from %s\n    %s)"
                    % (file_name, str(e)))
            inner_cmds = False
            for tbfr in tbs:  # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                    inner_cmds = True
                    SlTrace.lg("    --------------------")  # show bottom (in dots_commands.py)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            return False
        return True


        
                
    """
    Basic game file loading functions
    Generally one per file command
    """
    
    
    def version(self, version_str):
        if self.loader is not None:
            return self.loader.version(version_str)
            
        self.version_str = version_str
        
    
    def game(self, name=None, nplayer=2,
                nrow=None, ncol=None, nmove=None, ts=None):
        """ Start processing of game
        :returns:  False if not processing this game
        """
        if self.loader is not None:
            return self.loader.game(name=name, nplayer=nplayer,
                nrow=nrow, ncol=ncol, nmove=nmove, ts=ts)

        if self.skip_file:
            return False
        
        
        if self.nrow is not None:
            if nrow != self.nrow:
                self.skip_file = True   # Optimize
                raise SkipFile("skipping file")

        if self.ncol is not None:
            if ncol != self.ncol:
                self.skip_file = True   # Optimize
                raise SkipFile("skipping file")
                        
        SlTrace.lg("game(name=%s, nplayer=%d, nrow=%d, ncol=%d, nmoves=%d, ts=%s)"
                % (name, nplayer, nrow, ncol, nmove, ts), "game")
        gm = DotsGame(name=name, nplayer=nplayer, nrow=nrow, ncol=ncol, nmove=nmove, ts=ts)
        self.cur_gm = gm         # Current game
        self.nfgame += 1        # Count game
        return True
    
    def moves(self, *moves):
        """ Add next set of moves, game or part of game
        :moves: argument list
            Each argument is either:
                a move tuple (original format) (player number, row(1,..., col(1...)
                OR
                a list of  move  tuples, supporting larger (than 255) moves
        """
        if self.loader is not None:
            return self.loader.moves(*moves)


        if self.skip_file:
            return False

        for move in moves:
            if isinstance(move, tuple):
                self.cur_gm.game_moves.append(move) # List of tuples
            elif isinstance(move, list):
                self.cur_gm.game_moves.extend(move) # One move tuple
                SlTrace.lg("Adding list of %d moves" % len(move), "adding_list")
                
                
    def results(self, *res):
        """ End current game's input, specifying results
        :res: comma separated list of result tuples (player_no, nsquares)
        """
        if self.loader is not None:
            return self.loader.results(*res)
        

        if self.skip_file:
            return False

        self.cur_gm.results = res
        gm = self.cur_gm
        self.games.append(gm)            # Add to loaded games
        if SlTrace.trace("game_results"):
            move_no = 0
            for move in gm.game_moves:
                move_no += 1
                SlTrace.lg("%3d: move(player=%d, row=%d, col=%d)" % 
                            (move_no, move[0], move[1], move[2]))
            results_str = "results: "
            for result in gm.results:
                results_str += (" player=%d: squares=%d" % 
                            (result[0], result[1]))
            SlTrace.lg(results_str)




if __name__ == "__main__":
    from dots_results_commands import DotsResultsCommands
    
    rC = DotsResultsCommands()
    rF = DotsGameLoad(file_dir=r"..\test_gmres")
    rC.set_loader(rF)
    rF.load_game_files()
    SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))        
