# C:\Users\raysm\workspace\python\crs_dots\csrc\one_square.py
# On: March 16, 2020 15:57
from dots_commands import *

# one square --playing=Gp,Gm
set_playing("Gp,Gm")
set_play(label_name=None, auto=False)
start_game()        # Required for any game playing commands
lg("Testing one_square.py")
mark("h", 1, 3)
mark("v", 1, 3)
mark("h", 2, 3)
#mark("v", 1, 4)
lg("Checking Grammy's response to square opportunity")
set_play(label_name='Gm', auto=True, level=2) # Grammy should complete the square


