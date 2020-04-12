# sc_player_control.py 05Nov2018
"""
Player control window layout
Omitted to save room:
    steven (stay even) to right of level

players
Name      Label    Playing  Color    col bg  Voice Help   Pause Auto level
    
--------- ------   -        -------  ------  ----  -----  ----- ---- -----
comp1     c1       ()       gray     white   ( )   ( )    .1    x    0
comp2     c2       ()       gray     white   ( )   ( )    .1    x    -1
Alex      Ax       (.)      pink     white   (.)   ( )
Decklan   D        ()       blue     white   (.)   ( )
Avery     Av       ()       pink     white   (.)   ( )
Grampy    Gp       (.)      blue     white   (.)   ( )
Grammy    Gm       (.)      pink     white   (.)   ( )

[Add] [Change] [Remove]
"""
# ##from memory_profiler import profile

from tkinter import *
from tkinter.colorchooser import askcolor

from select_error import SelectError
from select_trace import SlTrace
from select_player import SelectPlayer
from player_info import PlayerInfo
from select_control_window import SelectControlWindow, content_var
from player_props import PlayerProps

        
class ColumnInfo:

    def __init__(self, field_name,
                 hd=None, val=None):
        """ column info
        :field_name: - SelectPlayer field name
        :hd: heading default: field_name.capitalized()
        :val: current / default value
                default: False (bool)
        """
        self.field_name = field_name
        if hd is None:
            hd = field_name.capitalize()
        self.heading = hd
        self.val = val
        self.player_field_by_widget = {}  # 2-tuple (player, field) by widget

        
class PlayerControl(SelectControlWindow):
    CONTROL_NAME_PREFIX = "player_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    
    show_delete = True  # Show delete field
    only_form_fields = {"delete" : show_delete}  # Fields only in form (not in player)
    player_fields = ["name", "label",
                     "playing",
                     "position",
                     "color", "color_bg",
                     "voice", "help_play", "pause",
                     "auto", "level", "steven", "delete"]
            
    def __init__(self, *args, title=None, control_prefix=None,
              play_control=None, **kwargs):
        """ Initialize subclassed SelectControlWindow singleton
        """
        self.max_color_len = len("#80ffff")  # For fields which have to contain hex color representation

                                        # Protect against early checking
        self.players = {}  # Dictionary of SelectPlayer
        self.playing = []  # Playing, in playing order
        self.cur_pindex = None  # Current player index in self.playing list
        self.controls_frame = None  # Set as no controls
        self.is_players_displayed = False  # Set when displayed
        self.players_frame = None  # Set when initialized
        self.player_field_by_widget = {}    
        if title is None:
            title = "Player Control"
        if control_prefix is None:
            control_prefix = PlayerControl.CONTROL_NAME_PREFIX
        self.play_control = play_control
        super().__init__(*args,
                      title=title, control_prefix=control_prefix,
                      **kwargs)
        SlTrace.set_mw(self.mw)  # Setup for reporting    
        self.score_control = None
        super().control_display()  # Do base work
        self.player_props = PlayerProps(self)        
        self.control_display_base()
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        self.selected_widget = None  # Last applicable field clicked
        self.mw.bind ("<Button-1>", self.button_click)
        self.mw.bind ("<Double-Button-1>", self.double_click)

    def report(self, msg):
        """ Report message with popup
        identifying us as the area
        :msg: message to display
        """
        msg_display = f"Player Control: {msg}"
        SlTrace.lg(msg_display)
        SlTrace.report(msg_display)
        
    def delete_window(self):
        SlTrace.lg("Closing Player Control Window")
        self.player_props.save_player_info()
        super().delete_window()
        super().destroy()

    def double_click(self, event):
        widget = event.widget
        if widget in self.player_field_by_widget:
            _, field = self.player_field_by_widget[widget]
            if field.startswith("color"):
                self.select_widget(widget)
                self.choose_color(widget)
                return
            else:
                self.select_widget(widget)
                return

    def button_click(self, event):
        widget = event.widget
        if widget in self.player_field_by_widget:
            self.select_widget(widget)
                        
    def get_player_control_fields(self, all=False):
        """ Get player control fields
        :all: True - return all field names
                default: False - just player saved fields
        """
        fields = []
        for field in self. player_fields:
            if all or not field in self.only_form_fields:  # TBD check this ???
                fields.append(field)
        return fields  
    
    def control_display_base(self):
        """ Display setup / re-setup for player info to support new players
        """
        if self.controls_frame is not None:
            self.controls_frame.pack_forget()
            self.controls_frame.destroy()
            self.controls_frame = None
        self.controls_frame = Frame(self.top_frame)
        self.controls_frame.pack(side="top", fill="x", expand=True)
        self.players_frame = Frame(self.controls_frame)
        self.players_frame.pack(side="top", fill="x", expand=True)
         
        """ fields in the order to present """        
        col_infos = []
        for field in self.player_fields:
            if field in self.only_form_fields:
                if not self.only_form_fields[field]:
                    continue  # Don't show field
                
                val = False  # Default to bool
            else:
                val = None
                if len(self.players) > 0:
                    player = list(self.players)[0]
                    if hasattr(player, field):
                        val = getattr(player, field)                    
            heading = self.get_heading(field)
            col_info = ColumnInfo(field, hd=heading, val=val)
            col_infos.append(col_info)
        self.col_infos = col_infos    
        self.add_players_form()  # Create players' control forms
        self.control_display()
    
    # ##@profile
    def control_display(self):
        """ display controls to enable
        entry / modification
        """
        """ Contol buttons """
        control_button_frame = Frame(self.controls_frame)
        control_button_frame.pack(side="top", fill="x", expand=True)
        color_button = Button(master=control_button_frame, text="Choose Color",
                            command=self.choose_color)
        color_button.pack(side="left", expand=True)
        add_button = Button(master=control_button_frame, text="Add Player",
                            command=self.add_new_player)
        add_button.pack(side="left", expand=True)
        ''' NO Delete button
        delete_button = Button(master=control_button_frame, text="Delete",
                            command=self.delete_player)
        delete_button.pack(side="left", expand=True)
        '''
        self.mw.bind('<Configure>', self.win_size_event)
        self.arrange_windows()
        self.is_players_displayed = True

    def select_widget(self, widget):
        """ Mark widget of interest e.g. intensify boundary
        :widget: widget, e.g. Entry, of interest
        """
        self.selected_widget = widget
        cfg = {"borderwidth" : 3, 'highlightbackground' : "blue", "relief" : "solid"}
        widget.config(cfg)

    def unselect_widget(self, widget):
        """ Mark widget of interest e.g. intensify boundary
        :widget: widget, e.g. Entry, of interest
        """
        cfg = {"borderwidth" : 2, "relief" : "raised"}
        widget.config(cfg)
        self.selected_widget = None

    def choose_color(self, widget=None):
        """ Facilitate chaning color (forground and background) with tkinter.colorchooser)
        :widget: widget to colorize
                default: use selected widget, if one
        """
        if widget is None:
            widget = self.selected_widget
        if widget is None:
            SlTrace.report("No entry is selected")
            return
        
        if widget in self.player_field_by_widget:
            (player, field) = self.player_field_by_widget[widget]
            if not field.startswith("color"):
                self.report(f"field {field} is not colorizable")
                return
            
        else:
            self.report("No appropriate widget found")
            return
        
        SlTrace.lg(f"field:{field} player: {player}")    
        _, color = askcolor()
        if color is None:
            SlTrace.report(f"No color selected")
            return
        
        ctl_var = player.ctls_vars[field]
        ctl_var.set(color)
        field_ctl = player.ctls[field]
        if field == "color":
            player_cfg = {"fg" : color}
        elif field == "color_bg":
            player_cfg = {"bg" : color}
        else:
            self.report(f"unhandled field: {field}")
            return
        
        field_ctl.config(player_cfg)
        
    def add_player_form1(self, player):
        """ Add player to form
        :player: SelectPlayer
        """
        for idx in range(len(self.player_fields)):
            self.set_player_frame(self.players_frame, player, idx)
        self.players_frame.rowconfigure(player.id, weight=1)

    def add_players_form(self):
        """ Add players' info to control form
        """
        self.set_field_headings(self.players_frame)
        for player in self.players.values():
            self.add_player_form(player)
        self.set_vals()  # Accent playing
        
    def add_player_form_internal(self, player, players_frame=None):
        """ Add player to form
        :player: SelectPlayer
        """
        for idx in self.player_fields.keys():
            self.set_player_frame(players_frame, player, idx)
        players_frame.rowconfigure(player.id, weight=1)

    def get_next_player(self, set_player=True):
        """ get next candidate player
        :set: True set as true default set as current player
        """
        SlTrace.lg(f"get_next_player, set_player={set_player}", "player")
        if len(self.playing) == 0:
            return None
        
        pindex = self.cur_pindex
        if pindex == None or pindex >= len(self.playing):
            pindex = 0
        pindex += 1
        if pindex >= len(self.playing):
            pindex = 0  # Wrap to first
        player = self.playing[pindex]
        if set_player:
            self.cur_pindex = pindex
        return player
    
    def get_first_position(self):
        """ get first playing player's position
        :returns: return position value
                    None if no playing
        """
        if len(self.playing):
            return None
        
        return self.playing[0].position
    
    def get_next_position(self, position):
        """ Get next position after given,
        :position: starting at 1..len(playing)-1
        among playing players, wrapping if necessar
        :returns: next player's position
                None if no one is playing
        """
        if len(self.playing) == 0:
            return None
        
        next_player = self.get_next_player()
        return None if next_player is None else next_player.position

    def set_set_cmd(self, cmd):
        """ Setup / clear Set button command
        """
        self.set_cmd = cmd

    def set_player(self, player):
        """ Record player  as next player
        """
        self.cur_player = player

    def set_play_level(self, play_level=None):
        """ Set players' level via
        comma separated string
        :play_level: comma separated string of playing player's Labels
        """
        players = self.get_players(all=True)
        play_levels = [x.strip() for x in play_level.split(',')]
        def_level = "2"
        if len(play_levels) == 0:
            SlTrace.lg("Setting to default level: {}".format(def_level)) 
            play_levels = def_level  # Default
        player_idx = -1
        for player in players:
            player_idx += 1
            if player_idx < len(play_levels):
                player_level = play_levels[player_idx]
            else:
                player_level = play_levels[-1]  # Use last level
            plevel = int(player_level)
            playing_var = player.ctls_vars["level"]
            player.level = plevel
            playing_var.set(plevel)
            SlTrace.lg("Setting {} play level to {:d}".format(player, plevel))

    def set_playing(self, playing=None):
        """ Set players playing via
        comma separated string
        :playing: comma separated string of playing player's Labels
        """
        players = self.get_players(all=True)  # Get playing
        if playing is None:
            player_str = ""
            for player in players:
                if player_str != "":
                    player_str += ","
                player_str += player.label
        playing = playing.lower()
        play_list = [x.strip() for x in playing.split(',')]
        for player in players:
            playing_var = player.ctls_vars["playing"]
            if player.label.lower() in play_list:
                player.playing = True
            else:
                player.playing = False
            playing_var.set(player.playing)
        self.set_vals()
        
    def set_score_control(self, control):
        """ Provide score control connection
        :control: score control instance
        """
        self.score_control = control

    def setup_game(self):
        """ Setup for new game
        """
        self.playing = self.get_players()
        self.cur_pindex = 0
    
    def get_player(self, position=None):
        """ Get player / current player
        Doesn't alter current player
        :position: playing position (index+1)
            default: current player
        :returns: player
                None if no players
        """
        if len(self.playing) == 0:
            return None  # None playing
        
        if position is None:
            pindex = self.cur_pindex
        else:
            pindex = position - 1
        if pindex >= len(self.playing):
            pindex = 0  # Wrap around to first
        player = self.playing[pindex]
        return player

    def get_player_num(self):
        """ Get current player's order number, starting with 1 for first play
        """
        if len(self.playing) == 0:
            return None
        
        return self.cur_pindex + 1
  
    def get_player_prop_key(self, player):
        """ Generate full properties name for this player
        """
        key = self.get_prop_key(str(player.id))
        return key
    
    def get_players(self, all=False):
        """ Get players
        :all: all players default: just currently playing
        :returns: list of players sorted in the order of their position
                    calculated from current players list
        """
        players = []
        for player in self.players.values():
            if all or player.playing:
                players.append(player)
        players.sort(key=lambda player: player.position)
        return players
                
    def set(self, push_info=True):
        """ Set info from form
        """
        if push_info:
            self.player_props.push_player_info()
        self.delete_players_checked()
        self.set_vals()
        self.control_display_base()
        if self.set_cmd is not None:
            self.set_cmd(self)
        if SlTrace.trace("set_updates_prop"):
            self.player_props.save_player_info()
        self.selected_widget = None  # Last applicable field clicked
        
    def add_new_player(self):
        """ Add new player
        """
        next_id = 1
        while len(self.players) > 0 and next_id in self.players:
            next_id += 1
        next_player = SelectPlayer(self, id=next_id)  # Next available id
        self.add_player_form(next_player)
        SlTrace.lg(f"new_player:{next_player}")

    def add_player_form(self, player):
        """ Add player
        :player: player to add to form
        """
        ''' # Already there
        for field in self.player_fields:
            field_key = f"{player.id}.{field}"
            val = getattr(player, field)
            self.set_prop_val(field_key, val)
        '''
        self.players[player.id] = player
        score_fields = ["score", "played", "wins", "ties"]
        for field in self.player_fields + score_fields:
            if field in self.only_form_fields:
                pass
            else:
                value = player.get_val(field)
                player.ctls_vars[field] = content_var(value)
                player.set_prop(field)
        self.add_player_form1(player)
        
    def set_field_headings(self, field_headings_frame):
        """ Setup player headings, possibly recording widths
        """
        for info_idx, col_info in enumerate(self.col_infos):
            heading = col_info.heading
            width = self.get_col_width(self.col_infos[info_idx].field_name)
            heading_label = Label(master=field_headings_frame,
                                  text=heading, anchor=CENTER,
                                  justify=CENTER,
                                  font="bold",
                                  width=width)
            heading_label.grid(row=0, column=info_idx, sticky=NSEW)
            field_headings_frame.columnconfigure(info_idx, weight=1)

    def get_col_infos_idx(self, field_name):
        """ Get field index in self.col_infos table
        """
        idx = -1
        for idx, info in enumerate(self.col_infos):
            if field_name == info.field_name:
                return idx
        
        raise SelectError(f"field_name({field_name} not found in col_infos")
    
    def get_col_width(self, field_name):
        """ Calculate widget text width
        :field_name: field name SelectPlayer attribute
        :returns:  proper column width, given heading and all values for this field
        """
        heading = self.get_heading(field_name)
        width = len(heading)  # Start with heading as width
        # ## Requires players to be already present
        for player in self.players.values():
            if hasattr(player, field_name):
                val = getattr(player, field_name)
            else:
                val = self.col_infos[self.get_col_infos_idx(field_name)].val
                if val is None:
                    val = False  # bool
            if isinstance(val, bool):
                pwidth = 1
            else:
                pwidth = len(str(val))
            if pwidth > width:
                width = pwidth
        return int(width)
    
    def get_field_name(self, heading):
        """ Convert heading into field name
        :heading:  Heading text
        """
        field = heading.lower()
        if field == "help":
            field = "help_play"
        return field
    
    def get_heading(self, field_name):
        """ Convert heading into field name
        :field_name:  field attribute
        """
        heading = field_name
        if heading == "help_play":
            heading = "help"
        elif heading == "delete":
            heading = "x"
        heading = heading.capitalize()
        return heading

    def max_color_width(self, width):
        """ Enlarge width, if necessary to hold hex representation
        :width: given width
                default: use max hex rep
        """
        if width is None:
            width = self.max_color_len
        width = max(width, self.max_color_len)
        return width
        
    # ##@profile
    def set_player_frame(self, frame, player, idx):
        """ Create player info line
        :frame: players frame
        :player: player info
        :idx: index into col_infos
        """
        col_info = self.col_infos[idx]
        field_name = col_info.field_name
        if field_name in self.only_form_fields:
            value = self.col_infos[idx].val
        else:
            value = player.get_val(field_name)
        width = self.get_col_width(field_name)
        frame = Frame(frame, height=1, width=width)
        frame.grid(row=player.id, column=idx, sticky=NSEW)

        if field_name == "name":
            self.set_player_frame_name(frame, player, value, width=width)
        elif field_name == "label":
            self.set_player_frame_label(frame, player, value, width=width)
        elif field_name == "playing":
            self.set_player_frame_playing(frame, player, value, width=width)
        elif field_name == "position":
            self.set_player_frame_position(frame, player, value, width=width)
        elif field_name == "color":
            self.set_player_frame_color(frame, player, value, width=self.max_color_width(width))
        elif field_name == "color_bg":
            self.set_player_frame_color_bg(frame, player, value, width=self.max_color_width(width))
        elif field_name == "voice":
            self.set_player_frame_voice(frame, player, value, width=width)
        elif field_name == "help_play":
            self.set_player_frame_help(frame, player, value, width=width)
        elif field_name == "pause":
            self.set_player_frame_pause(frame, player, value, width=width)
        elif field_name == "auto":
            self.set_player_frame_auto(frame, player, value, width=width)
        elif field_name == "level":
            self.set_player_frame_level(frame, player, value, width=width)
        elif field_name == "steven":
            self.set_player_frame_steven(frame, player, value, width=width)
        elif field_name == "delete":
            self.set_player_frame_delete(frame, player, value, width=width)
        else:
            raise SelectError("Unrecognized player field_name: %s" % field_name)    

    def get_num_playing(self):
        """ Calculate number playing
        """
        nplaying = 0
        for player in self.players.values():
            if player.playing:
                nplaying += 1
        return nplaying

    def set_player_frame_name(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["name"] = val_entry
        player.ctls_vars["name"] = content

    def set_player_frame_label(self, frame, player, value, width=None):
        field = "label"
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls[field] = val_entry
        player.ctls_vars[field] = content
        self.player_field_by_widget[val_entry] = (player, field)

    def set_player_frame_playing(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=None)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["playing"] = yes_button
        player.ctls_vars["playing"] = content

    def set_player_frame_position(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["position"] = yes_button
        player.ctls_vars["position"] = content

    def set_player_frame_color(self, frame, player, value, width=None):
        field = "color"
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls[field] = val_entry
        player.ctls_vars[field] = content
        self.player_field_by_widget[val_entry] = (player, field)

    def set_player_frame_color_bg(self, frame, player, value, width=None):
        field = "color_bg"
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls[field] = val_entry
        player.ctls_vars[field] = content
        self.player_field_by_widget[val_entry] = (player, field)

    def set_player_frame_voice(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["voice"] = yes_button
        player.ctls_vars["voice"] = content

    def set_player_frame_help(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["help_play"] = yes_button
        player.ctls_vars["help_play"] = content

    def set_player_frame_pause(self, frame, player, value, width=None):
        content = DoubleVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["pause"] = yes_button
        player.ctls_vars["pause"] = content

    def set_player_frame_auto(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["auto"] = yes_button
        player.ctls_vars["auto"] = content

    def set_player_frame_level(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["level"] = yes_button
        player.ctls_vars["level"] = content

    def set_player_frame_steven(self, frame, player, value, width=None):
        content = DoubleVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["steven"] = yes_button
        player.ctls_vars["steven"] = content

    def set_player_frame_delete(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["delete"] = yes_button
        player.ctls_vars["delete"] = content

    def set_ctls(self):
        """ Update control/display from internal values
        of those playing
        """
        for player in self.players.values():
            if player.playing:
                player.set_ctls()

    def set_vals(self):
        """ Read form, and update internal values
        Set form fields,if playing, based on player's color and background color
        """
        SlTrace.lg("set_vals", "set_vals")
        players = list(self.players.values())  # In case of delete
        for player in players:  # Update player from fields
            for field in player.ctls:
                if field in self.only_form_fields:
                    pass
                else:            
                    player.set_val_from_ctl(field)
            for field in player.ctls:  # Setup form display attributes
                field_ctl = player.ctls[field]
                player_cfg = {"fg" : player.color, "bg" : player.color_bg}
                if player.playing:
                    player_cfg["font"] = "bold"
                    field_ctl.config(player_cfg)
                else:
                    player_cfg["font"] = "system"
                    field_ctl.config(player_cfg)
        if self.play_control is not None:
            self.play_control.setup_scores_frame()

    def delete_player(self, player):
        """ Delete player for database
        :player: player to be deleted
        """
        SlTrace.lg(f"delete player: {player}")
        player.deleteProps()
        del self.players[player.id]

    def delete_players_checked(self):
        """ Delete player for database
        :player: player to be deleted
        """
        player_ids = [player_id for player_id in self.players.keys()]  # In case of delete
        delete_count = 0  # Redo display if any deletion
        for player_id in player_ids:  # Update player from fields
            player = self.players[player_id]
            field_var = player.ctls_vars["delete"]
            to_delete = field_var.get()
            if to_delete:
                self.delete_player(player)
                delete_count += 1
                
    def set_score(self, player, score):
        """ Set player score centrally 
        :player: to set
        :score: to set
        """
        cplayer = self.players[player.id]
        player.score = score  # Set possible copy
        cplayer.score = score

    def get_score(self, player):
        """ Get player score centrally 
        :player: to get
        """
        cplayer = self.players[player.id]
        return cplayer.score

    def set_played(self, player, played):
        """ Set player game centrally 
        :player: to set
        :played: to set
        """
        cplayer = self.players[player.id]
        player.played = played  # Set possible copy
        cplayer.played = played

    def get_played(self, player):
        """ Get player game centrally 
        :player: to get
        """
        cplayer = self.players[player.id]
        return cplayer.played

    def get_ties(self, player):
        """ Get player game centrally 
        :player: to get
        """
        cplayer = self.players[player.id]
        return cplayer.ties

    def set_ties(self, player, ties):
        """ Set player game centrally 
        :player: to set
        :ties: to set
        """
        cplayer = self.players[player.id]
        player.ties = ties  # Set possible copy
        cplayer.ties = ties

    def get_wins(self, player):
        """ Get player game centrally 
        :player: to get
        """
        cplayer = self.players[player.id]
        return cplayer.wins

    def set_wins(self, player, wins):
        """ Set player game centrally 
        :player: to set
        :wins: to set
        """
        cplayer = self.players[player.id]
        player.wins = wins  # Set possible copy
        cplayer.wins = wins
        
    def set_all_scores(self, score=0, only_playing=False):
        """ Set all player scores
        :score: player score default: 0
        :only_playing: only modify those playing default: all
        """
        for _, player in self.players.items():
            if only_playing and not player.playing:
                continue  # Not playing - leave alone
            player.set_score(score)

    def set_all_played(self, played=0, only_playing=False):
        """ Set all player played
        :played: player played default: 0
        :only_playing: only modify those playing default: all
        """
        for _, player in self.players.items():
            if only_playing and not player.playing:
                continue  # Not playing - leave alone
            player.set_played(played)

    def set_all_wins(self, wins=0, only_playing=False):
        """ Set all player wins
        :wins: player wins default: 0
        :only_playing: only modify those playing default: all
        """
        for _, player in self.players.items():
            if only_playing and not player.playing:
                continue  # Not playing - leave alone
            player.set_wins(wins)
       
    def delete_window(self):
        """ Process Trace Control window close
        """
        if self.mw is not None:
            self.mw.destroy()
            self.mw = None

    def destroy(self):
        """ relinquish resources
        """
        self.delete_window()
    
    def add(self):
        if "set" in self.call_d:
            self.call_d["set"]()
    
    def edit(self):
        if "edit" in self.call_d:
            self.call_d["edit"]()
        
    def delete(self):
        if "delete" in self.call_d:
            self.call_d["delete"]()

    def reset(self):
        """ Reset info to start up
        """
        self.player_props.reset()

    def undo(self):
        """
        Undo previous player change(s)
        """
        self.player_props.undo()

    def redo(self):
        """
        Redo previous player undo(s)
        """
        self.player_props.redo()

        
if __name__ == '__main__':
        
    root = Tk()

    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    SlTrace.setFlags("")
    plc = PlayerControl(frame, title="Player Control", display=True)
        
    root.mainloop()
