#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by fhenriquez on 3/18/19
    TODO: fill modude doc
"""

from newsapi import NewsApiClient
import argparse
from tabulate import tabulate
import json
from collections import OrderedDict
import logging
import getpass

countries = {'ae','ar','at','au','be','bg','br','ca','ch','cn','co','cu','cz','de','eg','fr','gb','gr','hk',
             'hu','id','ie','il','in','it','jp','kr','lt','lv','ma','mx','my','ng','nl','no','nz','ph','pl',
             'pt','ro','rs','ru','sa','se','sg','si','sk','th','tr','tw','ua','us','ve','za'}

languages = {'ar','en','cn','de','es','fr','he','it','nl','no','pt','ru','sv','ud'}

categories = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}

sort_method = {'relevancy','popularity','publishedAt'}

def set_logger(name, formatter, level):
    """
    does initial configuration of logger
    :param name: name of logger
    :param formatter: log format
    :param level: log level
    :return: logger
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Setting root logger
    if name == "root":
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)

    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    logger.propagate = False

    return logger


def init_parameters():
    """
    does initial configuration of arguments
    :return: arguments
    """

    # Getting Required Args
    parser = argparse.ArgumentParser(description="Gets news from https://newsapi.org/")
    parser.add_argument("-a", "--all", required=False, action='store_true', help="List all sources.")
    parser.add_argument("-d", "--desc", required=False, help="Get descriptor.")
    parser.add_argument("-l", "--list", required=False, nargs='?', const=1,
                        help="List all sources, with specific language <EN>.")
    parser.add_argument('--use-tricky-mock', help=argparse.SUPPRESS, action='store_true')
    group_common = parser.add_argument_group('Verbosity maniplutation')
    group_common.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, up to -vvv')
    group_common.add_argument('-fl', '--filename-log', dest='filename_log', metavar='stderr.log',
                              default=None, help='File with additional logging.')
    args = parser.parse_args()

    if args.use_tricky_mock:
        from ignored import api_creds
        api_creds.substitute_params(args)

    return args

def pprint_dict(dictionary, need_sort=True, indent_size=0):
    """
    pretty printing for dictionary with keys
    :param indent_size: space indentation in the begining
    :param need_sort: to sort or not keys
    :param dictionary:
    :return:
    """
    indent = " " * indent_size
    longest_key = max(len(k) for k in dictionary)
    if need_sort:
        keys = sorted(dictionary.keys())
    else:
        keys = dictionary.keys()
    for k in keys:
        # print wrapper.fill("{indent}{key:{width}} :{value}".format(indent=indent, key=k, value=dictionary[k],
        #                                                            width=longest_key))
        print ("{key:{width}} :{indent}{value}".format(indent=indent, key=k, value=dictionary[k],
                                                       width=longest_key))

def print_desc(desc):
    """
    :param desc: 
    :return: 
    """
    logger.info('Getting description for {}....'.format(desc))
    for source in sources:
        if source.get('id') == desc:
            pprint_dict(source, indent_size=1)

def print_source_list(languages='all'):
    """
    :param lanuages: Languages to be printed
    :return:
    """
    lang = languages

    if lang == 1:
        lang = 'en'

    list_sources = []
    if lang is not 'all':
        logger.info('Listing all sources with language {}....'.format(lang))
        lang = unicode(lang, "utf-8")
        for source in sources:
            # this is not working
            # print type(source.get('language'))
            # print type(unicode(lang, "utf-8"))
            if source.get('language') == lang:
                source_dict = {'Name': '', 'ID': ''}
                source_dict['Name'] = source.get('name')
                source_dict['ID'] = source.get('id')
                list_sources.append(source_dict)
    else:
        logger.info('Listing all sources....')
        for source in sources:
            source_dict = {'Name': '', 'ID': ''}
            source_dict['Name'] = source.get('name')
            source_dict['ID'] = source.get('id')
            list_sources.append(source_dict)

    headers = list_sources[0].keys()
    rows = [x.values() for x in list_sources]
    print tabulate(rows, headers)

def main():
    if args.desc:
        print_desc(args.desc)
        exit(0)

    if args.all:
        print_source_list()
        exit(0)

    if args.list:
        print_source_list(args.list)
    pass


if __name__ == '__main__':

    args = init_parameters()
    verbose = args.verbose
    fileLog = args.filename_log

    # Common Logging configs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = levels[min(len(levels) - 1, verbose)]  # capped to number of levels
    log_level_name = logging._levelNames[log_level]

    # Setting root logger
    root = set_logger("root", formatter, log_level)

    if verbose >= 3:  # include shade debug in log. actually, not only the shade but any inherited from root
        root.setLevel(log_level)
    else:
        root.setLevel(logging.CRITICAL)

    # Setting custom logger
    logger = set_logger(__name__, formatter,log_level)

    # Setting log file location
    if fileLog is not None:  # do also log to file
        file_handler = logging.FileHandler(args.filename_log)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        logger.addHandler(file_handler)

    logger.info("************************* Starting run.... *************************")
    logger.info('Gathering all news sources.')
    api = NewsApiClient(args.api_key)
    sources = api.get_sources()
    if sources.get('status') == 'ok':
        sources = sources.get('sources')

    try:
        main()
        print('')
        logger.debug("************************* Finished run.... *************************")
    except KeyboardInterrupt:  # do not want to see ugly stacktrace after ctrl-c
        exit(1)

