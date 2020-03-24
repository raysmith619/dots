# C:\Users\raysm\workspace\python\crs_dots\csrc\one_square.py
# On: March 16, 2020 15:57
from dots_commands import *

# one square --playing=Gp,Gm
start_game()        # Required for any game playing commands
lg("Testing one_square.py")
set_playing("Gp,Gm")
set_play(label_name=None, auto=False)
select("h", 1, 3);enter()
select("v", 1, 3);enter()
select("h", 2, 3);enter()
select("v", 1, 4);enter()

