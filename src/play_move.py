# play_move.py    24March2020  crs
"""
Supports move information for playback
"""

class PlayMove:
    SELECT_EDGE = "select_edge"     # May select edge to be markes
    MARK_EDGE = "mark_edge"         # May mark an already selected edge
    UNDO_MOVE = "undo_move"         # May undo a previous (select, mark)
    REDO_MOVE = "redo_move"         # May redo a previous select, mark
    SET_PLAY = "set_play"           # Set players playing settings
    SET_PLAYING = "set_playing"     # Set players
    PLAY_MOVE = "play_move"         # Play move from auto/manual
    PLAY_MOVE_TILL = "play_move_till"   # Play move until next player's turn
    GAME_CHECK = "game_check"       # Test / verify game state
    HV_H = "horizontal"
    HV_V = "vertical"
    
    def __init__(self, move_type, row=None, col=None, hv=None, player=None,
                    part=None, move_no=None,
                    playing=None,
                    label_name=None,
                    case_sensitive=None,
                    mode=None,
                    is_set=None,
                    show_fail=None,
                    kwargs=None,
                    pre_comment=None,
                    line_comment=None):
        """ Containing game move information for possible snapshot / analysis
        :move_type: type of move e.g. SELECT_EDGE,...
        :row: game board row
        :col: game board col
        :hg: vertical/horizontal
        :player: player making move
        :playing: list of players' labels/names
        :label_name: player's label/Name or None - every player
        :case_sensitive: True use case for checking
        :kwargs: dictionary of additional arguments/values
        :pre_comment: comments preceeding move
        :line_comment: comment to end of line
        """
        self.move_type = move_type

        self.row = row
        self.col = col
        self.hv = hv
                                    # Optional - possibly only for debugging / analysis
        self.player = player
        self.part = part
        self.move_no = move_no
        self.playing = playing
        self.label_name=label_name
        self.case_sensitive=case_sensitive
        self.mode=mode
        self.is_set=is_set
        self.show_fail=show_fail
        self.kwargs=kwargs
        self.pre_comment = pre_comment
        self.line_comment = line_comment
        self.removed = False        # True if remove from game
        
