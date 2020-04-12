# image_hash.py    11Apr2020  crs
"""  Hash images to reduce rereading/processing 
"""

class ImageHash:
    def __init__(self):
        self.images_by_key = {}
        
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
        return image
    
