# Roman Goj
# 02/12/2010
"""
Defines a function for performing scaling using different methodologies.

"""
from __future__ import division

from copy import deepcopy
from numpy import mean, vdot, sqrt, copy, zeros, max, min, abs

def perform_scaling(data, electrode_indices):
    """This function, suprisingly, performs scaling on a given set of data.

    The data is returned as a dictionary of 8 differently scaled data sets. The
    8 data sets represents all combinations of the following scaling
    methodologies:
        'Vector' of 'MinMax' scaling
        'Within'- or 'Across'-subject scaling
        'All' or 'Few' electrodes included in scaling

    The data can be accessed in the following way:
    
    data_scaled = perform_scaling(data, electrode_indices)
    print(data_scaled['Vector']['Across']['All']
    
    """
    # TODO: Should the scaled for selected electrodes data retain all the
    # unscaled values? I.e. for compatibility with other scripts - i.e. the
    # electrode numbers will be all screwed up...
    data_scaled = {'Vector': {'Across': {'All': None, 'Few': None}, 
                              'Within': {'All': None, 'Few': None}}, 
                   'MaxMin': {'Across': {'All': None, 'Few': None}, 
                              'Within': {'All': None, 'Few': None}}}

    mean_all = mean(data, 0)
    mean_few = mean(data[:, electrode_indices], 0)

    data_scaled['Vector']['Across']['All'] = \
        copy(data) / sqrt(vdot(mean_all, mean_all))
    data_scaled['Vector']['Across']['Few'] = \
        copy(data) / sqrt(vdot(mean_few, mean_few))
    
    min_point = min(mean_all)
    max_point = max(mean_all)
    diff = max_point - min_point
    data_scaled['MaxMin']['Across']['All'] = (copy(data) - min_point) / diff
    min_point = min(mean_few)
    max_point = max(mean_few)
    diff = max_point - min_point
    data_scaled['MaxMin']['Across']['Few'] = (copy(data) - min_point) / diff

    data_scaled['Vector']['Within']['All'] = zeros(data.shape)
    data_scaled['Vector']['Within']['Few'] = zeros(data.shape)
    data_scaled['MaxMin']['Within']['All'] = zeros(data.shape)
    data_scaled['MaxMin']['Within']['Few'] = zeros(data.shape)
    for i in range(data.shape[0]):
        data_scaled['Vector']['Within']['All'][i,:] = \
            copy(data[i,:]) / sqrt(vdot(data[i,:], data[i,:]))
        data_scaled['Vector']['Within']['Few'][i,:] = \
                copy(data[i,:]) / sqrt(vdot(data[i,electrode_indices], data[i,electrode_indices]))
        
        min_point = min(data[i,:])
        max_point = max(data[i,:])
        diff = max_point - min_point
        data_scaled['MaxMin']['Within']['All'][i,:] = \
                (copy(data[i,:]) - min_point) / diff
        
        min_point = min(data[i,electrode_indices])
        max_point = max(data[i,electrode_indices])
        diff = max_point - min_point
        data_scaled['MaxMin']['Within']['Few'][i,:] = \
                (copy(data[i,:]) - min_point) / diff

    return data_scaled

def test_scaling(data_scaled, electrode_indices):
    """This should just be a temporary test, before some more developed unit
    testing is in place... since that may really take a while, let's leave this
    test here for now.

    """
    any_problems = False
    data = data_scaled['Vector']['Across']['All']
    if abs(1 - vdot(mean(data,0),mean(data,0))) > 0.00001:
        print('Vector1')
        any_problems = True
    data = data_scaled['Vector']['Across']['Few']
    if abs(1 - vdot(mean(data[:,electrode_indices],0),
                    mean(data[:,electrode_indices],0))) > 0.00001:
        print abs(1 - vdot(mean(data,0),mean(data,0)))
        print('Vector2')
        any_problems = True
    data = data_scaled['Vector']['Within']['All']
    if abs(1 - vdot(data[1,:],data[1,:])) > 0.00001:
        print('Vector3')
        any_problems = True
    data = data_scaled['Vector']['Within']['Few']
    if abs(1 - vdot(data[1,electrode_indices],data[1,electrode_indices])) > 0.00001:
        print('Vector4')
        any_problems = True
    
    data = data_scaled['MaxMin']['Across']['All']
    if abs(1 - max(mean(data,0) + min(mean(data,0)))) > 0.00001:
        print('MaxMin5')
        any_problems = True
    data = data_scaled['MaxMin']['Across']['Few']
    if abs(1 - max(mean(data[:,electrode_indices],0) +
                   min(mean(data[:,electrode_indices],0)))) > 0.00001:
        print('MaxMin6')
        any_problems = True
    data = data_scaled['MaxMin']['Within']['All']
    if abs(1 - max(data[1,:]) + min(data[1,:],0)) > 0.00001:
        print abs(1 - max(mean(data[1,:],0) + min(mean(data[1,:],0))))
        print('MaxMin7')
        any_problems = True
    data = data_scaled['MaxMin']['Within']['Few']
    if abs(1 - max(data[1,electrode_indices]) + min(data[1,electrode_indices],0)) > 0.00001:
        print('MaxMin8')
        any_problems = True

    return any_problems


def create_scaled_data_structure(contents):
    data = {'Unrescaled': deepcopy(contents),
            'Vector': {'Across': {'All': deepcopy(contents), 
                                  'Few': deepcopy(contents)},
                       'Within': {'All': deepcopy(contents), 
                                  'Few': deepcopy(contents)}}, 
            'MaxMin': {'Across': {'All': deepcopy(contents), 
                                  'Few': deepcopy(contents)}, 
                       'Within': {'All': deepcopy(contents), 
                                  'Few': deepcopy(contents)}}}
    return data
