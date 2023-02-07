#!/usr/bin/env python3
'''
This module is entrypoint
'''
from __future__ import print_function
import pickle
import traceback
import argparse
import sys
import logging

__logging = logging.getLogger(__name__)

import coloredlogs

# TODO support multiple swagger_client
import swagger_client

import swagger_client_helpers
import test_group_utils


def dsl_iterate_prefix_summary_agg_group(prefix_summary_agg_group, custom_dsl):
    # iterate through all test groups

    criteria_meet_group_counter = 0
    criteria_not_meet_group_counter = 0

    for idx, j in enumerate(prefix_summary_agg_group):
    
        logging.debug(
            "iterating through test group: {}".format(
                str(test_group_utils.test_group_summary(j))
            )
        )

        if custom_dsl.test_group_criteria_meet(j):
            criteria_meet_group_counter += 1
            custom_dsl.test_group_custom_dsl(j)
        else:
            criteria_not_meet_group_counter += 1
        
    __logging.info('criteria_meet_group_counter: {}/{}'.format(
        criteria_meet_group_counter, criteria_meet_group_counter + criteria_not_meet_group_counter
        ))
    # __logging.info('criteria_not_meet_group_counter: {}'.format(criteria_not_meet_group_counter))


def argparse_arguments(parser: argparse.ArgumentParser):

    parser.add_argument('--prefix-summary-agg-group-pkl-path', 
        type=str,
        default='prefix-summary-agg-group.pkl',
        help='default=\'prefix-summary-agg-group.pkl\'',
    )

    # https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )

    return parser


def dsl_iterate_prefix_summary_agg_group_pkl_path(
    prefix_summary_agg_group_pkl_path: str, 
    custom_dsl,
):
    try:
        # load prefix-summary-agg-group
        with open(prefix_summary_agg_group_pkl_path, 'rb') as f:
            prefix_summary_agg_group = pickle.load(f)

        # Only one should be processed at a time, because client sdk are different from projects
        dsl_iterate_prefix_summary_agg_group(
            prefix_summary_agg_group, custom_dsl
        )

    except Exception as e:
        print(e)
        print('\n'.join(traceback.format_exception(type(e), e, e.__traceback__)))
        sys.exit(255)


def main():
    parser = argparse.ArgumentParser(
        description='default_parameter.py Generator'
    )
    # Append Parser's Arguments
    argparse_arguments(parser)
    args = parser.parse_args()

    # logging config
    logging.basicConfig(level=args.loglevel)
    coloredlogs.install(level=args.loglevel)

    # Vital for Response Type Capturing
    swagger_client_helpers.enable_swagger_client_mock_call_api(swagger_client=swagger_client)

    # dsl custom
    import custom_dsl as __custom_dsl

    dsl_iterate_prefix_summary_agg_group_pkl_path(
        args.prefix_summary_agg_group_pkl_path, __custom_dsl
    )

    __custom_dsl.post_main()
    
if __name__ == '__main__':
    main()
