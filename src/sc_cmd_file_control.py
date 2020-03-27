# sc_cmd_file_control.py
"""
Command File/Input Control
Facilitates Command File/Input Running
"""
import re
import os
import time
from tkinter import *
from tkinter import filedialog

from select_error import SelectError
from select_trace import SlTrace
from select_control_window import SelectControlWindow
from select_command_stream import SelectCommandStream
from select_stream_command import SelectStreamCmd    
    
    
    
class SelectCommandFileControl(SelectControlWindow):

    CONTROL_NAME_PREFIX = "command_file_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    snapshot_suffix = "_SN_"
    snapshot_ndig = 3         # Number of digits

    def __init__(self, *args,
                 title="File Control",
                 control_prefix=CONTROL_NAME_PREFIX,
                 run=False,
                 run_cmd=None,
                 paused=True,
                 new_board=None,
                 in_file=None,
                 save_as_file=None,
                 save_as_dir=None,
                 src_file = None,
                 src_dir=None,
                 src_lst=False,
                 stx_lst=False,
                 lst_file_name=None,
                 cmd_execute=None,
                 debugging=False,
                 display=True,
                 **kwargs
                 ):
        """ Initialize subclassed SelectControlWindow singleton
        """
        self.run_cmd = run_cmd
        self.save_as_file = save_as_file
        self.save_as_dir = save_as_dir
        self.src_dir = src_dir
        self.src_lst = src_lst
        self.stx_lst = stx_lst
        self.src_file_name = src_file
        self.run = run
        self.new_board = new_board
        self.cmd_execute = None
        self.running = False
        self.paused = paused
        self.debugging = debugging
        self.step_pressed = False
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = False
        self.is_to_line_nos = []
        self.is_to_line_pats = []   # Compiled rex
        self.stop_pressed = False
        self.command_stream = None
        super().__init__(*args,
                      title=title, control_prefix=control_prefix,
                      **kwargs)    
        """ Player attributes
        :title: window title
        :in_file: Opened input file handle, if one
        :src_file: source file name .py for python
                        else .csrc built-in language
        :open: Open source file default: True - open file on object creation
        :run: run file after opening
                default: False
        :run_cmd: command to run when run button hit
                default: self.run
        :src_dir: default src directory
                default: "csrc"
        :src_lst: List src as run
                    default: No listing
        :stx_lst: List expanded commands as run
                    default: No listing
        :lst_file_name: listing file name
                default: base name of src_file
                        ext: ".clst"
        :cmd_execute: function to be called to execute command
                        when running file default: none
        :display: True = display window default:True
        """
        if title is None:
            title = "Command Stream Control"
        self.title = title
        if src_file is not None:
            self.set_ctl_val("input.src_file_name", src_file)
        if self.play_control is not None:
            self.set_command_stream()
        self.control_display()

        if self.run:
            self.run_file()


    def set_command_stream(self):
        """ Setup links between command control
        and stream
        """
        self.command_stream = SelectCommandStream(
                execution_control=self,
                src_file=self.src_file_name,
                src_dir=self.src_dir,
                src_lst=self.src_lst,
                stx_lst=self.stx_lst,
                )
        self.command_stream.set_play_control(self.play_control)
        self.play_control.set_cmd_stream(self.command_stream)
        self.command_stream.set_cmd_stream_proc(self.play_control.cmd_stream_proc)
    
    def add_event_queue(self, proc):
        """ Add processing function to
        processing queue
        :proc: process to be called at appropriate time
        """
        if self.play_control is not None:
            return self.play_control.add_event_queue(proc)
        
        SlTrace.lg(f"add_event_queue ignored because no play_control")
                        
    def control_display(self):
        """ Setup control form
        entry / modification
        """
        super().control_display()       # Do base work        
        inputs_frame = Frame(self.top_frame)
        inputs_frame.pack()
        
        base_field_name = "input"
        field_name = "src_dir_name"
        dir_frame = Frame(inputs_frame)
        dir_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(dir_frame, base_field_name, title="")
        if self.src_dir is None:
            self.src_dir = "../csrc"
        self.src_dir = os.path.abspath(self.src_dir)
        self.set_entry(field=field_name, label="Dir", value=self.src_dir, width=60)
        self.set_button(field=field_name + "_search", label="Search", command=self.src_dir_search)

        field_name = "src_file_name"
        file_frame = Frame(inputs_frame)
        self.set_fields(file_frame, base_field_name, title="")
        prop_key = f"{base_field_name}.{field_name}"
        if self.src_file_name is not None:
            self.set_prop_val(prop_key, self.src_file_name)
        else:
            self.src_file_name = self.get_prop_val(prop_key, "")
        file_name = self.src_file_name
        self.set_ctl_val(prop_key, file_name)
        if os.path.isabs(file_name):
            dir_name = os.path.dirname(file_name)   # abs path => set dir,name
            self.set_ctl_val("input.dir_name", dir_name)    # reset
            file_name = os.path.basename(file_name)
        self.set_entry(field=field_name, label="Src File", value=file_name, width=20)
        self.set_button(field=field_name + "_search", label="Search", command=self.src_file_search)

        save_as_frame = Frame(self.top_frame)
        save_as_frame.pack()
        
        base_field_name = "save_as"
        field_name = "save_as_dir"
        save_as_dir_frame = Frame(save_as_frame)
        save_as_dir_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(save_as_dir_frame, base_field_name, title="Save Game")
        prop_key = f"{base_field_name}.{field_name}"
        self.save_as_dir_key = prop_key
        if self.save_as_dir is None:
            self.save_as_dir = "../gm_snaps"
        self.save_as_dir = os.path.abspath(self.save_as_dir)
        self.set_entry(field=field_name, label="Dir", value=self.save_as_dir, width=60)
        self.set_button(field=field_name + "_search", label="Search", command=self.save_as_dir_search)

        field_name = "save_as_file"
        save_as_file_frame = Frame(save_as_frame)
        self.set_fields(save_as_file_frame, base_field_name, title="")
        self.save_as_file_key = prop_key = f"{base_field_name}.{field_name}"
        if self.save_as_file is not None:
            self.set_prop_val(prop_key, self.save_as_file)
        else:
            self.save_as_file = self.get_prop_val(prop_key, "")
        self.set_ctl_val(prop_key, file_name)
        if file_name.startswith("+"):
            pass            # Leave special case alone
        elif file_name == "":
            pass            # Ask for explicit file
        elif os.path.isabs(file_name):
            dir_name = os.path.dirname(file_name)   # abs path => set dir,name
            self.set_ctl_val(f"{base_field_name}.save_as_dir", dir_name)    # reset
            file_name = os.path.basename(file_name)
        self.set_entry(field=field_name, label="Save Game File", value=file_name, width=20)
        self.set_button(field=field_name + "_save", label="SAVE", command=self.game_save_as)


        
        self.set_vert_sep(self.top_frame)
        field_name = "running"
        run_frame1 = Frame(self.top_frame)
        run_frame1.pack(side="top", fill="x", expand=True)
        self.set_fields(run_frame1, field_name, title="Running")
        self.set_button(field="Run", label="Run", command=self.run_button)
        self.set_check_box(field="paused", label="paused", value=self.paused)
        self.set_check_box(field="src_lst", label="List Src", value=self.stx_lst)
        self.set_check_box(field="stx_lst", label="List Exp", value=self.stx_lst)
        self.set_entry(field="cmd_delay", label="cmd delay", value = .5, width=5)
        self.set_button(field="stop", label="Stop", command=self.stop_button)
        
        run_frame2 = Frame(self.top_frame)
        run_frame2.pack(side="top", fill="x", expand=True)
        self.set_fields(run_frame2, field_name, title="")
        self.set_sep()
        self.set_check_box(field="new_game", label="New Game", value=False)
        self.set_check_box(field="new_board", label="New Board", value=False)
        self.set_sep()
        self.set_check_box(field="loop", label="Loop", value=False)
        self.set_entry(field="loop_time", label="Loop time", value=5., width=5)
        
        self.set_vert_sep(self.top_frame)
        field_name = "debugging"
        debugging_frame = Frame(self.top_frame)
        debugging_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(debugging_frame, field_name, title="Debugging")
        self.set_button(field="step", label="Step", command=self.step_button)
        self.set_button(field="to_end", label="To End", command=self.cont_to_end_button)
        self.set_button(field="to_line", label="To Line", command=self.cont_to_line_button)
        self.set_entry(field="line1", label="lines", value = "", width=10)
        self.set_entry(field="line2", label="", value = "", width=10)
        self.set_entry(field="line3", label="", value = "", width=10)


    def step_button(self):
        """ Debugging step button
        """
        SlTrace.lg("Step Button")
        self.step_pressed = True
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = False
        if not self.is_running():
            self.start_continue()

    def get_snapshot_name(self, orig_name):
        """ Compute, hopefully unique snapshot name
        :orig_name: orginal name with or without suffix
                    Adds suffix before .extension if one
                    No check currently on saved files
        """
        snapshot_dir = os.path.dirname(orig_name)
        basename = os.path.basename(orig_name)
        mext = re.match(r'^(.*)(\.[^.]+)$', basename)
        if mext:
            basename_beg = mext.group(1)
            basename_ext = mext.group(2)
        else:
            basename_beg = basename
        files = os.listdir(snapshot_dir)
        snfiles = [file for file in files if file.startswith(basename_beg + self.snapshot_suffix)]
        max_num = 0
        fpat_str = f'^.*{self.snapshot_suffix}(' + r'\d' * self.snapshot_ndig + r')\.[^.]+$'
        mpat = re.compile(fpat_str)
        for file in snfiles:
            mfile = mpat.match(file)
            if mfile:
                num = int(mfile.group(1))
                if num > max_num:
                    max_num = num
        max_num += 1            # Go to next larger number
        snapshot_add_str = (f"{self.snapshot_suffix}"
                            f"{max_num:0{self.snapshot_ndig}}")
        sn_name = basename_beg + snapshot_add_str            
        if mext:
            sn_name += basename_ext
        sn_name = os.path.join(snapshot_dir, sn_name)    
        return sn_name
 
  
 
    def is_debugging(self):
        """ Ck if we are debugging input stream
        """
        return self.debugging

 
    def is_running(self):
        """ Ck if we are running an input stream
        """
        return self.running
       
        
    def is_step(self):
        """ Are we doing a step
        """
        return self.step_pressed
        
        
        
        
    def is_to_line(self, cur_lineno=None, src_lines=None):
        """ Check if continue to line pressed
        """
        
        if not self.cont_to_line_pressed or cur_lineno is None:
            return False
        
        for lno in self.is_to_line_nos:
            if cur_lineno == lno:
                self.cont_to_line_pressed = False
                return True
        
        if src_lines is None:
            return False
        
        line_text = ""
        if cur_lineno > 0 and cur_lineno < len(src_lines):
            line_text = src_lines[cur_lineno-1]
        
        for pat in self.is_to_line_pats:
            sea = pat.search(line_text)
            if sea is not None:
                match_str = sea.group(0)
                SlTrace.lg("%s" % match_str)
                self.cont_to_line_pressed = False
                return True
                
        return False

    

    def wait_for_step(self):
        """ Wait for next user step/continue/stop command
        """
        self.step_pressed = False       # Wait for next
        while True:
            if (self.step_pressed
                    or self.cont_to_end_pressed
                    or self.cont_to_line_pressed
                    or self.stop_pressed):
                return
            if self.mw is not None and self.mw.winfo_exists():
                self.mw.update()
            time.sleep(.01)
            self.play_control.event_check()     # Process any pending events
        


    def stop_button(self):
        """ Stop file run
        """
        self.add_event_queue(self.stop_button_1)
        
    def add_event_queue_1(self):
        SlTrace.lg("Stop Button")
        self.stop_pressed = True


    def cont_to_end_button(self):
        """ Debugging continue to end button
        """
        self.add_event_queue(self.cont_to_end_button_1)
        
    def cont_to_end_button_1(self):
        SlTrace.lg("TBD")
        self.step_pressed = False
        self.cont_to_end_pressed = True
        self.cont_to_line_pressed = False
        if not self.is_running():
            self.start_continue()


    def cont_to_line_button(self):
        """ Debugging continue to line button
        """
        self.add_event_queue(self.cont_to_line_button_1)
        
    def cont_to_line_button_1(self):
        SlTrace.lg("Continue to Line")
        self.step_pressed = False
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = True
        self.set_vals()     # Collect edits
        self.is_to_line_nos = []
        self.is_to_line_pats = []   # Compiled rex

        value = self.get_val("debugging.line1", "")
        if value != "":
            if re.match(r'[1-9]\d*', value):
                self.is_to_line_nos.append(int(value))
            else:
                self.is_to_line_pats.append(re.compile(value))

        value = self.get_val("debugging.line2", "")
        if value != "":
            if re.match(r'[1-9]\d*', value):
                self.is_to_line_nos.append(int(value))
            else:
                self.is_to_line_pats.append(re.compile(value))

        value = self.get_val("debugging.line3", "")
        if value != "":
            if re.match(r'[1-9]\d*', value):
                self.is_to_line_nos.append(int(value))
            else:
                self.is_to_line_pats.append(re.compile(value))
        
        if not self.is_running():
            self.start_continue()


    def save_as_file_search(self):
        start_dir = self.save_as_dir
        filename =  filedialog.askopenfile("r",
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("all files","*.*"), ("csrc files","*.csrc")))
        if filename is None:
            return
        
        fullname = filename.name
        dir_name = os.path.dirname(fullname)
        base_name = os.path.basename(fullname)
        self.save_as_dir = dir_name
        self.save_as_file = base_name
        self.set_ctl_val("input.save_as_dir", dir_name)
        self.set_ctl_val("input.save_as_file", base_name)
        filename.close()


    def save_as_dir_search(self):
        start_dir = self.save_as_dir
        filedir =  filedialog.askdirectory(
            initialdir = start_dir,
            title = "Save As Dir")
        name = filedir
        self.save_as_dir = name
        self.set_ctl_val("input.save_as_dir", name)


    def src_dir_search(self):
        start_dir = self.src_dir
        filedir =  filedialog.askdirectory(
            initialdir = start_dir,
            title = "Select dir")
        name = filedir
        self.src_file_name = name
        self.set_ctl_val("input.src_dir_name", name)


    def game_save_as(self):
        initial_dir = self.get_val_from_ctl(self.save_as_dir_key)
        if initial_dir == "":
            initial_dir = os.path.abspath("../gm_snaps")
        src_file = self.get_val_from_ctl("input.src_file_name")
        game_save_file = self.get_val_from_ctl(self.save_as_file_key)
        if game_save_file is None or game_save_file == "":
            file_name =  filedialog.asksaveasfilename(
                initialdir = initial_dir,
                title = "Game State Files",
                filetypes = (("game files","*.py"),
                             ("all files","*.*")))
        elif game_save_file.startswith("+"):
            game_path = os.path.join(initial_dir, src_file)
            file_name = self.get_snapshot_name(os.path.abspath(game_path))
        else:
            file_name = game_save_file
        if not re.match(r'^.*\.[^.]*$', file_name):
            file_name += ".py"
        SlTrace.lg(f"save game as filename {file_name}")

        if file_name is not None:
            if not os.path.isabs(file_name):
                src_dir = self.get_val_from_ctl("input.src_dir_name")
                file_name = os.path.join(src_dir, file_name)
            self.play_control.save_game_file(file_name)


    def src_file_search(self):
        start_dir = self.src_dir
        filename =  filedialog.askopenfile("r",
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("all files","*.*"), ("csrc files","*.csrc")))
        if filename is None:
            return
        
        fullname = filename.name
        dir_name = os.path.dirname(fullname)
        base_name = os.path.basename(fullname)
        self.src_dir = dir_name
        self.src_file_name = base_name
        self.set_ctl_val("input.src_dir_name", dir_name)
        self.set_ctl_val("input.src_file_name", base_name)
        filename.close()
            
            
    def run_button(self):
        """ Called when our button is pressed
        """
        SlTrace.lg("run_button")
        self.start_continue()
        
        
    def start_continue(self):
        """ Start/continue program running
        """
        self.add_event_queue(self.start_continue_1)
        
    def start_continue_1(self):
        """ continue
        """
        self.running = True
        
        while True:
            self.set_vals()
            new_board = self.get_val("running.new_board")
            if new_board:
                if self.play_control is not None:
                    self.play_control.reset()
            if self.get_val("running.new_game"):
                self.clear_game_moves()
                ###self.new_game()
            src_file = self.get_val_from_ctl("input.src_file_name")
            if not os.path.isabs(src_file):
                src_dir = self.get_val_from_ctl("input.src_dir_name")
                if src_dir is not None and src_dir != "":
                    src_file = os.path.join(src_dir, src_file)
            self.play_control.run_cmd()
            if self.play_control is not None:
                src_lst = self.get_val_from_ctl("running.src_lst")
                stx_lst = self.get_val_from_ctl("running.stx_lst")
                res = self.play_control.run_file(src_file=src_file, src_lst=src_lst, stx_lst=stx_lst)
            else:
                res = self.run_file(src_file)
                
            if not res:
                SlTrace.lg("run file failed")
                return False       # Quit if run fails
            
            self.play_control.first_time = False        # Assume file did game start if wanted
            paused =  self.get_val_from_ctl("running.paused")
            if paused:
                self.running = False
                self.play_control.pause_cmd()
                return True
            
            is_looping = self.get_val("running.loop") 
            if is_looping:
                loop_time = self.msec(self.get_val("running.loop_time"))
                SlTrace.lg("Looping after %d msec" % loop_time)
                self.mw.after(loop_time)
                continue
            self.running = False
            return True

    
    def run_file(self, src_file=None, cmd_execute=None, src_lst=None, stx_lst=None):
        """ Run stream command file
        :src_file: source file name (absolute path or relative)
            If no extension: search for none, then supported extensions(.csrc, .py)
        :cmd_execute: function to call for each stcmd
        :src_lst: if present, set src listing option
        :stx_lst: if present, set expanded listing option
        :returns: True iff OK run
        """
        if cmd_execute is not None:
            self.cmd_execute = cmd_execute
        if self.command_stream is None:
            self.set_command_stream()
        self.command_stream.open(src_file=src_file, src_lst=src_lst, stx_lst=stx_lst)
        while True:
            stcmd = self.get_cmd()
            if stcmd is None:
                break
            if stcmd.is_type(SelectStreamCmd.EXECUTE_FILE):
                if not self.procFile(src_file=src_file):
                    raise SelectError("Error in procFile")
                continue        # Next cmd should be EOF
            cmd_delay =  self.msec(self.get_val("running.cmd_delay"))
            self.mw.after(cmd_delay)
            if stcmd.is_type(SelectStreamCmd.EOF):
                break
            if self.cmd_execute is not None:
                if not self.cmd_execute(stcmd):
                    raise SelectError("%s execute failure" % stcmd)

        return True
        

    def reset(self, src_file=None):
        """ Reset stream to allow traversing again
            closes current file, if any, reopen
            :src_file: new file name, if present default: use current name
        """
        if self.command_stream is not None:        
            self.command_stream.reset(src_file=src_file)

    def reset_board(self):
        """ Reset game board to pre-game
        """
        if self.play_control is not None:
            self.play_control.reset()

    def set_play_control(self, play_control):
        """ Connect command stream processing to game control
        :play_control:  game control
        """
        self.play_control = play_control        # Local reference

    def set(self):
        self.set_vals()
        if self.set_cmd is not None:
            self.set_cmd(self)


    def set_cmd_stream_proc(self, cmd_stream_proc):
        """ Connect command stream processing to command processing
        :play_control:  game control
        """
        self.command_stream.set_cmd_stream_proc(cmd_stream_proc)



    def msec(self, time_sec):
        """ Convert time in seconds to time in msec
        :time_sec: time in seconds
        """
        time_msec = int(1000*time_sec)
        return time_msec
    

    def is_eof(self):
        """ Are we at end of file?
        """
        if self.command_stream is None:
            return True         # Treat as eof
        
        return self.command_stream.is_eof()
    
    def set_eof(self, eof=True):
        """ Set as eof
        """
        self.command_stream.set_eof(eof=eof)
        
        
    def is_src_lst(self):
        """ Are we listing source lines?
        """
        return self.command_stream.is_src_lst()

    def set_src_lst(self, lst=True):
        """ Are we listing source lines?
        :lst: Listing default: True
        """
        self.command_stream.set_src_lst(lst=lst)

    def is_stx_lst(self):
        """ Are we listing executing commands?
        """
        return self.command_stream.is_stx_lst()

    def set_stx_lst(self, lst=True):
        """ Are we listing execution lines?
        :lst: Listing default: True
        """
        self.command_stream.set_stx_lst(lst=lst)



    """ Control functions for game control
    """
    def clear_game_moves(self):
        if self.play_control is not None:
            self.play_control.clear_game_moves()

    def new_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.new_game("New Game")

    def reset_score(self):
        """ Reset multi-game scores/stats, e.g., games, wins,..
        """
        if self.play_control is not None:
            self.play_control.reset_score()

    
    def stop_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.stop_game("Stop Game")


    def run_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.run_cmd()

    def pause_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.pause_cmd()



    def destroy(self):
        """ Destroy window resources
        """
        if self.mw is not None:
            self.mw.destroy()
        self.mw = None


    
    
    def get_cmd(self):
        """ Get next command: word [[, ] word]* [EOL|;]
         ==> cmd.name == first word
             cmd.args == subsequent words
        :returns: cmd, None on EOF
        """
        return self.command_stream.get_cmd()




    def get_src_file_path(self):
        """ Get current source file path
        """
        return self.command_stream.get_src_file_path()
    

    
    def procFile(self, src_file=None, exe_command=None, src_lst=None, stx_lst=None):
        """
        Process input files:
        :src_file: file input name default use stream_command's
            .py ==> python script
            .bwif ==> BlockWorld scrip
            default: use self.src_file_name
        :exe_command: command to execute for each stream command
        """
        return self.command_stream.procFile(src_file=src_file, src_lst=src_lst, stx_lst=stx_lst)

    def set_debugging(self, debugging=True):
        self.debugging=debugging

    
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    file = "one_square"
    run = False                     # Do we run file upon start
    src_lst = True                  # List source as run
    stx_lst = True                  # List Stream Trace cmd
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f', '--file', default=file)
    parser.add_argument('-r', '--run', action='store_true', default=run,
                        help=("Run program upon loading"
                              " (default:%s" % run))
    parser.add_argument('-l', '--src_lst', action='store_true', default=src_lst,
                        help=("List source as run"
                              " (default:%s" % src_lst))
    parser.add_argument('-x', '--stx_lst', action='store_true', default=stx_lst,
                        help=("List commands expanded as run"
                              " (default:%s" % stx_lst))

    args = parser.parse_args()             # or die "Illegal options"
    
    file = args.file
    src_lst = args.src_lst
    stx_lst = args.stx_lst
    run = args.run
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
        
    root = Tk()
    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    fC = SelectCommandFileControl(frame, title="Command Stream",
                     src_lst=src_lst,
                     stx_lst=stx_lst,
                     src_file=file, display=True)
    fC.set_debugging()
    if run:
        root.after(0, fC.run_file)
        
    root.mainloop()
    