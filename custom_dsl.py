import logging
import inspect
import itertools
import traceback

__logging = logging.getLogger(__name__)

import swagger_client

import swagger_client_helpers
import naming_convert
import common_key_name_infer

def test_group_criteria_meet(j) -> bool:
    # current path, post or put, A account
    # current path + /{xxxxx_id}, any, B account
    current_api_path = next(iter(j.keys()))
    # fdt: Comment Out for Swift: {'/v2.1/v1/{account}/{container}': {'#': {'methods': ['get', 'put', 'post', 'head', 'delete']}, '/{object}': {'#': {'methods': ['get', 'put', 'copy', 'delete', 'head', 'post']}}}}
    # if '{' not in current_api_path:

    sub_api_keys = list(
        filter(
            lambda x: '{' in x,
            iter(j[current_api_path].keys())
        )
    )

    sub_api_paths_contains_id = len(sub_api_keys) > 0

    __logging.debug('sub_api_paths_contains_id: {}'.format(sub_api_paths_contains_id))

    if sub_api_paths_contains_id:
        return True

    return False


class SDKNotModelException(Exception):
    def __init__(self, *args, **kwargs):
        super(SDKNotModelException, self).__init__(*args, **kwargs)

class SDKNoneTypeException(SDKNotModelException):
    def __init__(self, *args, **kwargs):
        super(SDKNoneTypeException, self).__init__(*args, **kwargs)

_statistics = {
    'statistics_common_keys_pair_count': 0,
    'statistics_common_keys_same': 0,
    'statistics_common_keys_not_found': 0,
}

def test_group_custom_dsl(j):
    __logging.debug('criteria met')
    # For Instance Creation, Intersection of {'post', 'put'} and methods set
    major_api_path = next(iter(j.keys()))

    def creating_request(creating_http_method, j):
        creating_request_path_prefix = ''
        __logging.debug('creating_http_method: {}'.format(creating_http_method))

        creating_request_sdk_api_method, creating_request_api_clz_instance = swagger_client_helpers.api_path_method_to_sdk_api_method(
            api_doc_section=j,
            path_prefix=creating_request_path_prefix,
            http_method=creating_http_method,
            swagger_client=swagger_client,
        )

        creating_request_parameters = swagger_client_helpers.api_method_parameter_type_from_docstring(creating_request_sdk_api_method)

        # In the following line, parameters' name is significant, 
        # at the same time, the values have no meaning, which means who makes no change to program control flow
        # and function api_method would not read any parameters' value
        creating_response_dict = creating_request_sdk_api_method(creating_request_api_clz_instance, **creating_request_parameters)

        creating_response_type_name = creating_response_dict['response_type']

        __logging.debug('creating_response_dict: {}'.format(str(creating_response_dict)))

        # filter possible creating response type name
        if creating_response_type_name == None:
            # TODO
            # This is a BUG in swagger-codegen-cli
            raise SDKNoneTypeException()
        if creating_response_type_name.startswith('list[') \
            or creating_response_type_name in {
                'str', 'int', 'Float', 'bool', 'object', 'file'
            }:
            raise SDKNotModelException()
            
        creating_response_model = swagger_client.models.__dict__[creating_response_type_name]

        # According to Swagger Codegen models
        #   swagger_types (dict): The key is attribute name and the value is attribute type.
        creating_response_parameters = list(filter(
            lambda x: (not x[0].startswith(
                '_')) and x[0] != 'attribute_map' and x[0] != 'swagger_types',
            inspect.getmembers(creating_response_model, lambda a: not inspect.isroutine(a))
        ))

        response_parameters_type_dict = {}

        for j in creating_response_parameters:
            if j[0] in creating_response_model.swagger_types:
                data_type = creating_response_model.swagger_types[j[0]]
                response_parameters_type_dict[j[0]] = data_type
        
        __logging.debug('response_parameters_type_dict: {}'.format(response_parameters_type_dict))

        return {
            'response_parameters_type_dict': response_parameters_type_dict,
        }

    def sub_request(sub_http_method, sub_api_doc_section):
        sub_request_path_prefix = major_api_path
        __logging.debug('sub_http_method: {}'.format(sub_http_method))

        sub_request_sdk_api_method, sub_request_api_clz_instance = swagger_client_helpers.api_path_method_to_sdk_api_method(
            api_doc_section=sub_api_doc_section,
            path_prefix=sub_request_path_prefix,
            http_method=sub_http_method,
            swagger_client=swagger_client,
        )

        sub_request_parameters = swagger_client_helpers.api_method_parameter_type_from_docstring(sub_request_sdk_api_method)

        __logging.debug('sub_request_parameters: {}'.format(sub_request_parameters))

        # In the following line, parameters' name is significant, 
        # at the same time, the values have no meaning, which means who makes no change to program control flow
        # and function api_method would not read any parameters' value
        sub_response_dict = sub_request_sdk_api_method(sub_request_api_clz_instance, **sub_request_parameters)

        __logging.debug('sub_response_dict: {}'.format(sub_response_dict))
        
        sub_request_path_params_camel = sub_response_dict['path_params']

        sub_request_path_params_type_dict = {}
        for camel_key in sub_request_path_params_camel.keys():
            snake_key = naming_convert.canonical_to_snake(camel_key)
            sub_request_path_params_type_dict[snake_key] = sub_request_path_params_camel[camel_key]

        __logging.debug('sub_request_path_params_type_dict {}'.format(sub_request_path_params_type_dict))

        return {
            'sub_request_parameters_type_dict': sub_request_parameters,
            'sub_request_path_params_type_dict': sub_request_path_params_type_dict,
        }

    try:
        statistics_common_keys_pair_count = 0
        statistics_common_keys_same = 0
        statistics_common_keys_not_found = 0

        # Creating request related
        creating_responses_type_dict = {}
        creating_methods = {'post', 'put'} & set(j[major_api_path]['#']['methods'])
        for creating_http_method in creating_methods:
            creating_responses_type_dict[creating_http_method] = creating_request(creating_http_method, j)['response_parameters_type_dict']
        __logging.debug('creating_responses_type_dict: {}'.format(creating_responses_type_dict))

        # Sub request related
        sub_requests_path_params_type_dict = {}
        sub_api_key = next(filter(lambda x: x.startswith('/{'), j[major_api_path]))
        __logging.debug('sub_api_key: {}'.format(sub_api_key))
        sub_api_doc_section = {}
        sub_api_doc_section[sub_api_key] = j[major_api_path][sub_api_key]
        for sub_http_method in sub_api_doc_section[sub_api_key]['#']['methods']:
            sub_requests_path_params_type_dict[sub_http_method] = sub_request(sub_http_method, sub_api_doc_section)['sub_request_path_params_type_dict']
        __logging.debug('sub_requests_path_params_type_dict: {}'.format(sub_requests_path_params_type_dict))

        # Analysis
        for c, s in itertools.product(creating_responses_type_dict.items(), sub_requests_path_params_type_dict.items()):
            '''
            c: creating request
            s: sub request
            '''
            # 1. Intersection of creating_responses_type_dict[one] and sub_request_path_params_type_dict[one]
            keys_intersection_of_creating_and_sub_request = c[1].keys() & s[1].keys()
            __logging.debug('keys_intersection_of_creating_and_sub_request: {}'.format(keys_intersection_of_creating_and_sub_request))

            # 1.1. If no common key was found, meaning that cannot find keys with common name
            if len(keys_intersection_of_creating_and_sub_request) < 1:
                __logging.critical('No common name parameter found')
                __logging.warning('creating_request: {}'.format(c[1]))
                __logging.warning('sub_request: {}'.format(s[1]))

                statistics_common_keys_not_found += 1

                for sub_request_path_param_name in s[1].keys():
                    # infer most likely common key by LCS
                    respose_most_likely_key = common_key_name_infer.infer_common_key_name(c[1].keys(), sub_request_path_param_name)
                    __logging.warning('infer common key: (sub, create) = ({}, {})'.format(sub_request_path_param_name, respose_most_likely_key))
            
            # 2. Find out this case: sub_request_path_params_type_dict[one]'s key not in creating_responses_type_dict[one]
            for common_key in keys_intersection_of_creating_and_sub_request:
                statistics_common_keys_pair_count += 1
                is_creating_and_sub_api_common_key_type_consistent = c[1][common_key] == s[1][common_key]
                if is_creating_and_sub_api_common_key_type_consistent:
                    __logging.info('They are the same: {}'.format(
                        {
                            'creating_method': c[0],
                            'common_key': common_key,
                            'sub_request_method': s[0],
                            'common_type': c[1][common_key],
                        }
                    ))
                    statistics_common_keys_same += 1
                else:
                    __logging.critical('They are NOT the same: {}'.format(
                        {
                            'creating_method': c[0],
                            'common_key': common_key,
                            'sub_request_method': s[0],
                            'creating_type': c[1][common_key],
                            'sub_request_type': s[1][common_key],
                        }
                    ))

    except (SDKNotModelException) as e:
        __logging.critical('\n'.join(traceback.format_exception(type(e), e, e.__traceback__)))
    finally:
        # Statistics
        _statistics['statistics_common_keys_not_found'] += statistics_common_keys_not_found
        _statistics['statistics_common_keys_pair_count'] += statistics_common_keys_pair_count
        _statistics['statistics_common_keys_same'] += statistics_common_keys_same
        
def post_main():
    __logging.info('common key found: {}/{}'.format(
        _statistics['statistics_common_keys_pair_count'], _statistics['statistics_common_keys_pair_count'] + _statistics['statistics_common_keys_not_found']
        ))
    __logging.info('    common key same: {}/{}'.format(
        _statistics['statistics_common_keys_same'], _statistics['statistics_common_keys_pair_count']
        ))
