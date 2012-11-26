# TODO: Test that covariances, etc. get updated when necessary
# TODO: Check that using the erp_model class gives the same results as doing
# the same calculations by hand

from nose.tools import assert_raises

from erp_variability_model import ERP_Variability_Model


def test_erp_variability_model_correct_initialization():
    erp_variability_model = ERP_Variability_Model(n_sub=16, n_gen=5,
                                variability_electrodes='constant')
    erp_variability_model = ERP_Variability_Model(n_sub=16, n_gen=5,
                                variability_generators='constant')
    erp_variability_model = ERP_Variability_Model(n_sub=16, n_gen=5,
                                variability_electrodes='constant',
                                variability_generators='individual',
                                variability_connections='individual')


def test_erp_variability_model_incorrect_initialization():
    assert_raises(ValueError, ERP_Variability_Model, n_sub=16, n_gen=5,
                  variability_electrodes='error')
    assert_raises(ValueError, ERP_Variability_Model, n_sub=16, n_gen=5,
                  variability_generators='error')
    assert_raises(ValueError, ERP_Variability_Model, n_sub=16, n_gen=5,
                  variability_connections='error')


def assert_up_to_date(erp_model, lead_field, mean, cov_gen, cov):
    assert erp_model.up_to_date['lead field'] == lead_field
    assert erp_model.up_to_date['mean'] == mean
    assert erp_model.up_to_date['covariance generators'] == cov_gen
    assert erp_model.up_to_date['covariance'] == cov


def test_erp_variability_model_recalculate_model():
    erp_model = ERP_Variability_Model(n_sub=16, n_gen=5,
                                variability_electrodes='constant',
                                variability_generators='individual',
                                variability_connections='individual')
    erp_model.set_random_locations_orientations()
    erp_model.set_random_magnitudes()
    erp_model.set_random_variability()
    assert_up_to_date(erp_model, False, False, False, False)
    erp_model.recalculate_model()
    assert_up_to_date(erp_model, True, True, True, True)


def test_erp_variability_model_recalculate_model_manual():
    erp_model = ERP_Variability_Model(n_sub=16, n_gen=5,
                                variability_electrodes='constant',
                                variability_generators='individual',
                                variability_connections='individual')
    erp_model.set_random_locations_orientations()
    erp_model.set_random_magnitudes()
    erp_model.set_random_variability()
    assert_up_to_date(erp_model, False, False, False, False)
    
    erp_model.calculate_lead_field()
    assert_up_to_date(erp_model, True, False, False, False)
    
    erp_model.calculate_mean()
    assert_up_to_date(erp_model, True, True, False, False)

    erp_model.calculate_cov_gen()
    assert_up_to_date(erp_model, True, True, True, False)

    erp_model.calculate_cov()
    assert_up_to_date(erp_model, True, True, True, True)

