import unittest

def canonical_to_snake(canonical: str):
    '''
    addPet -> add_pet
    '''
    return ''.join(map(lambda x: x if not x.isupper() else '_' + x.lower(), canonical))

class TestCanonicalToSnake(unittest.TestCase):
    def test_canonical_to_snake(self):
        self.assertEqual(canonical_to_snake('addPet'), 'add_pet')
        self.assertEqual(canonical_to_snake('createOAuth2Client'), 'create_o_auth2_client')

# operation_tag from swagger spec doc
def operation_tag_to_classname(tags):
    i = '_'.join(tags)
    # is tag name santitized, not from path

    i = i.replace(' ', '')

    # Replace '-', '{', '}', '.'
    i = i.replace(
        '-', '_').replace('{', '').replace('}', '').replace('.', '')

    # Camel
    i = ''.join(map(lambda x: x[0].upper() +
                ('' if len(x) < 2 else x[1:]), i.split('_')))

    return i + 'Api'

class TestOperationTagToClassname(unittest.TestCase):
    def test_operation_tag_to_classname(self):
        pass
        # TODO
        # self.assertEqual(operation_tag_to_classname(), 'Api')

def api_path_to_api_method_name(api_path):
    split_vec = api_path.split('/')
    if split_vec[0] == '':
        split_vec = split_vec[1:]

    def canonical_words_method_name(i):
        r = []
        for j in i:
            j = j.replace(
                '-', '_').replace('{', '').replace('}', '').replace('.', '')
            r += [j]
        return '_'.join(r)

    method_name = canonical_words_method_name(split_vec)

    return method_name

class TestApiPathToApiMethodName(unittest.TestCase):
    def test_api_path_to_api_method_name(self):
        # TODO
        pass
        # self.assertEqual()

if __name__ == '__main__':
    unittest.main()