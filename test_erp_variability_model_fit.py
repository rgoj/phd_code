from numpy import pi, zeros, random
from numpy.linalg import norm

from erp_variability_model_fit import ERP_Variability_Model_Fit, error_cov, \
                                      fit_variability_model


def test_erp_variability_model_fit_initialization():
    erp_model = ERP_Variability_Model_Fit(n_sub=16, n_gen=5,
                        variability_electrodes='constant',
                        variability_generators='individual',
                        variability_connections='individual')


def test_erp_variability_model_fit_set_and_get_parameters():
    erp_model_1 = ERP_Variability_Model_Fit(n_sub=16, n_gen=5,
                          variability_electrodes='constant',
                          variability_generators='individual',
                          variability_connections='individual')
    erp_model_1.set_random_locations_orientations()
    erp_model_1.set_random_magnitudes()
    erp_model_1.set_random_variability()
    
    erp_model_2 = ERP_Variability_Model_Fit(n_sub=16, n_gen=5,
                          variability_electrodes='constant',
                          variability_generators='individual',
                          variability_connections='individual')
    parameter_list = ['locations and orientations', 'amplitudes', 
                      'generator variance', 'generator covariance',
                      'electrode variance']
    erp_model_2.set_parameters(parameter_list, erp_model_1.get_parameters(
                                                            parameter_list))
    assert erp_model_1.gen_conf == erp_model_2.gen_conf
    assert erp_model_1.sigma_g == erp_model_2.sigma_g
    assert erp_model_1.sigma_c.all() == erp_model_2.sigma_c.all()
    assert erp_model_1.sigma_e == erp_model_2.sigma_e


def test_error_cov():
    erp_model_1 = ERP_Variability_Model_Fit(n_sub=16, n_gen=2,
                          variability_electrodes='constant',
                          variability_generators='individual',
                          variability_connections='individual')
    erp_model_1.set_gen_conf([{'depth': 6, 'theta': 0, 'phi': 0, 
                               'orientation': 0, 'orientation_phi': 0},
                              {'depth': 7, 'theta': 3*pi/8, 'phi': 3*pi/4,
                               'orientation': pi/4, 'orientation_phi': 3*pi/4}])
    erp_model_1.set_random_magnitudes()
    erp_model_1.sigma_e = 1
    erp_model_1.sigma_g = [1,1]
    erp_model_1.sigma_c = zeros((2,2))
    erp_model_1.sigma_c[1,0] = 0.5
    erp_model_1.sigma_c[0,1] = 0.5
    erp_model_1.recalculate_model()
    
    erp_model_2 = ERP_Variability_Model_Fit(n_sub=16, n_gen=5,
                        variability_electrodes='constant',
                        variability_generators='individual',
                        variability_connections='individual')
    erp_model_2.set_gen_conf([{'depth': 5, 'theta': 0, 'phi': 0, 
                             'orientation': 0, 'orientation_phi': 0},
                            {'depth': 6, 'theta': 3*pi/8, 'phi': 3*pi/4,
                             'orientation': pi/4, 'orientation_phi': 3*pi/4}])
    erp_model_2.set_random_magnitudes()
    erp_model_2.sigma_e = 1
    erp_model_2.sigma_g = [1,1]
    erp_model_2.sigma_c = zeros((2,2))
    erp_model_2.sigma_c[1,0] = 0.5
    erp_model_2.sigma_c[0,1] = 0.5
    erp_model_2.recalculate_model()
    
    error_manual = erp_model_1.cov - erp_model_2.cov
    error_manual = norm(error_manual.reshape((erp_model_1.n_el**2,1)),2)
    
    parameter_list = ['locations and orientations']
    error_fun = error_cov(erp_model_1.cov, erp_model_2, parameter_list,
                          erp_model_2.get_parameters(parameter_list))
    
    assert error_fun == error_manual


def test_fit_variability_model():
    erp_model_1 = ERP_Variability_Model_Fit(n_sub=16, n_gen=2,
                          variability_electrodes='constant',
                          variability_generators='individual',
                          variability_connections='individual')
    erp_model_1.set_gen_conf([{'depth': 6, 'theta': 0, 'phi': 0, 
                               'orientation': 0, 'orientation_phi': 0},
                              {'depth': 7, 'theta': 3*pi/8, 'phi': 3*pi/4,
                               'orientation': pi/4, 'orientation_phi': 3*pi/4}])
    erp_model_1.set_random_magnitudes()
    erp_model_1.sigma_e = 1
    erp_model_1.sigma_g = [100000,100000]
    erp_model_1.sigma_c = zeros((2,2))
    erp_model_1.sigma_c[1,0] = 50000
    erp_model_1.sigma_c[0,1] = 50000
    erp_model_1.recalculate_model()
    
    erp_model_2 = ERP_Variability_Model_Fit(n_sub=16, n_gen=2,
                          variability_electrodes='constant',
                          variability_generators='individual',
                          variability_connections='individual')
    random.seed(4)
    erp_model_2.set_random_locations_orientations()
    erp_model_2.set_random_magnitudes()
    erp_model_2.set_random_variability()
    
    parameter_list = ['generator variance', 'generator covariance',
                      'electrode_variance']
    fit_variability_model(erp_model_2, parameter_list, 'covariance',
                          erp_model_1.cov, max_fun_eval=100000)
    erp_model_1.print_model()
    erp_model_2.print_model()
    parameter_list = ['locations and orientations', 'generator variance',
                      'generator covariance', 'electrode variance']
    fit_variability_model(erp_model_2, parameter_list, 'covariance',
                          erp_model_1.cov, max_fun_eval=100000)
    erp_model_1.print_model()
    erp_model_2.print_model()
