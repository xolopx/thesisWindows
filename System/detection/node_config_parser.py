class node_config_parser:
    """ Reads a configuration file to determine the parameter calibrations for a node. """

    def __init__(self, file):
        """
        Parser object holds the information extracted from the configuration file.
        The configurations correspond to sub-processes in the detection component
        of the system.

        :param file: Path to configuration file.
        """
        self.file = file
        # Detection
        self.history = 0
        self.shadows = False
        # Morph & Filter
        self.med_size = 0
        self.morph_shape = None
        self.morph_size = 0
        self.morph_iter = 0
        # Contours & Bounds
        self.width = 0
        self.height = 0
        # Tracking
        self.consolidation_distance = 0
        self.disappeared_duration = 0
        # Count & Measure
        self.count_line_p1 = []
        self.count_line_p2 = []
        self.speed_line1_p1 = []
        self.speed_line1_p2 = []
        self.speed_line2_p1 = []
        self.speed_line2_p2 = []

    def parseConfig(self):

        return 0
