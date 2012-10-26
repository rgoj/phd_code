from __future__ import division

import pickle
import sys
sys.path.insert(0, 'scalingproject')
sys.path.insert(0, 'src')

from numpy import pi

from simulation import random_generator_configuration
from lead_field import calculate_lead_field


descriptions = []
gen_confs = []
lead_fields = []

descriptions.append('A single dipole, located at top of sphere, oriented ' +\
                    'parallel to the surface')
gen_confs.append([{'depth': 6, 'theta': 0, 'phi': 0, 'orientation': 0,
                   'orientation_phi': 0, 'magnitude': 1}])
lead_fields.append(calculate_lead_field(gen_confs[-1]))

descriptions.append('A single dipole, located at top of sphere, oriented ' +\
                    'perpendicular to the surface')
gen_confs.append([{'depth': 5, 'theta': 0, 'phi': 0, 'orientation': pi/2,
                   'orientation_phi': 0, 'magnitude': 1}])
lead_fields.append(calculate_lead_field(gen_confs[-1]))

descriptions.append('A single dipole, at a specific location')
gen_confs.append([{'depth': 7, 'theta': 3*pi/8, 'phi': 3*pi/4, 
                   'orientation': pi/4, 'orientation_phi': 3*pi/4, 
                   'magnitude': 1}])
lead_fields.append(calculate_lead_field(gen_confs[-1]))

descriptions.append('5 generators in a random configuration (with specified' +\
                    'seed')
gen_confs.append(random_generator_configuration((5,5))[0])
lead_fields.append(calculate_lead_field(gen_confs[-1]))

old_code = []
for i in range(len(gen_confs)):
    old_code.append({'description': descriptions[i],
                     'gen_conf': gen_confs[i],
                     'lead_field': lead_fields[i]})

with open('test_lead_field_same_output_as_old_code.data', 'wb') as f:
        pickle.dump(old_code, f)
