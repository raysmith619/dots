# dots_moves_text.py    09may2021  crs
""" Text mode display of DotsMoves
data
"""

import numpy as np
from math import ceil

from select_trace import SlTrace

from dots_moves import DotsMoves, EdgeState
from _sqlite3 import sqlite_version

class DotsMovesText:

    def __init__(self, dotsmoves):
        self.dotsmoves = dotsmoves
        
        
    def display_str(self, char_per_vert_edge=4, char_per_horz_edge=None,
                    show_sq_player=True, show_edge_move=True):
        """ Display current Position
        :char_per_vert_edge: Number of characters in vertical edges
        per edge, not counting intersections
        :char_per_horz_edge: Number of characters in horizontal edges
            default: 2*char_per_vert_edge
        :show_sq_player: Display owner of square
                default: True -> show
        :show_edge_move: Display move #
                default: True -> show move #
        """
        if char_per_horz_edge is None:
            char_per_horz_edge = char_per_vert_edge*2 # attempt to make square
        self.char_per_horz_edge = char_per_horz_edge
        self.char_per_vert_edge = char_per_vert_edge 
        self.show_sq_player = show_sq_player
        self.show_edge_move = show_edge_move
        
        self.dot_ch = '*'           # Character for "empty" dot
        self.dot_ch_join = '+'      # Character for dot with occupied edges
        self.empty_ch = ' '         # Character for empty
        self.hz_edge_ch = '-'       # Horizontal edge marker
        self.hz_edge_acc_ch = '='   # Horizontal edge accented marker
        self.vt_edge_ch = '|'       # Vertical edge marker
        self.vt_edge_acc_ch = '$'   # Vertical edge accented marker
        self.ncol = self.dotsmoves.ncol
        self.nrow = self.dotsmoves.nrow
        self.char_per_vert_side = self.nrow*(self.char_per_vert_edge+1)
        self.char_per_horz_side = self.ncol*(self.char_per_horz_edge+1)
        """ Create blank board
        """
        self.dchars = np.full([self.char_per_vert_side, self.char_per_horz_side],
                         self.empty_ch,
                         dtype=str)
        self.dc_col_ind = np.zeros([self.ncol+1], dtype=int)    # dchar index
        self.dc_row_ind = np.zeros([self.nrow+1], dtype=int)     # dchars index
        for icol in range(self.ncol+1):
            icch = icol*self.char_per_horz_edge
            self.dc_col_ind[icol] = icch
            for irow in range(self.nrow+1):
                irch = irow*self.char_per_vert_edge
                self.dc_row_ind[irow] = irch
                self.dchars[irch][icch] = self.dot_ch

        """Mark edges
        """
        for row in range(1, self.nrow+2):
            for col in range(1, self.ncol+2):
                for hv in [DotsMoves.HV_H, DotsMoves.HV_V]:
                    if col > self.ncol and hv == DotsMoves.HV_H:
                        continue    # right edge - no horz
                    if row > self.nrow and hv == DotsMoves.HV_V:
                        continue # bottom - no vert
                    edge_state = self.dotsmoves.get_edge_state(row=row, col=col, hv=hv)
                    if edge_state.is_set():
                        self.set_edge(row=row, col=col, hv=hv)

        """ Annotations
        """
        move_last = self.dotsmoves.moves[-1]
        self.set_edge(row=move_last.row, col=move_last.col, hv=move_last.hv,
                      acc=True)
        if self.show_sq_player:
            for irow in range(self.nrow):
                for icol in range(self.ncol):
                    sq = self.dotsmoves.squares[irow][icol]
                    if sq > 0:
                        self.mark_square(row=irow+1, col=icol+1, sq=sq)
        if self.show_edge_move:
            for move in self.dotsmoves.moves:
                move_no = move.move_no
                row = move.row
                col = move.col
                hv = move.hv
                self.mark_edge(row=row, col=col, hv=hv, move=move_no)
                        
        """ Create output string
        """
        move = self.dotsmoves.moves[-1]
        hv_str = "H" if move.hv == DotsMoves.HV_H else "V"        
        dchars_str = f"Move:{move.move_no}: Player:{move.player}"
        dchars_str += f" row:{move.row} col:{move.col} {hv_str}"
        if len(move.squares) > 0:
            dchars_str += " squares: "
            for square in move.squares:
                dchars_str += f" [{square[0]},{square[1]}]"
        
        dchars_str += "\n"
        for irch in range(self.char_per_vert_side):
            ch_row = self.dchars[irch]
            ch_row_str = 4*" " + "".join(ch_row) + "\n"
            dchars_str += ch_row_str
        return dchars_str

    def mark_square(self, row, col, sq):
        """ Mark take square with taker
        :row: row # 1..
        :col: col # 1..
        :sq: player #
        """
        irow = row-1
        icol = col-1
        ct_row_ch = int((self.dc_row_ind[irow] + self.dc_row_ind[irow+1])/2)
        ct_col_ch = int((self.dc_col_ind[icol] + self.dc_col_ind[icol+1])/2)
        mk_text = chr(ord("0")+sq)  # TBD - only good for 1-9
        self.dchars[ct_row_ch][ct_col_ch] = mk_text
    
    def mark_edge(self, row, col, hv, player=None, move=None):
        """ Mark edge in dchars character array
        :row: edge row 1..
        :col: edge col 1..
        :hv: horzontal(HV_H)/vertical(HV_V)
        :player: player number, if present
                defalt: no marking
        :move: move number, if present
                default: no marking
        """
        if hv == DotsMoves.HV_H:
            ch_left = (col-1)*(self.char_per_horz_edge) + 1 # count dot pos
            ch_row = (row-1)*(self.char_per_vert_edge)
            if move is not None:
                ct_row_ch = ch_row
                ct_col_ch = ch_left+int(self.char_per_horz_edge/2)-1
                move_str = str(move)
                mk_col_ch = ct_col_ch
                for i in range(len(move_str)):
                    c = move_str[i]
                    self.dchars[ct_row_ch][mk_col_ch+i] = c
        else:       # vertical
            ch_col = (col-1)*(self.char_per_horz_edge) # count dot pos
            ch_top = (row-1)*(self.char_per_vert_edge) + 1
            if move is not None:
                ct_row_ch = ((row-1)*(self.char_per_vert_edge)
                               + int(self.char_per_vert_edge/2))
                ct_col_ch = ch_col
                move_str = str(move)
                mk_col_ch = ct_col_ch
                for i in range(len(move_str)):
                    c = move_str[i]
                    self.dchars[ct_row_ch][mk_col_ch+i] = c
            
            ###for ir in range(self.char_per_vert_edge-1):
            ###    self.dchars[ch_top+ir][ch_col] = self.vt_edge_ch
    
    def set_edge(self, row, col, hv, acc=False):
        """ Set edge in dchars character array
        :row: edge row 1..
        :col: edge col 1..
        :hv: horzontal(HV_H)/vertical(HV_V)
        :acc: accentuate move
        """
        if acc:
            if hv == DotsMoves.HV_H:
                mk_char = self.hz_edge_acc_ch
            else:
                mk_char = self.vt_edge_acc_ch
        else:
            if hv == DotsMoves.HV_H:
                mk_char = self.hz_edge_ch
            else:
                mk_char = self.vt_edge_ch
                
        if hv == DotsMoves.HV_H:
            ch_left = (col-1)*(self.char_per_horz_edge) + 1 # count dot pos
            ch_row = (row-1)*(self.char_per_vert_edge)
            for ic in range(self.char_per_horz_edge-1):
                if acc:
                    if ch_row > 0:
                        self.dchars[ch_row-1][ch_left+ic] = "V"
                self.dchars[ch_row][ch_left+ic] = mk_char
                if acc:
                    if ch_row < self.char_per_vert_side:
                        self.dchars[ch_row+1][ch_left+ic] = "^"
        else:       # vertical
            ch_col = (col-1)*(self.char_per_horz_edge) # count dot pos
            ch_top = (row-1)*(self.char_per_vert_edge) + 1
            for ir in range(self.char_per_vert_edge-1):
                if acc:
                    if ch_col > 1:
                        self.dchars[ch_top+ir][ch_col-2] = ">"
                    if ch_col > 0:
                        self.dchars[ch_top+ir][ch_col-1] = ">"
                self.dchars[ch_top+ir][ch_col] = mk_char
                if acc:
                    if ch_col < self.char_per_horz_side-2:
                        self.dchars[ch_top+ir][ch_col+2] = "<"
                    if ch_col < self.char_per_horz_side:
                        self.dchars[ch_top+ir][ch_col+1] = "<"
    
    
if __name__ == '__main__':
    dT = DotsMoves()
    dTT = DotsMovesText(dT)
    test = 2
    #test = 1
    SlTrace.lg(f"Test: {test}")
    if test == 1:
        for row in range(1, dT.nrow+2):
            for col in range(1, dT.ncol+2):
                for hv in [DotsMoves.HV_H, DotsMoves.HV_V]:
                    if col > dT.ncol and hv == DotsMoves.HV_H:
                        continue    # right edge - no horz
                    if row > dT.nrow and hv == DotsMoves.HV_V:
                        continue # bottom - no vert
                    dT.set_edge(row=row, col=col, hv=hv)
                    dstr = dTT.display_str()
                    SlTrace.lg(f"After: set_edge({row},{col},{hv})\n{dstr}")
    if test == 2:
        while True:
            player = dT.get_next_player()
            rcd_edge = dT.get_next_move(move_type="random")
            if rcd_edge is None:
                SlTrace.lg("End of game")    # No move
                break
            row, col, hv = rcd_edge
            hvs = "H" if hv == DotsMoves.HV_H else "V"
            SlTrace.lg(f"Player:{player} row:{row}, col:{col} {hvs}")
            if not dT.make_move(player=player, row=row, col=col, hv=hv):
                SlTrace.lg(f"Unexpected move failure Player:"
                           f" {player} row:{row}, col:{col} {hvs}\n")
                break
            
            dstr = dTT.display_str()
            SlTrace.lg(f"After: set_edge({row},{col},{hv})\n{dstr}")
    if test == 3:
        while True:
            player = dT.get_next_player()
            rcd_edge = dT.get_next_move(move_type="random")
            if rcd_edge is None:
                SlTrace.lg("End of game")    # No move
                break
            row, col, hv = rcd_edge
            hvs = "H" if hv == DotsMoves.HV_H else "V"
            SlTrace.lg(f"Player:{player} row:{row}, col:{col} {hvs}")
            if not dT.make_move(player=player, row=row, col=col, hv=hv):
                SlTrace.lg(f"Unexpected move failure Player:"
                           f" {player} row:{row}, col:{col} {hvs}\n")
                break
            
            dstr = dTT.display_str()
            SlTrace.lg(f"After: set_edge({row},{col},{hv})\n{dstr}")
            
