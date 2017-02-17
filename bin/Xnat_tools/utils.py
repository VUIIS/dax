#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 16th February, 2017:

File containing all useful functions for the different executables.

@author: Benjamin Yvernault, Electrical Engineering, Vanderbilt University
'''

import logging
import os
import sys

from dax.errors import XnatToolsError, XnatToolsArgumentsError


LENGTH = 60
DISPLAY_TEMPLATE = """#######################################################\
#########
{name}
#                                                              #
# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
# If issues, please start a thread here:                       #
# https://groups.google.com/forum/#!forum/vuiis-cci            #
# Usage:                                                       #
{description}
# Arguments :                                                  #
{args}
################################################################
"""


def get_xnat_tools_argparser(name, description):
    """
    Return default argparser arguments for all Spider

    :return: argparser obj

    """
    from argparse import ArgumentParser, RawTextHelpFormatter
    ap = ArgumentParser(prog=name, description=description,
                        formatter_class=RawTextHelpFormatter)
    ap.add_argument('--host', dest='host', default=None,
                    help='Host for XNAT. Default: env XNAT_HOST.')
    ap.add_argument('-u', '--username', dest='username', default=None,
                    help='Username for XNAT.')
    return ap


def setup_info_logger(name, log_file=None):
    """
    Using logger for the executables output.
     Setting the information for the logger.

    :param name: Name of the logger
    :param log_file: log file path to write outputs
    :return: logging object
    """
    if log_file:
        handler = logging.FileHandler(log_file, 'w')
    else:
        handler = logging.StreamHandler(sys.stdout)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


def check_arguments(script, args, display):
    """
    Method to check arguments given to the tools.

    :param args: Parser.parse_args() arguments
    :param display: dictionary defining how to display
    :return: True if arguments are fine, raise Error otherwise
    """
    args_info = display['required_args']
    default_args = display['default_args']
    arguments = vars(args)
    if arguments == default_args:
        return False
    else:
        for _arg, _dict in args_info.items():
            need_to_check = True
            if _dict.get('ifnotand', None):
                for c_arg in _dict['ifnotand']:
                    if arguments.get(c_arg):
                        need_to_check = False
            if need_to_check:
                _is_path = _dict.get('path', False)
                _ext = _dict.get('ext', None)
                check_arg(script, _arg, arguments.get(_arg), is_path=_is_path,
                          has_ext=_ext)
        return True


def check_arg(script, name, value, is_path=False, has_ext=None):
    """
    Method to check singel argument.

    :param name: argument name
    :param value: argument value
    :param path: check path
    :param ext: has extension and need to check it
    :return: True if argument is fine, False otherwise
    """
    if not value:
        raise XnatToolsArgumentsError(script, name)
    elif is_path and not os.path.exists(value):
        raise XnatToolsArgumentsError(script, name, path_not_found=True)
    elif has_ext and not value.split('.')[-1] == has_ext:
        raise XnatToolsArgumentsError(script, name, wrong_ext=True)
    else:
        pass


def main_display(name, parser, display):
    """
    Main display of the executables before any process

    :param name: name of the executable
    :param parser: parser for executable
    :param display: dictionary defining how to display
    :return: None
    """
    description = display['description']
    default_args = display['default_args']
    display_info = display['info']
    args = parser.parse_args()
    print_help = False

    if vars(args) == default_args:
        _args = ['No Arguments given.',
                 'See the help bellow or Use "%s" -h' % name]
        print_help = True
    else:
        _args = list()
        for key, value in vars(args).items():
            if value:
                str_tmp = '%*s -> %*s'
                _dict = display_info.get(key, None)
                # Only print if a dict was define in the display
                if _dict:
                    _info = _dict.get('display')
                    _end = _dict.get('end', False)
                    _value = _dict.get('default', value)
                    _args.append(str_tmp % (-20, _info,
                                            -32, get_proper_str(_value, _end)))

    _args_str = edit_string_size(_args, left_spaces=4)
    if _args_str is '':
        _args_str = '# %s #' % (' ' * LENGTH)
    _spaces = (LENGTH - len(name))/2
    _name = edit_string_size(name, left_spaces=_spaces)
    _desc = edit_string_size(description, left_spaces=4)
    display = DISPLAY_TEMPLATE.format(name=_name,
                                      description=_desc,
                                      args=_args_str)
    print display
    if print_help:
        print_separators('-')
        parser.print_help()
        print_separators('-')


def edit_string_size(strings, max_length=LENGTH, left_spaces=0):
    """
    Edit the string to by adding spaces at the beginning and end.
    If string is a list, return list of strings edited.

    :param string: string to edit or list of strings
    :param length: length of the string
    :return: new string of length 60
    """
    if isinstance(strings, str):
        _lspaces = ' ' * left_spaces
        _str = '%s%s' % (_lspaces, strings)
        _space = (max_length - len(_str))
        return '# %s%s #' % (_str, ' ' * _space)
    elif isinstance(strings, list):
        # Separate the string in several
        new_strings = list()
        for string in strings:
            _str = edit_string_size(string, max_length, left_spaces)
            new_strings.append(_str)
        return '\n'.join(new_strings)
    else:
        err = "Wrong type for 'strings' argument in edit_string_size. Required\
 <type 'str'> or <type 'list'>, found: %s"
        raise XnatToolsError(err % type(string))


def read_txt(txt_file):
    """
    Method to read the txt file path with per line, the name
     of the variable on REDCap you want to extract

    :param txt_file: filepath
    :return: list of REDCap variables
    """
    if txt_file:
        print 'INFO: Export data from text file %s ...' % txt_file
        obj_list = list()
        if not os.path.exists(txt_file):
            raise XnatToolsError('  error: %s does not exist.' % txt_file)
        else:
            with open(txt_file, 'r') as input_file:
                for line in input_file:
                    obj_list.append(line.strip().split('\n')[0])
    else:
        obj_list = None
    return obj_list


def write_csv(csv_string, csv_file):
    """
    Method to write the report as a csv file
     with the values from REDCap

    :param csv_string: data to write in the csv
    :param csv_file: csv filepath
    :return: None
    """
    print 'INFO: Writing report ...'
    with open(csv_file, 'w') as output_file:
        for line in csv_string:
            output_file.write(line)


def get_option_list(string):
    """
    Method to switch the string of value separated by a comma into a list.
     If the value is 'all', keep all.

    :param string: string to change
    :return: None if not set, all if all, list of value otherwise
    """
    if not string:
        return None
    elif string == 'all':
        return 'all'
    elif string == 'nan':
        return None
    else:
        return string.split(',')


def get_proper_str(str_option, end=False):
    """
    Method to shorten a string into the proper size for display

    :param str_option: string to shorten
    :param end: keep the end of the string visible (default beginning)
    :return: shortened string
    """
    if len(str_option) > 31:
        if end:
            return '...%s' % str_option[-28:]
        else:
            return '%s...' % str_option[:28]
    else:
        return str_option


def prompt_user_yes_no(question):
    """Prompt the user for a question with answer Y/N.

    :return: True if yes, False if no, ask again if any other answer
    """
    value = ''
    while value.lower() not in ['yes', 'no', 'n', 'y']:
        value = raw_input("%s [yes/no] " % question)
    if value.lower() in ['yes', 'y']:
        return True
    else:
        return False


def print_separators(symbol='=', length=LENGTH):
    """
    Print line to separate: symbolx60

    :param symbol: symbol to print length time (60)
    """
    print '%s' % (symbol * length)


def print_end(name):
    """
    Last display when the tool script finish.
    """
    print '------- %s DONE -------' % name
    print_separators()
    print '\n'