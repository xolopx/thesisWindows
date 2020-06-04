import re

class ConfigParser:
    """ Reads a configuration file to determine the parameter calibrations for a node. """
    check_list = {
        "history": False,
        "shadows": False,
        "med_size": False,
        "morph_shape": False,
        "morph_size": False,
        "morph_iter": False,
        "width": False,
        "height": False,
        "consolidation_distance": False,
        "disappeared_duration": False,
        "count_line_p1": False,
        "count_line_p2": False,
        "speed_line1_p1": False,
        "speed_line1_p2": False,
        "speed_line2_p1": False,
        "speed_line2_p2": False
    }

    key_list = ["history","shadows","med_size","morph_shape","morph_size","morph_iter"
        ,"width","height","consolidation_distance","disappeared_duration","count_line_p1"
        ,"count_line_p2","speed_line1_p1","speed_line1_p2","speed_line2_p1","speed_line2_p2"]

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
        self.parameters = {
            "history": 0,
            "shadows": False,
            "med_size": 0,
            "morph_shape": 0,
            "morph_size": 0,
            "morph_iter": 0,
            "width": 0,
            "height": 0,
            "consolidation_distance": 0,
            "disappeared_duration": 0,
            "count_line_p1": (0,0),
            "count_line_p2": (0,0),
            "speed_line1_p1": (0,0),
            "speed_line1_p2": (0,0),
            "speed_line2_p1": (0,0),
            "speed_line2_p2": (0,0)
    }

    def parseConfig(self):
        # Cartesian point regex.
        pattern = re.compile("^\(\-{0,1}\d*,\-{0,1}\d*\)")
        file = open(self.file, "r")
        # For each line in the file
        for x in file:
            # Split string
            string_list = x.split(" ")
            # Check if valid string
            if len(string_list) == 3:
                # Check if string matches key.
                if string_list[0] in self.key_list:
                    # remove trailing \n from values.
                    if "\n" in string_list[2]:
                        string_list[2] = string_list[2][:-1]
                    if pattern.match(string_list[2]) is not None:
                        self.parameters[string_list[0]] = string_list[2]
                        self.check_list[string_list[0]] = True
                    else:
                        # assign based on dictionary
                        self.parameters[string_list[0]] = string_list[2]
                        self.check_list[string_list[0]] = True
                else:
                    raise Exception("Specified setting not in parameter list for string: {}".format(x))

            else:
                raise Exception("Wrong number of entities in string: {}".format(x))

        errorList = []
        for (key,value) in self.check_list.items():
            if not value:
                errorList.append(key)
        if errorList:
            raise Exception("The following parameter values were not set: {}".format(errorList))

    def print_parser(self):

        for (key, value) in self.parameters.items():
            print("{} : {}".format(key, value))