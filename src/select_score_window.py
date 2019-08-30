# select_score_window.py    21-Feb_2019  crs
"""
Window control for display of game score_window
"""
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
            
        
class ScoreWindow:
    CONTROL_NAME_PREFIX = "score_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 0
    
    wd = 15
    col_infos = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ]
    col_infos_wins = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ]
    col_infos_ties = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ["ties", "ties", wd],
        ]
    
    def __init__(self, play_control,
                control_prefix=None,
                show_ties=False,
                ):
        """ Setup score /undo/redo window
        """
        self.play_control = play_control
        self.show_ties = show_ties
        if show_ties:
            self.col_infos = ScoreWindow.col_infos_ties
        else:
            self.col_infos = ScoreWindow.col_infos
        self.mw = Toplevel()
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.mw.withdraw()       # Hide main window
        self.mw = Toplevel()
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        top_frame = Frame(self.mw)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        move_frame = Frame(top_frame)
        move_frame.pack(side="top", fill="x", expand=True)
        move_no_frame = Frame(move_frame)
        move_no_frame.pack()
        move_no = 0
        move_no_str = "Move: %d" % move_no
        move_font = ('Helvetica', '25')
        self.move_no_label = Label(move_no_frame,
                              text=move_no_str,
                              font=move_font
                              )
        self.move_no_label.pack(side="left", expand=True)
        ###move_no_label.config(width=2, height=1)
        
        scores_frame = Frame(self.mw)
        scores_frame.pack()
        players = self.play_control.get_players()
        
        headings_frame = Frame(scores_frame)
        headings_frame.pack()
        self.set_field_headings(headings_frame)
        
        for player in players:
            player_frame = Frame(scores_frame)
            player_frame.pack(side="top", fill="both", expand=True)
            self.set_player_frame(player_frame, player, "name")
            self.set_player_frame(player_frame, player, "label")
            self.set_player_frame(player_frame, player, "score")
            self.set_player_frame(player_frame, player, "played")
            self.set_player_frame(player_frame, player, "wins")
            if self.show_ties:
                self.set_player_frame(player_frame, player, "ties")

        
        bw = 5
        bh = 1
        undo_font = ('Helvetica', '50')
        undo_button = Button(master=move_frame, text="Undo",
                            font=undo_font,
                            command=self.undo_button)
        undo_button.pack(side="left", expand=True)
        undo_button.config(width=bw, height=bh)
        redo_button = Button(master=move_frame, text="ReDo",
                             font=undo_font,
                            command=self.redo_button)
        redo_button.pack(side="left", expand=True)
        redo_button.config(width=bw, height=bh)
    
        ###self.setup_score_window(move_no_label=move_no_label)
        self.arrange_windows()
        self.mw.bind( '<Configure>', self.win_size_event)
        ###self.update_window()


    def win_size_event(self, event):
        """ Window sizing event
        """
        win_x = self.mw.winfo_x()
        win_y = self.mw.winfo_y()
        win_width = self.mw.winfo_width()
        win_height = self.mw.winfo_height()
        self.set_window_size(win_x, win_y, win_width, win_height)

        
    def set_window_size(self, x, y, width, height, change=False):
        """ Size our window
        :change: True force window resize
        """
        self.set_prop_val("win_x", x)
        self.set_prop_val("win_y", y)
        self.set_prop_val("win_width", width)
        self.set_prop_val("win_height", height)
        if change:
            geo_str = "%dx%d+%d+%d" % (x, y, width, height)
            self.mw.geometry(geo_str)
    
    def arrange_windows(self):
        """ Arrange windows
            Get location and size for properties if any
        """
        win_x = self.get_prop_val("win_x", self.DEF_WIN_X)
        if win_x < 0:
            win_x = 50
        win_y = self.get_prop_val("win_y", self.DEF_WIN_Y)
        if win_y < 0:
            win_y = 50
        
        win_width = self.get_prop_val("win_width", self.mw.winfo_width())
        win_height = self.get_prop_val("win_height", self.mw.winfo_height())
        self.set_window_size(win_width, win_height, win_x, win_y, change=True)
        
    
    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
        """        
        key = self.control_prefix + "." + name
        return key

    def get_prop_val(self, name, default):
        """ Get property value as (string)
        :name: field name
        :default: default value, if not found
        :returns: "" if not found
        """
        prop_key = self.get_prop_key(name)
        prop_val = SlTrace.getProperty(prop_key)
        if prop_val is None:
            return default
        
        if isinstance(default, int):
            if prop_val == "":
                return 0
           
            return int(prop_val)
        elif isinstance(default, float):
            if prop_val == "":
                return 0.
           
            return float(prop_val)
        else:
            return prop_val

    def set_prop_val(self, name, value):
        """ Set property value as (string)
        :name: field name
        :value: default value, if not found
        """
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))
        
       
    def set_field_headings(self, field_headings_frame):
        """ Setup player headings, possibly recording widths
        """
        col_infos = self.col_infos
        for info_idx, col_info in enumerate(col_infos):
            field_name = col_info[0]
            if len(col_info) >= 2:
                heading = col_info[1]
            else:
                heading = field_name
            ###width = 20      # Hack
            if len(col_info) >= 3:
                width = col_info[2]
            heading_label = Label(master=field_headings_frame,
                                  text=heading, anchor="w",
                                  justify=CENTER,
                                  width=width)
            heading_label.grid(row=0, column=info_idx, sticky=NSEW)
            field_headings_frame.columnconfigure(info_idx, weight=1)
    

    def set_player_frame(self, frame, player, field):
        """ Create player info line
        Adapted form PlayerControl.set_player_control
        :frame: players frame
        :player: player info
        :field: name of field
        """
        col_infos = self.col_infos
        col_info = None     # Set if name found
        idx = 0             # Bumped after each check
        for cinfo in col_infos:
            if cinfo[0] == field:
                cname = field
                if len(cinfo) >=2:
                    cheading = cinfo[1]
                else:
                    cheading = cname
                if len(cinfo) >= 3:
                    cwidth = cinfo[2]
                else:
                    cwidth = None
                col_info = (cname, cheading, cwidth)
                break
            idx += 1        # Next grid column
        if col_info is None:
            raise SelectError("field name %s not found" % field)
        
        field_name = col_info[0]
        value = player.get_val(field_name)
        width = col_info[2]
        frame = Frame(frame, height=1, width=width)
        frame.grid(row=player.id, column=idx, sticky=NSEW)

        if field_name == "name":
            self.set_player_frame_name(frame, player, value, width=width)
        elif field_name == "label":
            self.set_player_frame_label(frame, player, value, width=width)
        elif field_name == "score":
            self.set_player_frame_score(frame, player, value, width=width)
        elif field_name == "played":
            self.set_player_frame_played(frame, player, value, width=width)
        elif field_name == "wins":
            self.set_player_frame_wins(frame, player, value, width=width)
        elif field_name == "ties":
            self.set_player_frame_ties(frame, player, value, width=width)
        else:
            raise SelectError("Unrecognized player field_name: %s" % field_name)    

    
            

    def set_player_frame_name(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["name"] = val_entry
        player.ctls_vars["name"] = content

    def set_player_frame_label(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["label"] = val_entry
        player.ctls_vars["label"] = content

    def set_player_frame_score(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", expand=True)
        player.ctls["score"] = val_entry
        player.ctls_vars["score"] = content

    def set_player_frame_played(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", expand=True)
        player.ctls["played"] = val_entry
        player.ctls_vars["played"] = content

    def set_player_frame_wins(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", expand=True)
        player.ctls["wins"] = val_entry
        player.ctls_vars["wins"] = content

    def set_player_frame_ties(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", expand=True)
        player.ctls["ties"] = val_entry
        player.ctls_vars["ties"] = content



    def destroy(self):
        """ Destroy window resources
        """
        if self.mw is not None:
            self.mw.destroy()
        self.mw = None
        
        
    def delete_window(self):
        """ Handle window deletion
        """
        if self.play_control is not None:
            self.play_control.close_score_window()
        else:
            self.destroy()
        self.play_control = None
        
    
    def update_window(self):
        if self.mw is None:
            return
        
        if self.move_no_label is not None:
            scmd = self.play_control.get_last_cmd()
            if scmd is None:
                self.move_no_label.config(text="Start")
            else:
                move_no_str = "Move: %d" % scmd.move_no
                self.move_no_label.config(text=move_no_str)
        players = self.play_control.get_players()
        for player in players:
            score_ctl_var = player.ctls_vars["score"]
            score = player.get_score()
            score_ctl_var.set(score)
            SlTrace.lg("score: %d %s" % (score, player), "score")
            played_ctl_var = player.ctls_vars["played"]
            played = player.get_played()
            played_ctl_var.set(played)
            SlTrace.lg("played: %d %s" % (played, player), "score")
            wins_ctl_var = player.ctls_vars["wins"]
            wins = player.get_wins()
            wins_ctl_var.set(wins)
            SlTrace.lg("wins: %d %s" % (wins, player), "score")

        
        
    def undo_button(self):
        SlTrace.lg("undoButton")
        res = self.play_control.undo()
        return res
                
        
    def redo_button(self):
        SlTrace.lg("redoButton")
        res = self.play_control.redo()
        return res
