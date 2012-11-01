import sys

from numpy import pi, mean, zeros, ones, identity, transpose, dot, ndarray
from numpy.linalg import norm
from numpy.random import multivariate_normal, uniform
from scipy import optimize
from matplotlib import pyplot

sys.path.insert(0, 'briskbrain-code/scalingproject')
sys.path.insert(0, 'briskbrain-code/src')

from simulation import random_generator_configuration
from lead_field import Lead_Field
from topographicmap import plot_topographic_map


class ERP_Model():
    def __init__(self, parameter_list=None, parameters=None, n_sub=23, n_gen=1):
        # Optimal bounds for fitting
        self.magnitude_bounds = (0, None) # unnecessary?
        self.depth_bounds = (4.49, 7.05) # cortex
        self.theta_bounds = (0,pi/2)
        self.phi_bounds = (0,2*pi) # unnecessary?
        self.orientation_bounds = (0, pi/2)
        self.orientation_phi_bounds = (0,2*pi) # unnecessary?
        self.gen_variance_bounds = (None, None)
        self.gen_covariance_bounds = (None, None)
        self.el_variance_bounds = (None, None)

        # Parameter limits for randomizing model
        self.magnitude_lim = (1, 10000000)
        self.depth_lim = (4.49, 7.05) # cortex
        self.phi_lim = (0,2*pi)
        self.theta_lim = (0,pi/2)
        self.orientation_lim = (0, pi/2) # cortex
        self.orientation_phi_lim = (0,2*pi)
        self.gen_variance_lim = [0, 1000000]
        self.gen_covariance_lim = [0, 1000000]
        self.el_variance_lim = [0, 20]

        # Variability parameters
        self.sigma_e = 0
        self.sigma_g = 0
        self.sigma_c = 0

        self.n_gen = n_gen
        self.n_sub = n_sub
        self.n_el = 62
        
        self.lf = Lead_Field()

        self.gen_conf = None

        self.up_to_date = {}
        
        if parameter_list == None or 'locations and orientations' not in parameter_list:
            self.set_random_parameters(['locations and orientations']) 
            # Amplitudes should be set separately, but for now they're not...
            #self.set_random_parameters(['locations and orientations', 
            #                            'amplitudes'])
        
        if parameter_list != None:
            self.set_parameters(parameter_list, parameters)
       
        # This is not working, amplitudes are being set above along with
        # locations and orientations, which shouldn't be the case
        #if 'amplitudes' not in parameter_list:
        #    self.set_random_parameters(['amplitudes'])
        
        self.recalculate_model()


    def print_model(self, topographies=False):
        print('ERP Model Parameters')
        print('====================')
        print('Number of generators: ' + str(self.n_gen) + '\n')
        print('Variability')
        print('-----------')
        if self.sigma_e == 0:
            print('* No electrode variance.')
        else:
            print('* Electrode variance: ' + str(self.sigma_e))
        print('* Generator covariance matrix:')
        print(self.cov_gen)
        #if self.n_gen > 1 and isinstance(self.sigma_g, list):
        #    print('* Individual generator variance.')
        #elif self.n_gen > 1:
        #    print('* Generator variance: ' + str(self.sigma_g))
        #if self.n_gen > 1 and isinstance(self.sigma_c, list):
        #    print('* Individual generator covariance.')
        #elif self.n_gen > 1:
        #    print('* Generator variance: ' + str(self.sigma_g))
        for gen in range(self.n_gen):
            print('Generator ' + str(gen+1))
            print('-------------------')
            print('LOCATION, Depth: ' + str(self.gen_conf[gen]['depth']))
            print('LOCATION, Theta: ' + str(self.gen_conf[gen]['theta']))
            print('LOCATION, Phi: ' + str(self.gen_conf[gen]['phi']))
            print('ORIENTATION: ' + str(self.gen_conf[gen]['orientation']))
            print('ORIENTATION, Phi: ' + str(self.gen_conf[gen]['orientation_phi']))
            print('MAGNITUDE: ' + str(self.gen_conf[gen]['magnitude']))
            if topographies:
                pyplot.figure()
                plot_topographic_map((self.gen_conf[gen]['magnitude'] *
                                      self.lf.calculate(
                                      [self.gen_conf[gen]]))[:,0])


    def set_random_parameters(self, parameter_list):
        for i in range(len(parameter_list)):
            if parameter_list[i] == 'locations and orientations':
                self.gen_conf = random_generator_configuration((self.n_gen,
                                self.n_gen), self.depth_lim, self.orientation_lim, 
                                self.magnitude_lim)[0]
            
            elif parameter_list[i] == 'generator variance':
                self.sigma_g = self.gen_variance_lim[0] +\
                        uniform(self.gen_variance_lim[1] -\
                                self.gen_variance_lim[0])
            
            elif parameter_list[i] == 'generator variances individual':
                self.sigma_g = []
                for j in range(self.n_gen):
                    sigma_g = self.gen_variance_lim[0] +\
                                uniform(self.gen_variance_lim[1] -\
                                        self.gen_variance_lim[0])
                    self.sigma_g.append(sigma_g)
            
            elif parameter_list[i] == 'generator covariance':
                self.sigma_c = self.gen_covariance_lim[0] +\
                        uniform(self.gen_covariance_lim[1] -\
                                self.gen_covariance_lim[0])

            elif parameter_list[i] == 'generator covariances individual':
                self.sigma_c = zeros((self.n_gen, self.n_gen))
                for row in range(self.n_gen):
                    for column in range(self.n_gen):
                        if row < column:
                            sigma_c = self.gen_covariance_lim[0] +\
                                        uniform(self.gen_covariance_lim[1] -\
                                                self.gen_covariance_lim[0])
                            self.sigma_c[row,column] = sigma_c
                            self.sigma_c[column,row] = sigma_c
            
            elif parameter_list[i] == 'electrode variance':
                self.sigma_e = self.el_variance_lim[0] +\
                        uniform(self.el_variance_lim[1] -\
                                self.el_variance_lim[0])

        self.up_to_date['lead field'] = False
        self.up_to_date['mean'] = False
        self.up_to_date['covariance generators'] = False
        self.up_to_date['covariance'] = False

    def set_parameters(self, parameter_list, parameters):
        """This function enables you to fit any sets of parameters, i.e.:
        
        * location and orientations
        * amplitudes
        * generator variance
        * generator variances individual
        * generator covariance
        * generator covariances individual
        * electrode variance
        
        You need to pass the list of parameters and a list of their values:
            
            set_parameters(self, parameter_list, parameters),
        
        where parameter_list would be of the form (GLVM model):
            
            ['locations and orientations', 'amplitudes', 'equal variance']
        
        and depending on what parameters are listed, the parameters variable
        will be expected to hold different values, but always in a list
        """
        par = 0 # the current parameter
        for i in range(len(parameter_list)):
            gen_amplitudes = []
            for j in range(self.n_gen):
                gen_amplitudes.append(self.gen_conf[j]['magnitude'])
            if parameter_list[i] == 'locations and orientations':
                self.gen_conf = []
                n_gen_parameters = 5
                # Creating generator configuration
                for gen in range(self.n_gen):
                    self.gen_conf.append({})
                    self.gen_conf[gen]['depth'] = parameters[par]
                    self.gen_conf[gen]['orientation'] = parameters[par + 1]
                    self.gen_conf[gen]['orientation_phi'] = parameters[par + 2]
                    self.gen_conf[gen]['phi'] = parameters[par + 3]
                    self.gen_conf[gen]['theta'] = parameters[par + 4]
                    self.gen_conf[gen]['magnitude'] = gen_amplitudes[gen]
                    par += n_gen_parameters                
                    
            if parameter_list[i] == 'amplitudes':
                if self.gen_conf == None:
                    print('WARNING: Trying to set amplitudes without generators')
                for gen in range(self.n_gen):
                    self.gen_conf[gen]['magnitude'] = parameters[par]
                    par += 1
            
            if parameter_list[i] == 'generator variance':
                self.sigma_g = parameters[par]
                par += 1

            if parameter_list[i] == 'generator variances individual':
                self.sigma_g = list(parameters[par : par + self.n_gen])
                par += self.n_gen

            if parameter_list[i] == 'generator covariance':
                self.sigma_c = parameters[par]
                par += 1
            
            if parameter_list[i] == 'generator covariances individual':
                self.sigma_c = zeros((self.n_gen, self.n_gen))
                for row in range(self.n_gen):
                    for col in range(self.n_gen):
                        if row < col:
                            self.sigma_c[row,col] = parameters[par]
                            self.sigma_c[col,row] = parameters[par]
                            par += 1
            
            if parameter_list[i] == 'electrode variance':
                self.sigma_e = parameters[par]
                par += 1
        
        self.up_to_date['lead field'] = False
        self.up_to_date['mean'] = False
        self.up_to_date['covariance generators'] = False
        self.up_to_date['covariance'] = False

    def get_parameters(self, parameter_list):
        parameters = []
        for i in range(len(parameter_list)):
            if parameter_list[i] == 'locations and orientations':
                for gen in range(self.n_gen):
                    parameters.append(self.gen_conf[gen]['depth'])
                    parameters.append(self.gen_conf[gen]['orientation'])
                    parameters.append(self.gen_conf[gen]['orientation_phi'])
                    parameters.append(self.gen_conf[gen]['phi'])
                    parameters.append(self.gen_conf[gen]['theta'])
            
            if parameter_list[i] == 'amplitudes':
                for gen in range(self.n_gen):
                    parameters.append(self.gen_conf[gen]['magnitude'])
            
            if parameter_list[i] == 'generator variance':
                if not isinstance(self.sigma_g, list):
                    parameters.append(self.sigma_g)
                else:
                    print('WARNING: Variances expected to be identical for \
                          all generators, however self.sigma_g holds a list, \
                          not a single value')

            if parameter_list[i] == 'generator variances individual':
                if isinstance(self.sigma_g, list):
                    for j in range(len(self.sigma_g)):
                        parameters.append(self.sigma_g[j])
                else:
                    print('WARNING: Variances expected to be different for \
                          all generators, however self.sigma_g does not hold \
                          a list')
            
            if parameter_list[i] == 'generator covariance':
                if not isinstance(self.sigma_c, ndarray):
                    parameters.append(self.sigma_c)
                else:
                    print('WARNING: Generator covariance expected to be \
                          identical for all generators, however self.sigma_c \
                          holds an array, not a single value')

            if parameter_list[i] == 'generator covariances individual':
                if isinstance(self.sigma_c, ndarray):
                    for row in range(self.n_gen):
                        for col in range(self.n_gen):
                            if row < col:
                                parameters.append(self.sigma_c[row,col])
                else:
                    print('WARNING: Generator covariances expected to be \
                          different for all generator pairs, however \
                          self.sigma_c is not an array')

            if parameter_list[i] == 'electrode variance':
                parameters.append(self.sigma_e)

        return parameters
    
    def get_bounds(self, parameter_list):
        bounds = []
        for i in range(len(parameter_list)):
            if parameter_list[i] == 'locations and orientations':
                for j in range(self.n_gen):
                    bounds.append(self.depth_bounds)
                    bounds.append(self.orientation_bounds)
                    bounds.append(self.orientation_phi_bounds)
                    bounds.append(self.phi_bounds)
                    bounds.append(self.theta_bounds)
            
            if parameter_list[i] == 'amplitudes':
                for j in range(self.n_gen):
                    bounds.append(self.magnitude_bounds)
        
            if parameter_list[i] == 'generator variance':
                bounds.append(self.gen_variance_bounds)

            if parameter_list[i] == 'generator variances individual':
                for j in range(self.n_gen):
                    bounds.append(self.gen_variance_bounds)

            if parameter_list[i] == 'generator covariance':
                bounds.append(self.gen_covariance_bounds)

            if parameter_list[i] == 'generator covariances individual':
                for j in range(self.n_gen*(self.n_gen-1)/2):
                    bounds.append(self.gen_covariance_bounds)
            
            if parameter_list[i] == 'electrode variance':
                bounds.append(self.el_variance_bounds)

        return bounds
    
    def calculate_lead_field(self):
        self.lead_field = self.lf.calculate(self.gen_conf)
        self.up_to_date['lead field'] = True
        self.up_to_date['mean'] = False
        self.up_to_date['covariance'] = False
        return self.lead_field

    def calculate_mean(self):
        if not self.up_to_date['lead field']: self.calculate_lead_field()
        gen_amplitudes = []
        for i in range(self.n_gen):
            gen_amplitudes.append(self.gen_conf[i]['magnitude'])
        self.mean = dot(self.lead_field, gen_amplitudes)
        self.up_to_date['mean'] = True
        return self.mean

    def calculate_cov_gen(self):
        self.cov_gen = zeros((self.n_gen, self.n_gen))
        for row in range(self.n_gen):
            for column in range(self.n_gen):
                if row == column:
                    if isinstance(self.sigma_g, list):
                        self.cov_gen[row,column] = self.sigma_g[row]
                    else:
                        self.cov_gen[row,column] = self.sigma_g
                elif column > row:
                    if isinstance(self.sigma_c, ndarray):
                        self.cov_gen[row,column] = self.sigma_c[row,column]
                        self.cov_gen[column,row] = self.sigma_c[row,column]
                    else:
                        self.cov_gen[row,column] = self.sigma_c
                        self.cov_gen[column,row] = self.sigma_c
        
        self.up_to_date['covariance generators'] = True
        self.up_to_date['covariance'] = False

        return self.cov_gen

    def calculate_cov(self):
        if not self.up_to_date['lead field']: self.calculate_lead_field()
        if not self.up_to_date['covariance generators']:
            self.calculate_cov_gen()
        self.cov = dot(dot(self.lead_field, self.cov_gen),
                  transpose(self.lead_field)) + self.sigma_e *\
                  identity(self.n_el)
        self.up_to_date['covariance'] = True
        return self.cov

    def simulate(self):
        self.data = multivariate_normal(self.mean,self.cov,self.n_sub)
        return self.data
    
    def recalculate_model(self):
        self.calculate_lead_field()
        self.calculate_mean()
        self.calculate_cov()
        self.simulate()


def error_cov(cov_data, erp_model, parameter_list, parameters):
    erp_model.set_parameters(parameter_list, parameters)
    erp_model.calculate_cov()
    # TODO: erp_model.cov should be a property to avoid the possibility of using
    # outdated covariance when accessing it
    error = cov_data - erp_model.cov
    error = norm(error.reshape((erp_model.n_el**2,1)), 2)
    return error


def fit_model_to_covariance(cov_data, erp_model, parameter_list,
                            method='fmin_tnc', no_bounds=False, disp=False):
    fn = lambda parameters: error_cov(cov_data, erp_model, parameter_list,
                                         parameters)
    
    initial_parameters = erp_model.get_parameters(parameter_list)
    if no_bounds:
        print('Running fitting without bounds, was this intended?')
        parameter_bounds = None
    else:
        parameter_bounds = erp_model.get_bounds(parameter_list)
    
    start_error = fn(initial_parameters)
    if disp:
        print('Starting error: ' + str(start_error))

    if method == 'fmin_tnc': # Supposedly the best methods for bounds
        output = optimize.fmin_tnc(fn, initial_parameters, 
                                   bounds=parameter_bounds, maxfun=100,
                                   disp=5, approx_grad=True)
        if disp:
            print('After ' + str(output[1]) + \
                  ' iterations, the TNC algorithm returned: ' +\
                  optimize.tnc.RCSTRINGS[output[2]])
    if method == 'minimize_l-bfgs-b':
        output = optimize.minimize(fn, initial_parameters, 
                                   bounds=parameter_bounds, 
                                   options={'disp':1},
                                   method='l-bfgs-b')
    if method == 'minimize_cobyla':
        output = optimize.minimize(fn, initial_parameters, 
                                   bounds=parameter_bounds, 
                                   options={'disp':2},
                                   method='cobyla')
    elif method == 'minimize_slsqp':
        output = optimize.minimize(fn, initial_parameters, 
                                   bounds=parameter_bounds, 
                                   options={'disp':2},
                                   method='slsqp')
    elif method == 'fmin_slsqp':
        output = optimize.fmin_slsqp(fn, initial_parameters,
                                     bounds=parameter_bounds,
                                     full_output=True,iprint=2)
    
    end_error = fn(erp_model.get_parameters(parameter_list))
    if disp:
        print('Ending error: ' + str(fn(end_error)))
    
    erp_model.recalculate_model()

    return [output, start_error, end_error]
    

def fit_model(erp_model, fit_type, target_type, target):
    # Fit types could be:
    # 'sources'
    # 'variability'
    # 'all'
    #
    # Target types could be:
    # 'mean'
    # 'covariance'
    # ['mean', 'covariance']
    if fit_type == 'source' and target_type == 'mean':
        mean_data = target
        fn = lambda parameters: error_sources_real_sim(mean_data,
                            parameters[0], parameters[1], parameters[2],
                            parameters[3], parameters[4], parameters[5])
        
        gen_conf = random_generator_configuration((1,1), depth_lim,
                                                  orientation_lim,
                                                  magnitude_lim)[0]
        
        full_output = optimize.fmin_slsqp(fn, [gen_conf[0]['depth'],
                        gen_conf[0]['magnitude'], gen_conf[0]['orientation'],
                        gen_conf[0]['orientation_phi'], gen_conf[0]['phi'], 
                        gen_conf[0]['theta']], bounds=[depth_bounds, 
                        magnitude_bounds, orientation_bounds, orientation_phi_bounds,
                        phi_bounds, theta_bounds], full_output=True, iprint=0)
    
        
