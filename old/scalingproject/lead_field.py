from __future__ import division
from numpy import arange, array, ones, identity, dot, zeros, sin, cos, pi, sqrt, sum, arccos
from topographicmap import read_electrode_locations

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
      
    for i_el in range(n_el):
        # Calculating the coordinates of the electrode in the Cartesian coordinates associated with the head
        # The X axis points towards the right ear, while the Y axis points towards the front
        el_theta = el_thetas[i_el]
        el_phi = el_phis[i_el]
        xyz_el_head = zeros(3);
        xyz_el_head[0] = radius * sin(el_theta) * cos(el_phi);
        xyz_el_head[1] = radius * sin(el_theta) * sin(el_phi);
        xyz_el_head[2] = radius * cos(el_theta);
            
        for i_gen in range(n_gen):
            #
            # Infinite homogeneous conductor
            #
            # Calculating the coordinates of the dipole in the Cartesian coordinates associated with the head
            dipole_radius = radius - gen_conf[i_gen]['depth']
            dipole_theta = gen_conf[i_gen]['theta']
            dipole_phi = gen_conf[i_gen]['phi']
            xyz_dipole_head = zeros(3);
            xyz_dipole_head[0] = dipole_radius * sin(dipole_theta) * cos(dipole_phi);
            xyz_dipole_head[1] = dipole_radius * sin(dipole_theta) * sin(dipole_phi);
            xyz_dipole_head[2] = dipole_radius * cos(dipole_theta);
            
            # Calculating the coordinates of the electrode in the coordinates associated with the dipole
            xyz_el_dipole = xyz_el_head - xyz_dipole_head;
            
            # Calculating the distance between the dipole and the electrode
            distance = 0;
            distance += pow(xyz_el_dipole[0],2.0)
            distance += pow(xyz_el_dipole[1],2.0)
            distance += pow(xyz_el_dipole[2],2.0)
            distance = sqrt(distance)

            # The Orientation vector
            orientation_theta = gen_conf[i_gen]['orientation']
            orientation_phi = gen_conf[i_gen]['orientation_phi']
            xyz_orientation_dipole_rotated = zeros(3);
            xyz_orientation_dipole_rotated[0] = sin(orientation_theta) * cos(orientation_phi);
            xyz_orientation_dipole_rotated[1] = sin(orientation_theta) * sin(orientation_phi);
            xyz_orientation_dipole_rotated[2] = cos(orientation_theta);
            
            #
            # Bounded spherical conductor
            # Brody 1973
            #
            r_cos_phi = dot(xyz_el_head, xyz_dipole_head) / radius

            field_vector = zeros(3);
            for i in range(3):
                field_vector[i] = 2*(xyz_el_head[i] - xyz_dipole_head[i])/pow(distance,2.0)
                field_vector[i] += (1/pow(radius,2.0)) * (xyz_el_head[i] + (xyz_el_head[i] * r_cos_phi - radius * xyz_dipole_head[i])/(distance + radius - r_cos_phi))
                field_vector[i] = field_vector[i] / 4 / pi / sigma / distance
            
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
                
            # Rotating Orientation to translated dipole coordinates
            xyz_orientation_dipole = dot(rotation_matrix, xyz_orientation_dipole_rotated)
                
            lead_field_brody_1973[i_el, i_gen] = dot(field_vector, xyz_orientation_dipole)
    
    return lead_field_brody_1973
