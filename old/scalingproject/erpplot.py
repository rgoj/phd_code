# Roman Goj
# 29/11/2010
"""
This module contains funtions for plotting ERP waveforms.

"""
from matplotlib import pyplot

def plot_ERP(data):
    pyplot.plot(data)





############
# OLD CODE #
############

#pylab.figure(figsize=(8,5))

#time = []
#for i in range(len(dataOld[0])):
#    time.append( len(dataOld[0])/511*4 *i - 104 )
#
#for i in range(3):
#    for j in range(3):
#        thenumber = i*3+j
#        print thenumber
#        if i == 0 and j ==0:
#            ax = pylab.subplot(4,3,thenumber+1)
#        else:
#            ax = pylab.subplot(4,3,thenumber+1)
#
#        
    #pylab.plot(time,dataOld[thenumber],'g', time,dataNew[thenumber],'b')
        
#        ax.spines['left'].set_position('zero')
#        ax.spines['right'].set_color('none')
#        ax.spines['bottom'].set_position('zero')
#        ax.spines['top'].set_color('none')
#        #ax.spines['left'].set_smart_bounds(True)
#        #ax.spines['bottom'].set_smart_bounds(True)
#        ax.xaxis.set_ticks_position('bottom')
#        ax.yaxis.set_ticks_position('left')


#        pylab.title(channelsOld[thenumber])
#        pylab.axvspan(300, 500, facecolor='red', alpha=0.1)
#        pylab.axvspan(500, 700, facecolor='orange', alpha=0.1)
#        pylab.xlim((-104,1000))
#        pylab.ylim((-4,8))
#        ax.set_aspect(48);
#        ax.set_xticks([300, 500, 700])
#        ax.set_yticks([-4,0,4,8])
#
#        ax.set_xticklabels([])
#        ax.set_yticklabels([])

        #if i==2 and j==0:
            #pylab.xlabel('Time [ms]')
            #ax.xaxis.set_label_position('bottom')
            #pylab.ylabel('Scalp potential [$\mu$V]')
        #else:
            #ax.set_xticklabels([])
            #ax.set_yticklabels([])
            #pylab.box( False )
            #pylab.tick_params(labetbottm=False,labelleft=False)
            #ax.set_xticks([])
            #ax.set_yticks([])
    
#    ax = pylab.subplot(4,3,10)
#    ax.spines['left'].set_position('zero')
#    ax.spines['right'].set_color('none')
#    ax.spines['bottom'].set_position('zero')
#    ax.spines['top'].set_color('none')
#    #ax.spines['left'].set_smart_bounds(True)
#    #ax.spines['bottom'].set_smart_bounds(True)
#    ax.xaxis.set_ticks_position('bottom')
#    ax.yaxis.set_ticks_position('left')
#    pylab.xlim((-104,1000))
#    pylab.ylim((-4,8))
#    ax.set_aspect(48);
#    ax.set_xticks([100, 300, 500, 700, 900])
#    ax.set_yticks([-4,0,4,8])
#    pylab.xlabel('Time [ms]')
#    ax.xaxis.set_label_position('bottom')
#    pylab.ylabel('Scalp potential [$\mu$V]')
#    for label in ax.xaxis.get_ticklabels():
#        label.set_rotation(90)
