# PyBrainSim
# Copyright 2009 Roman Goj
#
# This file is part of PyBrainSim.
#
# PyBrainSim is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PyBrainSim is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PyBrainSim.  If not, see <http://www.gnu.org/licenses/>.
  
from __future__ import division        
__metaclass__ = type # New style classes. Is this necessary?

"""
The Experiment class holds information about stimuli, the recorded data and the
even-related potential. It could be used to perform the basic operations on EEG
data, such as baseline correction, averaging, etc. It should also serve as an
interface to Neuroscan, e.g. by providing an export to .cnt files feature.  
"""

from pylab import *

class Experiment:
    def __init__(self, samplingFrequency = 128, duration = 1,  recording = [], stimulusTimes = [], baseline = 0.1, epochDuration = 0.3):
        self.samplingFrequency = samplingFrequency
        self.duration = duration
        self.recording = recording
        self.stimulusTimes = stimulusTimes
        self.baseline = baseline
        self.epochDuration = epochDuration

        timeStep = 1.0/self.samplingFrequency
        self.timePoints = list(arange( timeStep, self.duration + timeStep, timeStep ))
        
        startIndex = int( - (self.baseline // timeStep))
        endIndex = int(1 + ((self.epochDuration - self.baseline) // timeStep))
        self.epochTimePoints = list((arange(endIndex - startIndex) - (self.baseline // timeStep)) * timeStep)

    def setSamplingFrequency(self, samplingFrequency):
        self.samplingFrequency = samplingFrequency

    def getSamplingFrequency(self):
        return self.samplingFrequency
    
    def setDuration(self, duration):
        self.duration = duration

    def getDuration(self):
        return self.duration

    def setRecording(self, recording):
        self.recording = recording
    
    def getRecording(self):
        return self.recording

    def setStimulusTimes(self, stimulusTimes):
        #TODO: If dimension of stimulusTimes is 1... it needs to be two :/
        self.stimulusTimes = stimulusTimes

    def getStimulusTimes(self):
        return self.stimulusTimes

    def findNearestTimeIndex(self, timePoint):
        """ Returns the index of the closest time point within timePoints that
        is smaller than the given value timePoint"""
        if timePoint in self.timePoints:
            return self.timePoints.index(timePoint)
        elif (timePoint > max(self.timePoints)) | (timePoint < min(self.timePoints)):
            print("findNearestTimeIndex: Something is WRONG! timePoint: " + str(timePoint) )
            return -1
        else:
            for i in range(len(self.timePoints)):
                if timePoint < self.timePoints[i]:
                    if timePoint > self.timePoints[i-1]:
                        return i

    def getRecordingSlice(self, stimulus, sliceChannel=0):
        stimulusIndex = self.findNearestTimeIndex(stimulus)
        timeStep = 1.0 / self.samplingFrequency
        startIndex = int(stimulusIndex - (self.baseline // timeStep))
        endIndex = int(stimulusIndex + 1 + ((self.epochDuration - self.baseline) // timeStep))

        return self.recording[sliceChannel][startIndex:endIndex]

    def getERP(self, stimulusNumber=0):
        # We will be returning a list of ERPs for each channel
        channelERPs = []

        # Choosing the stimulus that will be used to make ERPs
        stimuli = self.stimulusTimes[stimulusNumber]

        for channel in range(len(self.recording)):
            # Retrieving slices of recordings around each stimulus (epochs)
            epochs = []
            for i in range(len(stimuli)):
                epochs.append(self.getRecordingSlice(stimuli[i], channel))
            
            # Making sure all epochs are of the same length
            for i in range(len(epochs))[1:]:
                if (len(epochs[i]) != len(epochs[i-1])):
                    print("Not all epochs are of the same length: " +
                          str(len(epochs[i])) + " " + str(len(epochs[i-1])))
            
            # Calculating the average of all the epochs
            average = list(zeros(len(epochs[0])))
            for i in range(len(epochs)):
                for j in range(len(epochs[i])):
                    average[j] += epochs[i][j] / len(epochs)
            channelERPs.append(average)
        
        return channelERPs        

    def plotChannels(self, channelData, time, stimuli, fig, bottom, height):
        # Multiple axes will be created, all sharing the same properties
        axes = []
        axesProperties = dict([])
        
        # Each channel will have a plot of the same width and height
        plotWidth = 0.8
        plotHeight = height/len(self.recording)
        
        for channel in range(len(channelData)):
            # Plotting the recording for each channel
            axes.append(fig.add_axes([0.1, bottom + plotHeight * channel,
                                          plotWidth, plotHeight],
                                         **axesProperties))
            axes[channel].plot(time, channelData[channel])
            axes[channel].set_ylabel("CH " + str(channel+1))
            
            # All channels must be zoomed in/out and moved at the same time
            if channel == 0:
                axesProperties['sharex'] = axes[0]
                axesProperties['sharey'] = axes[0]
                
            # Plotting vertical lines to indicate times of stimuli
            if isinstance(stimuli, float):
                axvline(stimuli, color='r')
            else:
                for i in range(len(stimuli)):
                    axvline(stimuli[i], color='r')
        
        # Time values will be printed only for the lowest axis
        axes[0].set_xlabel("Time")
        for axis in axes[1:]:
            setp(axis.get_xticklabels(), visible=False)
    
    def plotRecording(self):
        # Creating a new matplotlib figure for the plots
        fig = figure()

        # Ongoing activity
        self.plotChannels(self.recording, self.timePoints,
                          self.stimulusTimes[0], fig, 0.55, 0.4)
        figtext( 0.93, 0.75, 'Ongoing activity', rotation = 'vertical', 
                verticalalignment = 'center')
        
        # Event-related activity
        self.plotChannels(self.getERP(), self.epochTimePoints, 
                          0.0, fig, 0.075, 0.4)
        figtext( 0.93, 0.275, 'Event-related activity', rotation = 'vertical',
                verticalalignment = 'center' )
        
        # Showing the prepared figure
        show()
