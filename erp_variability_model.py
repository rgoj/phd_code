import sys
sys.path.insert(0, 'old/scalingproject')
sys.path.insert(0, 'util')

from numpy import pi, dot, zeros, ndarray, transpose, identity, sqrt, newaxis
from numpy.random import multivariate_normal, uniform
from matplotlib import pyplot

from lead_field import Lead_Field
from generator_configuration import random_generator_placement
from topographicmap import plot_topographic_map, plot_topographic_map_array
from variability_visualization import plot_covariance_matrix


#TODO sigma should be sigma_sq_ throghout, or var, because it's variance, so
# sigma squared


class ERP_Variability_Model():
    def __init__(self, n_sub, n_gen, variability_electrodes='none',
                 variability_generators='none', 
                 variability_connections='none'):
        self.n_gen = n_gen # generators
        self.n_sub = n_sub # subjects
        self.n_el = 60 # Hard-coded to use a specific electrode set
        
        self.up_to_date = {}
        self.set_parameter_limits()
        self.gen_conf = None
        self.lf = Lead_Field()

        self.set_variability_type(variability_electrodes,
                                  variability_generators,
                                  variability_connections)
        self.sigma_e = 0
        self.sigma_g = zeros(self.n_gen)
        self.sigma_c = zeros((self.n_gen, self.n_gen))


    def print_model(self, topographies=False):
        print('ERP Model Parameters')
        print('====================')
        print('Number of generators: ' + str(self.n_gen) + '\n')
        print('Variability')
        print('-----------')
        print('* Electrodes (self.sigma_e)')
        print self.sigma_e
        print('* Generators (self.cov_gen)')
        print self.cov_gen
        print('* Final covariance matrix (self.cov)')
        print self.cov
        for gen in range(self.n_gen):
            print('\nGenerator ' + str(gen+1))
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
    

    def plot_model(self, to_plot):
        for one_plot in to_plot:
            if one_plot == 'mean':
                plot_topographic_map(self.mean)
                pyplot.title('Topographic map of mean')
                
                # Individual generator means
                pyplot.figure()
                for i in range(self.n_gen):
                    pyplot.subplot(1,self.n_gen,i)
                    plot_topographic_map(self.mean)
                pyplot.figtext(0.5, 0.75, 'Topographic maps of means of each generator',
                               ha='center')
                
            if one_plot == 'variance':
                pyplot.figure()
                plot_topographic_map(self.cov.diagonal())
                pyplot.title('Topographic map of variance')
                
                # Individual generator variances
                pyplot.figure()
                for i in range(self.n_gen):
                    pyplot.subplot(1,self.n_gen,i)
                    single_cov = dot(transpose(self.lead_field[:,i][newaxis]),
                                     self.lead_field[:,i][newaxis])
                    if self.variability_generators == 'constant':
                        single_cov = self.sigma_g * single_cov
                    elif self.variability_generators == 'individual':
                        single_cov = self.sigma_g[i] * single_cov
                    plot_topographic_map(single_cov.diagonal())
                pyplot.figtext(0.5, 0.75, 'Topographic maps of variance of each generator',
                               ha='center')

            if one_plot == 'covariance matrix':
                pyplot.figure()
                plot_covariance_matrix(self.data,self.cov)
                pyplot.title('Covariance matrix')


    def set_parameter_limits(self):
        # Parameter bounds for randomizing model parameters
        self.limits = {}
        # Location and orientation
        self.limits['depth']= (4.49,7.05) # roughly the cortex
        self.limits['phi'] = (0,2*pi)
        self.limits['theta'] = (0,pi/2)
        self.limits['orientation'] = (0, pi/2) # cortex
        self.limits['orientation_phi'] = (0,2*pi)
        # Magnitude
        self.limits['magnitude'] = (0, 1000)
        # Variability
        self.limits['generator_variance'] = [0, 1000000]
        self.limits['electrode_variance'] = [0, 20]
        # Covariance needs no limits becuase it is limited by the variance of
        # the two generators in question
        #self.limits['generator_covariance'] = [0, 1000000]
        # Constant number of generators
        self.limits['n_gen'] = (self.n_gen, self.n_gen)


    def set_variability_type(self, variability_electrodes, 
                             variability_generators, variability_connections):
        if variability_electrodes not in ['constant', 'individual', 'none']:
            raise ValueError
        else:
            self.variability_electrodes = variability_electrodes
        
        if variability_generators not in ['constant', 'individual', 'none']:
            raise ValueError
        else:
            self.variability_generators = variability_generators
        
        if variability_connections not in ['individual', 'none']:
            raise ValueError
        else:
            self.variability_connections = variability_connections

    
    def set_gen_conf(self, gen_conf):
        self.gen_conf = gen_conf
        self.n_gen = len(gen_conf)


    def set_random(self):
        self.set_random_locations_orientations()
        self.set_random_magnitudes()
        self.set_random_variability()


    def set_random_locations_orientations(self):
        self.gen_conf = random_generator_placement(self.limits)
        self.up_to_date['lead field'] = False
        self.up_to_date['mean'] = False
        self.up_to_date['covariance generators'] = False
        self.up_to_date['covariance'] = False


    def set_random_magnitudes(self):
        limits = self.limits['magnitude']
        for i in range(self.n_gen):
            self.gen_conf[i]['magnitude'] = limits[0] + uniform(limits[1] - limits[0])
        self.up_to_date['mean'] = False


    def set_random_variability(self):
        self.set_random_variability_electrodes()
        self.set_random_variability_generators()
        self.set_random_variability_connections()
    
    def set_random_variability_electrodes(self):
        limits = self.limits['electrode_variance']
        if self.variability_electrodes == 'none':
            self.sigma_e = 0
        elif self.variability_electrodes == 'constant':
            self.sigma_e = limits[0] + uniform(limits[1] - limits[0])
        elif self.variability_electrodes == 'individual':
            self.sigma_e = []
            for i in range(self.n_el):
                self.sigma_e.append(limits[0] + uniform(limits[1] - limits[0]))
        
    def set_random_variability_generators(self):
        limits = self.limits['generator_variance']
        if self.variability_generators == 'none':
            self.sigma_g = 0
        elif self.variability_generators == 'constant':
            self.sigma_g = limits[0] + uniform(limits[1] - limits[0])
        elif self.variability_generators == 'individual':
            self.sigma_g = []
            for i in range(self.n_gen):
                self.sigma_g.append(limits[0] + uniform(limits[1] - limits[0]))
        
    def set_random_variability_connections(self):
        if self.variability_connections == 'none':
            self.sigma_c = zeros((self.n_gen, self.n_gen))
        elif self.variability_connections == 'individual':
            self.sigma_c = zeros((self.n_gen, self.n_gen))
            for row in range(self.n_gen):
                for column in range(self.n_gen):
                    if row < column:
                        sigma_c = uniform(sqrt(self.sigma_g[row] *
                                               self.sigma_g[column]))
                        self.sigma_c[row, column] = sigma_c
                        self.sigma_c[column, row] = sigma_c
        

    def calculate_lead_field(self):
        self.lead_field = self.lf.calculate(self.gen_conf)
        self.up_to_date['lead field'] = True
        self.up_to_date['mean'] = False
        self.up_to_date['covariance generators'] = False
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
        if not self.up_to_date['lead field']: self.calculate_lead_field()
        
        self.cov_gen = zeros((self.n_gen, self.n_gen))
        for row in range(self.n_gen):
            for column in range(self.n_gen):
                if row == column:
                    if self.variability_generators == 'individual':
                        self.cov_gen[row,column] = self.sigma_g[row]
                    elif self.variability_generators == 'constant':
                        self.cov_gen[row,column] = self.sigma_g
                elif column > row:
                    if self.variability_connections == 'individual':
                        self.cov_gen[row,column] = self.sigma_c[row,column]
                        self.cov_gen[column,row] = self.sigma_c[row,column]
        
        self.up_to_date['covariance generators'] = True
        self.up_to_date['covariance'] = False

        return self.cov_gen


    def calculate_cov(self):
        if not self.up_to_date['lead field']: self.calculate_lead_field()
        if not self.up_to_date['covariance generators']:
            self.calculate_cov_gen()
        
        # TODO: Make it work for individual electrode variance as well
        self.cov = dot(dot(self.lead_field, self.cov_gen),
                  transpose(self.lead_field)) + self.sigma_e *\
                  identity(self.n_el)
        
        self.up_to_date['covariance'] = True
        
        return self.cov


    def simulate(self):
        self.data = multivariate_normal(self.mean,self.cov,self.n_sub)
        return self.data


    def recalculate_model(self):
        self.up_to_date['lead field'] = False
        self.up_to_date['mean'] = False
        self.up_to_date['covariance generators'] = False
        self.up_to_date['covariance'] = False
        
        self.calculate_lead_field()
        self.calculate_mean()
        self.calculate_cov()
        self.simulate()
            
