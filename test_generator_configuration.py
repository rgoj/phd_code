from nose import with_setup
from numpy import array_equal
from numpy.testing import assert_array_equal, assert_array_almost_equal

from lead_field import calculate_lead_field, Lead_Field
from generator_configuration import random_generator_placement


def test_random_generator_placement_good_for_lead_field_calculation():
    gen_conf = random_generator_placement()
    calculate_lead_field(gen_conf)
