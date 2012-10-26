import pickle

from nose import with_setup
from numpy import array_equal

from lead_field import calculate_lead_field


old_code = None

def setup_func():
    global old_code
    with open('test_lead_field_same_output_as_old_code.data', 'r') as f:
        old_code = pickle.load(f)

@with_setup(setup_func)
def test_lead_field_same_output_as_old_code():
    global old_code
    for i in range(len(old_code)):
        lead_field = calculate_lead_field(old_code[i]['gen_conf'])
        assert array_equal(lead_field, old_code[i]['lead_field'])
