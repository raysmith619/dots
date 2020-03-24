# C:\Users\raysm\workspace\python\crs_dots\src\+_SN_001.py
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
select("h", 1, 1)
mark("h", 1, 1)
select("v", 1, 2)
mark("v", 1, 2)
select("h", 2, 1)
mark("h", 2, 1)
select("v", 2, 1)
mark("v", 2, 1)
select("h", 1, 1)
mark("h", 1, 1)
select("v", 1, 2)
mark("v", 1, 2)
select("h", 2, 1)
mark("h", 2, 1)
select("v", 1, 1)
mark("v", 1, 1)
mark("h", 5, 4)
