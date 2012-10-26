from numpy import sqrt, square, cov, var, mean, array
from scipy.stats.stats import pearsonr
from scipy import optimize
from matplotlib import pyplot
from topographicmap import read_electrode_locations
import topographicmap


def plot_variability_visualization(data, to_plot='all'):
    if to_plot == 'all':
        to_plot = ['topography', 'variance topography', 'covariance matrix', 
                'variogram', 'unnormalized variogram', 'mean and variance']
    for next_plot in to_plot:
        pyplot.figure()
        if next_plot == 'topography':
            topographicmap.plot_topographic_map(mean(data,0))
            pyplot.title('Mean')
        elif next_plot == 'variance topography':
            topographicmap.plot_topographic_map(var(data,0))
            pyplot.title('Variance')
        elif next_plot == 'covariance matrix':
            plot_covariance_matrix(data)
        elif next_plot == 'variogram':
            plot_variogram(data, norm='normalized')
        elif next_plot == 'unnormalized variogram':
            plot_variogram(data, norm='unnormalized')
        elif next_plot == 'mean and variance':
            plot_mean_and_variance(data)

def plot_covariance_matrix(data, cov_data):
    max_covariance = max(cov_data.reshape(cov_data.shape[0]*\
                                            cov_data.shape[1],1))
    handle = pyplot.imshow(cov_data,vmin=-max_covariance,vmax=max_covariance,cmap=pyplot.cm.RdBu_r)
    #pyplot.title('Covariance matrix')
    pyplot.xlabel('Electrodes')
    pyplot.ylabel('Electrodes')
    pyplot.colorbar()
    return handle

def plot_variogram(data, cov_data, norm='normalized'):
    # Correlation (across subjects) between electrodes depending on distance
    # between the electrodes
    electrode_correlations = []
    electrode_distances = []
    [electrodes_file, pos_x, pos_y, pos_theta, pos_phi] = \
            topographicmap.read_electrode_locations()
    for electrode1 in range(data.shape[1]):
        for electrode2 in range(data.shape[1]):
            #if electrode1 <= electrode2:
            #    break
            if norm == 'normalized':
                [coefficient, pvalue] = pearsonr(data[:,electrode1], data[:,electrode2])
            elif norm == 'unnormalized':
                coefficient = cov_data[electrode1][electrode2]
            else:
                print norm + ' not recognized!!!'

            electrode_correlations.append(coefficient)
            distance = sqrt(square(pos_x[electrode1] - pos_x[electrode2])
                            + square(pos_y[electrode1] - pos_y[electrode2]))
            electrode_distances.append(distance)
    pyplot.plot(electrode_distances, electrode_correlations, '.')
    handle = pyplot.gca()

    #if norm == 'normalized':
        #pyplot.title('Variogram')
    #elif norm == 'unnormalized':
        #pyplot.title('Unnormalized variogram (variance and covariance)')
    pyplot.xlabel('Distance between two electrodes')
    if norm == 'normalized':
        pyplot.ylabel('Correlation between two\nelectrodes across subjects')
        pyplot.ylim(-1,1)
    elif norm == 'unnormalized':
        pyplot.ylabel('Unnormalized correlation between\ntwo electrodes across subjects')

    fitfunc = lambda p, x: p[0]*x + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    p0 = [1,1]
    #p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, tY))
    p1, success = optimize.leastsq(errfunc, p0[:], 
                                   args=(array(electrode_distances),
                                   electrode_correlations))
    [coeff, pvalue] = pearsonr(electrode_distances, electrode_correlations)
    pyplot.plot(electrode_distances,
                fitfunc(p1,array(electrode_distances)),'r-')
    print(p1)
    print(pvalue)
    return handle


def plot_mean_and_variance(data):
    #pyplot.subplot(1,3,1)
    pyplot.plot(mean(data,0))
    pyplot.xlabel('Electrode')
    pyplot.ylabel('Mean')
    #pyplot.subplot(1,3,2)
    pyplot.figure()
    pyplot.plot(var(data,0))
    pyplot.xlabel('Electrode')
    pyplot.ylabel('Variance')
    #pyplot.subplot(1,3,3)
    pyplot.figure()
    pyplot.plot(mean(data,0),var(data,0), '.')
    pyplot.xlabel('Mean')
    pyplot.ylabel('Variance')
    
    fitfunc = lambda p, x: p[0]*x + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    p0 = [1,1]
    #p1, success = optimize.leastsq(errfunc, p0[:], args=(Tx, tY))
    p1, success = optimize.leastsq(errfunc, p0[:], args=(mean(data,0),
                                   var(data,0)))

    [coeff, pvalue] = pearsonr(mean(data,0),var(data,0))
    pyplot.plot(mean(data,0), fitfunc(p1,mean(data,0)),'r-')
    print(p1)
    print(pvalue)

def plot_mean_vs_variance(data):
    pyplot.plot(mean(data,0),var(data,0), '.')
    pyplot.xlabel('Mean')
    pyplot.ylabel('Variance')
    
    handle = pyplot.gca()

    fitfunc = lambda p, x: p[0]*x + p[1]
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    
    p0 = [1,1]
    p1, success = optimize.leastsq(errfunc, p0[:], args=(mean(data,0),
                                   var(data,0)))

    [coeff, pvalue] = pearsonr(mean(data,0),var(data,0))
    
    pyplot.plot(mean(data,0), fitfunc(p1,mean(data,0)),'r-')
    
    print("    Mean and variance correlation coefficient: " + str(coeff) + \
          ", p value: " + str(pvalue) )

    return handle

def quick_variability_plots(data, cov_data=None):
    if cov_data==None:
        print('WARNING: No covariance given, calculating it.')
        cov_data = cov(data.transpose())
    pyplot.figure(figsize=(10,10))
    pyplot.subplot(2,2,1)
    plot_covariance_matrix(data,cov_data)
    pyplot.subplot(2,2,2)
    #pyplot.figure()
    plot_variogram(data,cov_data)
    pyplot.subplot(2,2,3)
    #pyplot.figure()
    plot_variogram(data,cov_data, 'unnormalized')
    pyplot.subplot(2,2,4)
    #pyplot.figure()
    foo = pyplot.hist(cov_data.reshape((62*62,1)),20)
