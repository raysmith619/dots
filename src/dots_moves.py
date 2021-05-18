# dots_moves.py    30Apr2021  crs
"""
Position, opportunity, threat recorder/evaluator for the
complete-the-squares dots game
Position specification records the edges (horizontal, vertical)
currently selected.
Given a lattuce of M (rows) by N(columns) of squares constructed
b M+1 (rows) of dots by N+1(colunns of dots(intersections)

               vert        vert      vert    vert        vert       vert
               edge        edge      edge    edge        edge       edge
                1            2         3      N-1          N         N+1
  horz edge 1  -+-- 1,1,h --+--1,2,h -+- ...  -+- 1,N-1,h -+- 1,N,h --+
                |   [1,1]   |  [2,1]   |  ...  |           |          |
              1,1,v     1,2,v 1,2 1,3,v... 1,N-1,v    1,N,v      1,N+1,v
                |           |          |  ...  |           |          |
  horz edge 2   +-- 2,1,h --+--2,2,h --+- ... -+- 2,N-1,h -+-2,N,h  --+
                |   [2,1]   |  [2,2]   |  ...  |           |          |
              2,1,v       2,2,v     2,3,v ... 2,N-1,v    2,N,v      2,N+1,v
                |           |          |  ...  |           |          |
                .           .          .       .           .          .
                .           .          .       .           .          .
                .           .          .       .           .          .
                |           |          |  ...  |           |          |
  horz edge M-1 +- M-1,1,h -+-M-1,2,h -+- ... -+ M-1,N-1,h +- M-1,N,h +
                |  [M-1,1]  |  [M-1,2] |  ...  | [M-1,N-1] | [M-1,N]  |
            M-1,1,v      M-1,2,v   M-1,3,v...M-1,N-1,v   M-1,N,v  M-1,N+1,v
                |           |          |  ...  |           |          |
  horz edge M   +-  M,1,h  -+-- M,2,h -+- ... -+- M,N-1,h -+- M,N,h --+
                |   [M,1]   |          |  ...  |  [M,N-1]  |  [M,N]   |
              M,1,v       M,2,v      M,3,v... M,N-1,v    M,N,v    M,N+1,v
                |           |          |  ...  |           |          |
  horz edge M+1 +- M+1,1,h -+- M+1,2,h-+- ... -+ M+1,N-1,h +- M+1,N,h +

    Edge state information is stored in integer
        Bits:
        0-4: player number 1-15 : currently 0 or 1(any player)
        5-6: before connection count 0-3
        7-8: after connection count 0-3


Evaluation is based on the idea that the square may
be completed on the comming move if:
    1. The edge is free AND
    2. the "before" or "after" three completion edges    
       are filled

    Horizontal edges
                   +-------2------+
        before     |              |
                   1              3
                   |              |
                   +-----EDGE-----+
        after      |              |
                   1              3
                   |              |
                   +-------2------+

    Vertical edges
        before                after
           +-----1-----+-----1-----+
           |           |           |
           |           E           |
           2           D           2
           |           G           |
           |           E           |
           |           |           |                   
           +-----3-----+-----3-----+
If an edge is available, the following opportunities / threats
are present:
  1. If the three completion edges are filled, selecting the
     edge will complete a square.
  2. If two of the three completion edges are filled,
     selecting the edge will present the completion opportunity
     to the opponent.

"""
import numpy as np
import random

from select_trace import SlTrace
from dots_error import DotsError
from pip._vendor.pyparsing import col

HV_H = 0            # Horizontal
HV_V = 1            # Vertical

CG_BF = 0           # Before completion group
CG_AF = 1           # After completion group
EV_USED = 0xF       # Mark as used

class MoveInfo:
    """ Move info in compact form
    """
    move_no = 0
    
    def __init__(self, dotsmove, row=None, col=None, hv=None,
                 player=None, move_no=None,
                 squares=[]):
        """ Setup move info
        :dotsmoves: game control
        :row: edge info tuple
        :col:
        :hv:
        :player: player number
        :move_no: move number
                    default: increment
        :squares: list of squares completed by the move
        """
        if move_no is None:
            MoveInfo.move_no += 1
            move_no = MoveInfo.move_no
        self.move_no = move_no
        self.row = row
        self.col = col
        self.hv = hv
        self.move_no = move_no
        if player is None:
            player = self.dotsmoves.get_next_player()
        self.player = player
        self.squares = squares

class EdgeState:
    """ Outward facing evaluation of edge state
    Not necessarily efficient but easy to interpret
    """
    def __init__(self, player=0, before=0, after=0, edge_val=None):
        """ Set up edge state
        :player: 0 - not set, non-zero some player set
        :before: before count
        :after: after count
        :edge_val: used to set from edge
        """
        if edge_val is not None:
            self.player = edge_val&0xF
            self.before = (edge_val>>4)&0x3
            self.after = (edge_val>>6)&0x3
        else:
            self.player = player
            self.before = before
            self.after = after
 
    def is_set(self):
        """ Check if played
        :returns: True iff edge played
        """
        return self.player > 0
    
class DotsMoves:
    """ Opportunity / Threat class:
    Provides capability to evaluate / manage current
    opportunities / threats of connect-the-dots game in progress
    """
    EV_USED = EV_USED
    HV_H = HV_H
    HV_V = HV_V
    
    def __init__(self, nrow=6, ncol=None,
                 nplayer=2):
        """ Setup initalized nrow by ncol square dots
        :nrow: number of square rows (nrow+1 dots)
            default: 6
        :ncol: number of  square columns (ncol+1 dots)
            default: nrow
        :nplayer: number of playters <= 15
                default: 2
        """
        if ncol is None:
            ncol = nrow
        self.nrow = nrow
        self.ncol = ncol
        self.edges = np.zeros([nrow+1,ncol+1, 2], dtype=int)
        self.squares = np.zeros([nrow,ncol], dtype=int)    # Player if completed, else 0
        self.moves = []
        self.nsq_completed = 0          # Number completed by on previous move
        self.next_player = nplayer+1    # Force new player on first play
        self.nplayer = nplayer
        """ Make out-of-bound edges used by nplayer+1
        """
        for irow in range(nrow+1):    # set right edge horz as used
            self.edges[irow][ncol][HV_H] = EV_USED
            
        for icol in range(ncol+1):      # Set bottom edge vert as used
            self.edges[nrow][icol][HV_V] = EV_USED    # set as used
            
            

    def clear(self):
        """ clear setting to empty (game beginning)
        """
        self.edges = np.zeros(nrow+1,ncol+1, 2)


    def get_free_edges(self, index=True):
        """ Get ndarray of edges set
        :index: True - leave row,col as raw indices starting a 0
                else convert to  base 1 values
        :returns: ndarray of ct_edge tuples of 
        """
        sets = np.argwhere((self.edges&0xF)==0)
        if index:
            return sets
        return self.edges2base(sets)

    def get_set_edges(self, index=True):
        """ Get ndarray of edges set
        :index: True - leave row,col as raw indices starting a 0
                else convert to  base 1 values
        :returns: ndarray of ct_edge tuples of 
        """
        sets = np.argwhere((self.edges&0xF)!=0)
        if index:
            return sets
        return self.edges2base(sets)

    def get_edge_state(self, row, col, hv):
        """ Get edge state
        :row: row 1..
        :col: col 1..
        :hv: HV_H/HV_V
        :returns: EdgeState for given edge
        """
        ct_edge = self.get_ct_edge(row=row, col=col, hv=hv)
        edge_val = self.get_edge_value(ct_edge=ct_edge)
        return EdgeState(edge_val=edge_val)

    def get_next_move(self, move_type=None):
        """ Builtin move generator for test/demonstration
        :move_type: "random" - give random choice of remaining
                            legal moves
                    "seq" - sequential legal moves row,col,hv
                    default: "random"
        :returns: rcd_edge (row, col, edge) 1..
        """
        if move_type is None:
            move_type = "random"
        moves = self.get_free_edges(index=False)
        if len(moves) == 0:
            return None         # No moves left
        
        if move_type == "random":
            mi = random.randint(0,len(moves)-1)
        elif move_type == "seq":
            mi = 0
        else:
            raise DotsError(f"get_next_move({move_type} is not supported")
        move = moves[mi]
        row, col, hv = move
        return (row, col, hv)
         
    def get_next_player(self):
        """ Get next player
        Genteraly changes unless previous play
        completed some squares
        :returns next player 
        """
        if self.nsq_completed > 0:
            return self.next_player
        
        self.next_player += 1
        if self.next_player > self.nplayer:
            self.next_player = 1
        return self.next_player
        
    def get_nextsq_edges(self, dist=1, index=True):
        """ Get ndarray of edges, not yet set but dist away from square
            completion.
        :dist: distance, in edges, to completed square
                e.g. if this completes atleast one square dist==1
                default: 1
        :orcloser: if equal or closer dist==2 match 2,1,
        :index: True - leave row,col as raw indices starting a 0
                else convert to  base 1 values
        :returns: ndarray of ct_edge tuples of 
        """
        sets = np.argwhere(((self.edges&0xF)==0)
                           &(
                              ((self.edges>>4)&0xF==dist)        # before
                             |((self.edges>>6)&0xF==dist)        # after
                            )
                        )
        if index:
            return sets
        
        return self.edges2base(sets)

    def edges2base(self, edges):
        """ Convert ndarray of ct_edge tupple to row,col one base
        :edges: ndarray of ct_edge tupples 0 row,col based
        :returns ndarray of ct_edge tupples 1 row, col based
        """
        sh = edges.shape
        edges_1base = edges.copy()
        for i in range(sh[0]):
            ct_edge = edges[i]
            st = (ct_edge[0]+1, ct_edge[1]+1, ct_edge[2])
            edges_1base[i] = st 
        return edges_1base

    def make_move(self, row=None, col=None, hv=None,
                   player=None):
        """ Make move (make edge to connect dots)
        :row: row 1..
        :col: col 1..
        :hv: horizontal/vertical   HV_H/HV_V
            default: random legal move
        :player: number default: next player
        :returns: True if move made
        """
        if player is None:
            player = self.get_next_player()
        
        if row is None or col is None or hv is None:
            rcd_edge = self.get_next_move(move_type="random")
            if rcd_edge is None:
                return False    # No move
            
            row, col, hv = rcd_edge
        if not self.is_free(row=row, col=col, hv=hv):
            return False
        
        self.set_edge(row=row, col=col, hv=hv, value=player)
        sqs = self.get_comp_squares(row=row, col=col, hv=hv)
        move = MoveInfo(self, player=player, row=row, col=col,
                        hv=hv, squares=[])
        self.nsq_completed = 0
        for sq in sqs:
            if sq is not None:
                self.nsq_completed += 1
                row, col = sq
                move.squares.append(sq)
                self.squares[row-1][col-1] = player
        self.moves.append(move)
        return True         # Successful move
        
    def get_comp_squares(self, row, col, hv):
        """ Return any squares completed by this edge
        :ct_edge: row,col,hv
        :returns: list of SquareInfo of completed squares
        """
        comp_edge_grps = self.get_comp_edges(row=row, col=col, hv=hv)
        side_squares = self.get_side_squares(row=row, col=col, hv=hv)
        sqs = []
        for i in range(len(comp_edge_grps)):
            cedges = comp_edge_grps[i]
            side_square = side_squares[i]
            nset = self.get_nset(cedges)
            if nset > 0 and  nset == len(cedges):
                sqs.append(side_square)
            else:
                sqs.append(None) 
        return sqs
    
    def get_nset(self, edges):
        """ Return number of edges set
        :edges: list of edges (row,col, hv) row:1..
        :returns: number of edges in group set
        """
        nset = 0
        for edge in edges:
            row,col,hv = edge
            if self.is_set(row=row, col=col, hv=hv):
                nset += 1    
        return nset
    
    def get_comp_edges(self, row, col, hv):
        """ Return list of ct_edge of completion edges
        :ct_edge: (row,col,hv) tuple
        :returns: list of list of before and list of  after
                row, col, hv 1..
        """
        bf_grp = []             # before edges
        af_grp = []             # after edges
        if hv == 0:             # if horizontal
            if row > 1:         # if not on top edge
                                   # Add before group
                
                bf_grp.append((row-1, col, HV_V))
                bf_grp.append((row-1, col, HV_H))
                bf_grp.append((row-1, col+1, HV_V))
            if row <= self.nrow: # if not on bottom edge
                                # Add after group
                af_grp.append((row, col, HV_V))        
                af_grp.append((row+1, col, HV_H))        
                af_grp.append((row, col+1, HV_V))        
        else:                   # if vertical
            if col > 1:         # if not on left edge
                                   # Add before group
                bf_grp.append((row, col-1, HV_H))
                bf_grp.append((row, col, HV_V))
                bf_grp.append((row+1, col-1, HV_H))
            if col <= self.ncol: # if not on right edge
                                # Add after group
                af_grp.append((row, col, HV_H))        
                af_grp.append((row, col+1, HV_V))        
                af_grp.append((row+1, col, HV_H))        
        return (bf_grp, af_grp)

    def get_side_squares(self, row, col, hv):
        """ get adjacent squares(row,col) before, after
        :row:
        :col:
        :hv:
        :returns: list of side squares (row,col)
                    None if side square is out of board
        """
        bf_sq = None
        af_sq = None
        if hv == HV_H:
            if row > 1:
                bf_sq = (row-1,col)
            if row < self.nrow+1:
                af_sq = (row,col)
        else:       # HV_V
            if col > 1:
                bf_sq = (row, col-1)
            if col < self.ncol+1:
                af_sq = (row,col)
        return (bf_sq, af_sq)
                
    def set_edge(self, row, col, hv, value=1, must_change=True):
        """ Set edge (dot connection)
        :row: row of edge (1 - top edge of board latuce)
        :col: column of edge (1- left edge of latuce)
        :hv: horizontal/vertical 0 - horizontal, 1 - vertical
        :value: value to set default: 1
        :must_change: True - must change existing value
        """
        ct_edge = self.get_ct_edge(row=row, col=col, hv=hv)
        self.set_edge_val(ct_edge=ct_edge, value=value,
                           must_change=must_change)
        self.adjust_completions(row, col, hv, value)

    def set_edge_val(self, ct_edge, value, must_change=True):
        """ Set edge value (composite value)
        """
        irow = ct_edge[0]
        icol = ct_edge[1]
        hv = ct_edge[2]
        if must_change and self.edges[irow][icol][hv] == value:
            raise DotsError(f"set_edge_val({row},{col}, {hv}):"
                            f" row({col}) already {value}")
        self.edges[irow][icol][hv] = value
        
    def clear_edge(self, row, col, hv, must_change=False):
        """ Remove edge (dot connection)
        :row: row of edge (1 - top edge of board latuce)
                0 "off board" edge above board, used to provide
                "before" completion to allow "before" completion edges 
                at board edge 
        :col: column of edge (1- left edge of latuce)
                0 "off board" edge to left of board used to provide 
                "before" completion to allow "before" completion edges
                at board edge
        :hv: horizontal/vertical 1 - horizontal
        """
        self.set_edge(row=row, col=col, hv=hv, value=0,
                       must_change=must_change)

    def adjust_completions(self, row, col, hv, value):
        """ Adjust up(1)/down(0) completion values of surrounding edges
        Goals: Produce completion sums such that every edge's comletion
        sums provide valid number of edges, including that edge, towards
        a completed square(4). Note that 3 means that setting that edge
        completes a square, 2 means that setting that edge provides an
        opportunity to complete that square on the next move. 
        :row: edge row 
        :col: edge col 
        :hv: horizontal/vertical
        :value:  nonzero(1) - set
        """
        bf_grp = []             # Before count group
        af_grp = []             # After count group
        if hv == 0:             # if horizontal
            if row > 1:         # if not on top edge
                                   # Add before group
                bf_grp.append((row-1, col, HV_V))
                bf_grp.append((row-1, col, HV_H))
                bf_grp.append((row-1, col+1, HV_V))
            if row <= self.nrow: # if not on bottom edge
                                # Add after group
                af_grp.append((row, col, HV_V))        
                af_grp.append((row+1, col, HV_H))        
                af_grp.append((row, col+1, HV_V))        
        else:                   # if vertical
            if col > 1:         # if not on left edge
                                   # Add before group
                bf_grp.append((row, col-1, HV_H))
                bf_grp.append((row, col, HV_V))
                bf_grp.append((row+1, col-1, HV_H))
            if col <= self.ncol: # if not on right edge
                                # Add after group
                af_grp.append((row, col, HV_H))        
                af_grp.append((row, col+1, HV_V))        
                af_grp.append((row+1, col, HV_H))        

        for ct_edge in bf_grp:
            self.adjust_completion_edge(cgrp=CG_BF, ct_edge=ct_edge, value=value)

        for ct_edge in af_grp:
            self.adjust_completion_edge(cgrp=CG_AF, ct_edge=ct_edge, value=value)
        
    def adjust_completion_edge(self, cgrp=CG_BF, ct_edge=None, value=1):
        """ Increase competion count before/after count
        :cgrp: completion group: CG_BF - before, CG_AF - after
        :ct_edge: (row, col, hv) row, column, hv to adjust
        :value: 1 - increase, 0 - decrease
        """
        if self.is_off_board(ct_edge=ct_edge):
            return
        
        count = self.get_completion_val(cgrp=cgrp, ct_edge=ct_edge)
        if value > 0:
            count += 1
        else:
            if count > 0:
                count -= 1
        
        self.set_completion_val(cgrp=cgrp, ct_edge=ct_edge, count=count)
        
    def get_completion_val(self, cgrp, ct_edge):
        """ Get completion value, if one
        :ct_edge: r,c,hv tuple for edge
        :ct_grp: group value: CG_BF/CG_AF
        :returns: 0 if off board
        """
        edge_val = self.get_edge_value(ct_edge=ct_edge)
        if cgrp == CG_BF:
            comp_val = (edge_val >> 4)&3
        elif cgrp == CG_AF:
            comp_val = (edge_val >> 6)&3
        return comp_val    

    def get_ct_edge(self, row, col, hv):
        """ Convert row,col, hv to ct_edge tuple
        :row: row 1..
        :col: col 1..
        :hv: HV_H/HV_V
        :returns: ct_edge tuple
        """
        if row < 1:
            raise DotsError(f"get_ct_edge({row},{col},{hv}): row({row}) out of range")
        if (row > self.nrow and hv == HV_V
                or row > self.nrow+1):
            hv_str = "H" if hv == HV_H else "V"
            raise DotsError(f"get_ct_edge({row},{col},{hv_str}):"
                            f" row({row}) out of range")
        if col < 1:
            hv_str = "H" if hv == HV_H else "V"
            raise DotsError(f"get_ct_edge({row},{col},{hv_str}): row({col}) out of range")
        if (col > self.ncol and hv == HV_H
                or col > self.ncol+1):
            hv_str = "H" if hv == HV_H else "V"
            raise DotsError(f"get_ct_edge({row},{col},{hv_str}):"
                            f" col({col}) out of range")
        return (row-1, col-1, hv)

    def get_edge_value(self, ct_edge):
        """ Get edge evaluation
        :ct_edge: (row, col,  hv) specification tuple
        :return: edge value int
        """
        
        irow = ct_edge[0]
        icol = ct_edge[1]
        hv = ct_edge[2]
        return self.edges[irow][icol][hv]

    def get_player_num(self, row, col, hv):
        """ Get player num
            non-zero if set
        """
        ct_edge = self.get_ct_edge(row=row, col=col, hv=hv)
        edge_val = self.get_edge_value(ct_edge=ct_edge)
        player_num = edge_val & 0x0f
        return player_num

    def is_free(self, row, col, hv):
        """ Check if edge is free to be set
        :row: 1.. row
        :col:
        :hv:
        :returns: True if valid free edge
        """
        if self.is_off_board(row=row, col=col, hv=hv):
            return False        # off board --> not free
        
        state = self.get_edge_state(row=row, col=col, hv=hv)
        if state.is_set():
            return False
        
        return True
    
    def is_set(self, row, col, hv):
        """ Check if edge is set (i.e. not free)
        :row,col,hf: edge specificaion row:1..
        :returns: True if set else False
        """
        return not self.is_free(row=row, col=col, hv=hv)
        
    def is_off_board(self, ct_edge=None, row=None, col=None, hv=None):
        """ Check if out of bounds
        :ct_edge: (irow, icol, hv)
         OR
        :row:
        :col:
        :hv:
        :returns: True if edge is not part of board
        """
        if ct_edge is not None:
            irow, icol, hv = ct_edge
        else:
            irow, icol, hv = (row-1, col-1, hv)
        if irow < 0:
            return True
        if irow > self.nrow-1 and hv == HV_V:
            return True
        
        if irow > self.nrow:
            return True
        
        if icol < 0:
            return True
        
        if icol > self.ncol-1 and hv == HV_H:
            return True
        
        if icol > self.ncol:
            return True
        
        return False
            
        
    def set_completion_val(self, cgrp, ct_edge, count):
        """ Get completion value
        :ct_edge: r,c,hv tuple for edge
        :ct_grp: group value: CG_BF/CG_AF
        :count: count to set
        """
        edge_val = self.get_edge_value(ct_edge=ct_edge)
        if cgrp == CG_BF:
            comp_val = edge_val & ~(3<<4)    # clear bits 4-5
            comp_val |= count<<4
        elif cgrp == CG_AF:
            comp_val = edge_val & ~(3<<6)    # clear bits 6-7
            comp_val |= (count << 6)
        self.set_edge_val(ct_edge=ct_edge, value=comp_val, must_change=False)

if __name__ == "__main__":
    nrow = 3
    ncol = nrow+1
    SlTrace.setFlags("traverse")
    dT = DotsMoves(nrow=nrow, ncol=ncol)
    for row in range(1, nrow+1):
        for col in range(1, ncol+1):
            for hv in [HV_H, HV_V]:
                dr = "H" if hv == 0 else "V"
                SlTrace.lg(f"Doing {row},{col}:{dr}", "traverse")
                dT.set_edge(row=row, col=col, hv=hv)
                sets = dT.get_set_edges(index=False)
                next2sqs = dT.get_nextsq_edges(index=False)
                if len(next2sqs) > 1:
                    SlTrace.lg(f"next2sqs: {next2sqs}")
                SlTrace.lg(f"sets: {sets}")
               