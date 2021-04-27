# label_button_control.py
"""
Support for image/text selection of button labeling plus image selection
User selects images or enters text into entry
"""
import re
from PIL import ImageTk, Image
from tkinter import Button, StringVar

from select_trace import SlTrace
from image_hash import ImageHash
from select_list import SelectList

class LabelButtonControl:
    def __init__(self, image_hash, frame, player=None, label_text=None,
                  width=None, select_list_hash=None):
        """ Setup image/text button to select another image/text to replace our image/text
        :image_hash: image storage, shared if present
                default: create own storage
        :select_list_hash: independent control over list select hash
        :frame: dedicated frame, allowing destroy, forget, and reconstucting new button in place
        :player: player for whome the button is
        :label_text: button description / identifier 
                    <file:...file name...>
                    else text as is
        :width: with of field, in characters (TBD how do we convert to pixels)
        :select_list_hash: separate control of select_list to facilitate different sizes for
                    same figure
        """
        self.btn = None
        self.frame = frame
        self.player_field_by_text_field = {}        # (player, btn, label_text) by label_text
        self.player = player
        if image_hash is None:
            image_hash = ImageHash()
        self.image_hash = image_hash
        if select_list_hash is None:
            select_list_hash = ImageHash()
        self.select_list_hash = select_list_hash
        self.select_list_hash = select_list_hash
        btn = self.button_from_label(frame, player, label_text=label_text, width=width)
        btn.pack(side="left", fill="none", expand=False)
        self.set_btn_fields(player, btn, label_text)

    def set_btn_fields(self, player, btn, label_text):
        field = "label"                 # Used by PlayerControl set_vars
        self.btn = btn
        content = StringVar()
        content.set(label_text)
        player.ctls[field] = btn
        player.ctls_vars[field] = content


    def button_from_label(self, frame, player, label_text=None, width=None):
        """ Convert player, label_text to button
        :frame: containing frame
        :player: player associated
        :label_text: label text (could be <file...>
        :width: suggested width in characters
        returns button, saves (player, btn, label text) in self.player_field_by_text_field
        """
        fm = re.match(self.image_hash.file_pattern, label_text)
        
        if fm is not None:
            image_key = file_name = fm.group(1)
            size = self.get_label_size(width=width)
            image = self.image_hash.get_image(file_name, size=size)
            btn = Button(frame, image=image, width=size[0],
                               height=size[1], command=lambda : self.do_label(label_text))
        else:
            btn = Button(frame, text=label_text, width=width,
                              command=lambda : self.do_label(label_text))
        if self.btn is not None:
            ###self.btn.pack_forget()
            self.btn.destroy()
        btn.pack(side="left", fill="none", expand=False)    
        self.player_field_by_text_field[label_text] = (player, btn, label_text)
        self.btn = btn
        self.set_btn_fields(player, btn, label_text)
        return btn
        
    def do_label(self, label_text):
        """ Do label image processing
        """
        SlTrace.lg(f"label text:{label_text}")
        player, btn, label_text = self.player_field_by_text_field[label_text]
        SlTrace.lg(f"player: {player}")
        images = self.select_list_hash.get_image_files()
        image_width = image_height = 125
        player_control = player.control
        pc_win = player_control.mw
        win_x0 = pc_win.winfo_x()
        win_y0 = pc_win.winfo_y()
        list_x0 = win_x0 + 250
        list_y0 = win_y0 + 100
        win_height = pc_win.winfo_height()
        list_height = int(.8*win_height)
        list_width = int(image_width * 1.2)
        
        sel_list = SelectList(title=f"{player.name}'s Label", items=images,
                              size=(list_width, list_height),
                              position=(list_x0, list_y0),
                              image_size=(image_width, image_height),
                              image_hash=self.select_list_hash, default_to_files=True) 
        new_label_text = sel_list.get_selected()
        SlTrace.lg(f"new_label_text: {new_label_text}")
        if new_label_text is None:
            return                  # Ignore if canceled
        
        self.button_from_label(self.frame, player, label_text=new_label_text)
        
        
    def get_image_files(self, player, label_text):
        """ Get list of selectable images for given player
        :player: player for list
        :label_text: current label text
        """
        _ = player
        _ = label_text
        image_files = self.image_hash.get_image_files(None) # All for now
        return image_files
        
    def select_image(self, image_file_list, player, label_text=None):
        """ Display list of selectable images for this player
        facilitating the players selection of desired image
        :image_file_list: list of image files to select from
        :player: player on which to select
        :label_text: current button's text
        :returns: label_text of selection, None if cancel / no selection
        """
        
        return None

    def update_button(self, widget, player, new_label_text):
        """ Update current button, in place if possible
        based current widget and new_label_text
        :widget: current button's widget
        :player: current player
        :new_label_text: new label text
        """
        # TBD

        
                
    def get_button(self):
        return self.btn
    
    def get_label_size(self, width=None):
        """ Get button size in pixels
        :width: width in characters
            default: guess
        :returns: width, height in pixels
        """
        return self.image_hash.width2size(width)
