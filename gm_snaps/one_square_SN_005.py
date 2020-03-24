# C:\Users\raysm\workspace\python\crs_dots\gm_snaps\one_square_SN_005.py
# On: March 22, 2020

from dots_commands import *

set_playing("Gp,Gm")
set_play(label_name="Grampy", name="Grampy", label="Gp", playing=True, 
        position=1, color="blue", color_bg="light blue", voice=False, 
        help_play=False, pause=0.0, auto=False, level=2, steven=0.0)
set_play(label_name="Grammy", name="Grammy", label="Gm", playing=True, 
        position=2, color="red", color_bg="light yellow", voice=False, 
        help_play=False, pause=0.0, auto=True, level=2, steven=0.0)
start_game()
