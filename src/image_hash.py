# image_hash.py    11Apr2020  crs
"""  Hash images to reduce rereading/processing 
"""
from select_trace import SlTrace

class ImageHash:
    def __init__(self):
        self.images_by_key = {}
        self.destroy_function = None
        
    def get_image(self, key):
        """ Get image if one stored
        
        NOTE: image must be independently stored till no longer needed
        Refer to http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm

        :key: unique key e.g. file name
        :returns: saved image if image present else None
        """
        if key in self.images_by_key:
            return self.images_by_key[key]
        
        return None
        
    def add_image(self, key, image):
        self.images_by_key[key] = image
        SlTrace.lg(f"image {len(self.images_by_key)}: {key}")
        return image
    
    def clear_cache(self):
        """ Clear the image cache so new calls will check for change
        """
        for key in self.images_by_key:
            image = self.images_by_key[key]
            if self.destroy_function is not None:
                self.destroy_function(image)
            else:
                pass
        self.images_by_key = {}

    def set_image_destroy(self, destroy_function):
        """ Set custome image resource releasing function
        :destroy_function: will be called with image (destroy_function(image)
        Default operation no special releasing action
        """
        self.destroy_function = destroy_function
        
        
