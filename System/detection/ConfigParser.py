import re

class ConfigParser:
    """ Reads a configuration file to determine the parameter calibrations for a node. """
    check_list = {
        "print_negative": False,
        "print_positive": False,
        "history_count": False,
        "test_length": False,
        "rapid_test": False,
        "refresh_count": False,
        "training": False,
        "grid": False,
        "frame_count": False,
        "boxes": False,
        "centroids": False,
        "count_line": False,
        "count_graphics": False,
        "graphics": False,
        "frame_wait": False,
        "traffic_orientation": False,
        "scale_percent": False,
        "history": False,
        "shadows": False,
        "med_size": False,
        "morph_shape": False,
        "morph_size": False,
        "morph_iter": False,
        "min_width": False,
        "min_height": False,
        "max_width": False,
        "max_height": False,
        "max_dist": False,
        "min_dist": False,
        "missing": False,
        "count_line_p1": False,
        "count_line_p2": False,
        "speed_line1_p1": False,
        "speed_line1_p2": False,
        "speed_line2_p1": False,
        "speed_line2_p2": False
    }

    def __init__(self, file):
        self.file = file
        self.parameters = {
            "print_negative": False,
            "print_positive": False,
            "history_count": False,
            "test_length": False,
            "rapid_test": False,
            "refresh_count": False,
            "training": False,
            "grid": False,
            "frame_count": False,
            "boxes": False,
            "centroids": False,
            "count_line": False,
            "count_graphics": False,
            "graphics": False,
            "frame_wait": 0,
            "traffic_orientation": 0,
            "scale_percent": 0,
            "history": 0,
            "shadows": False,
            "med_size": 0,
            "morph_shape": 0,
            "morph_size": 0,
            "morph_iter": 0,
            "min_width": 0,
            "min_height": 0,
            "max_width": 0,
            "max_height": 0,
            "height": 0,
            "max_dist": 0,
            "min_dist": 0,
            "missing": 0,
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
                if string_list[0] in self.check_list:
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