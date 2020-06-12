from configparser import ConfigParser
import os


def read_db_config(filename = 'config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: Config file name
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, filename)
    # create parser and read ini configuration file
    parser = ConfigParser()
    try:
       f = open(path)
    except FileNotFoundError as e:
        print(e)
    finally:
       f.close()

    parser.read(path)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        msg = "{0} not found in the {1} file".format(section, path)
        raise Exception(msg)

    return db