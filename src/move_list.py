# move_list.py
"""
Support for MoveList an iterable list of move specfications (row,col,hv)
"""
import random
import numpy as np

from select_error import SelectError
from select_edge import SelectEdge
from select_region import SelectRegion

"""
Dots Square / Edge numbering
Squares are numbered row, col starting at 1,1 in upper left
Edges, bordering a square are numbered as follows:

    Lve_row = sq_row          (Left vertical edge)
    Lve_col = sq_col
    
    Rve_row = sq_row          (Right vertical edge)
    Rve_col = sq_col + 1
     
    The_row = sq_row          (Top horizontal edge)
    The_col = sq_col
    
    Bhe_row = sq_row + 1      (Botom horizontal edge)
    Bhe_col = sq_col

"""
class MVP:
    """ MoveList entry in movelist list expansion
    """
    HV_H = 0
    HV_V = 1
    def __init__(self, row=0, col=0, hv=HV_H):
        self.row = row
        self.col = col
        self.hv = hv

class MoveListIterator:
    ''' Iterator class '''
    def __init__(self, move_list):
        # Team object reference
        self._move_list = move_list
        # member variable to keep track of current index
        self._index = 0
        
    def __next__(self):
        """Returns the next MVP entry from MoveList """
        if self._index < self._move_list.nmove:
            result = self._move_list.get_mvp(self._index)
            self._index +=1
            return result
        # End of Iteration
        raise StopIteration
 
 

    
    
class MoveList:
    """ List of moves (edge specifications) which can be efficiently manipulated
    """
    def __init__(self, shadow, max_move=None, moves=None, avails=None):
        """ Setup list
        :shadow:  Playing shadow data control
            shadow must support:
                    obj = self.shadow.lines_obj[irt]
                    move = self.shadow.get_edge(row, col, hv)

        :max_move: Maximum number of moves
        :moves: if present, initialize list
        :avails: if present, ndarray of irow, icol, hv tupples
        """
        self.shadow = shadow
        if max_move is None:
            if avails is not None:
                max_move = len(avails)
                
            elif moves is not None:
                max_move = len(moves)
            else:
                max_move = 10
        self.moves = np.zeros([max_move, 3], dtype=int)     #  [row, col, hv(0-horizontal, 1-vertical]
        self.nmove = 0                          # Empty
        self.nmove_max = max_move
        if moves is not None:
            for move in moves:
                self.add_move(move)
        if avails is not None:
            for mvd in avails:
                mvp = MVP(row=mvd[0]+1, col=mvd[1]+1, hv=mvd[2])
                self.add_move(mvp)
 
    def __iter__(self):
        """ Returns the Iterator object MoveListIterator
        """
        return MoveListIterator(self)

    def get_mvp(self, mindex):
        """ Retrieve move at index (zero starting)
        :mindex: move index in list
        """
        mv = self.moves[mindex]
        row, col, hv = mv
        mvp = MVP(row=row, col=col, hv = hv)
        return mvp
    
    def move2mvp(self, move):
        """ Generate MVP from move
        :move: move part
        :returns: MVP of move
        """
        hv = MVP.HV_H if move.is_horizontal() else MVP.HV_V
        mvp = MVP(row=move.row, col=move.col, hv=hv)
        return mvp


    def add_move(self, move_mvp=None):
        """ Add move Move/MVP to move list
        Currently no check or handling for overflow
        :move: move (tuple) to add
        """
        if isinstance(move_mvp, MVP):
            mvp = move_mvp
        else:
            hv = MVP.HV_H if move_mvp.is_horizontal() else MVP_HV_V
            mvp = MVP(row=move_mvp.row, col = move_mvp.row, hv = hv)
        if self.nmove >= self.nmove_max:
            self.expand_moves()
        self.moves[self.nmove, 0] = mvp.row
        self.moves[self.nmove, 1] = mvp.col
        self.moves[self.nmove, 2] = mvp.hv
        self.nmove += 1
        

    def expand_moves(self, new_max=None):
        """ Expand list
        :new_max: new maximum
                default: max(20, 2*nmoves)
        """
        if new_max is None:
            new_max = 2*self.nmove
            if new_max < 20:
                new_max = 20
        new_moves = np.zeros([new_max, 3], dtype=int)       # Create zeroed enlarged array
        new_moves[0:self.nmove, 0:3] = self.moves          # Copy existing array to beginning
        self.moves = new_moves                              # Place new array in place
        self.nmove_max = new_max
        
    def number(self):
        """ Get number in list
        :returns: number in list
        """
        return self.nmove
    
    
    def rand_move(self):
        """ Get random list entry
        """
        ir = random.randint(0,self.nmove-1)
        mvp = self.get_mvp(ir)
        return mvp
    
    
    def rand_obj(self):
        """ Get random list entry object e.g. edge
        """
        mvp = self.rand_move()
        row, col, hv = mvp.row, mvp.col, mvp.hv
        obj = self.shadow.lines_obj[row-1, col-1, hv]
        return obj


    def get_entry_array(self):
        """ Provide access to entry array
        """
        return self.moves


    def get_moves(self):
        """ Provide python list of moves(part)
        """
        moves = []
        for i in range(self.nmove):
            row = self.moves[i,0]
            col = self.moves[i,1]
            hv = self.moves[i,2]
            move = self.shadow.get_edge(row, col, hv)
            moves.append(move)
        return moves


    def get_mvps(self):
        """ Provide MoveList of moves(part)
        """
        mvps = MoveList(self, max_move=self.nmove)
        for i in range(self.nmove):
            mvp = self.get_mvp(i)
            mvps.add_move(mvp)
        return mvps


    def get_moves(self):
        """ Provide MoveList of moves(part)
        """
        moves = []
        mvps = self.get_mvps()
        
        for i in range(mvps.get_nmoves()):
            mvp = mvps.get_mvp(i)
            move = self.shadow.get_edge(mvp.row, mvp.col, mvp.hv)
            moves.append(move)
        return moves

    def get_nmoves(self):
        """ fast count of moves
        :returns: number of moves in list
        """
        return self.nmove
