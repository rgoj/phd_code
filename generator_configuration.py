"""
So far, this only has a random_generator_placement() function, would it
make sense to do more?
"""

from __future__ import division

import sys
from numpy import pi, array, max, min, mean, power, sqrt
from numpy.random import randint, uniform


def random_generator_placement(limits={'n_gen':(1,5),'depth':(4.49,7.05),
                                       'theta':(0,pi/2),'phi':(0,2*pi),
                                       'orientation':(0,pi/2),
                                       'orientation_phi': (0,2*pi)}):
    gen_conf = []
    # Number of generators
    n_gen = randint(limits['n_gen'][0],limits['n_gen'][1]+1)

    for i in range(n_gen):
        gen_conf.append({})

        # Dipole location
        gen_conf[i]['depth'] = uniform(limits['depth'][0],limits['depth'][1])
        gen_conf[i]['theta'] = uniform(limits['theta'][0],limits['theta'][1])
        gen_conf[i]['phi']   = uniform(limits['phi'][0],  limits['phi'][1])
        
        # Dipole orientation
        gen_conf[i]['orientation'] = uniform(limits['orientation'][0],
                                             limits['orientation'][1])
        gen_conf[i]['orientation_phi'] = uniform(limits['orientation_phi'][0],
                                                 limits['orientation_phi'][1])
    
    return gen_conf


