# Roman Goj
# 13/12/2010
"""
This is a collection of functions related to performing ANOVA analyses.

"""
import sys
from cStringIO import StringIO
from rpy2 import robjects

def assign_factors_to_electrodes(electrodes):
    """This helper function returns 3 lists containing levels of hemisphere,
    location and site factors for each electrode provided in the electrodes
    variable.

    Factors, associated levels and their coding (in parenthesis) are listed
    below:
        I. Hemisphere
            Left (1)
            Right (2)
        II. Location
            Frontal (1)
            Fronto-Central (2)
            Central (3)
            Centro-Parietal (4)
            Parietal (5)
        III. Site
            Superior (1)
            Medial (2)
            Inferior (3)

    This is very specific to the particular factors I want to use, i.e.
    hemisphere, location and site. So, very generic factors/anovas will not be
    possible and the following functions will have to be heavily modified for
    that. Oh well.

    """
    hemisphere = []
    location = []
    site = []
    
    for electrode in electrodes:
        # Reading electrode names
        electrode_name = list(electrode.strip())
        name1 = electrode_name.pop()
        name2 = ''.join(electrode_name)
    
        # Site
        if name1 == '1' or name1 == '2':
            site.append(1) # superior
        elif name1 == '3' or name1 == '4':
            site.append(2) # medial
        elif name1 == '5' or name1 == '6':
            site.append(3) # inferior
        elif name1 == 'Z':
            site.append(0) # midline
        else:
            site.append(None)

        # Hemisphere
        if name1 == '1' or name1 == '3' or name1 == '5':
            hemisphere.append(1) # left
        elif name1 == '2' or name1 == '4' or name1 == '6':
            hemisphere.append(2) # right
        elif name1 == 'Z':
            hemisphere.append(0) # midline
        else:
            hemisphere.append(None)
        
        # Location
        if name2 == 'F':
            location.append(1) # frontal
        elif name2 == 'FC':
            location.append(2) # fronto-central
        elif name2 == 'C':
            location.append(3) # central
        elif name2 == 'CP':
            location.append(4) # centro-parietal
        elif name2 == 'P':
            location.append(5) # parietal
        else:
            location.append(None)

    return [hemisphere, site, location]


def scrape_anova_output(anovaOutput):
    # TODO: Ohhh, this is a mess, let's leave it as it is for now, but we need
    # to figure out a way to do anovas without output scraping!
    """This helper function scrapes all relevant values from car package
    Anova() output, which needs to be first redirected from standard output to
    the anovaOutput variable

    """
    # In order to quickly read out significance values for all main and
    # interaction effects, this line of code comes in very handy:
    # 
    # for name in results: print(name + '   ' + str(results[name]['p']))

    # Splitting lines of output into separate items
    anovaOutputSplit = anovaOutput.split('\n')
    #print(anovaOutputSplit)
    # This dictionary will hold results for all effects
    results = {}

    # Getting the index of the lines with the relevant ANOVA results
    if 'Univariate Type III Repeated-Measures ANOVA Assuming Sphericity' in anovaOutputSplit:
        indexResults = 3 + anovaOutputSplit.index('Univariate Type III Repeated-Measures ANOVA Assuming Sphericity')
    else:
        print('WARNING: Results missing from anova output, something must be wrong!')

    # Getting the index of the lines with the relevant Greenhouse-Geisser correction results
    if ' for Departure from Sphericity' in anovaOutputSplit:
        indexGreenhouseGeisser = 3 + anovaOutputSplit.index(' for Departure from Sphericity')
    else:
        indexGreenhouseGeisser = 0
        print('WARNING: No Greenhouse-Geisser correction, maybe something wrong?')

    # First reading the main anova results
    line = indexResults
    pValuesOneLine = False
    pValues = False

    # Looping through all lines with ANOVA results
    while True:
        # Preparing the lines for scraping
        resultsLine = anovaOutputSplit[line]
        resultsLineSplit = resultsLine.split(' ')
        line += 1

        # Various conditions for lines to skip or end the loop
        if resultsLine.strip() == 'Pr(>F)': pValues = True; continue
        if resultsLine == '---': break
        if resultsLine.strip() == '': break
        if resultsLineSplit[0] == '(Intercept)': continue

        # More preparation for scraping
        while '' in resultsLineSplit:
            resultsLineSplit.remove('')

        # Reading the degrees of freedom F statistic, etc.
        if not pValues:
            if len(resultsLineSplit) >= 7: nameList = ['SS', 'num Df', 'Error SS', 'den Df', 'F', 'p']
            else: nameList = ['SS', 'num Df', 'Error SS', 'den Df', 'F']
            results[ resultsLineSplit[0] ] = {}
            for i in range(len(nameList)):
                if resultsLineSplit[i+1][0] == '<': 
                    results[ resultsLineSplit[0] ]['p'] = 0.0000000001
                else:
                    results[ resultsLineSplit[0] ][nameList[i]] = float(resultsLineSplit[i+1])
        
        # Reading the p-values
        else:
            if resultsLineSplit[1][0] == '<':
                results[ resultsLineSplit[0] ]['p'] = 0.0000000001
            else:
                results[ resultsLineSplit[0] ]['p'] = float(resultsLineSplit[1])

    # Read lines pertaining to the Greenhouse-Geisser correction only if they are present
    if indexGreenhouseGeisser:
        resultsLine = ''
        line = indexGreenhouseGeisser

        # Looping through all lines with Greenhouse-Geisser results
        while True:
            # Preparing the lines for scraping
            resultsLine = anovaOutputSplit[line]
            resultsLineSplit = resultsLine.split(' ')
            line += 1
            
            # Stopping condition
            if resultsLine == '---': break
            if resultsLine.strip() == '': break

            # More preparation for scraping
            while '' in resultsLineSplit:
                resultsLineSplit.remove('')
            
            # Reading the Greenhouse-Geisser epsilon and the corrected p-value
            nameList = ['GG eps', 'p', 'p uncorrected']
            results[ resultsLineSplit[0] ]['p not GG'] = results[ resultsLineSplit[0] ]['p']
            results[ resultsLineSplit[0] ]['GG eps'] = float(resultsLineSplit[1])
            if resultsLineSplit[2][0] == '<':
                results[ resultsLineSplit[0] ]['p'] = 0.0000000001
            else:
                results[ resultsLineSplit[0] ]['p'] = float(resultsLineSplit[2])

    return results


def select_electrodes(hemisphere, site, location, electrodes):
    """This helper function selects electrodes based on the factors that the
    user intends to run ANOVA with. It takes three lists of factors and outputs
    the selected electrodes' indices along with their respective factor codes.
    This is all messy, but it doesn't really make sense to clean it up yet.

    """
    # Creating hemisphere, site and location information for each electrode
    [electrodeHemisphere, electrodeSite, electrodeLocation] = \
        assign_factors_to_electrodes(electrodes)
    
    # Now we want to pick only those electrodes/factors that interest us
    hemispherePicked = []
    sitePicked = []
    locationPicked = []
    electrodesPicked = []
    electrodeIndices = []
    for i in range(len(electrodes)):
        if hemisphere.count(electrodeHemisphere[i]) and\
           site.count(electrodeSite[i]) and\
           location.count(electrodeLocation[i]):
            hemispherePicked.append(electrodeHemisphere[i])
            sitePicked.append(electrodeSite[i])
            locationPicked.append(electrodeLocation[i])
            electrodesPicked.append(electrodes[i])
            electrodeIndices.append(i)
 
    return [hemispherePicked, sitePicked, locationPicked, electrodesPicked,
            electrodeIndices]


def run_anova(pickHemisphere, pickSite, pickLocation, dataCondition1,
              dataCondition2, electrodes, doElectrodesAsFactor = False,
              printResults = False, name = ''):
    """This function ... runs ANOVA.
    
    Don't start me on how ugly it is, PLEASE FIX!!!
    
    """
    # TODO: Figure out a way to do ANOVA without output scraping
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

    # Running ANOVA
    anovaResults = robjects.r('Anova(model, idata=allFactors, idesign=~condition' + allFactors.replace(',', '*') + ', type=\"III\")')

    # Printing ANOVA results... and rediricting that output to a variable
    old_stdout = sys.stdout
    sys.stdout = stdout = StringIO()
    robjects.r.summary(anovaResults, multivariate=False)
    sys.stdout = old_stdout
    anovaOutput = stdout.getvalue()

    if printResults:
        print('\n#\n# ANOVA results \n#\n')
        if doElectrodesAsFactor:
            print('ANOVA run with factors: electrodes\n\n')
        else:
            print('ANOVA run with factors: hemispheres, sites, locations\n\n')
        robjects.r.summary(anovaResults, multivariate=False)

    # Scraping the redirected Anova() output
    results = scrape_anova_output(anovaOutput)
    return [results, electrodeIndices]
