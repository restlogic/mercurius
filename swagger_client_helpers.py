import re
import logging

__logging = logging.getLogger(__name__)

import inspect

import naming_convert
import swagger_client_helpers

def get_openstack_client_by_token(token, target_host, swagger_client):
    '''
    Helper function for instantiating a swagger client for openstack
    By providing openstack token, which was being issued by OpenStack/Keytone

    target_host is the host of specified openstack service, e.g. 'http://10.104.252.177:8774' for Nova
    '''
    conf = swagger_client.configuration.Configuration()
    conf.host = target_host

    # It didn't work
    # conf.api_key['X-Auth-Token'] = token
    # # https://stackoverflow.com/questions/57920052/how-to-set-the-bearer-token-in-the-python-api-client-generated-by-swagger-codege
    # # https://github.com/OpenAPITools/openapi-generator/issues/1577
    # # https://github.com/OpenAPITools/openapi-generator/pull/1999/files

    api_client = swagger_client.api_client.ApiClient(configuration=conf)
    # Set header for token 
    api_client.set_default_header('X-Auth-Token', token)
    return api_client

# https://github.com/swagger-api/swagger-codegen/blob/751e59df060b1c3ecf54921e104f2086dfa9f820/modules/swagger-codegen/src/main/resources/python/api.mustache
DOCSTRING_PARAM_REGEX = re.compile(r'        :param (?P<dataType>\S+) (?P<paramName>\S+):(?P<description>.+)?( ?P<required>\(required\))?(?P<optinal>optional(?P<defaultValue>, default to (.+)))?')
def api_method_parameter_type_from_docstring(api_method):
    param = filter(lambda x: x.startswith('        :param'), api_method.__doc__.split('\n'))
    param = filter(lambda x: x != '        :param async_req bool', param)
    # Strip Tailing '\n'
    param = map(lambda x: x.rstrip(), param)

    r = {}
    for i in param:
        __logging.debug('api_method_parameter_type_from_docstring_loop: {}'.format(i))
        m = DOCSTRING_PARAM_REGEX.match(i)
        __logging.debug('api_method_parameter_type_from_docstring_loop_match: {}'.format(str(m)))
        r[str(m.group('paramName'))] = str(m.group('dataType'))

    __logging.debug('api_method_parameter_type_from_docstring: {}'.format(str(r)))
    return r

def api_path_method_to_sdk_api_method(api_doc_section, path_prefix, http_method, swagger_client):
    k = next(iter(api_doc_section.keys()))

    # 'tags' field from current path's API detail and method = post
    # default from go-gin-example
    tags = api_doc_section[k]['#']['detail'][http_method]['tags'] if 'tags' in api_doc_section[k]['#']['detail'][http_method] else [ 'default' ]

    # petstore
    operation_id = api_doc_section[k]['#']['detail'][http_method]['operationId'] if 'operationId' in api_doc_section[k]['#']['detail'][http_method] else None

    api_full_path = path_prefix + k

    classname = naming_convert.operation_tag_to_classname(tags)

    __logging.debug('sdk_api_classname: {}'.format(classname))

    method_name = \
        naming_convert.canonical_to_snake(operation_id) if operation_id else \
        naming_convert.api_path_to_api_method_name(api_full_path) + '_' + http_method

    __logging.debug('sdk_method_name: {}'.format(method_name))

    mock_target_host = 'http://localhost'
    mock_openstack_token = 'MOCK_OPENSTACK_TOKEN'

    # The following client is for API metadata analysis only
    api_client = swagger_client_helpers.get_openstack_client_by_token(
        mock_openstack_token,
        mock_target_host,
        swagger_client=swagger_client,
    )
    api_clz_instance = swagger_client.__dict__[
        classname](api_client=api_client)
    api_method = api_clz_instance.__class__.__dict__[
        method_name
    ]

    return api_method, api_clz_instance

def mock_call_api(self, resource_path, method,
    path_params=None, query_params=None, header_params=None,
    body=None, post_params=None, files=None,
    response_type=None, auth_settings=None, async_req=None,
    _return_http_data_only=None, collection_formats=None,
    _preload_content=True, _request_timeout=None):

    __logging.debug("mock_call_api called with: {}".format(locals()))

    return locals()

def enable_swagger_client_mock_call_api(swagger_client):
    '''
    For capturing response type
    '''
    swagger_client.api_client.ApiClient.call_api = mock_call_api
