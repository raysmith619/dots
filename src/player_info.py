#player_info.py    31Mar2020    crs
""" Player information 
 including list of players 

 
 """
import copy

from select_trace import SlTrace
from select_player import SelectPlayer
from psutil import pid_exists



class PlayerInfo:
    """ Player info for possible restoration
    """
    def __init__(self, player_control, players=None):
        """ Save players info for restoration
        :player_control: overall player control
        :players: dictionary of players (keys ignored)
        """
        self.player_control = player_control
        self.players = {}       # copy for restoration
        if players is not None:
            for player in players.values():
                self.add_player(player)
        

    def __str__(self):
        """ String representation
        """
        string = ""
        for player_id in self.players:
            player = self.players[player_id]
            if string != "":
                string += "\n "
            string += f"    {player_id} {player}"
        return string
    def add_player(self, player):
        """ Add player copy to info
        :player: player to add
        :returns: saved copy of player
        """
        self.players[player.id] = copy.copy(player)
        return self.players[player.id]

    def get_player(self, player_id):
        """ Get/add player to info
        :player_id: id for player
        :returns: player in list
        """
                
        if player_id in self.players:
            player = self.players[player_id]
        else:
            player = SelectPlayer(self.player_control, id=player_id)
            player = self.add_player(player)
        return player
    
    def get_players(self):
        """ Return list of players 
        """
        return self.players.values()

    def has_player(self, id):
        """ Check if we have this player
        :id: player's id
        :returns: True if we have this player
        """
        if id in self.players:
            return True
        
        return False
    
    def get_max_id(self):
        """ Get maximum id of all players
        """
        max_id = None
        for pid in self.players:
            if max_id is None or pid > max_id:
                max_id = pid
        return max_id

    def get_min_id(self):
        """ Get minimum id of all players
        """
        min_id = None
        for pid in self.players:
            if min_id is None or pid < min_id:
                min_id = pid
        return min_id
        
    def change_print(self, prev_player_info, prefix="", incremental=True):
        """ Print change in player information
        :prev_player: previous player information
        :prefix: optional prefix string for  printout
            if present space is added
        :incremental: changes only else all fields
        """
        if prefix != "":
            prefix += " "
        min_id = min(self.get_min_id(), prev_player_info.get_min_id())
        max_id = max(self.get_max_id(), prev_player_info.get_max_id())
        for pl_id in range(min_id, max_id+1):
            if self.has_player(pl_id) and prev_player_info.has_player(pl_id):
                self.player_diff_print(prev_player_info.get_player(pl_id),
                                        self.get_player(pl_id), prefix,
                                        incremental=incremental)
            elif self.has_player(pl_id):
                player = self.get_player(pl_id)
                SlTrace.lg(f"{prefix} added: {player}")
            elif prev_player_info.has_player(pl_id):
                player = prev_player_info.get_player(pl_id)
                SlTrace.lg(f"{prefix} dropped {player}")
                
    def player_diff_print(self, prev_player, player, prefix="", incremental=True):
        """ Show player change
        :prev_player: previous player (state)
        :prefix: optional identifying prefix
        :incremental: only print changes
        """
        if prefix != "":
            prefix += " "
        fields = player.get_player_control_fields()
        for field in fields:
            prev_attr = getattr(prev_player, field)
            attr = getattr(player, field)
            if prev_attr != attr or not incremental:
                SlTrace.lg(f"{prefix}{field}: {prev_attr} => {attr} {player}")
        
        