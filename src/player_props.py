# player_props.py    02Apr2020  crs
""" Support for player properties including undo/redo/base save / restoring

Player properties are controlled through an instance of PlayerControl
The save / restore of the base player attributes is done directly through PlayerControl.
The save/restore of the undo/redo stacks is done via PlayerControl via PlayerProps/PlayerProp

"""
import atexit
import re

from select_trace import SlTrace
from select_error import SelectError

from player_prop import PlayerProp
from player_info import PlayerInfo
from pandas._libs.writers import max_len_string_array

class PlayerProps:
    
    def __init__(self, player_control):
        """ Control player attributes 
        """
        self.player_control = player_control
        self.undo_stack = []
        self.redo_stack = []
        self.load_player_info()
        SlTrace.traceButton("clear_info_stacks", self.clear_info_stacks)
        SlTrace.traceButton("show_info", self.show_info)

    def load_player_info(self):
        """ Load players info, plus undo, and redo stack
        Note: During the game, players current info is stored here while the undo
        and redo information is stored in self.player_props.
         
        values stored in properties file
        All values stored under "player_control.".<player_id>
        The player_id is constructed by replacing all
        sequences of [^a-zA-Z_0-9]+ by "_" in the player name
        to produce a legal properties file id string
        Value strings:
            id                  value type
            ------------        -------------
            name                string
            label               string
            playing             bool
            position            int
            mV                  int
            color               string (fill)
            voice               bool
            help_play           bool
            pause               float
            auto                bool
            level               int
            steven              float
        
        Note: indicator display colors icolor, icolor2 are set to
                color and color_bg respectively

        ###Toplevel.__init__(self, parent)
        Setup control names found in properties file
        Updated as new control entries are added
        """
        player_infos = PlayerProp(self.player_control).get_player_infos()
        player_info = player_infos[0]
        self.reset_info = player_info
        self.player_control.players = player_info.players
        undo_infos = PlayerProp(self.player_control, "undo").get_player_infos()
        self.undo_stack = list(reversed(undo_infos))
        self.undo_stack_count = 0       # Keep track of change for comparison
        redo_infos = PlayerProp(self.player_control, "redo").get_player_infos()
        self.redo_stack = list(reversed(redo_infos))
        self.redo_stack_count = 0       # Keep track of change for comparison
        atexit.register(self.save_player_info)
        
    def pop_player_info(self, stack="undo"):
        """ recover player info
        :stack: "undo" - undo stack, "redo" - redo stack
                default: "undo"
        :returns: PlayerInfo with saved info 
        """
        if stack == "undo":
            pi = self.undo_stack.pop()
            self.undo_stack_count -= 1      # Keep track of level change
        elif stack == "redo":
            pi = self.redo_stack.pop()
            self.redo_stack_count -= 1      # Keep track of level change
        else:
            raise SelectError(f"Unrecognized stack type:{stack}")
        return pi
        
    def check_player_info_stack(self, stack="undo"):
        """ check if player info for possible resoration
        :stack: "undo" - undo stack, "redo" - redo stack
                default: "undo"
        :returns: True iff some on stack
        """
        if stack == "undo":
            stk_len = len(self.undo_stack)
        elif stack == "redo":
            stk_len = len(self.redo_stack)
        else:
            raise SelectError(f"Unrecognized stack type:{stack}")
        return stk_len > 0
        
    def push_player_info(self, stack="undo"):
        """ push player info for possible resoration
        :stack: "undo" - undo stack, "redo" - redo stack
                default: "undo"
        """
        player_info = PlayerInfo(self.player_control, players=self.player_control.players)
        if stack == "undo":
            self.undo_stack.append(player_info)
            self.undo_stack_count += 1      # Keep track of level change
        elif stack == "redo":
            self.redo_stack.append(player_info)
            self.undo_stack_count += 1      # Keep track of level change
        else:
            raise SelectError(f"Unrecognized stack type:{stack}")
        
    def restore_player_info(self, player_info):
        """ Restore setting from player_info in self.player_control.players
        :player_info: player information (PlayerInfo)
        """
        self.player_control.players = {}
        for key, player in player_info.players.items():
            self.player_control.players[key] = player
        self.player_control.control_display_base()
        if self.player_control.set_cmd is not None:
            self.player_control.set_cmd(self)

    def clear_info_stacks(self):
        """ Clear out info stacks
        Mostly for debugging purposes
        NOTE: Don't save properties file unless  you want to remove proerties info
        """
        SlTrace.lg("Clearing undo/redo stack info")
        self.undo_stack = []
        self.redo_stack = []
        
    def save_player_info(self):
        """ Save player states plus undo/redo info for properties saving
        """
        max_undo_save = 20
        SlTrace.lg("Saving player current info")
        player_info = PlayerInfo(self.player_control, players=self.player_control.players)
        PlayerProp(self.player_control).save_props(player_info)
        SlTrace.lg(f"Saving player undo info max={max_undo_save}", "player_prop")
        PlayerProp(self.player_control, "undo").save_props(self.undo_stack[-max_undo_save:], stack_count=self.undo_stack_count)
        SlTrace.lg(f"Saving player redo info max={max_undo_save}", "player_prop")
        PlayerProp(self.player_control, "redo").save_props(self.redo_stack[-max_undo_save:], stack_count=self.undo_stack_count)
        if SlTrace.trace("set_updates_prop"):
            if not SlTrace.trace("set_updates_prop_abs"):
                sn1 = SlTrace.properties_properties_prev_sn()
            else:
                sn1 = None
                
            SlTrace.properties_change_print(sn1=sn1, req_match=r'.*\.(redo|undo)', req_match_not=True)
        if SlTrace.trace("undo_prop"):
            self.properties_stack_print(self.player_control.CONTROL_NAME_PREFIX)

    def show_info(self):
        """ Show current info
        """
        SlTrace.lg("show_info")
        if not SlTrace.trace("set_updates_prop_abs"):
            sn1 = SlTrace.properties_properties_prev_sn()
        else:
            sn1 = None
                
        SlTrace.properties_change_print(sn1=sn1, req_match=r'.*\.(redo|undo)', req_match_not=True)
        self.properties_stack_print(self.player_control.CONTROL_NAME_PREFIX)


    def reset(self):
        """ Reset info to start up
        """
        self.push_player_info()     # So we can back out of this too
        self.restore_player_info(self.reset_info)
        
    def undo(self):
        """
        Undo previous player change(s)
        """
        SlTrace.lg("undo", "trace_undo")
        if not self.check_player_info_stack():
            SlTrace.lg("Nothing to undo")
            return
        
        self.push_player_info("redo")
        pi = self.pop_player_info()
        self.restore_player_info(pi)
        if SlTrace.trace("set_updates_prop"):
            self.save_player_info()

    def redo(self):
        """
        Redo previous player undo(s)
        """
        SlTrace.lg("redo", "trace_undo")
        if not self.check_player_info_stack("redo"):
            SlTrace.lg("Nothing to redo")
            return
        
        self.push_player_info("undo")
        pi = self.pop_player_info("redo")
        self.restore_player_info(pi)
        if SlTrace.trace("set_updates_prop"):
            self.save_player_info()

    def properties_stack_print(self, base_prefix, snap_shot=None, incremental=True, max_len=None, title=None):
        """ Print stacks
        :base_prefix: section prefix, with or without trailing "." e.g. "player_control"
        :snapshot: properties snapshot
                default: current properties
        :sect_name: section name e.g. "undo"
        :incremental: just changes from previous entry
        :title: printed before listing
                default: sect_name
        """
        undo_stack_len = SlTrace.trace("undo_stack_len", default=6)
        redo_stack_len = SlTrace.trace("redo_stack_len", default=3)
        if max_len is None:
            undo_len = undo_stack_len
            redo_len = redo_stack_len
        else:
            undo_len = max_len
            redo_len = undo_len/2
        if SlTrace.trace("long_info"):
            redo_len = undo_len = 20
            
        if title is None:
            title = "player info stack"
        self.properties_sect_print(base_prefix, snapshot=snap_shot, sect_name="undo", max_len=undo_len, incremental=incremental)
        self.properties_sect_print(base_prefix, snapshot=snap_shot, sect_name="redo", max_len=redo_len, incremental=incremental)
        
        
    
    def properties_sect_print(self, base_prefix, snapshot=None, sect_name="undo", max_len=None, incremental=True, title=None):
        """ Print properties sect
        :base_prefix: section prefix, with or without trailing "." e.g. "player_control"
        :snapshot: properties snapshot
                default: current properties
        :sect_name: section name e.g. "undo"
        :max_len: print at most this many entries
        :incremental: just changes from previous entry
        :title: printed before listing
                default: sect_name
        """
            
        if title is None:
            title = sect_name
        SlTrace.lg(title)
        if not base_prefix.endswith("."):
            base_prefix += "."

        player_info = self.player_info(base_prefix, snapshot)
        player_infos = self.player_infos(base_prefix, snapshot, sect_name=sect_name)
        nprint = 0
        for i in range(len(player_infos)):
            prev_player_info = player_infos[i]
            if max_len is None or nprint < max_len:
                player_info.change_print(prev_player_info, prefix=f"{i:2}", incremental=incremental)
                SlTrace.lg("")
                nprint += 1
            player_info = prev_player_info
            

    def player_info(self, base_prefix, snapshot=None):
        """ Return current player info, based on properties
        :startswith: each key starts with this
        :returns: snapshot with current state but as if n the stack
        """
        if snapshot is None:
            snapshot = SlTrace.snapshot_properties()
        if not base_prefix.endswith("."):
            base_prefix += "." 
        sn = snapshot.snapshot_properties(sn=snapshot, req_match=re.escape(base_prefix) + r'\d+\.\w+')
        pp = PlayerProp(self.player_control)
        player_info = pp.get_player_infos(snapshot=sn)
        return player_info[0]
    

    def player_infos(self, base_prefix, snapshot=None, sect_name=None):
        """ Get current stack of player infos
        :base_prefix: prop key beginning prefix
        :snapshot: information snapshot
                    default: current snapshot
        :sect_name: section name e.g. "undo"
        sect_num: number 1 being last pushed
        """
        if snapshot is None:
            snapshot = SlTrace.snapshot_properties()
        if not base_prefix.endswith("."):
            base_prefix += "." 
        sn = snapshot.snapshot_properties(sn=snapshot, req_match=re.escape(base_prefix) + sect_name + r'\.')
        pp = PlayerProp(self.player_control, sect_name=sect_name)
        player_infos = pp.get_player_infos(snapshot=sn)
        return player_infos

            
    
if __name__ == "__main__":
    import argparse
    
    from sc_player_control import PlayerControl
    
    propfile = "player_props_test"
    propfile_new_ext = "props_out"
    propfile_update = True
    show_passes = True
    ###show_passes = False
    quit_on_fail = True      # True - stop testing on first failure
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--propfile', default=propfile,
                        help=("properties file name"
                              " (default:generate from script name)"))
    parser.add_argument('-n', '--propfile_new_ext', default=propfile_new_ext,
                        help=("new properties file ext"
                              " (default:no extension change)"))
    parser.add_argument('-u', '--propfile_update', default=propfile_update,
                        help=("update properties file"
                              " (default:write out new properties file)"))
    parser.add_argument('-s', '--show_passes', action='store_true', default=show_passes,
                        help=(f"Show passes"
                              f" (default: {show_passes}"))
    parser.add_argument('-q', '--quit_on_fail', action='store_true', default=quit_on_fail,
                        help=(f"Quit on first failure"
                              f" (default: {quit_on_fail}"))

    args = parser.parse_args()             # or die "Illegal options"
    
    propfile = args.propfile
    propfile_new_ext = args.propfile_new_ext
    propfile_update = args.propfile_update
            
    logName = propfile
    SlTrace.setupLogging(logName, propName=propfile)     # Setup log/properties names
    SlTrace.setProps(newExt=propfile_new_ext, update=propfile_update)
    SlTrace.lg("args: {}\n".format(args))
    
    import difflib
    def diff(file1, file2, req=None):
        """ Compare files
        :file1:  first
        :file2: second
        :req: required string only print lines including this string
        """
        lines1 = open(file1).readlines()
        lines2 = open(file2).readlines()
        for line in difflib.unified_diff(lines1, lines2, fromfile='file1', tofile='file2', lineterm='\n', n=0):
            for prefix in ('---', '+++', '@@'):
                if line.startswith(prefix):
                    break
            else:
                if req is not None and line.find(req) >= 0:
                    print(line, end="")        
            
    player_control = PlayerControl(title="testing")      # Testing
    prop_file_beg = SlTrace.getPropPath()
    ppS = PlayerProps(player_control)
    ppS.push_player_info()
    ppS.player_control.add_new_player()
    ppS.push_player_info()
    ppS.player_control.add_new_player()
    ppS.push_player_info()
    ppS.player_control.add_new_player()
    ppS.save_player_info()
    SlTrace.save_propfile()
    prop_file_new = SlTrace.getPropPathSaved()
    diff(prop_file_beg, prop_file_new, ".name")
    SlTrace.lg("End of Test")
        