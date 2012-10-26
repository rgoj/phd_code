#!/usr/bin/python

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

"""
PyBrainSim is an interactive tool for the simulation and visualization of the
electromagnetic activity of the brain, currently under development.

This script allows you to choose from a few example simulations, ranging from
adding numbers to neural mass models.

pybrainsim.sourceforge.net
"""

import wx
from wx import xrc

import numpy
import pylab
from random import random
from scipy.integrate import ode

from Head import Head
from HeadModel import HeadModel
from HeadModelHalfSphere import HeadModelHalfSphere
from HeadModelDipoleSphere import HeadModelDipoleSphere
from Experiment import Experiment
from Stimulus import Stimulus
from StimulusDummy import StimulusDummy
from GeneratorDummy import GeneratorDummy
from GeneratorNumberIncrementing import GeneratorNumberIncrementing
from GeneratorNoisy import GeneratorNoisy
from GeneratorSine import GeneratorSine
from Connection import Connection
from ConnectionDummy import ConnectionDummy

class PyBrainSimGUI(wx.App):
    def OnInit(self):
        self.res1 = xrc.XmlResource("PyBrainSimGUI1.xrc")
        self.res2 = xrc.XmlResource("PyBrainSimGUI2.xrc")
        
        self.frame = self.res1.LoadFrame(None, "menuFrame")
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton1, id=xrc.XRCID("menuButton1"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton2, id=xrc.XRCID("menuButton2"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton3, id=xrc.XRCID("menuButton3"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton4, id=xrc.XRCID("menuButton4"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton5, id=xrc.XRCID("menuButton5"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton6, id=xrc.XRCID("menuButton6"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton7, id=xrc.XRCID("menuButton7"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton8, id=xrc.XRCID("menuButton8"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButton9, id=xrc.XRCID("menuButton9"))
        self.frame.Bind(wx.EVT_BUTTON, self.menuButtonQuit, id=xrc.XRCID("menuButtonQuit"))
        self.frame.Show()
        
        self.logWindow = self.res2.LoadFrame(None, "outputWindow")
        self.log = xrc.XRCCTRL(self.logWindow, "outputLog")
        
        return True

    def menuButton1(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModel(exampleHead)
        exampleHead.setSamplingFrequency(10)
        exampleHead.addRegistrationSite([0, 0, 0])

        exampleStimulus = StimulusDummy('Stim', exampleHead)
        exampleGenerator = GeneratorDummy('Gen', exampleHead)
        exampleConnection = ConnectionDummy('Con', exampleHead, exampleStimulus, exampleGenerator)
        
        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 1.0, exampleHead.runSimulation( 1.0 ))
        output = str(exampleExperiment.getRecording())
        self.log.SetValue(output)
        self.logWindow.Show()
    
    def menuButton2(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModel(exampleHead)
        exampleHead.setSamplingFrequency(10)
        exampleHead.addRegistrationSite([0, 0, 0])

        exampleStimulus = Stimulus('Stim', exampleHead)
        exampleStimulus.setStimulusTimes([0.3, 0.6])
        exampleGenerator = GeneratorNumberIncrementing('Gen', exampleHead)
        exampleConnection = Connection('Con', exampleHead, exampleStimulus, exampleGenerator)

        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 1.0, exampleHead.runSimulation( 1.0 ))
        output = str(exampleExperiment.getRecording())
        self.log.SetValue(output)
        self.logWindow.Show()
    
    def menuButton3(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModel(exampleHead)
        exampleHead.setSamplingFrequency(10)
        exampleHead.addRegistrationSite([0, 0, 0])

        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 1.0)
        exampleExperiment.setStimulusTimes([[0.3, 0.6], [0.5]])

        exampleStimulus1 = Stimulus('Stim1', exampleHead)
        exampleStimulus2 = Stimulus('Stim2', exampleHead)
        exampleStimulus1.setStimulusTimes(exampleExperiment.getStimulusTimes()[0])
        exampleStimulus2.setStimulusTimes(exampleExperiment.getStimulusTimes()[1])

        exampleGenerator1 = GeneratorNumberIncrementing('Gen1', exampleHead)
        exampleGenerator2 = GeneratorNumberIncrementing('Gen2', exampleHead)
        exampleConnection1 = Connection('Con1', exampleHead, exampleStimulus1, exampleGenerator1)
        exampleConnection2 = Connection('Con2', exampleHead, exampleStimulus2, exampleGenerator2)

        exampleExperiment.setRecording(exampleHead.runSimulation(exampleExperiment.getDuration()))
        output = str(exampleExperiment.getRecording())
        self.log.SetValue(output)
        self.logWindow.Show()

    def menuButton4(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModel(exampleHead)
        exampleHead.setSamplingFrequency(128)
        exampleHead.addRegistrationSite([0, 0, 0])
        
        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 10.0)
        exampleExperiment.setStimulusTimes([[0.3, 1.75, 2.16, 3.87, 4.31, 5.183, 6.34, 7.13]])

        exampleStimulus = Stimulus('Stim', exampleHead)
        exampleStimulus.setStimulusTimes(exampleExperiment.getStimulusTimes()[0])
        exampleGenerator = GeneratorSine('Gen', exampleHead)
        exampleConnection = Connection('Con', exampleHead, exampleStimulus, exampleGenerator)

        exampleExperiment.setRecording(exampleHead.runSimulation(exampleExperiment.getDuration()))
        exampleExperiment.plotRecording()
    
    def menuButton5(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModel(exampleHead)
        exampleHead.setSamplingFrequency(256)
        exampleHead.addRegistrationSite([0, 0, 0])
        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 100.0)
        
        # Randomizing stimuli times
        stimuli = []
        for i in range(100):
            stimuli.append( i + 0.2 +random()/2 )
        exampleExperiment.setStimulusTimes([stimuli])
        exampleStimulus = Stimulus('Stim', exampleHead)
        exampleStimulus.setStimulusTimes(exampleExperiment.getStimulusTimes()[0])

        # Creating many generators with random frequencies in the range 2-20 Hz and
        # random phases. Connecting some of them to the stimulus generator
        exampleGenerators = []
        exampleConnections = []
        for i in range(100):
            randomFrequency = 2.0 + random() * 18
            randomPhaseShift = random()
            exampleGenerators.append(GeneratorSine('Gen', exampleHead, frequency=randomFrequency, phaseShift=randomPhaseShift))
            if(random() > 0.75):
                exampleConnections.append(Connection('Con', exampleHead, exampleStimulus, exampleGenerators[i]))

        exampleExperiment.setRecording(exampleHead.runSimulation(exampleExperiment.getDuration()))
        exampleExperiment.plotRecording()
    
    def menuButton6(self, control):
        exampleHead = Head()
        exampleHeadModel = HeadModelHalfSphere(exampleHead)
        exampleHead.setSamplingFrequency(128)
        exampleHead.addRegistrationSite([ 0.5, 0.0, 0.866])
        exampleHead.addRegistrationSite([ 0.0, 0.0, 0.866])
        exampleHead.addRegistrationSite([-0.5, 0.0, 0.866])
        
        exampleExperiment = Experiment(exampleHead.getSamplingFrequency(), 10.0)
        exampleExperiment.setStimulusTimes([[0.3, 1.75, 2.16, 3.87, 4.31, 5.183, 6.34, 7.13]])

        exampleStimulus = Stimulus('Stim', exampleHead)
        exampleStimulus.setStimulusTimes(exampleExperiment.getStimulusTimes()[0])
        exampleGenerator = GeneratorSine('Gen', exampleHead, position = [0.5, 0, 0.366], frequency = 7)
        exampleGenerator = GeneratorSine('Gen', exampleHead, position = [-0.5, 0, 0.366], frequency = 4)
        exampleConnection = Connection('Con', exampleHead, exampleStimulus, exampleGenerator)

        exampleExperiment.setRecording(exampleHead.runSimulation(exampleExperiment.getDuration()))
        exampleExperiment.plotRecording()
    
    def menuButton7(self, control):
        exampleHead = Head()
        exampleHead.displayHead()

    def menuButton8(self, control):
        # This class will produce noise that will be fed into the modelled
        # cortical area as input.
        class NeuralNoise:
            def __init__(self, timeSpan, dtime):
                self.noise = []
                self.dtime = dtime
                self.timePoints = range( int(timeSpan//dtime+1) )
                # Random noise distributed evenly between 120 and 320
                for i in self.timePoints:
                    self.noise.append( 120+200*random() )
            def getNoise(self, time):
                # Searching for the appropriate time point
                for i in self.timePoints:
                    if time < self.timePoints[i]*self.dtime:
                        # Interpolating between the randomly generated values
                        return self.noise[i] + \
                               (self.noise[i+1]-self.noise[i]) \
                               * ((self.timePoints[i]*self.dtime-time)/self.dtime)
        
        # The sigmoid function
        def sigmoidFunction(v):
            """Constants taken from Jansen and Rit 1995, p. 360"""
            cEzero = 2.5
            cR = 0.56
            cVzero = 6
        
            """Sigmoid function taken from Jansen and Rit 1995, p. 360"""
            return 2*cEzero / ( 1 + numpy.exp( cR*( cVzero - v ) ) )
        
        # Defining the equations
        def f(t, y, noiseObject, cC):
            cA=3.25
            ca=100.0
            cB=22.0
            cb=50.0
            cC1=cC
            cC2=0.8*cC1
            cC3=0.25*cC1
            cC4=0.25*cC1
            noise = noiseObject.getNoise(t)
            return [y[1], cA*ca*( sigmoidFunction(y[2] - y[4]) ) - 2*ca*y[1] -
                    ca**2*y[0], y[3], cA*ca*( noise + cC2*sigmoidFunction(cC1*y[0]) ) -
                    2*ca*y[3] - ca**2*y[2], y[5], cB*cb*( cC4*sigmoidFunction(cC3*y[0])
                                                    ) - 2*cb*y[5] - cb**2*y[4]]
        
        # How many seconds should be modelled and how accurately
        timeSpan = 3
        dtime = 0.001
        firstPointToDisplay = 1000

        # A noise object that will be used as input into the equations
        someNoise = NeuralNoise(timeSpan+1, dtime*10)
        
        # Initial conditions
        y0, t0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0

        # Preparing for simulations
        r = []
        recording = [ [], [],  [],  [],  [],  [] ]
        parameter = [ 68, 128, 135, 270, 675, 1350 ]

        # Differential equation integration
        for i in range(len(parameter)):
            # Preparing the integration
            r.append(ode(f).set_integrator('vode', method='bdf'))
            r[i].set_initial_value(y0, t0)
            r[i].set_f_params( someNoise, parameter[i] )
            # Integrating
            while r[i].successful() and r[i].t < timeSpan:
                r[i].integrate(r[i].t+dtime)
                recording[i].append(r[i].y[2] - r[i].y[4])

        # Show results of simulations
        for i in range(len(parameter)):
            pylab.subplot( len(parameter), 1, i+1)
            if i==0:
                pylab.title("Simulations based on Fig. 3 from Jansen and Rit 1995")
            pylab.ylabel( "C = " + str(parameter[i]) )
            pylab.plot(recording[i][firstPointToDisplay:])
        pylab.show()
    
    def menuButton9(self, control):
        # head will hold sources, registrations sites and the head model
        head1 = Head()
        head2 = Head()
        head3 = Head()
        
        # headModel will be our single sphere head model
        headModel1 = HeadModelDipoleSphere(head1, 10.0)
        headModel2 = HeadModelDipoleSphere(head2, 10.0)
        headModel3 = HeadModelDipoleSphere(head3, 10.0)

        # We need only one data point per simulation
        head1.setSamplingFrequency(1)
        head2.setSamplingFrequency(1)
        head3.setSamplingFrequency(1)
        
        # Adding registration sites
        nElectrodes = 201
        angles = []
        for i in range(nElectrodes):
            angles.append(i*numpy.pi/(nElectrodes-1) - numpy.pi/2)
            head1.addRegistrationSite([angles[-1],0])
            head2.addRegistrationSite([angles[-1],0])
            head3.addRegistrationSite([angles[-1],0])
        
        # Adding a generator
        orientation1= 0;
        orientation2= numpy.pi/2;
        orientation3= numpy.pi/4;
        generator1 = GeneratorNoisy('Gen', head1, position = [ 4.0, 0, 0, orientation1, numpy.pi/2], mean=1, stddev=0.0)
        generator2 = GeneratorNoisy('Gen', head2, position = [ 4.0, numpy.pi/4, 0, orientation2, numpy.pi/2], mean=1, stddev=0.0)
        generator30 = GeneratorNoisy('Gen', head3, position = [ 4.0, 0, 0, orientation1, numpy.pi/2], mean=1, stddev=0.5)
        generator31 = GeneratorNoisy('Gen', head3, position = [ 4.0, numpy.pi/4, 0, orientation2, numpy.pi/2], mean=3, stddev=0.5)
        generator32 = GeneratorNoisy('Gen', head3, position = [ 4.0, -numpy.pi/4, 0, orientation3, numpy.pi/2], mean=2, stddev=0.5)


        # Run the simulation just once (or, equivalently for one second with the sampling rate of 1 Hz)
        simulatedData1 = numpy.array(head1.runSimulation(1))
        simulatedData2 = numpy.array(head2.runSimulation(1))
        simulatedData3 = numpy.array(head3.runSimulation(1))
        
        pylab.subplot(311)
        pylab.plot(angles,simulatedData1)
        pylab.title("Potential from superficial dipoles of different orientations")
        pylab.subplot(312)
        pylab.plot(angles,simulatedData2)
        pylab.subplot(313)
        pylab.plot(angles,simulatedData3)
        pylab.xlabel("Location of measurement on scalp [radians]")
        pylab.ylabel("Scalp potential [relative]")
        pylab.show()
        
    
    def menuButtonQuit(self, control):
        self.Exit()

if __name__ == '__main__':
    app = PyBrainSimGUI(0)
    app.MainLoop()
