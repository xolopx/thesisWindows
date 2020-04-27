import threading

class Globs:
    """ Holds global variables that need to be shared. Like a shitty
        database."""

    # These variables are static and hence the same for all instances of the class.
    lock = threading.Lock() # Protects the image from concurrent modification.
    currentFrame = None     # This is a class variable because of the way it's defined.
