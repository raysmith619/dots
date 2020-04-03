#player_info.py    31Mar2020    crs
""" Player information 
 including list of players 

 
 """
import copy
from select_player import SelectPlayer

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