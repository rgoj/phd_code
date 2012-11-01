import pickle

from nose import with_setup
from numpy import array_equal
from numpy.testing import assert_array_equal, assert_array_almost_equal

from lead_field import calculate_lead_field, Lead_Field


old_code = None

def setup_func():
    global old_code
    with open('test_lead_field_same_output_as_old_code.data', 'r') as f:
        old_code = pickle.load(f)

@with_setup(setup_func)
def test_lead_field_same_output_as_old_code_0():
    global old_code
    lead_field = calculate_lead_field(old_code[0]['gen_conf'])
    assert_array_almost_equal(lead_field, old_code[0]['lead_field'], 17)

@with_setup(setup_func)
def test_lead_field_same_output_as_old_code_1():
    global old_code
    lead_field = calculate_lead_field(old_code[1]['gen_conf'])
    assert_array_almost_equal(lead_field, old_code[1]['lead_field'], 17)

@with_setup(setup_func)
def test_lead_field_same_output_as_old_code_2():
    global old_code
    lead_field = calculate_lead_field(old_code[2]['gen_conf'])
    assert_array_almost_equal(lead_field, old_code[2]['lead_field'], 17)

@with_setup(setup_func)
def test_lead_field_same_output_as_old_code_3():
    global old_code
    lead_field = calculate_lead_field(old_code[3]['gen_conf'])
    assert_array_almost_equal(lead_field, old_code[3]['lead_field'], 17)

@with_setup(setup_func)
def test_lead_field_class():
    global old_code
    lf = Lead_Field()
    for i in range(len(old_code)):
        lead_field = lf.calculate(old_code[i]['gen_conf'])
        assert_array_almost_equal(lead_field, old_code[i]['lead_field'], 17)

@with_setup(setup_func)
def test_lead_field_class_same_output_as_function():
    global old_code
    lf = Lead_Field()
    for i in range(len(old_code)):
        lead_field_class = lf.calculate(old_code[i]['gen_conf'])
        lead_field_function = calculate_lead_field(old_code[i]['gen_conf'])
        assert_array_equal(lead_field_class, lead_field_function)
    
