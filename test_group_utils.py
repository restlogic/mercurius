import copy 

def test_group_summary(test_group, init_deepcopy=True):
    if init_deepcopy:
        test_group = copy.deepcopy(test_group)
    for i in test_group.keys():
        if i == '#':
            del test_group['#']['detail']
        else:
            test_group_summary(test_group[i], init_deepcopy=False)

    return test_group
