from configparser import ConfigParser


def read_db_config(filename=r'C:\Users\Tom\Desktop\thesisWindows\System\database_interface\config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        msg = "{0} not found in the {1} file".format(section, filename)
        raise Exception(msg)

    return db