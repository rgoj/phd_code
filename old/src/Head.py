# PyBrainSim Copyright 2009 Roman Goj
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
from numpy import pi, sin, cos, mgrid, arange
#from mayavi import mlab
__metaclass__ = type # New style classes. Is this necessary?

"""
The Head class is the main class in PyBrainSim. It holds a list of generators
and connections between these generators, as well as a head model that governs
the propagation of the activity of the generation throughout the modeled head,
to the specified registration sites.  
"""

class Head:
    def __init__(self):
        self.samplingFrequency = 10;
        self.generatorList = []
        self.generatorSiteList = []
        self.connectionList = []
        self.registrationSiteList = []
        self.headModel = None
    
    def setSamplingFrequency(self, samplingFrequency):
        self.samplingFrequency = samplingFrequency

    def getSamplingFrequency(self):
        return self.samplingFrequency

    def addGenerator(self, generator, position = [0,0,0]):
        if self.headModel.checkPosition(position):
            self.generatorSiteList.append(position)
            self.generatorList.append(generator)
        else:
            print("Wrong position of generator!")
    
    def addConnection(self, connection):
        self.connectionList.append(connection)

    def addRegistrationSite(self, position):
        if self.headModel.checkPosition(position):
            self.registrationSiteList.append(position)
        else:
            print("Wrong position of registration site!")

    def setHeadModel(self, headModel):
        self.headModel = headModel

    def displayHead(self):
        dphi, dtheta = pi/10.0, pi/10.0
        #[phi,theta] = mgrid[0:pi+dphi*1.5:dphi,0:2*pi+dtheta*1.5:dtheta]
        [phi,theta] = mgrid[0:pi/2+dphi:dphi,0:2*pi+dtheta:dtheta]
        r = 1
        x = r*sin(phi)*cos(theta)
        y = r*sin(phi)*sin(theta)
        z = r*cos(phi)

        s = mlab.mesh(x, y, z, opacity=1, color = ( 0.5,0.5,1.0 ))
        mlab.show()

    def runSimulation(self, duration=1):
        """Queries all generators, sends the generators' output to connections,
        to the head model and then to the specified registration sites"""
        
        # Preparing a variable to hold the recording for all registration sites
        recording = [] 
        for i in range(len(self.registrationSiteList)):
            recording.append([])
        
        # Preparing a variable where the output of each of the generators will
        # be stored
        generatorOutput = [] 
        for generator in self.generatorList:
            generatorOutput.append(0)

        # Querying all generators and sending generator output through
        # connections
        timeStep = 1/self.samplingFrequency
        timeRange = list(arange(timeStep, duration + timeStep, timeStep))
        for timePoint in timeRange:
            # Recording the output of each generator
            for i in range(len(self.generatorList)):
                generatorOutput[i] = (self.generatorList[i]).runGenerator(timePoint)

            # Sending the output of generators through connections
            for i in range(len(self.connectionList)):
                # Checking which generator's output must a connection recieve
                sourceGeneratorIndex = self.generatorList.index(self.connectionList[i].getSource())
                self.connectionList[i].runConnection(generatorOutput[sourceGeneratorIndex])
            
            # Passing the output of the generators through to the head model
            recording = self.headModel.runHeadModel(generatorOutput, recording)

        return recording
