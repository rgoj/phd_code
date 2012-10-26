# Roman Goj
# 14/12/2010
"""
This should be a collection of functions related to performing assumption
tests. Right now it is just a single function that does all this... in a very
ugly way.

"""
import sys
from numpy import mean, std
from rpy2 import robjects

from anova import select_electrodes

def test_assumptions(pickHemisphere, pickSite, pickLocation, dataCondition1,
                     dataCondition2, electrodes, doElectrodesAsFactor = False,
                     name = ''):
    """This function ... tests assumptions.

    Don't start me on how ugly it is, PLEASE FIX!!!
    
    """
    # TODO: Clean up mess inside this function
    nSubjects = len(dataCondition1)
    
    [hemispherePicked, sitePicked, locationPicked, electrodesPicked,
     electrodeIndices] = select_electrodes(pickHemisphere, pickSite,
                                           pickLocation, electrodes)

    # Reading all relevant data into a single vector
    dataVector = []
    for subject in range(nSubjects):
        dataVector = dataVector + list( dataCondition1[subject][electrodeIndices] )
        dataVector = dataVector + list( dataCondition2[subject][electrodeIndices] )

    # Converting data into an R matrix with rows corresponding to subjects and columns
    # corresponding to groups of levels of factors
    rDataVector = robjects.FloatVector(dataVector)
    robjects.globalenv["dataVector"] = rDataVector
    rData = robjects.r['matrix'](rDataVector, nrow = nSubjects, byrow = True)
    robjects.globalenv["data"] = rData

    # Representing factors as R variables
    rHemisphere = robjects.IntVector(2 * hemispherePicked)
    rSite = robjects.IntVector(2 * sitePicked)
    rLocation = robjects.IntVector(2 * locationPicked)
    rElectrodes = robjects.StrVector(2 * electrodesPicked)

    # The condition factor as an R variable
    rConditions = robjects.r.gl(2, len(electrodesPicked), 2*len(electrodesPicked), labels = ['old', 'new'])

    # Creating the variables in the R environment
    robjects.globalenv["conditions"] = rConditions
    robjects.globalenv["hemispheres"] = rHemisphere
    robjects.globalenv["locations"] = rLocation
    robjects.globalenv["sites"] = rSite
    robjects.globalenv["electrodes"] = rElectrodes
    
    # Creating R factors, currently can't do it via RPy2, need version 2.1
    fCondition = robjects.r("condition <- factor(conditions)")
    fHemisphere = robjects.r("hemisphere <- factor(hemispheres)")
    fLocation = robjects.r("location <- factor(locations)")
    fSite = robjects.r("site <- factor(sites)")
    fElectrode = robjects.r("electrode <- factor(electrodes)")
    
    # Now we need to choose which factors will be included in the Anova.
    # We exclude all those that have only one level
    allFactors = ''
    if doElectrodesAsFactor == True:
        allFactors = ',electrode'
    else:
        if len(pickHemisphere)>1: allFactors += ',hemisphere'
        if len(pickLocation)>1: allFactors += ',location'
        if len(pickSite)>1 and not pickSite.count(0): allFactors += ',site'

    rFactors = robjects.r('allFactors <- data.frame(condition' + allFactors + ')')

    robjects.r("options(contrasts=c(\"contr.sum\", \"contr.poly\"))")
    anovaModel = robjects.r("model <- lm(data ~ 1)")
    robjects.r("library(car)")

    # Testing ANOVA assumptions for each electrode
    # Electrode factors for levene's test
    electrodesPicked1 = []
    electrodesPicked2 = []
    for electrode in electrodesPicked:
        electrodesPicked1.append('Old ' + electrode)
        electrodesPicked2.append('New ' + electrode)
    electrodesPickedLevene = electrodesPicked1 + electrodesPicked2
    rElectrodesLevene = robjects.StrVector((len(rDataVector)/len(electrodesPickedLevene)) * electrodesPickedLevene)
    robjects.globalenv["electrodesLevene"] = rElectrodesLevene
    fElectrodeLevene = robjects.r("electrodeLevene <- factor(electrodesLevene)")

    # NORMALITY ASSUMPTION
    print('\n#\n# Testing ANOVA assumptions\n#')

    # Preparing to plot normal q-q plots
    dev_off = robjects.r('dev.off')
    nRows = len(pickLocation)
    if pickSite.count(0):
        nColumns = len(pickHemisphere)
    else:
        nColumns = len(pickHemisphere) * len(pickLocation)

    # Looping through all electrodes to do plots and the Shapiro-Wilk test
    print('\n# Shapiro-Wilk test for normality of noise at each electrode')
    for i in [1,2]:
        robjects.r.pdf('qqPlots' + name + str(i) + '.pdf')
        robjects.r('par(mfrow=c('+str(nRows)+','+str(nColumns) + '), pty="s", mar=c(2.5,2.5,1.5,0), mgp=c(1.5,0.1,0),tck=0.03,cex=0.8)')
        for j in range(len(electrodesPicked)):
            # Shapiro-Wilk test
            shapiro_test = robjects.r('shapiro.test')
            sw = shapiro_test(rData.rx(True,(i-1)*len(electrodesPicked)+j+1))
            print('Shapiro-Wilk test for electrode ' + electrodesPicked[j] + ' in condition ' + str(i) + ', p = '+str(sw[1][0]))

            # Plotting q-q plots
            ylimits=robjects.FloatVector([-10,10])
            if j == len(electrodesPicked)-1:
                robjects.r.qqnorm(rData.rx(True,(i-1)*len(electrodesPicked)+j+1),main=electrodesPicked[j].strip(),ylim=ylimits,col='blue', ylab='Scalp potential [uV]', xlab='Standard normal quantiles')
                robjects.r.qqline(rData.rx(True,(i-1)*len(electrodesPicked)+j+1), col='green4')
            else:
                #labels=False to turn off labels with numbers
                robjects.r.qqnorm(rData.rx(True,(i-1)*len(electrodesPicked)+j+1), ann=False, ylim=ylimits, tck=0.03, col='blue')
                robjects.r.qqline(rData.rx(True,(i-1)*len(electrodesPicked)+j+1), ann=False, ylim=ylimits, tck=0.03, col='green4')
            robjects.r.title(electrodesPicked[j].strip())
        dev_off()

    # HOMOGENEITY OF VARIANCE ASSUMPTION
    # Levene's test
    print('\n# Levene\'s test for homogeneity of variance between electrodes in all conditions')
    levene_test = robjects.r('levene.test')
    lt = levene_test(rDataVector,fElectrodeLevene)
    print lt

    # Plot
    robjects.r.pdf('variancePlot' + name + '.pdf')
    robjects.r('par(mar=c(5,4,1,1), mgp=c(2,1,0),tck=0.01,cex=1, las=2)')
    robjects.r('boxplot(dataVector ~ electrodeLevene, range=0, col="green3", ylab=expression(paste("Scalp potential [",u,"V]")) )')
    dev_off()

    # Magnitude measurements
    print('\n#\n# Measuring the magnitude range of the data \n#')
    print('\n# Max - min magnitude for condition 1:')
    print(max(mean(dataCondition1,0)) - min(mean(dataCondition1,0)))
    print('\n# Max - min magnitude for condition 2:')
    print(max(mean(dataCondition2,0)) - min(mean(dataCondition2,0)))
    print('\n# Difference between maximal values in the two conditions:')
    print(max(mean(dataCondition1,0)) - max(mean(dataCondition2,0)))
    print('\n# The mean standard deviation for all electrodes for both conditions is: \n' + str(mean([mean(std(dataCondition1,0)), mean(std(dataCondition2,0))])))
    print('\n# Max - min magnitude for difference between conditions:')
    print(max(mean(dataCondition1-dataCondition2,0)) - min(mean(dataCondition1-dataCondition2,0)))
    print('\n# The mean standard deviation for all electrodes for difference between conditions is: \n' + str(mean(std(dataCondition1-dataCondition2,0))))
