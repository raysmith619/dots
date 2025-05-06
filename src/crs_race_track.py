# crs_race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
import os
import sys
import re

from tkinter import *    
from tkinter import filedialog
import argparse
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError
from block_window import BlockWindow
from block_panel import BlockPanel
from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,SurfaceType
from road_straight import RoadStraight
from race_track import RaceTrack
from road_bin_setup import RoadBinSetup
from car_bin_setup import CarBinSetup
from road_track_setup import RoadTrackSetup
from road_block import RoadBlock
from road_turn import RoadTurn
from block_arc import BlockArc
from position_window import PositionWindow
from race_control_window import RaceControlWindow

src_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(src_dir)
SlTrace.lg(f"Using work directory:{src_dir}")

SlTrace.setFlags("short_points,starter_track,down"
                 + ",front_road"
                 + ",add_block,mouse_right_info")

width = 600     # Window width
height = width  # Window height
rotation = None # No rotation
maximum_speed = 20  # Maximum car speed mph
minimum_speed = 5  # Maximum car speed mph
maximum_speed = 10.
minimum_speed = 1.
ncar = 3
turn_speed = 2.
pos_x = None
pos_y = None
parser = argparse.ArgumentParser()
dispall = False      # Display every change
track_file = r'..\crsrc\double_circled.crsrc'
starter_track = True
###starter_track = False
update_interval = .02
bind_key = True             # Key binding enabled default: True
race_track_src_dir = "../crsrc"  # Race track source directory
parser.add_argument('--bind_key', '-bk', type=bool, dest='bind_key', default=starter_track)
parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
parser.add_argument('--maximum_speed=', '-mas', type=float, dest='maximum_speed', default=maximum_speed)
parser.add_argument('--minimum_speed=', '-mis', type=float, dest='minimum_speed', default=maximum_speed)
parser.add_argument('--ncar=', '-nc', type=int, dest='ncar', default=ncar)
parser.add_argument('--turn_speed=', '-tus', type=float, dest='turn_speed', default=turn_speed)
parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
parser.add_argument('--track_file', '-tf', dest='track_file', default=track_file)
parser.add_argument('--starter_track', '-st', type=bool, dest='starter_track', default=starter_track)
parser.add_argument('--update_interval', '-ui', type=float, dest='update_interval', default=update_interval)
args = parser.parse_args()             # or die "Illegal options"

bind_key = args.bind_key
width = args.width
height = args.height
pos_x = args.pos_x
pos_y = args.pos_y
maximum_speed = args.maximum_speed
minimum_speed = args.minimum_speed
ncar = args.ncar
rotation = args.rotation
starter_track = args.starter_track
track_file = args.track_file
update_interval = args.update_interval

SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
SlTrace.lg("args: %s\n" % args)

# Program exit control
def pgm_exit():
    ###ActiveCheck.clear_active()  # Disable activities
    quit()
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

def play_exit():
    """ End playing
    Called from Window control
    """
    ###ActiveCheck.clear_active()  # Disable activities
    pgm_exit()


mw = Tk()        
app = BlockWindow(master=mw,
                title="My Race Track",
                pgmExit=play_exit,
                cmd_proc=True,
                cmd_file=None,
                arrange_selection=False,
                game_control=None
                )
frame = Frame(app, width=width, height=height, bg="", colormap="new")
frame.pack(fill=BOTH, expand=YES)
canvas = Canvas(frame, width=width, height=height)
canvas.pack(fill=BOTH, expand=YES)
BlockBlock.set_canvas(canvas)           # Set for auxiliary routines, e.g., mkpoint
th_width = 1.
th_height = 1.
position = None
if pos_x is not None or pos_y is not None:
    if pos_x is None:
        pos_x = 0.
    if pos_y is None:
        pos_y = 0.
    position = Pt(pos_x, pos_y)

tR = RaceTrack(mw=mw, canvas=canvas, width=th_width, height=th_height,
               position=position,
               bind_key=bind_key,
               cv_width=width, cv_height=height,
               rotation=rotation,
               maximum_speed=maximum_speed,
               minimum_speed=maximum_speed,
               ncar=ncar,
               turn_speed=turn_speed,
               update_interval=update_interval)
tR.display()
pos_ctl = PositionWindow("Part Positioning",
                         change_control_proc=tR.pos_change_control_proc)    
race_ctl = RaceControlWindow("Race Control",
                         command_control_proc=tR.race_control_proc)    
road_bin = tR.get_road_bin()
RoadBinSetup(road_bin)
select_road = True
if select_road:
    road = road_bin.get_entry(0)            # Select first entry in road_bin
    tR.set_selected(road.id)
    tR.save_bin_selection(road)
car_bin = tR.get_car_bin()
CarBinSetup(car_bin)

if starter_track:
    road_track = tR.get_road_track()
    RoadTrackSetup(road_track, race_track_file=track_file)
    tR.set_reset()



def save_track_proc():
    """ Save current track state
    """
    SlTrace.lg("save_track_proc")
    filename =  filedialog.asksaveasfilename(
        initialdir = "../crsrc",
        title = "Track Files",
        filetypes = (("track files","*.crsrc"),
                     ("all files","*.*")))
    if not re.match(r'^.*\.[^.]+$', filename):
        filename += ".crsrc"
    
    SlTrace.lg("filename %s" % filename)
    track_file = filename
    tR.save_track_file(track_file)
    
app.set_file_save_proc(save_track_proc)


def load_track_proc():
    """ Load current track state
    """
    SlTrace.lg("load_track_proc")
    filename =  filedialog.askopenfilename(
        initialdir = "../crsrc",
        title = "Track Files",
        filetypes = (("track files","*.crsrc"),
                     ("all files","*.*")))
    if not re.match(r'^.*\.[^.]+$', filename):
        filename += ".crsrc"
    
    SlTrace.lg("filename %s" % filename)
    
    track_file = filename
    tR.load_track_file(track_file)


app.set_file_load_proc(load_track_proc)
tR.enable_window_resize()

###RoadBinSetup(road_track)
tR.display()


mainloop()