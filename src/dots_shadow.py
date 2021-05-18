# dots_shadow.py
"""
Support for shadow dots game board - logical function of the game without display
"""
import random    
import numpy as np

from select_trace import SlTrace
from select_error import SelectError
from select_edge import SelectEdge
from select_region import SelectRegion
from move_list import MoveList, MVP
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
    
            
class DotsShadow:
    """ Shadow of Dots structure to facilitate testing speed when display is not required
    """
    def __init__(self, select_dots, nrows=None, ncols=None):
        self.select_dots = select_dots
        self.nrows = nrows
        self.ncols = ncols
        self.squares = np.zeros([nrows, ncols], dtype=int)
        self.lines = np.zeros([nrows+1, ncols+1, 2], dtype=int)     # row, col, [horiz=0, vert=1]
        
                                                    # Mark illegal edges as used
        for ir in range(nrows+1):
            self.lines[ir, ncols, MVP.HV_H] = 1     # No horizontal edge at right end
        for ic in range(ncols+1):
            self.lines[nrows, ic, MVP.HV_V] = 1     # No vertical edge at bottom end

        self.squares_obj =  np.zeros([nrows, ncols], dtype=SelectRegion)
        self.lines_obj = np.zeros([nrows+1, ncols+1, 2], dtype=SelectEdge)     # row, col, [horiz=0, vert=1]
                                                    # completion counts
        self.comp_before_counts = np.zeros([nrows+1, ncols+1, 2])
        self.comp_after_counts = np.zeros([nrows+1, ncols+1, 2])
        
        ###self.lines_obj = np.zeros([nrows+1+1, ncols+1+1, 2], dtype=SelectEdge)     # row, col, [horiz=0, vert=1]
        self.nopen_line = 2*nrows*ncols + nrows + ncols


    def get_avail_lines(self):
        """ Get ndarray of available line (indices)
        """
        avails = np.argwhere(self.lines==0)
        return avails
    
    def get_legal_list(self):
        """ Return MoveList of legal moves
        :returns: list(MoveList) of moves(MoveList)
        """
        avails = self.get_avail_lines()
        
        legals = MoveList(self, avails=avails)
        '''
        for ir in range(0, self.nrows+1):
            for ic in range(0, self.ncols+1):
                for hv in [MVP.HV_H, MVP.HV_V]:
                    if self.lines[ir, ic, hv] == 0:
                        legals.add_move(MVP(row=ir+1, col=ic+1, hv=hv))    # unused
        '''
        return legals


    def get_legal_moves(self):
        """ Return list of legal moves
        :returns: list(MoveList) of moves(MoveList)
        """
        legal_list = self.get_legal_list()
        legal_moves = legal_list.get_moves()
        
        return legal_moves


    def get_num_legal_moves(self):
        """ Fast check on number of legal moves
        """
        return self.nopen_line


    def get_square_moves(self, move_list=None):
        """ Get moves that will complete a square
        :move_list: list of candidate moves(MoveList)
                    default: use legal moves (get_legal_moves)
        :returns: list(MoveList) of moves that will complete a square
        """
        if move_list is None:
            move_list = self.get_legal_list()
        square_move_list = MoveList(self, max_move=move_list.nmove)
        
        for mvp in move_list:
            nr = mvp.row
            nc = mvp.col
            hv = mvp.hv    
            if self.does_complete_square(nr, nc, hv):
                square_move_list.add_move(mvp)
        return square_move_list


    def get_square_distance_list(self, min_dist=2, move_list=None):
        """ Get moves give a minimum distance(additional number of
        moves to complete a square) to square completion
        :min_dist: minimum distance requested, e.g. 1: next move can
                complete a square, 2: two moves required to complete
                a square default: 2 moves
        :move_list: list of candidate moves(MoveList)
                    default: use legal moves (get_legal_moves)
        :returns: list(MoveList) of moves that will complete a square
        """
        if move_list is None:
            move_list = self.get_legal_moves()
        dist_move_list = MoveList(self, max_move=move_list.nmove)
        
        for mvp in move_list:
            nr = mvp.row
            nc = mvp.col
            hv = mvp.hv    
            if self.distance_from_square(nr, nc, hv) >= min_dist:
                dist_move_list.add_move(mvp)
        return dist_move_list
    

    def distance_from_square(self, nr, nc, hv):
        """ Find the minimum number of meves, after this edge, to complete square
        :nr: row number, starting at 1
        :nc: col number starting at 1
        0 => a completed square
        1 => sets up opponent to complete square
        """
        ir = nr - 1     # index
        ic = nc - 1
        min_dist = None
        if hv == 0:     # Horizontal
            if ir > 0:
                                                            # Square above
                dist = 0
                if self.lines[ir, ic, 1] == 0:               # left vertical edge
                    dist += 1
                if self.lines[ir-1, ic, 0] == 0:            # top horizontal edge
                    dist += 1
                if self.lines[ir, ic+1, 1] == 0:            # right vertical edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                            
                if min_dist is None or dist < min_dist:
                    min_dist = dist


            if ir < self.nrows:     
                                                            # Square below
                dist = 0
                
                if self.lines[ir+1, ic, 1] == 0:            # left vertical edge
                    dist += 1
                if self.lines[ir+1, ic, 0] == 0:            # bottom horizontal edge
                    dist += 1
                if self.lines[ir+1, ic, 1] > 0:             # right vertical edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min

                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    
        else:     # Vertical
            if ic > 0:
                                                            # Square to left
                dist = 0
                if self.lines[ir+1, ic-1, 0] > 0:           # bottom horizontal edge
                    dist += 1
                if self.lines[ir, ic-1, 1] > 0:             # left vertical edge
                    dist += 1
                if self.lines[ir, ic-1, 0] > 0:   # top horizontal edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                if min_dist is None or dist < min_dist:
                    min_dist = dist

            if ic < self.ncols:            
                                                            # Square to right
                dist = 0
                if self.lines[ir+1, ic, 0] == 0:            # bottom horizontal edge
                    dist += 1
                if self.lines[ir+1, ic, 1] == 0:            # right vertical edge
                    dist += 1     
                if self.lines[ir+1, ic, 0] == 0:            # top horizontal edge
                    dist += 1
                if dist == 0:
                    return dist                             # At min
                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    
        return min_dist

    def get_player(self):
        """ Get current player for debugging purposes
        """
        import select_play
        
        play_control = select_play.SelectPlay.current_play
        player = play_control.get_player()
        return player
        
    
    def does_complete_square(self, nr, nc, hv):
        """ Check if edge will complete square
        :nr: row number, starting at 1 for top of board
        :nc: col number, starting at 1 for left of board
        :hv: horizontal/vertical 0- horizontal, 1-vertical
        """
        if nr < 1 or nr > self.nrows+1:
            raise SelectError(f"row:{nr} out of range")
        if nc < 1 or nc > self.ncols+1:
            raise SelectError(f"col:{nc} out of range")
        if hv < 0 or hv > 1:
            raise SelectError(f"hv:{hv} out of range")
        ir = nr - 1
        ic = nc - 1
        SlTrace.lg(f"ir={ir} ic={ic} hv={hv}", "complete_square looking")
        if hv == 0:     # Horizontal
            if ir > 0:
                                                            # Square above
                if (self.lines[ir-1, ic, 1] > 0               # left vertical edge
                        and self.lines[ir-1, ic, 0] > 0     # top horizontal edge
                        and self.lines[ir-1, ic+1, 1] == 0):  # right vertical edge
                    if SlTrace.trace("complete_square"):
                        self.show_play(nr, nc, hv, desc="Square above")
                        self.line_desc(nr, nc, hv, desc="Completing line before")
                        self.line_desc(ir-1, ic, 0, index=True, desc="left vertical edge")
                        self.line_desc(ir-1, ic, 0, index=True, desc="top horizontal edge")
                        self.line_desc(ir-1, ic+1, 1, index=True, desc="right vertical edge")
                    return True            
                
            if ir < self.nrows:                             # Square below
                if (self.lines[ir+1, ic, 1] > 0             # left vertical edge
                        and self.lines[ir+1, ic, 0] > 0       # bottom horizontal edge
                        and  self.lines[ir, ic+1, 1] > 0): # right vertical edge
                    if SlTrace.trace("complete_square"):
                        self.show_play(nr, nc, hv, desc="Square below")
                        self.line_desc(nr, nc, hv, desc="Completing line before")
                        self.line_desc(ir+1, ic, 1, index=True, desc="left vertical edge")
                        self.line_desc(ir+1, ic,0, index=True, desc="bottom horizontal edge")
                        self.line_desc(ir+1, ic+1,1, index=True, desc="right vertical edge")
                    return True
                
        else:     # Vertical
            if ic > 0:
                                                            # Square to left
                if (self.lines[ir+1, ic-1, 0] > 0           # bottom horizontal edge
                        and self.lines[ir, ic-1, 1] > 0     # left vertical edge
                        and self.lines[ir, ic-1, 0] > 0):   # top horizontal edge
                    if SlTrace.trace("complete_square"):
                        self.show_play(nr, nc, hv, desc="Square to left")
                        self.line_desc(nr, nc, hv, desc="Completing line before")
                        self.line_desc(ir+1, ic-1, 0, index=True, desc="bottom horizontal edgee")
                        self.line_desc(ir, ic-1, 1, index=True, desc="left vertical edge")
                        self.line_desc(ir, ic-1, 0, index=True, desc="top horizontal edge")
                    return True     # complete sq on left

                                                            # Square to right
            if ic < self.ncols:                             # but not right most column
                if (self.lines[ir+1, ic, 0] > 0             # bottom horizontal edge
                        and self.lines[ir, ic+1, 1] > 0     # right vertical edge     
                        and self.lines[ir, ic, 0] > 0):    # top horizontal edge
                    if SlTrace.trace("complete_square"):
                        self.show_play(nr, nc, hv, desc="Square to right")
                        self.line_desc(nr, nc, hv, desc="Completing line before")
                        self.line_desc(ir+1, ic, 0, index=True, desc="bottom horizontal edge")
                        self.line_desc(ir+1, ic, 1, index=True, desc="right vertical edge")
                        self.line_desc(ir+1, ic, 0, index=True, desc="top horizontal edge")
                    return True     # complete sq on right
                    
        return False            # Completed squares            


    def get_edge(self, row=None, col=None, hv=None):
        """ Retrieve actual edge part from shadow
        :row: row number, starting with 1
        :col: col number, starting with 1
        :hv: horizontal==0, vertical==1
        """
        return self.lines_obj[row-1, col-1, hv]
    
    def get_mvpart(self, mvpart=None):
        """ get shadowed part (edge only)
        :mvpart: MoveList entry designation
        """
        if mvpart is not None:
            ir, ic, hv = mvpart.row-1, mvpart.col-1, mvpart.hv
            return self.lines_obj[ir, ic, hv]
        
        return None

    def show_play(self, nr, nc, hv, desc=None):
        if desc is None:
            desc = ""
        player = self.get_player()
        name = player.name if player is not None else "Unknown"
        
        
        SlTrace.lg(f"{name} found completing square nr={nr} nc={nc} hv={hv} {desc}")

    def line_desc(self, row, col, hv, index=False, desc=None):
        """ line description
        ;row: row or row index
        :col: col or col index
        :hv:  0 horizontal, 1 vertical
        :index: use zero based, default use 1 based
        :desc: optional description
        """
        if index:
            ir = row
            row = row+1
            ic = col
            col = col+1
        else:
            ir = row-1
            ic = col-1
        line_val = self.lines[ir, ic, hv]
        direct = "horizontal" if hv == 0 else "vertical"
        if desc is None:
            desc = ""
        SlTrace.lg(f"line row={row} col={col} {direct} : lines[{ir},{ic},{hv}] = {line_val} {desc}")
        part = self.lines_obj[ir, ic, hv]
        SlTrace.lg(f"        part: {part}") 
            

    def set_part(self, part):
        """ Add reference to actual part for reference / conversion
        :part: Part to add to shadow
        """
        row = part.row 
        col =  part.col
        if part.is_region():
            self.squares_obj[row-1,col-1] = part 
        elif part.is_edge():
            if part.sub_type() == 'h':
                self.lines_obj[row-1, col-1, 0] = part
            elif part:
                self.lines_obj[row-1, col-1, 1] = part

    def turn_on(self, part=None, player=None, move_no=None):
        """ Shadow part turn on operation to facilitate speed when display is not required
        :part: part to turn on
        :player: who made operation
        :move_no: current move number
        """
        if player is None:
            return              # Short circuit if no player
        
        pn = player.get_playing_num()
        if pn is None:
            return
        
        row = part.row 
        col = part.col
        sub_type = part.sub_type()
        if part.is_edge():
            if sub_type == 'h':
                self.lines[row-1, col-1, 0] = pn
            else:
                self.lines[row-1, col-1, 1] = pn
        elif part.is_region():
            self.squares[row-1, col-1] = pn
        else:
            raise SelectError("turn_on Can't shadow part type {} at row={:d} col={;d}"
                              .format(part, row, col))
        self.nopen_line -= 1            # Reduce number of open lines by 1
        
        
    def turn_off(self, part=None):
        """ Shadow part turn off operation to facilitate speed when display is not required
        :part: part to turn off
        :player: who made operation
        :move_no: current move number
        """
        row = part.row 
        col = part.col
        sub_type = part.sub_type()
        if part.is_edge():
            if sub_type == 'h':
                if self.lines[row-1, col-1, 0] > 0:
                    self.nopen_line += 1
                self.lines[row-1, col-1, 0] = 0
            else:
                self.lines[row-1, col-1, 1] = 0
                if self.lines[row-1, col-1, 1] > 0:
                    self.nopen_line += 1
        elif part.is_region():
            self.squares[row-1, col-1] = 0
        else:
            raise SelectError("turn_off Can't shadow part type {} at row={:d} col={;d}"
                              .format(part, row, col))
