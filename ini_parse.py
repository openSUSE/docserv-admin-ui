import configparser
import config

# initialize the parser
def GetParser():
    parser = configparser.ConfigParser()
    parser.read(config.docserv_conf_file)
    return parser

# get first valid server section
def first_valid_server_section():
    parser = GetParser()
    for section in parser.sections():
        if parser.has_option(section, 'host'):
            return section

# create dictionary with docserv config
def get_docserv_config():
    docserv_conf_dict = {}
    parser = GetParser()
    server_section = first_valid_server_section()
    for option in parser.options(first_valid_server_section()):
        if option == 'loglevel' or option == 'max_threads' or option == 'port':
            docserv_conf_dict[option] = parser.getint(server_section, option)
        elif option == 'valid_languages':
            lang_list = parser.get(server_section, option).split(' ')
            docserv_conf_dict[option] = lang_list
        else:
            docserv_conf_dict[option] = parser.get(server_section, option)
    return docserv_conf_dict



