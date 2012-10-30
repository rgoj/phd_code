from __future__ import division

import sys

from numpy import arange, array, ones, identity, dot, zeros, sin, cos, pi, sqrt, sum, arccos
from numpy.linalg import norm

sys.path.insert(0, 'old/scalingproject')
sys.path.insert(0, 'old/src')
from topographicmap import read_electrode_locations

@profile
def calculate_lead_field(gen_conf):
    # Reading in electrode locations from external file electrodeLocations.elp
    [el, el_x, el_y, el_thetas, el_phis] = read_electrode_locations()

    # Setting the radius of the head to 11.5 cm
    radius = 11.5
    
    # How many generators and electrodes do we have?
    n_gen = len(gen_conf)
    n_el = len(el)

    # Assuming ideal conductivity
    sigma = 1.0

    # The number of electrodes and generators defines the size of the lead field matrix
    lead_field_brody_1973 = zeros((n_el,n_gen))

    # Coordinates of each dipole in the frame of reference associated with the
    # head and the orienation of the dipole in the frame of reference
    # associated with the dipole, with axes parallel to the head frame of
    # reference.
    xyz_dipole = zeros((n_gen,3))
    xyz_orientation = zeros((n_gen,3))
    for i_gen in range(n_gen):
        # Calculating the coordinates of the dipole in the Cartesian coordinates associated with the head
        dipole_radius = radius - gen_conf[i_gen]['depth']
        dipole_theta = gen_conf[i_gen]['theta']
        dipole_phi = gen_conf[i_gen]['phi']
        xyz_dipole[i_gen,0] = dipole_radius * sin(dipole_theta) * cos(dipole_phi);
        xyz_dipole[i_gen,1] = dipole_radius * sin(dipole_theta) * sin(dipole_phi);
        xyz_dipole[i_gen,2] = dipole_radius * cos(dipole_theta);
            
        # The Orientation vector
        orientation_theta = gen_conf[i_gen]['orientation']
        orientation_phi = gen_conf[i_gen]['orientation_phi']
        xyz_orientation_rotated = zeros(3);
        xyz_orientation_rotated[0] = sin(orientation_theta) * cos(orientation_phi);
        xyz_orientation_rotated[1] = sin(orientation_theta) * sin(orientation_phi);
        xyz_orientation_rotated[2] = cos(orientation_theta);
        
        # Rotation matrix for translating the coordinates in the dipole frame of reference to the
        # coordinates associated with the dipole parallel to the head coordinates.
        rotation_matrix = zeros((3,3));
        dipole_theta = gen_conf[i_gen]['theta']
        dipole_phi = gen_conf[i_gen]['phi']
        # Row 1
        rotation_matrix[0,0] = sin(dipole_phi)
        rotation_matrix[0,1] = cos(dipole_theta) * cos(dipole_phi)
        rotation_matrix[0,2] = sin(dipole_theta) * cos(dipole_phi)
        # Row 2
        rotation_matrix[1,0] = -cos(dipole_phi)
        rotation_matrix[1,1] = cos(dipole_theta) * sin(dipole_phi)
        rotation_matrix[1,2] = sin(dipole_theta) * sin(dipole_phi)
        # Row 3
        rotation_matrix[2,0] = 0
        rotation_matrix[2,1] = -sin(dipole_theta)
        rotation_matrix[2,2] = cos(dipole_theta)
            
        # Rotating orientation to translated dipole coordinates
        xyz_orientation[i_gen,:] = dot(rotation_matrix,xyz_orientation_rotated)

    # Coordinates of the electrodes (in the frame of reference associated with
    # the center of the head)
    xyz_el = zeros((n_el,3))
    for i_el in range(n_el):
        # Calculating the coordinates of the electrode in the Cartesian coordinates associated with the head
        # The X axis points towards the right ear, while the Y axis points towards the front
        el_theta = el_thetas[i_el]
        el_phi = el_phis[i_el]
        xyz_el[i_el,0] = radius * sin(el_theta) * cos(el_phi);
        xyz_el[i_el,1] = radius * sin(el_theta) * sin(el_phi);
        xyz_el[i_el,2] = radius * cos(el_theta);
           
    for i_el in range(n_el):
        for i_gen in range(n_gen):
            #
            # Infinite homogeneous conductor
            #
            distance = norm(xyz_el[i_el,:] - xyz_dipole[i_gen,:])

            #
            # Bounded spherical conductor
            # Brody 1973
            #
            r_cos_phi = dot(xyz_el[i_el,:], xyz_dipole[i_gen,:]) / radius

            field_vector = zeros(3);
            for i in range(3):
                field_vector[i] = 2*(xyz_el[i_el,i] - xyz_dipole[i_gen,i])/pow(distance,2.0)
                field_vector[i] += (1/pow(radius,2.0)) * (xyz_el[i_el,i] +
                                                          (xyz_el[i_el,i] *
                                                           r_cos_phi - radius *
                                                           xyz_dipole[i_gen,i])/(distance + radius - r_cos_phi))
                field_vector[i] = field_vector[i] / 4 / pi / sigma / distance
            
            lead_field_brody_1973[i_el, i_gen] = dot(field_vector,xyz_orientation[i_gen,:])
    
    return lead_field_brody_1973
