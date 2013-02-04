import time
import pickle
import sys
sys.path.insert(0, 'meetpy')
sys.path.insert(0, 'meetpy/util')
sys.path.insert(0, 'meetpy/old/scalingproject')

from scipy import optimize
from numpy import random
from numpy.linalg import norm

from read_example_data import read_example_data
from erp_variability_model_fit import ERP_Variability_Model_Fit,\
                                      fit_variability_model, error_mean,\
                                      error_cov, error_mean_and_cov


def run_fitting_schemes(model_types, number_of_generators, random_seeds,
                        schemes, mean_data, cov_data, max_fun_eval=100000):
    all_models = def_all_models_dict(schemes, model_types, 
                                     number_of_generators, random_seeds)

    overall_start_time = time.time()
    for (model_type, n_gen, seed, scheme) in [(model_type, n_gen, seed, scheme)
                                              for scheme in schemes
                                              for model_type in model_types 
                                              for n_gen in number_of_generators
                                              for seed in random_seeds]:
        random.seed(seed)
        entry = def_empty_entry_dict()
        erp_model = ERP_Variability_Model_Fit(n_sub=23, n_gen=n_gen)
        parameter_list = prepare_variability_parameter_list(erp_model, 
                                                            model_type, n_gen)
        # If parameter_list is None that means the combination of model_type
        # and number of generators shouldn't be taken into account.
        if parameter_list is None:
            continue
        parameter_list.insert(0,'amplitudes')
        parameter_list.insert(0,'locations and orientations')
        erp_model.set_random_parameters(parameter_list)

        description = 'Fitting scheme: ' + scheme + ', model type: ' +\
                      model_type + ', with ' + str(n_gen) +\
                      ' generator(s) and seed ' + str(seed)
        print(description + '\n' + '=' * len(description))
        
        entry['starting_error_mean'] = error_mean(mean_data, erp_model, [], 
                []) / norm(mean_data, 2)
        entry['starting_error_covariance'] = error_cov(cov_data, erp_model, 
                [], []) / norm(cov_data.reshape((erp_model.n_el**2,1)), 2)
        entry['starting_error_mean_and_covariance'] =\
                error_mean_and_cov(mean_data, cov_data, erp_model, [], [])
        print('Starting error on mean: ' + str(entry['starting_error_mean']))
        print('Starting error on covariance: ' +\
              str(entry['starting_error_covariance']))
        print('Starting error on mean and covariance combined: ' +\
              str(entry['starting_error_mean_and_covariance']) + '\n')
        
        # Simplifying calling of fitting functions to make fitting scheme code
        # clearer and easier to read.
        fit_amplitudes_lambda = lambda erp_model, with_locations:\
                fit_amplitudes(erp_model, n_gen, seed, mean_data,
                               with_locations=with_locations,
                               max_fun_eval=max_fun_eval)
        fit_variability_lambda = lambda erp_model, with_locations:\
                fit_variability(erp_model, model_type, n_gen, seed, cov_data, 
                               with_locations=with_locations,
                               max_fun_eval=max_fun_eval)
        
        if scheme == 'covariance and locations':
            entry['fits'].append(fit_variability_lambda(erp_model, True))
        elif scheme == 'amplitudes, covariance and locations':
            entry['fits'].append(fit_amplitudes_and_variability(erp_model, 
                    model_type, n_gen, seed, mean_data, cov_data,
                    with_locations=True, max_fun_eval=max_fun_eval))
        if scheme == 'amplitudes and locations, then covariance':
            entry['fits'].append(fit_amplitudes_lambda(erp_model, True))
            entry['fits'].append(fit_variability_lambda(erp_model, False))
        if scheme == 'covariance and locations, then amplitudes':
            entry['fits'].append(fit_variability_lambda(erp_model, True))
            entry['fits'].append(fit_amplitudes_lambda(erp_model, False))
        if scheme == 'amplitudes and locations, then covariance and ' +\
                     'locations, multiple times':
            n_repeats = 10
            for i in range(n_repeats):
                entry['fits'].append(fit_amplitudes_lambda(erp_model, True))
                entry['fits'].append(fit_variability_lambda(erp_model, True))

        #if entry['fits'][-1] != None:
        entry['scheme'] = scheme
        entry['erp_model'] = erp_model
        all_models[scheme][model_type][n_gen][seed] = entry

        entry['final_error_mean'] = error_mean(mean_data, erp_model, [], [])\
                / norm(mean_data, 2)
        entry['final_error_covariance'] = error_cov(cov_data, erp_model, [],
                []) / norm(cov_data.reshape((erp_model.n_el**2,1)), 2)
        entry['final_error_mean_and_covariance'] =\
                error_mean_and_cov(mean_data, cov_data, erp_model, [], [])
        print('Final error on mean: ' + str(entry['final_error_mean']))
        print('Final error on covariance: ' +\
              str(entry['final_error_covariance']))
        print('Final error on mean and covariance combined: ' +\
              str(entry['final_error_mean_and_covariance']) + '\n')
        
    print('Overall time elapsed: ' + str(round(time.time() -\
                                               overall_start_time,2)))

    return all_models


def def_all_models_dict(schemes, model_types, number_of_generators, 
                        random_seeds):
    """
    The all_models dictionary will hold all ERP model objects after fitting
    along with information about the fitting procedures performed and the final
    results. 
    
    Each ERP model object will be held in a separate entry for model type,
    number of generators and randomization seed, such that:
        
        all_models[scheme][model_type][n_gen][seed]
    
    will hold an ERP model object and other information in the dictionary 
    defined by:

        empty_entry = def_empty_entry_dict()
    """
    all_models = {}
    for scheme in schemes:
        all_models[scheme] = {}
        for model_type in model_types:
            all_models[scheme][model_type] = {}
            for n_gen in number_of_generators:
                all_models[scheme][model_type][n_gen] = {}
                for seed in random_seeds:
                    all_models[scheme][model_type][n_gen][seed] = None
    return all_models


def def_empty_entry_dict():
    """
    The empty_entry dictionary defines what information should be stored in:

        entry = all_models[scheme][model_type][n_gen][seed]

    for each model type, number of generators and random seed.
    """
    empty_entry = {}   
    empty_entry['starting_error_mean'] = None
    empty_entry['starting_error_covariance'] = None
    empty_entry['starting_error_mean_and_covariance'] = None
    empty_entry['final_error_mean'] = None
    empty_entry['final_error_covariance'] = None
    empty_entry['final_error_mean_and_covariance'] = None
    empty_entry['scheme'] = None
    empty_entry['fits'] = []
    empty_entry['erp_model'] = None

    return empty_entry


def fit_amplitudes(erp_model, n_gen, seed, mean_data, with_locations=False,
                   max_fun_eval=100000):
    parameter_list = ['amplitudes']
    if with_locations is True:
        parameter_list.insert(0,'locations and orientations')
        description = 'Fit of generator locations and amplitudes to mean'
    else:
        description = 'Fit of generator amplitudes to mean'
    print(description + '\n' + '-' * len(description))

    start_time = time.time()
    output = fit_variability_model(erp_model,
                                   parameter_list, 
                                   fit_to='mean', fit_data=mean_data, 
                                   method='tnc', bounds= True, 
                                   max_fun_eval=max_fun_eval,
                                   disp=True)
    elapsed_time = time.time() - start_time
    print('* Elapsed time: ' + str(elapsed_time) + 's\n')

    return fit_info(erp_model, description, output)


def fit_variability(erp_model, model_type, n_gen, seed, cov_data, 
                    with_locations=False, max_fun_eval=100000):
    parameter_list = prepare_variability_parameter_list(erp_model, model_type,
                                                        n_gen)
    if with_locations is True:
        parameter_list.insert(0,'locations and orientations')
        description = 'Fit of generator locations and variability to ' +\
                      'covariance'
    else:
        description = 'Fit of variability to covariance'
    print(description + '\n' + '-' * len(description))
    
    start_time = time.time()
    output = fit_variability_model(erp_model, parameter_list,
                                   fit_to='covariance', 
                                   fit_data=cov_data, 
                                   method='tnc', bounds= True,
                                   max_fun_eval=max_fun_eval, 
                                   disp=True)
    elapsed_time = time.time() - start_time
    print('* Elapsed time: ' + str(elapsed_time) + 's\n')

    return fit_info(erp_model, description, output)


def fit_amplitudes_and_variability(erp_model, model_type, n_gen, seed, 
                                   mean_data, cov_data, with_locations=False, 
                                   max_fun_eval=100000):
    parameter_list = prepare_variability_parameter_list(erp_model, model_type,
                                                        n_gen)
    parameter_list.insert(0,'amplitudes')
    
    if with_locations is True:
        parameter_list.insert(0,'locations and orientations')
        description = 'Fit of generator locations, amplitudes and ' +\
                      'variability to mean and covariance'
    else:
        description = 'Fit of generator amplitudes and variability to ' +\
                      'mean and covariance'
    print(description + '\n' + '-' * len(description))
    
    start_time = time.time()
    output = fit_variability_model(erp_model, parameter_list,
                                   fit_to='mean and covariance', 
                                   fit_data=[mean_data, cov_data], 
                                   method='tnc', bounds= True, 
                                   max_fun_eval=max_fun_eval, disp=True)
    elapsed_time = time.time() - start_time
    print('* Elapsed time: ' + str(elapsed_time) + 's\n')

    return fit_info(erp_model, description, output)


def prepare_variability_parameter_list(erp_model, model_type, n_gen):
    variability_electrodes='none' 
    variability_generators='none' 
    variability_connections='none'
    
    if model_type == 'cELVM':
        parameter_list = ['electrode variance']
        variability_electrodes = 'constant' 
    elif model_type == 'cGLVM':
        parameter_list = ['generator variance']
        variability_generators = 'constant'
    elif model_type == 'iGLVM':
        if n_gen < 2:
            return None
        parameter_list = ['generator variance']
        variability_generators='individual' 
    elif model_type == 'iGiCLVM':
        if n_gen < 2:
            return None
        parameter_list = ['generator variance', 
                          'generator covariance']
        variability_generators='individual' 
        variability_connections='individual'
    elif model_type == 'iGiCcELVM':
        if n_gen < 2:
            return None
        parameter_list = ['generator variance', 
                          'generator covariance', 
                          'electrode variance']
        variability_electrodes='constant'
        variability_generators='individual'
        variability_connections='individual'

    erp_model.set_variability_type(variability_electrodes,
                                   variability_generators,
                                   variability_connections)
    
    return parameter_list


def fit_info(erp_model, description, output):
    """
    Common information that should be saved for all fits performed. It can then
    be accessed from:

        all_models[scheme][model_type][n_gen][seed]['fits'][i_fit]

    where i_fit is the index of the fit corresponding to the order in which 
    fits were performed.
    """
    fit_info = {}
    fit_info['erp_model'] = erp_model
    fit_info['fit_description'] = description
    fit_info['starting_error'] = output[1]
    fit_info['fit_iterations'] = output[0][1]
    fit_info['fit_result'] = output[0][2]
    fit_info['fit_message'] = optimize.tnc.RCSTRINGS[output[0][2]]
    fit_info['final_error'] = output[2]
    
    return fit_info
