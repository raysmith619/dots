# C:\Users\raysm\workspace\python\crs_dots\src\one_edge_shy_2_SN_002.py
# On: March 21, 2020

from dots_commands import *

set_playing("Gp,Gm")
set_play(label_name="Grampy", name="Grampy", label="Gp", playing=True, 
        position=1, color="blue", color_bg="light blue", voice=False, 
        help_play=False, pause=0.0, auto=False, level=2, steven=0.0)
set_play(label_name="Grammy", name="Grammy", label="Gm", playing=True, 
        position=2, color="red", color_bg="light yellow", voice=False, 
        help_play=False, pause=0.0, auto=True, level=2, steven=0.0)
start_game()
select("h", 1, 3)
mark("h", 1, 3)
select("v", 1, 3)
mark("v", 1, 3)
select("h", 2, 3)
mark("h", 2, 3)
select("v", 1, 4)
mark("v", 1, 4)
select("h", 6, 2)
mark("h", 6, 2)
select("h", 6, 3)
mark("h", 6, 3)
select("v", 5, 3)
mark("v", 5, 3)
select("h", 5, 3)
mark("h", 5, 3)
