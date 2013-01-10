from numpy import zeros, pi
from numpy.linalg import norm
from scipy import optimize

from erp_variability_model import ERP_Variability_Model

class ERP_Variability_Model_Fit(ERP_Variability_Model):
    """This class inherits all the functionality of ERP_Variability_Model and
    adds functions set_parameters and get_parameters that allow objects of it's
    class to be fit to ERP data using methods defined below in this file. The
    added functionality allows all the different parameters of the
    ERP_Variability_Model to be set using a single list of parameters.
    """
    def __init__(self, n_sub, n_gen, variability_electrodes='none',
                 variability_generators='none', 
                 variability_connections='none'):
        ERP_Variability_Model.__init__(self, n_sub, n_gen, 
                                       variability_electrodes,
                                       variability_generators,
                                       variability_connections)
        
        # Parameter bounds for fitting
        self.magnitude_bounds = (0, None) # unnecessary?
        self.depth_bounds = (4.49, 7.05) # cortex # TODO: Check values
        self.theta_bounds = (0,pi/2)
        self.phi_bounds = (0,2*pi) # unnecessary?
        self.orientation_bounds = (0, pi/2)
        self.orientation_phi_bounds = (0,2*pi) # unnecessary?
        self.gen_variance_bounds = (None, None)
        self.gen_covariance_bounds = (None, None)
        self.el_variance_bounds = (None, None)


    def set_random_parameters(self, parameter_list):
        for i in range(len(parameter_list)):
            if parameter_list[i] == 'locations and orientations':
                self.set_random_locations_orientations()
            elif parameter_list[i] == 'amplitudes':
                self.set_random_magnitudes()
            elif parameter_list[i] == 'generator variance':
                self.set_random_variability_generators()
            elif parameter_list[i] == 'generator covariance':
                self.set_random_variability_connections()
            elif parameter_list[i] == 'electrode variance':
                self.set_random_variability_electrodes()


    def set_parameters(self, parameter_list, parameters):
        """Allowed parameter_list arguments:
        
        * 'locations and orientations'
        * 'amplitudes'
        * 'generator variance'
        * 'generator covariance'
        * 'electrode variance'
        
        Example usage:
            
            set_parameters(self, ['locations and orientations', 'amplitudes',
                                  'generator variance'], [6, ..., 100000])
        """
        par = 0 # this will be used to walk through all parameters in the
                # parameters variable
        for i in range(len(parameter_list)):
            if parameter_list[i] == 'locations and orientations':
                gen_amplitudes = []
                if self.gen_conf != None:
                    for j in range(self.n_gen):
                        gen_amplitudes.append(self.gen_conf[j]['magnitude'])
                else:
                    for j in range(self.n_gen):
                        gen_amplitudes.append(0)
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
                    
            elif parameter_list[i] == 'amplitudes':
                for gen in range(self.n_gen):
                    self.gen_conf[gen]['magnitude'] = parameters[par]
                    par += 1
            
            elif parameter_list[i] == 'generator variance':
                if self.variability_generators == 'constant':
                    self.sigma_g = parameters[par]
                    par += 1
                elif self.variability_generators == 'individual':
                    self.sigma_g = list(parameters[par : par + self.n_gen])
                    par += self.n_gen

            elif parameter_list[i] == 'generator covariance':
                if self.variability_connections == 'individual':
                    self.sigma_c = zeros((self.n_gen, self.n_gen))
                    for row in range(self.n_gen):
                        for col in range(self.n_gen):
                            if row < col:
                                self.sigma_c[row,col] = parameters[par]
                                self.sigma_c[col,row] = parameters[par]
                                par += 1
            
            elif parameter_list[i] == 'electrode variance':
                if self.variability_electrodes == 'constant':
                    self.sigma_e = parameters[par]
                    par += 1
                elif self.variabiliy_electrodes == 'individual':
                    self.sigma_e = list(parameters[par : par + self.n_el])
                    par += self.n_el
        
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
            
            elif parameter_list[i] == 'amplitudes':
                for gen in range(self.n_gen):
                    parameters.append(self.gen_conf[gen]['magnitude'])
            
            elif parameter_list[i] == 'generator variance':
                if self.variability_generators == 'constant':
                    parameters.append(self.sigma_g)
                elif self.variability_generators == 'individual':
                    for j in range(len(self.sigma_g)):
                        parameters.append(self.sigma_g[j])

            elif parameter_list[i] == 'generator covariance':
                if self.variability_connections == 'individual':
                    for row in range(self.n_gen):
                        for col in range(self.n_gen):
                            if row < col:
                                parameters.append(self.sigma_c[row,col])
                
            elif parameter_list[i] == 'electrode variance':
                if self.variability_electrodes == 'constant':
                    parameters.append(self.sigma_e)
                if self.variability_electrodes == 'individual':
                    for j in range(len(self.sigma_e)):
                        parameters.append(self.sigma_e[j])

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
                if self.variability_generators == 'constant':
                    bounds.append(self.gen_variance_bounds)
                elif self.variability_generators == 'individual':
                    for j in range(self.n_gen):
                        bounds.append(self.gen_variance_bounds)

            if parameter_list[i] == 'generator covariance':
                if self.variability_connections == 'individual':
                    for j in range(self.n_gen*(self.n_gen-1)/2):
                        bounds.append(self.gen_covariance_bounds)

            if parameter_list[i] == 'electrode variance':
                if self.variability_electrodes == 'constant':
                    bounds.append(self.el_variance_bounds)
                if self.variability_electrodes == 'individual':
                    for j in range(len(self.sigma_e)):
                        bounds.append(self.el_variance_bounds)

        return bounds


def error_mean(mean_data, erp_model, parameter_list, parameters):
    erp_model.set_parameters(parameter_list, parameters)
    erp_model.calculate_mean()
    error = mean_data - erp_model.mean
    error = norm(error, 2)
    return error


def error_cov(cov_data, erp_model, parameter_list, parameters):
    erp_model.set_parameters(parameter_list, parameters)
    erp_model.calculate_cov()
    error = cov_data - erp_model.cov
    error = norm(error.reshape((erp_model.n_el**2,1)), 2)
    return error


def fit_variability_model(erp_model, parameter_list, fit_to, fit_data,
                          method='tnc', bounds=True, max_fun_eval=100, 
                          disp=True):
    if fit_to == 'mean':
        fn = lambda parameters: error_mean(fit_data, erp_model, parameter_list,
                                          parameters)
    if fit_to == 'covariance':
        fn = lambda parameters: error_cov(fit_data, erp_model, parameter_list,
                                          parameters)
    
    if bounds:
        parameter_bounds = erp_model.get_bounds(parameter_list)
    else:
        parameter_bounds = None
    
    initial_parameters = erp_model.get_parameters(parameter_list)
    start_error = fn(initial_parameters)
    if disp: print('* Starting error: ' + str(start_error))

    if method == 'tnc':
        output = optimize.fmin_tnc(fn, initial_parameters,
                                   bounds=parameter_bounds,
                                   maxfun=max_fun_eval, disp=5,
                                   approx_grad=True)
        if disp: print('* After ' + str(output[1]) + ' iterations, the TNC ' +\
                       'algorithm returned: ' +\
                       optimize.tnc.RCSTRINGS[output[2]])
    
    erp_model.recalculate_model()
    
    end_error = fn(erp_model.get_parameters(parameter_list))
    if disp: print('* Final error: ' + str(end_error))
    
    return [output, start_error, end_error]
