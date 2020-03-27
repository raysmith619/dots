# move_testing.py
# On: March 23, 2020
"""
Test how well commands are snapshot
"""
from dots_commands import *

set_playing("Gp,W")
set_play(label_name="Grampy", name="Grampy",label="Gp",playing=True,
        position=1,color="blue",color_bg="light blue",voice=False,
        help_play=False,pause=0.0,auto=False,level=2,steven=0.0)
set_play(label_name="Willow",name="Willow2",label="W2",playing=True,
        position=2,color="red",color_bg="light yellow",voice=False,
        help_play=False,pause=0.0,auto=True,level=2,steven=0.0)
start_game()
mark("h", 1, 1)
mark("v", 1, 2)
mark("h", 2, 1)
play_move()             # Play next game move e.g. auto/manual
game_check("v", 1, 1)   # Assumed move
game_check("sq", 1,1)   # Check that square was awarded

