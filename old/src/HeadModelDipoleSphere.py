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
from numpy import arange, array, ones, identity, dot, zeros, sin, cos, pi, sqrt, sum, arccos
__metaclass__ = type # New style classes. Is this necessary?

"""
This reimplemenation of the HeadModel class models the head as a single 
conductant sphere containing dipolar sources.
"""

from HeadModel import HeadModel

class HeadModelDipoleSphere(HeadModel):
    def __init__(self, head, radius):
        HeadModel.__init__(self, head)
        self.head = head
        self.radius = radius # Radius of the head in [cm]
        self.leadField = 0;
    
    def checkPosition(self,position):
        # Checking if position is a list of two or five numbers
        # The position of each registration site is given in spherical coordinates
        # associated with the center of the spherical head. The radial coordinate of the electrode
        # is always equal to the radius of the head, hence it doesn't need to be specified.
        # The only two parameters that need to be specified are the angles theta and phi in this
        # order.
        # For each generator, all three cordinates must be given: the depth of the dipole and the
        # theta and phi angles. Additionaly, angles specyfying the orientation of the dipole in
        # the spherical coordinates of the dipole must also be given. The theta angle is then the
        # orientation with respect to the surface of the head - i.e. theta = 0 means a radial
        # dipole, while theta = pi/2 means a tangential dipole. Only values in this range are
        # allowed! The specification of the phi angle is considered less important and should be
        # explained more thoroughly in other documentation.
        if not isinstance(position, list):
            return False
        if len(position) != 2 and len(position) != 5:
            return False
        # Check the radial coordinate (depth) of the dipole
        if len(position) == 5 and (position[0] <= 0 or position[0] >= self.radius):
            return False
        # Check the theta angle of the orientation of the dipole
        if len(position) == 5 and (position[3] < 0 or position[3] > pi/2):
            return False
        for i in range(len(position)):
            if (not isinstance(position[i], float)) and (not isinstance(position[i], int)):
                return False
        
        # If none of the conditions above fail, the position is correct
        return True

    def calculateLeadField(self):
        # How many generators and electrodes do we have?
        nGenerators = len(self.head.generatorSiteList)
        nElectrodes = len(self.head.registrationSiteList)

        # Assuming ideal conductivity
        sigma = 1.0

        # The number of electrodes and generators defines the size of the lead field matrix
        self.leadField = zeros((nElectrodes,nGenerators))
        self.leadFieldInfinite = zeros((nElectrodes,nGenerators))
        self.leadFieldBrody1973 = zeros((nElectrodes,nGenerators))
        self.leadFieldFrank1952 = zeros((nElectrodes,nGenerators))
        
        for iElectrode in range(nElectrodes):
            # Calculating the coordinates of the electrode in the Cartesian coordinates associated with the head
            # The X axis points towards the right ear, while the Y axis points towards the front
            electrodeTheta = self.head.registrationSiteList[iElectrode][0]
            electrodePhi = self.head.registrationSiteList[iElectrode][1]
            xyzElectrodeHead = zeros(3);
            xyzElectrodeHead[0] = self.radius * sin(electrodeTheta) * cos(electrodePhi);
            xyzElectrodeHead[1] = self.radius * sin(electrodeTheta) * sin(electrodePhi);
            xyzElectrodeHead[2] = self.radius * cos(electrodeTheta);
            
            for iGenerator in range(nGenerators):
                #
                # Infinite homogeneous conductor
                #

                # Calculating the coordinates of the dipole in the Cartesian coordinates associated with the head
                dipoleRadius = self.radius - self.head.generatorSiteList[iGenerator][0]
                dipoleTheta = self.head.generatorSiteList[iGenerator][1]
                dipolePhi = self.head.generatorSiteList[iGenerator][2]
                xyzDipoleHead = zeros(3);
                xyzDipoleHead[0] = dipoleRadius * sin(dipoleTheta) * cos(dipolePhi);
                xyzDipoleHead[1] = dipoleRadius * sin(dipoleTheta) * sin(dipolePhi);
                xyzDipoleHead[2] = dipoleRadius * cos(dipoleTheta);
                
                # Calculating the coordinates of the electrode in the coordinates associated with the dipole
                xyzElectrodeDipole = xyzElectrodeHead - xyzDipoleHead;
                
                # Calculating the distance between the dipole and the electrode
                distance = 0;
                distance += pow(xyzElectrodeDipole[0],2.0)
                distance += pow(xyzElectrodeDipole[1],2.0)
                distance += pow(xyzElectrodeDipole[2],2.0)
                distance = sqrt(distance)
                
                # Rotation matrix for translating the coordinates of the electrode in the dipole coordinates parallel
                # to the reference coordinates at the center of the head to dipole coordinates where the dipole is specified
                # i.e. where the z axis is radial.
                rotationMatrix = zeros((3,3));
                dipoleTheta = self.head.generatorSiteList[iGenerator][1]
                dipolePhi = self.head.generatorSiteList[iGenerator][2]
                # Row 1
                rotationMatrix[0,0] = sin(dipolePhi)
                rotationMatrix[0,1] = -cos(dipolePhi)
                rotationMatrix[0,2] = 0
                # Row 2
                rotationMatrix[1,0] = cos(dipoleTheta) * cos(dipolePhi)
                rotationMatrix[1,1] = cos(dipoleTheta) * sin(dipolePhi)
                rotationMatrix[1,2] = -sin(dipoleTheta)
                # Row 3
                rotationMatrix[2,0] = sin(dipoleTheta) * cos(dipolePhi)
                rotationMatrix[2,1] = sin(dipoleTheta) * sin(dipolePhi)
                rotationMatrix[2,2] = cos(dipoleTheta)
                
                rotationMatrixHeadToDipole = rotationMatrix

                # The Electrode coordinates in the dipole rotated frame of reference and scaleda
                xyzElectrodeDipoleRotatedScaled = dot(rotationMatrix, xyzElectrodeDipole) / distance

                # The Orientation vector
                orientationTheta = self.head.generatorSiteList[iGenerator][3]
                orientationPhi = self.head.generatorSiteList[iGenerator][4]
                xyzOrientationDipoleRotated = zeros(3);
                xyzOrientationDipoleRotated[0] = sin(orientationTheta) * cos(orientationPhi);
                xyzOrientationDipoleRotated[1] = sin(orientationTheta) * sin(orientationPhi);
                xyzOrientationDipoleRotated[2] = cos(orientationTheta);
                
                # The cosine of the angle between the dipole orientation and the electrode
                cosAngleOrientationElectrode = sum(xyzElectrodeDipoleRotatedScaled * array(xyzOrientationDipoleRotated))

                # Homogeneous conductor without boundaries
                self.leadFieldInfinite[iElectrode, iGenerator] = cosAngleOrientationElectrode/distance/distance/4/pi/sigma

                #
                # Bounded spherical conductor
                # Brody 1973
                #
                rCosPhi = dot(xyzElectrodeHead, xyzDipoleHead) / self.radius
                #print rCosPhi

                fieldVector = zeros(3);
                for i in range(3):
                    fieldVector[i] = 2*(xyzElectrodeHead[i] - xyzDipoleHead[i])/pow(distance,2.0)
                    fieldVector[i] += (1/pow(self.radius,2.0)) * (xyzElectrodeHead[i] + (xyzElectrodeHead[i] * rCosPhi - self.radius * xyzDipoleHead[i])/(distance + self.radius - rCosPhi))
                    fieldVector[i] = fieldVector[i] / 4 / pi / sigma / distance

                # Rotation matrix for translating the coordinates in the dipole frame of reference to the
                # coordinates associated with the dipole parallel to the head coordinates.
                rotationMatrix = zeros((3,3));
                dipoleTheta = self.head.generatorSiteList[iGenerator][1]
                dipolePhi = self.head.generatorSiteList[iGenerator][2]
                # Row 1
                rotationMatrix[0,0] = sin(dipolePhi)
                rotationMatrix[0,1] = cos(dipoleTheta) * cos(dipolePhi)
                rotationMatrix[0,2] = sin(dipoleTheta) * cos(dipolePhi)
                # Row 2
                rotationMatrix[1,0] = -cos(dipolePhi)
                rotationMatrix[1,1] = cos(dipoleTheta) * sin(dipolePhi)
                rotationMatrix[1,2] = sin(dipoleTheta) * sin(dipolePhi)
                # Row 3
                rotationMatrix[2,0] = 0
                rotationMatrix[2,1] = -sin(dipoleTheta)
                rotationMatrix[2,2] = cos(dipoleTheta)

                rotationMatrixDipoleToHead = rotationMatrix
                
                # Rotating Orientation to translated dipole coordinates
                xyzOrientationDipole = dot(rotationMatrixDipoleToHead, xyzOrientationDipoleRotated)
                
                self.leadFieldBrody1973[iElectrode, iGenerator] = dot(fieldVector, xyzOrientationDipole)
    
                #if self.leadFieldBrody1973[iElectrode, iGenerator] < 0:
                #    self.leadFieldBrody1973[iElectrode, iGenerator] = 0

                #
                # Bounded spherical conductor
                # Frank 1952
                #
                xyzElectrodeDipoleRotated = dot(rotationMatrixHeadToDipole, xyzElectrodeHead)
                # The below line causes problems because of arccos!
                phi = arccos(xyzElectrodeDipoleRotated[0] / xyzElectrodeDipoleRotated[1]) - orientationPhi
                cosPhi = cos(phi)
                psi = orientationTheta
                cosPsi = cos(psi)
                sinPsi = sin(psi)
                cosTheta = dot(xyzDipoleHead,xyzElectrodeHead) / sqrt(dot( xyzDipoleHead, xyzDipoleHead )) / sqrt(dot( xyzElectrodeHead, xyzElectrodeHead))
                sinTheta = sqrt(1-pow(cosTheta,2.0))
                b = self.radius - self.head.generatorSiteList[iGenerator][0]
                f = b/self.radius
                self.leadFieldFrank1952[iElectrode, iGenerator] = cosPsi * (( 1-pow(f,2.0) )/pow( 1+pow(f,2.0)-2*f*cosTheta, 3/2)-1)
                self.leadFieldFrank1952[iElectrode, iGenerator] += sinPsi*cosPhi/sinTheta* ( ( 3*f - 3*pow(f,2.0)*cosTheta + pow(f,3.0) - cosTheta )/pow(1+pow(f,2.0)-2*f*cosTheta,3/2) + cosTheta )
                self.leadFieldFrank1952[iElectrode, iGenerator] = self.leadFieldFrank1952[iElectrode, iGenerator] / 4 /pi / sigma / self.radius / b
                
                # This is a nasty trick to make runHeadModel aware that the lead field has already been calculated
                self.leadField = 1
                
    def runHeadModel(self, generatorOutput, recording):
        # Calculating the lead field
        if self.leadField == 0:
            self.calculateLeadField()

        # Calculating the recording by multyplying the lead field by the generator output
        #newRecording = dot(self.leadField, (array([generatorOutput])).transpose())
        #newRecordingInfinite = dot(self.leadFieldInfinite, (array([generatorOutput])).transpose())
        newRecordingBrody1973 = dot( self.leadFieldBrody1973, (array([generatorOutput])).transpose())
        #newRecordingFrank1952 = dot(self.leadFieldFrank1952, (array([generatorOutput])).transpose())
        
        # Converting the new recording to list format for compatibility with rest of the code
        #newRecording = list(newRecording[:,0])
        #newRecordingInfinite = list(newRecordingInfinite[:,0])
        newRecordingBrody1973 = list(newRecordingBrody1973[:,0])
        #newRecordingFrank1952 = list(newRecordingFrank1952[:,0])
        
        # Brody1973 rules, see comments below...
        newRecording = newRecordingBrody1973

        #for i in range(len(newRecording)):
            # All three of the lead field calculation methods implemented above can be used, however
            # only Brody1973 and Frank1952 give results in a bounded homogeneous conducting sphere,
            # and of these only Brody1973 gives results for all combinations of angles, etc.
            # Additionally, due to and arccos in my implementation above, Frank1952 for now gives even
            # worse results than it should for many angles...
            #newRecording[i] = newRecordingBrody1973[i]
            #newRecording[i] = newRecordingFrank1952[i]
            #newRecording[i] = newRecordingInfinite[i]
            #newRecording[i] = (newRecordingBrody1973[i])/(newRecordingFrank1952[i])

        for channel in range(len(recording)):
            recording[channel].append(newRecording[channel])
            
        return recording
