# player_prop.py    31Mar2020  crs
""" Player properties handling - loading, storing
Including undo/redo and standard properties

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

import re 

from crs_funs import str2val
from select_trace import SlTrace
from select_error import SelectError
from player_info import PlayerInfo

class PlayerProp:
                            # Index in properties key
    SECT_NAME_IDX = 1       # field index "undo", "redo"
    SECT_NUM_IDX = 2        # position in section group
    SECT_PLAYER_NUM_IDX = SECT_NUM_IDX + 2  # position in player group -sect_num.player.player_num
    PLAYER_NUM_IDX = 1      # player id
     
    def __init__(self, player_control, sect_name=None, control_prefix="player_control"):
        """ get player info from properties
        :player_control: overall player control
        :sect_name: "undo" - undo list(stack)
                    "redo" - redo list(stack)
                    default player list
        :control_prefix: first field in properties file
                    default: "player_control"
        Properties file Pattern:
                ctl_prefix.sect_name.sect_pos.  player...pattern
                           "undo"
                           "redo"
                ctl_prefix. player...pattern
        """
        self.player_control = player_control
        self.control_prefix = control_prefix
        self.sect_name = sect_name
        self.sect_parts = {}        # if not section only one

    def delete(self, player_infos, idx=0):
        """ delete info at idx
        :player_infos: list of player_infos
                default: use self.select_parts
        :idx: index into list
                default: 0
        :returns: deleted info
        """
        if player_infos is None:
            player_infos = self.select_parts
        pi = player_infos[idx]
        del player_infos[idx]
        return pi
            
    def get_player_infos(self, snapshot=None):
        """ 
        :returns: list of PlayerInfo
            in decending order of num to add to stack
        """
        if snapshot is None:
            snapshot = SlTrace.snapshot_properties()
        prop_keys = snapshot.getPropKeys()
        for prop_key in prop_keys:
            prop_fields = prop_key.split(".")
            if prop_fields[0] != self.control_prefix:
                continue                # Not this group
            
            
            if self.sect_name == None:
                self.add_player_prop(prop_fields)
            elif self.sect_name == "undo" or self.sect_name == "redo":
                self.add_sect_prop(prop_fields)

        infos = []
        for key in sorted(self.sect_parts.keys()):
            infos.append(self.sect_parts[key])
        return infos

    
    def add_player_prop(self, prop_fields, snapshot=None, in_section=False):
        """ Add player property to given section
        :prop_fields: list of property keys - whole key
        :snapshot: properties into which we add player
                    default: current properties
        :in_section: in a section (e.g. "undo") default: False
        """
        if snapshot is None:
            snapshot = SlTrace.getDefaultProps()
        if in_section:
            player_idx = PlayerProp.SECT_PLAYER_NUM_IDX
            sect_num = prop_fields[PlayerProp.SECT_NUM_IDX]
        else:
            player_idx =  PlayerProp.PLAYER_NUM_IDX
            sect_num = None
        player_info = self.get_sect_part(sect_num)
        player_id_str = prop_fields[player_idx]
        if re.match(r'\d+$', player_id_str) is None:
            return          # Not  a player num
        
        player_id = int(player_id_str)
        player = player_info.get_player(player_id)  # Create player, if not there
        prop_key = ".".join(prop_fields)
        
        player_attr = prop_fields[player_idx+1]     # Just after id
        prop_val = snapshot.getProperty(prop_key, None)
        if player_attr == "move":
            player_attr = "position"
        if not hasattr(player, player_attr):
            raise SelectError(f"Unrecognized player attribute {player_attr} in {prop_val}")
        player_val = getattr(player, player_attr)
        try:
            property_value = str2val(prop_val, player_val)
        except:
            SlTrace.lg(f"Can't convert {prop_val} in prop field {player_attr} to type: {type(player_val)}")
            raise SelectError(f"Bad Input: {'.'.join(prop_fields)}")
        setattr(player, player_attr, property_value)
        if player_attr == "color":
            player.icolor = player.color
        elif player_attr == "color_bg":
            player.icolor2 = player.color_bg

    def add_sect_prop(self, prop_fields):
        """ Add section properties
        Creates player entry if not present
        :prop_fields: list of property keys - whole key
        """
        if prop_fields[PlayerProp.SECT_NAME_IDX] != self.sect_name:
            return      # Not our section
        
        if prop_fields[PlayerProp.SECT_NUM_IDX].startswith("__"):
            return      # Internal field
        
        self.add_player_prop(prop_fields, in_section=True)
        
            
    def get_sect_part(self, sect_num):
        """ Find, or create section part
        :sect_num: section part number string
                default: create new section part 1
        :returns: section part
        """
        if sect_num is None:
            sect_n = 1           # Arbitrary
        else:
            sect_n = int(sect_num)
        if sect_n in self.sect_parts:
            sect_part = self.sect_parts[sect_n]
        else:
            sect_part = PlayerInfo(self.player_control)
            self.sect_parts[sect_n] = sect_part
        return sect_part

    def save_props(self, player_infos, stack_count=None):
        """ Save infos in properties 
            to be saved by normal properties saving
            Sets sect numbers to correspond to stack list position
            First removes properties of the form:
                    {self.control_prefix}\.{self.sect_name}\.\d+\.
                      or (if self.sect_name is None)
                    {self.control_prefix}\.\d+\.
        :prop_infos: PlayerInfo or list, most recent == last, position == 1
        :stack_count: current stack level, used for stack comparisons
        """

        if not isinstance(player_infos, list):
            player_infos = [player_infos]
        self.remove_props()
        if stack_count is not None:
            after_len = len(f"0.player.")
            bk = self.get_base_key(0)[:-after_len]      # less "undo.0."
            prop_key = f"{bk}__STACK_COUNT"       # To facilitate stack comparison
            SlTrace.setProperty(prop_key, stack_count)
        for n, player_info in enumerate(reversed(player_infos),start=1):
            base_key = self.get_base_key(n)
            self.save_prop_player_info(player_info, base_key=base_key)

    def remove_props(self):
        """ Remove all properties for 
        :player_infos:
        """
        base_key = self.get_base_key(include_num=False)
        SlTrace.lg(f"remove_props: base_key={base_key}", "player_prop")
        if self.sect_name is None:
            base_pat = base_key + r'\d+'
            base_match = re.compile(base_pat)
            SlTrace.lg(f"base_pat={base_pat}", "player_prop")
        prop_keys = SlTrace.getPropKeys()
        for prop_key in prop_keys:
            if prop_key.startswith(base_key):
                if self.sect_name is None:
                    m = base_match.match(prop_key)
                    if m is None:
                        continue            # Not base: ...nnn
                    
                SlTrace.lg(f"remove_props: key={prop_key}", "player_prop")
                SlTrace.deleteProperty(prop_key)

    def get_base_key(self, sect_num=None, include_num=True):
        """ Generate base_key for sect/player_info
        :sect_num: section number
        :include_num" iff True include section number
                    default: True
        """
        if self.sect_name is None:
            base_key = f"{self.control_prefix}."
        else:
            base_key = f"{self.control_prefix}.{self.sect_name}."
            if include_num:
                base_key += f"{sect_num}.player."
        return base_key
                
    def save_prop_player_info(self, player_info, base_key=None):
        """ Save PlayerInfo in properties
        :n: list number
        :player_info: PlayerInfo object
        """
        for player in player_info.players.values():            
            self.save_prop_player(player, base_key=base_key)
        
    def save_prop_player(self, player, base_key=None):
        """ Save player's info
        :player: player to save
        :base_key: prop_key preceeding player's id
        """
        player_id = player.id 
        player_fields = self.player_control.get_player_control_fields()
        for field in player_fields:
            prop_key = f"{base_key}{player_id}.{field}"
            prop_val = str(getattr(player, field))
            SlTrace.lg(f"save_prop_player: key={prop_key} val={prop_val}", "player_prop")
            SlTrace.setProperty(prop_key, prop_val)

            
    
if __name__ == "__main__":
    import argparse
    
    from sc_player_control import PlayerControl
    
    propfile = "player_prop_test"
    propfile_new_ext = "prop_out"
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
            
    logName = "prop_test"
    SlTrace.setupLogging(logName, propName=propfile)     # Setup log/properties names
    SlTrace.setProps(newExt=propfile_new_ext, update=propfile_update)
    SlTrace.lg("args: {}\n".format(args))
    player_control = PlayerControl(title="testing")      # Testing
    
    def get_player_infos(player_control, sect_name=None):
        """ return Player Infos from properties list
        :sect_name: undo, redo or None for base
        :returns: PlayerInfo list
        """
        pi = PlayerProp(player_control, sect_name=sect_name)
        return pi, pi.get_player_infos()
     
    pi, pinfos = get_player_infos(player_control)
    SlTrace.lg("Infos:")
    for info in pinfos:
        SlTrace.lg(str(info))
    SlTrace.lg("deleting infos")
    pi.delete(pinfos, 0)
    SlTrace.lg("Saving infos")
    pi.save_props(pinfos)

    
    SlTrace.lg("Getting undo")
    undo_pi, undo_pinfos = get_player_infos(player_control, sect_name="undo")    
    SlTrace.lg("undo Infos:")
    for i in range(len(undo_pinfos)):
        info = undo_pinfos[i]
        SlTrace.lg(f"{i+1}: {info}")
    SlTrace.lg("deleting undo")
    undo_pi.delete(undo_pinfos, 0)
    SlTrace.lg("Saving undo")
    undo_pi.save_props(undo_pinfos)
    
    SlTrace.lg("Getting redo")
    redo_pi, redo_pinfos = get_player_infos(player_control, sect_name="redo")    
    SlTrace.lg("redo Infos:")
    for i in range(len(redo_pinfos)):
        info = redo_pinfos[i]
        SlTrace.lg(f"{i+1}: {info}")
        SlTrace.lg("deleting redo")
    redo_pi.delete(redo_pinfos, 0)
    SlTrace.lg("Saving redo")
    redo_pi.save_props(redo_pinfos)

    


    
    SlTrace.lg("End of Test")
    