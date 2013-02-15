# Roman Goj
# 25/11/2010
"""
This module contains functions to read electrode locations from pre-prepared
text files and to plot a topographic map of scalp activity.

"""
import csv
from numpy import cos, sin, abs, pi, array, append, copy, linspace, sqrt, mean
from numpy.random import uniform
from numpy.ma import masked_array
from matplotlib.mlab import griddata
from matplotlib import pyplot

def read_electrode_locations():
    """Reads electrode locations from a previously prepared text file."""
    # TODO: This should really be reimplemented more cleanly, i.e. a
    # documentation of exactly where are the supposed 10-20 electrode locations
    # coming from, how they were calculated, etc. Perhaps an automated script
    # for the calculation of the electrode location file should also be
    # provided.
    reader = csv.reader(open('electrodeLocations.elp', 'rb'),
                        dialect='excel-tab')

    electrodes = []
    electrode_theta = []
    electrode_phi = []
    electrode_x = []
    electrode_y = []

    for row in reader:
        # Omit first row with number of electrodes
        if reader.line_num != 1:
            electrodes.append(row[1])
            electrode_theta.append(float(row[2]))
            electrode_phi.append(float(row[3]))

    max_theta = max(electrode_theta)
    electrode_theta = array(electrode_theta)
    electrode_theta = electrode_theta / max_theta
    
    for i in range(len(electrodes)):
        electrode_x.append(electrode_theta[i] *\
                           cos(electrode_phi[i] / 180 * pi))
        electrode_y.append(electrode_theta[i] *\
                           sin(electrode_phi[i] / 180 * pi))

    # Transforming into electrode locations for PyBrainSim
    for i in range(len(electrode_theta)):
        if electrode_theta[i] < 0:
            electrode_phi[i] = electrode_phi[i] / 180 * pi + pi
        else:
            electrode_phi[i] = electrode_phi[i] / 180 * pi
    electrode_theta = abs(electrode_theta) * pi / 2

    return [electrodes, electrode_x, electrode_y,
            electrode_theta, electrode_phi]


def plot_topographic_map(values, scale=0, plot_legend=True, ax=None):
    """Plots a topgraphic map of scalp activity.
    
    In order to show edges of the plot we add four courners around the circle
    of the head. This allows us to easily interpolate the data beyond the last
    electrodes. However this makes the edges of the head show irrelevant data.
    This, though is only to be expected sine we don't really have any
    information around the edges--beyond the last electrodes.
    """
    [electrodes, electrode_x, electrode_y, electrode_theta, electrode_phi] =\
        read_electrode_locations()
    
    # Converting to numpy arrays for easier processing
    electrode_x = array(electrode_x)
    electrode_y = array(electrode_y)
    values = array(values)
    value_z = copy(values)
    
    # TODO: This needs some consideration, because we're forcing the user to
    # provide a data array of a specific format and yet it's not documented
    # anywhere!
    if len(value_z.shape) == 1:
        if value_z.shape[0] != len(electrodes):
            print('ERROR: invalid number of electrodes')
    else:
        if value_z.shape[1] != len(electrodes):
            print('ERROR: invalid number of electrodes')
        # In case of data array not averaged across subjects
        value_z = mean(value_z, 0)
    
    # Adding four points to trick griddata to extrapolate, for a nicer plot
    electrode_x = append(electrode_x, [-1.5, 1.5, -1.5, 1.5])
    electrode_y = append(electrode_y, [-1.5, -1.5, 1.5, 1.5])
    value_z = append(value_z, [0,  0, 0, 0])

    # Define interpolation grid
    # The number_of_points variable severely effects the speed of the 
    # computation, choose value of 50 to get fast speed and value of 300 to 
    # get a decent topographic map.
    number_of_points = 300
    #number_of_points = 100
    #number_of_points = 50
    grid_x = linspace(-1.03, 1.03, number_of_points)
    grid_y = linspace(-1.03, 1.03, number_of_points)

    # Interpolating values on the grid
    interpolated_z = griddata(electrode_x, electrode_y, value_z, grid_x, grid_y)

    # Create oval mask
    mask_z = copy(interpolated_z)
    for i in range(interpolated_z.shape[0]):
        for j in range(interpolated_z.shape[1]):
            if sqrt(grid_x[i]**2 + grid_y[j]**2) <= 1.03:
                mask_z[i][j] = False
            else:
                mask_z[i][j] = True
    masked_z = masked_array(interpolated_z, mask = mask_z)
    
    # Preparing handle for axes, if not explicitly given
    if ax == None:
        ax = pyplot.gca()

    # A circle around the activity plot
    circle = pyplot.Circle((0, 0), 1.03, facecolor='none', edgecolor='black',
                    linewidth=2.5)
    ax.add_patch(circle)
    
    colormap_choice = pyplot.cm.RdBu_r # pyplot.cm.jet
    
    # If called with specific max and min values
    if scale!=0:
        img = ax.imshow(masked_z, origin='lower', aspect=1,
                         extent=(-1.03, 1.03, -1.03, 1.03),
                         cmap=colormap_choice, vmin=scale[0], vmax=scale[1])
        #pyplot.contour(grid_x,grid_y,interpolated_z,10,linewidths=0.5,colors='k',
        #            vmin=scale[0], vmax=scale[1])
    else:
        img = ax.imshow(masked_z, origin='lower', aspect=1,
                         extent=(-1.03, 1.03, -1.03, 1.03),
                         cmap=colormap_choice)
        #pyplot.contour(grid_x,grid_y,interpolated_z,10,linewidths=0.5,colors='k')
    
    if plot_legend:
        ax.get_figure().colorbar(img, ax=ax, shrink=0.7)
    
    # Electrodes as black dots
    ax.scatter(electrode_x[0:len(electrodes)], electrode_y[0:len(electrodes)], marker='o', c='b', s=1,
                facecolor='black')
    ax.set_xlim(-1.04, 1.04)
    ax.set_ylim(-1.04, 1.04)
    
    #ax.set_agrid_xs_off()
    ax.set_frame_on( False )
    ax.set_xticks([])
    ax.set_yticks([])

    return img


def plot_topographic_map_array(values, scale=False, 
                               label_x=False, label_y=False, title=False,
                               fig=None):
    """This function is intended for plotting simple arrays of topographic
    maps.
    
    The topographic map data is specified in the 'values' variable, e.g:

    values = [[erp_condition_1A, erp_condition_2A, erp_condition_3A],
              [erp_condition_1B, erp_condition_2B, erp_condition_3B]]
    plot_topographic_map_array(values)

    The above will result in a plot with two rows (corresponding to conditions
    A and B) and three columns (corresponing to conditions 1, 2 and 3).
    
    If you provide a value of None in the values array, no subplot will be
    printed for that particular row and column.

    The scales of the plots can be adjusted using the 'scale' variable. For any
    given topographic map in the array, the scale can either be independent
    from the rest of the plots or can match the preceding plots. One caveat is
    that it is currently not possible to set identical scales for columns. It
    is possible to set identical scales for rows, though, e.g. using:

    plot_topographic_map_array(values, 
        scale=[[False, False, True], [False, False, True]])

    which will generate a two row plot, with all three topographic maps in both
    rows having identical scales (differing between rows). Similarily, you can
    set all topographic maps in all columns and rows to have identical scale by
    using:
    
    plot_topographic_map_array(values, 
        scale=[[False, False, False], [False, False, True]])
    
    In a similar fashion you can add titles and X/Y axis labels to each plot
    separately. By combining e.g. the Y axis labels and titles you can describe
    the conditions presented in our first example above:

    plot_topographic_map_array(values, 
        label_y=[['A',False,False], ['B', False, False]],
        title=[['1', '2', '3'], [False, False, False]])

    This will put a text descrption left of the two topographic maps in the
    first column and above each of the three topographic maps in the first row.

    """
    # TODO: Implement specyfying scale values for all plots or each plot.
    # TODO: This function should return a handle to the figure to allow
    # specific modifications of the plot. This is simple, but let's add this
    # only when there's some time to test it.
    # array[row][column]
    n_rows = len(values)
    n_columns = len(values[0])
    plot_list = []
    if fig == None:
        fig = pyplot.figure()
    for row in range(n_rows):
        for column in range(n_columns):
            if values[row][column] != None:
                if fig == None:
                    ax = pyplot.subplot(n_rows, n_columns, 
                                        row * n_columns + column + 1)
                else:
                    ax = fig.add_subplot(n_rows, n_columns,
                                         row * n_columns + column + 1)
                if scale:
                    if scale[row][column]:
                        legend = True
                    else:
                        legend = False
                else:
                    legend = False
                
                plot_list.append(plot_topographic_map(values[row][column],
                                                      plot_legend=legend, 
                                                      ax=ax))
                
                if scale:
                    if scale[row][column]:
                        scale_values = []
                        for one_plot in plot_list:
                            scale_values.append(one_plot.get_clim()[0])
                            scale_values.append(one_plot.get_clim()[1])
                        for one_plot in plot_list:
                            one_plot.set_clim(min(scale_values),
                                              max(scale_values))
                        plot_list = []
                
                if label_x:
                    if label_x[row][column]:
                        pyplot.xlabel(label_x[row][column])
                if label_y:
                    if label_y[row][column]:
                        pyplot.ylabel(label_y[row][column])
                if title:
                    if title[row][column]:
                        pyplot.title(title[row][column])


def plot_simulated_topographies(
                      simulated_gen_1, simulated_gen_2, 
                      normal_noise_1, normal_noise_2, 
                      topographic_noise_1, topographic_noise_2, 
                      simulated_data_1, simulated_data_2,
                      subject=False, fig=None, filename=None):
    simulated_gen = [simulated_gen_1, simulated_gen_2,
                     array(simulated_gen_1) - array(simulated_gen_2)]
    map_array = [simulated_gen]
    title_array = [['Condition 1', 'Condition 2', 'Condition 1 - 2']]
    label_y_array = [['Generators only', False, False]] 
    scale_array = [[False, False, True]]

    if topographic_noise_1 != None:
        if subject=='average':
            topographic_noise = [topographic_noise_1, topographic_noise_2,
                                 array(topographic_noise_1) -\
                                 array(topographic_noise_2)]
        else:
            topographic_noise = [topographic_noise_1[subject], 
                                 topographic_noise_2[subject],
                                 array(topographic_noise_1[subject]) -\
                                 array(topographic_noise_2[subject])]
        map_array.append(topographic_noise)
        title_array.append([False, False, False])
        label_y_array.append(['Topographic noise', False, False])
        scale_array.append([False, False, True])
    if normal_noise_1 != None:
        if subject=='average':
            normal_noise = [normal_noise_1, normal_noise_2,
                            array(normal_noise_1) -
                            array(normal_noise_2)]
        else:
            normal_noise = [normal_noise_1[subject], normal_noise_2[subject],
                            array(normal_noise_1[subject]) -
                            array(normal_noise_2[subject])]
        map_array.append(normal_noise)
        title_array.append([False, False, False])
        label_y_array.append(['Normal noise', False, False])
        scale_array.append([False, False, True])
    if subject=='average':
        simulated_data = [simulated_data_1, 
                          simulated_data_2, 
                          array(simulated_data_1) -\
                          array(simulated_data_2)]
    else:
        simulated_data = [simulated_data_1[subject], 
                          simulated_data_2[subject], 
                          array(simulated_data_1[subject]) -\
                          array(simulated_data_2[subject])]
    map_array.append(simulated_data)
    title_array.append([False, False, False])
    label_y_array.append(['Simulated data', False, False])
    scale_array.append([False, False, True])
    
    plot_topographic_map_array(map_array, scale=scale_array, 
                               label_y=label_y_array,
                               title=title_array, fig=fig)

    if filename != None:
        pyplot.savefig(filename + '.png', format='png')


