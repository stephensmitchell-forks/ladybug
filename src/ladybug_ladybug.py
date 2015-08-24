# This is the heart of the Ladybug
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Ladybug is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Ladybug is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
This component carries all of Ladybug's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!

-
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
You should have received a copy of the GNU General Public License
along with Ladybug; If not, see <http://www.gnu.org/licenses/>.

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

Source code is available at: https://github.com/mostaphaRoudsari/ladybug

-
Provided by Ladybug 0.0.60
    Args:
        defaultFolder_: Optional input for Ladybug default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: Current Ladybug mood!!!
"""

ghenv.Component.Name = "Ladybug_Ladybug"
ghenv.Component.NickName = 'Ladybug'
ghenv.Component.Message = 'VER 0.0.60\nAUG_24_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import math
import shutil
import sys
import os
import System.Threading.Tasks as tasks
import System
import time
from itertools import chain
import datetime

PI = math.pi
rc.Runtime.HostUtils.DisplayOleAlerts(False)


class CheckIn():
    
    def __init__(self, defaultFolder, folderIsSetByUser = False):
        
        self.folderIsSetByUser = folderIsSetByUser
        self.letItFly = True
        
        if defaultFolder:
            # user is setting up the folder
            defaultFolder = os.path.normpath(defaultFolder) + os.sep
            
            # check if path has white space
            if (" " in defaultFolder):
                msg = "Default file path can't have white space. Please set the path to another folder." + \
                      "\nLadybug failed to fly! :("
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                sc.sticky["Ladybug_DefaultFolder"] = ""
                self.letItFly = False
                return
            else:
                # create the folder if it is not created
                if not os.path.isdir(defaultFolder):
                    try: os.mkdir(defaultFolder)
                    except:
                        msg = "Cannot create default folder! Try a different filepath" + \
                              "\nLadybug failed to fly! :("
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        sc.sticky["Ladybug_DefaultFolder"] = ""
                        self.letItFly = False
                        return
            
            # looks fine so let's set it up
            sc.sticky["Ladybug_DefaultFolder"] = defaultFolder
            self.folderIsSetByUser = True
        
        #set up default pass
        if not self.folderIsSetByUser:
            if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
                # folder already exists so it is all fine
                sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
            elif os.access(os.path.dirname("c:\\"), os.F_OK):
                #the folder does not exists but write privileges are given so it is fine
                sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
            else:
                # let's use the user folder
                username = os.getenv("USERNAME")
                # make sure username doesn't have space
                if (" " in username):
                    msg = "User name on this system: " + username + " has white space." + \
                          " Default fodelr cannot be set.\nUse defaultFolder_ to set the path to another folder and try again!" + \
                          "\nLadybug failed to fly! :("
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    sc.sticky["Ladybug_DefaultFolder"] = ""
                    self.letItFly = False
                    return
                
                sc.sticky["Ladybug_DefaultFolder"] = os.path.join("C:\\Users\\", username, "AppData\\Roaming\\Ladybug\\")
    
    def getComponentVersion(self):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        ver, verDate = ghenv.Component.Message.split("\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
        
    def isNewerVersionAvailable(self, currentVersion, availableVersion):
        # print int(availableVersion.replace(".", "")), int(currentVersion.replace(".", ""))
        return int(availableVersion.replace(".", "")) > int(currentVersion.replace(".", ""))
    
    def checkForUpdates(self, LB= True, HB= True, OpenStudio = True, template = True):
        
        url = "https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/versions.txt"
        versionFile = os.path.join(sc.sticky["Ladybug_DefaultFolder"], "versions.txt")
        client = System.Net.WebClient()
        client.DownloadFile(url, versionFile)
        with open("c:/ladybug/versions.txt", "r")as vf:
            versions= eval("\n".join(vf.readlines()))

        if LB:
            ladybugVersion = versions['Ladybug']
            currentLadybugVersion = self.getComponentVersion() # I assume that this function will be called inside Ladybug_ladybug Component
            if self.isNewerVersionAvailable(currentLadybugVersion, ladybugVersion):
                msg = "There is a newer version of Ladybug available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        if HB:
            honeybeeVersion = versions['Honeybee']
            currentHoneybeeVersion = self.getComponentVersion() # I assume that this function will be called inside Honeybee_Honeybee Component
            if self.isNewerVersionAvailable(currentHoneybeeVersion, honeybeeVersion):
                msg = "There is a newer version of Honeybee available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        if OpenStudio:
            # This should be called inside OpenStudio component which means Honeybee is already flying
            # check if the version file exist
            openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
            versionFile = os.path.join(openStudioLibFolder, "osversion.txt")
            isNewerOSAvailable= False
            if not os.path.isfile(versionFile):
                isNewerOSAvailable= True
            else:
                # read the file
                with open(versionFile) as verFile:
                    currentOSVersion= eval(verFile.read())['version']
            
            OSVersion = versions['OpenStudio']
            
            if isNewerOSAvailable or self.isNewerVersionAvailable(currentOSVersion, OSVersion):
                sc.sticky["isNewerOSAvailable"] = True
            else:
                sc.sticky["isNewerOSAvailable"] = False
                
        if template:
            honeybeeDefaultFolder = sc.sticky["Honeybee_DefaultFolder"]
            templateFile = os.path.join(honeybeeDefaultFolder, 'OpenStudioMasterTemplate.idf')
            
            # check file doesn't exist then it should be downloaded
            if not os.path.isfile(templateFile):
                return True
            
            # find the version
            try:
                with open(templateFile) as tempFile:
                    templateVersion = eval(tempFile.readline().split("!")[-1].strip())["version"]
            except Exception, e:
                return True
            
            # finally if the file exist and already has a version, compare the versions
            currentTemplateVersion = versions['Template']
            
            return self.isNewerVersionAvailable(currentTemplateVersion, templateVersion)
            

checkIn = CheckIn(defaultFolder_)

class versionCheck(object):
    
    def __init__(self):
        self.version = self.getVersion(ghenv.Component.Message)
    
    def getVersion(self, LBComponentMessage):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        try: ver, verDate = LBComponentMessage.split("\n")
        except: ver, verDate = LBComponentMessage.split("\\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
    
    def isCurrentVersionNewer(self, desiredVersion):
        return int(self.version.replace(".", "")) >= int(desiredVersion.replace(".", ""))
    
    def isCompatible(self, LBComponent):
        code = LBComponent.Code
        # find the version that is supposed to be flying
        try: version = code.split("compatibleLBVersion")[1].split("=")[1].split("\n")[0].strip()
        except: self.giveWarning(LBComponent)
        
        desiredVersion = self.getVersion(version)
        
        if not self.isCurrentVersionNewer(desiredVersion):
            self.giveWarning(LBComponent)
            return False
        
        return True
        
    def giveWarning(self, GHComponent):
        warningMsg = "You need a newer version of Ladybug to use this compoent." + \
                     "Use updateLadybug component to update userObjects.\n" + \
                     "If you have already updated userObjects drag Ladybug_Ladybug component " + \
                     "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)


class Preparation(object):
    """ Set of functions to prepare the environment for running the studies"""
    def __init__(self):
        self.monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        self.numOfDaysEachMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.numOfHours = [24 * numOfDay for numOfDay in self.numOfDays]
    
    def giveWarning(self, warningMsg, GHComponent):
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)
        
    def checkUnits(self):
        units = sc.doc.ModelUnitSystem
        if `units` == 'Rhino.UnitSystem.Meters': conversionFactor = 1.00
        elif `units` == 'Rhino.UnitSystem.Centimeters': conversionFactor = 0.01
        elif `units` == 'Rhino.UnitSystem.Millimeters': conversionFactor = 0.001
        elif `units` == 'Rhino.UnitSystem.Feet': conversionFactor = 0.305
        elif `units` == 'Rhino.UnitSystem.Inches': conversionFactor = 0.0254
        else:
            print 'Kidding me! Which units are you using?'+ `units`+'?'
            print 'Please use Meters, Centimeters, Millimeters, Inches or Feet'
            return
        print 'Current document units is in', sc.doc.ModelUnitSystem
        print 'Conversion to Meters will be applied = ' + "%.3f"%conversionFactor
        return conversionFactor
    
    def angle2north(self, north):
        try:
            # print north
            northVector = rc.Geometry.Vector3d.YAxis
            northVector.Rotate(math.radians(float(north)), rc.Geometry.Vector3d.ZAxis)
            northVector.Unitize()
            return math.radians(float(north)), northVector
        except Exception, e:
            # print `e`
            try:
                northVector = rc.Geometry.Vector3d(north)
                northVector.Unitize()
                return rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Vector3d.YAxis, northVector, rc.Geometry.Plane.WorldXY), northVector
            except:
                    #w = gh.GH_RuntimeMessageLevel.Warning
                    #ghenv.Component.AddRuntimeMessage(w, "North should be a number or a vector!")
                    return 0, rc.Geometry.Vector3d.YAxis
    
    def setScale(self, scale, conversionFac = 1):
        try:
            if float(scale)!=0:
                try:scale = float(scale)/conversionFac
                except: scale = 1/conversionFac
            else: scale = 1/conversionFac
        except: scale = 1/conversionFac
        return scale
    
    def nukedir(self, dir, rmdir = True):
        # copied from 
        if dir[-1] == os.sep: dir = dir[:-1]
        files = os.listdir(dir)
        for file in files:
            if file == '.' or file == '..': continue
            path = dir + os.sep + file
            if os.path.isdir(path):
                self.nukedir(path)
            else:
                os.unlink(path)
        if rmdir: os.rmdir(dir)
    
    def readRunPeriod(self, runningPeriod, p = True, full = True):
        if not runningPeriod or runningPeriod[0]==None:
            runningPeriod = ((1, 1, 1),(12, 31, 24))
            
        stMonth = runningPeriod [0][0]; stDay = runningPeriod [0][1]; stHour = runningPeriod [0][2];
        endMonth = runningPeriod [1][0]; endDay = runningPeriod [1][1]; endHour = runningPeriod [1][2];
        
        if p:
            startDay = self.hour2Date(self.date2Hour(stMonth, stDay, stHour))
            startHour = startDay.split(' ')[-1]
            startDate = startDay.Replace(startHour, "")[:-1]
            
            endingDay = self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            endingHour = endingDay.split(' ')[-1]
            endingDate = endingDay.Replace(endingHour, "")[:-1]
            
            #if full:
            #    print 'Analysis period is from', startDate, 'to', endingDate
            #    print 'Between hours ' + startHour + ' to ' + endingHour
            #
            #else: print startDay, ' - ', endingDay
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    def checkPlanarity(self, brep, tol = 1e-3):
        # planarity tolerance should change for different 
        return brep.Faces[0].IsPlanar(tol)
    
    def findDiscontinuity(self, curve, style, includeEndPts = True):
        # copied and modified from rhinoScript (@Steve Baer @GitHub)
        """Search for a derivatitive, tangent, or curvature discontinuity in
        a curve object.
        Parameters:
          curve_id = identifier of curve object
          style = The type of continuity to test for. The types of
              continuity are as follows:
              Value    Description
              1        C0 - Continuous function
              2        C1 - Continuous first derivative
              3        C2 - Continuous first and second derivative
              4        G1 - Continuous unit tangent
              5        G2 - Continuous unit tangent and curvature
        Returns:
          List 3D points where the curve is discontinuous
        """
        dom = curve.Domain
        t0 = dom.Min
        t1 = dom.Max
        points = []
        #if includeEndPts: points.append(curve.PointAtStart)
        get_next = True
        while get_next:
            get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
            if get_next:
                points.append(curve.PointAt(t))
                t0 = t # Advance to the next parameter
        if includeEndPts: points.append(curve.PointAtEnd)
        return points
    
    def checkHour(self, hour):
        if hour<1: hour = 1
        elif hour%24==0: hour = 24
        else: hour = hour%24
        return hour

    def checkMonth(self, month):
        if month<1: month = 1
        elif month%12==0: month = 12
        else: month = month%12
        return month

    def checkDay(self, day, month, component = None):
        w = gh.GH_RuntimeMessageLevel.Warning
        if day<1:
            if component!=None:
                component.AddRuntimeMessage(w, "Day " + `day` + " is changed to 1.")
            day = 1
        if month == 2 and day > 28:
            if component!=None:
                msg = "Feb. has 28 days. The date is corrected by Ladybug."
                component.AddRuntimeMessage(w, msg)
            day = 28
            
        elif (month == 4 or month == 6 or month == 9 or month == 11) and day > 30:
            if component!=None:
                msg = self.monthList[month-1] + " has 30 days. The date is corrected by Ladybug."
                component.AddRuntimeMessage(w, msg)
            day = 30
            
        elif day > 31:
            if component!=None:
                msg = self.monthList[month-1] + " has 31 days. The date is corrected by Ladybug."
                component.AddRuntimeMessage(w, msg)
            day = 31
        
        return day
    
    def hour2Date(self, hour, alternate = False):
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        numOfHours = [24 * numOfDay for numOfDay in numOfDays]
        #print hour/24
        if hour%8760==0 and not alternate: return `31`+ ' ' + 'DEC' + ' 24:00'
        elif hour%8760==0: return 31, 11, 24
    
        for h in range(len(numOfHours)-1):
            if hour <= numOfHours[h+1]: month = self.monthList[h]; break
        try: month
        except: month = self.monthList[h] # for the last hour of the year
    
        if (hour)%24 == 0:
            day = int((hour - numOfHours[h]) / 24)
            time = `24` + ':00'
            hour = 24
        else:
            day = int((hour - numOfHours[h]) / 24) + 1
            minutes = `int(round((hour - math.floor(hour)) * 60))`
            if len(minutes) == 1: minutes = '0' + minutes
            time = `int(hour%24)` + ':' + minutes
        if alternate:
            time = hour%24
            if time == 0: time = 24
            month = self.monthList.index(month)
            return day, month, time
            
        return (`day` + ' ' + month + ' ' + time)

    def tupleStr2Tuple(self, str):
        strSplit = str[1:-1].split(',')
        return (int(strSplit[0]), int(strSplit[1]), int(strSplit[2]))

    def date2Hour(self, month, day, hour):
        # fix the end day
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        JD = numOfDays[int(month)-1] + int(day)
        return (JD - 1) * 24 + hour
    
    def getHour(self, JD, hour):
        return (JD - 1) * 24 + hour
    
    def getJD(self, month, day):
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        return numOfDays[int(month)-1] + int(day)
        
    def getCenPt(self, cenPt):
        if cenPt is None:
            return rc.Geometry.Point3d.Origin
        else:
            try: return rs.coerce3dpoint(cenPt)
            except:
                try: return rc.Geometry.Point3d(cenPt)
                except: return rc.Geometry.Point3d.Origin
    
    def selectHourlyData(self, hourlyData, analysisPeriod):
        # separate data
        indexList, listInfo = self.separateList(hourlyData, self.strToBeFound)
    
        #separate lists of lists
        separatedLists = []
        for i in range(len(indexList)-1):
            selList = []
            [selList.append(float(x)) for x in hourlyData[indexList[i]+7:indexList[i+1]]]
            separatedLists.append(selList)
    
        # read analysis period
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(analysisPeriod)
        
        selHourlyData =[];
        
        for l in range(len(separatedLists)):
            [selHourlyData.append(item) for item in listInfo[l][:4]]
            selHourlyData.append('Hourly')
            selHourlyData.append((stMonth, stDay, stHour))
            selHourlyData.append((endMonth, endDay, endHour))
            # select data
            stAnnualHour = self.date2Hour(stMonth, stDay, stHour)
            endAnnualHour = self.date2Hour(endMonth, endDay, endHour)
            
            # check it goes from the end of the year to the start of the year
            if stAnnualHour < endAnnualHour:
                for i, item in enumerate(separatedLists[l][stAnnualHour-1:endAnnualHour]):
                    if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
                type = True
            else:
                for i, item in enumerate(separatedLists[l][stAnnualHour-1:]):
                    if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
                
                for i, item in enumerate(separatedLists[l][:endAnnualHour]):
                    if stHour-1 <= i %24 <= endHour-1: selHourlyData.append(item)
                type = False
        
        return selHourlyData
    
    
    def getHOYs(self, hours, days, months, timeStep, method = 0):
        
        if method == 1: stDay, endDay = days
            
        numberOfDaysEachMonth = self.numOfDaysEachMonth
        
        if timeStep != 1: hours = rs.frange(hours[0], hours[-1] + 1 - 1/timeStep, 1/timeStep)
        
        HOYS = []
        
        for monthCount, m in enumerate(months):
            # just a single day
            if method == 1 and len(months) == 1 and stDay - endDay == 0:
                days = [stDay]
            # few days in a single month
            
            elif method == 1 and len(months) == 1:
                days = range(stDay, endDay + 1)
            
            elif method == 1:
                #based on analysis period
                if monthCount == 0:
                    # first month
                    days = range(stDay, numberOfDaysEachMonth[m-1] + 1)
                elif monthCount == len(months) - 1:
                    # last month
                    days = range(1, self.checkDay(endDay, m) + 1)
                else:
                    #rest of the months
                    days = range(1, numberOfDaysEachMonth[m-1] + 1)
            
            for d in days:
                for h in hours:
                    h = self.checkHour(float(h))
                    m  = self.checkMonth(int(m))
                    d = self.checkDay(int(d), m)
                    HOY = self.date2Hour(m, d, h)
                    if HOY not in HOYS: HOYS.append(int(HOY))
        
        return HOYS
    
    
    def getHOYsBasedOnPeriod(self, analysisPeriod, timeStep):
        
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(analysisPeriod, True, False)
        
        if stMonth > endMonth:
            months = range(stMonth, 13) + range(1, endMonth + 1)
        else:
            months = range(stMonth, endMonth + 1)
        
        # end hour shouldn't be included
        hours  = range(stHour, endHour+1)
        
        days = stDay, endDay
        
        HOYS = self.getHOYs(hours, days, months, timeStep, method = 1)
        
        return HOYS, months, days
    
    
    
    def readLegendParameters(self, legendPar, getCenter = True):
        if legendPar == []: legendPar = [None] * 8
        if legendPar[0] == None: lowB = 'min'
        elif legendPar[0] == 'min': lowB = 'min'
        else: lowB = float(legendPar[0])
        if legendPar[1] == None: highB = 'max'
        elif legendPar[1] == 'max': highB = 'max'
        else: highB = float(legendPar[1])
        if legendPar[2] == None: numSeg = 11
        else: numSeg = float(legendPar[2])
        if not legendPar[3] or legendPar[3][0] == None:
            customColors = [System.Drawing.Color.FromArgb(75, 107, 169), System.Drawing.Color.FromArgb(115, 147, 202),
                        System.Drawing.Color.FromArgb(170, 200, 247), System.Drawing.Color.FromArgb(193, 213, 208),
                        System.Drawing.Color.FromArgb(245, 239, 103), System.Drawing.Color.FromArgb(252, 230, 74),
                        System.Drawing.Color.FromArgb(239, 156, 21), System.Drawing.Color.FromArgb(234, 123, 0),
                        System.Drawing.Color.FromArgb(234, 74, 0), System.Drawing.Color.FromArgb(234, 38, 0)]
        else: customColors = legendPar[3]
        
        # get the base point
        if legendPar[4] or getCenter: legendBasePoint = self.getCenPt(legendPar[4])
        else: legendBasePoint = None
        
        # print len(legendPar)
        if legendPar[5] == None or float(legendPar[5])==0: legendScale = 1
        else: legendScale = legendPar[5]
        
        if legendPar[6] == None: legendFont = 'Verdana'
        else: legendFont = legendPar[6]
        
        if legendPar[7] == None: legendFontSize = None
        else: legendFontSize = legendPar[7]
        
        try:
            if legendPar[8] == None: legendBold = False
            else: legendBold = legendPar[8]
        except: legendBold = False

        return lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold
    
    def readOrientationParameters(self, orientationStudyP):
        try:
            runOrientation = orientationStudyP[0]
            
            if orientationStudyP[1]==[] or orientationStudyP[1]==False: rotateContext = False
            elif orientationStudyP[1]==True: rotateContext = True
            else:
                # just carry the geometries to next component
                rotateContext = orientationStudyP[1]
            
            if orientationStudyP[2] != None: rotationBasePt = rs.coerce3dpoint(orientationStudyP[2])
            else: rotationBasePt = 'set2center'
            angles = orientationStudyP[3]
            return runOrientation, rotateContext, rotationBasePt, angles
        
        except Exception, e:
            #print `e`
            return False, False, None, [0]
    
    def cleanAndCoerceList(self, brepList):
        """ This definition clean the list and add them to RhinoCommon"""
        outputMesh = []
        outputBrep = []
        
        for id in brepList:
            if rs.IsMesh(id):
                geo = rs.coercemesh(id)
                if geo is not None:
                    outputMesh.append(geo)
                    try: rs.DeleteObject(id)
                    except: pass
                
            elif rs.IsBrep(id):
                geo = rs.coercebrep(id)
                if geo is not None:
                    outputBrep.append(geo)
                    try: rs.DeleteObject(id)
                    except: pass
                    
                else:
                    # the idea was to remove the problematice surfaces
                    # not all the geometry which is not possible since
                    # badGeometries won't pass rs.IsBrep()
                    tempBrep = []
                    surfaces = rs.ExplodePolysurfaces(id)
                    for surface in surfaces:
                        geo = rs.coercesurface(surface)
                        if geo is not None:
                            tempBrep.append(geo)
                            try: rs.DeleteObject(surface)
                            except: pass
                    geo = rc.Geometry.Brep.JoinBreps(tempBrep, sc.doc.ModelAbsoluteTolerance)
                    for Brep in tempBrep:
                        Brep.Dispose()
                        try: rs.DeleteObject(id)
                        except: pass
                    outputBrep.append(geo)
        return outputMesh, outputBrep
    
    def flattenList(self, l):
        return list(chain.from_iterable(l))
    
    def makeWorkingDir(self, workingDir = sc.sticky["Ladybug_DefaultFolder"]):
        
        if workingDir== None:
            workingDir = sc.sticky["Ladybug_DefaultFolder"]
        if not os.path.exists(workingDir):
            try:
                os.makedirs(workingDir)
                # print 'current working directory is set to: ', workingDir
            except:
                print 'cannot create the working directory as: ', workingDir + \
                      '\nPlease set a new working directory'
                return -1
        return workingDir

    ## download File
    def downloadFile(self, url, workingDir, timeout = 20):
        localFilePath = workingDir + '/' + url.split('/')[-1]
        client = System.Net.WebClient()
        client.DownloadFile(url, localFilePath)
        
        
    def downloadGenCumulativeSky(self, workingDir):
        # download the Gencumulative Sky
        if not os.path.isfile(workingDir + '\GenCumulativeSky.exe'):
            try:
                print 'Downloading GenCumulativeSky.exe to ', workingDir
                self.downloadFile('https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/GenCumulativeSky.exe', workingDir, 30)
                print 'Download complete!'
            except:
                allSet = False
                print 'Download failed!!! You need GenCumulativeSky.exe to use this component.' + \
                '\nPlease check your internet connection, and try again!' + \
                '\nIf that does not work, you must manually download the file from this address:' + \
                '\nhttps://github.com/mostaphaRoudsari/ladybug/raw/master/resources/GenCumulativeSky.exe' + \
                '\nand copy it here:' + str(workingDir)
        else:
            pass
            #print 'GenCumulativeSky.exe is already available at ', workingDir + \
            #'\nPlease make sure you are using the latest version of GenCumulativeSky.exe'


    def downloadGendaymtx(self, workingDir):
        # download the Gencumulative Sky
        if not os.path.isfile(workingDir + '\gendaymtx.exe'):
            try:
                print 'Downloading gendaymtx.exe to ', workingDir
                self.downloadFile('https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/gendaymtx.exe', workingDir, 20)
                print 'Download complete!'
            except:
                allSet = False
                print 'Download failed!!! You need gendaymtx.exe to use this component.' + \
                '\nPlease check your internet connection, and try again!' + \
                '\nIf that does not work, you must manually download the file from this address:' + \
                '\nhttps://github.com/mostaphaRoudsari/ladybug/raw/master/resources/gendaymtx.exe' + \
                '\nand copy it here:' + str(workingDir)
        else:
            pass
            #print 'GenCumulativeSky.exe is already available at ', workingDir + \
            #'\nPlease make sure you are using the latest version of GenCumulativeSky.exe'

    def separateList(self, list, key):
            indexList = []; listInfo = [];
            for item in range(len(list)):
                if list[item] == key:
                    indexList.append(item)
                    listInfo.append(list[item : item+7])
            # in case of numbers with no str information
            if len(indexList) == 0:
                indexList = [-7, len(list)];
                listInfo = [[key, 'somewhere','someData', 'someUnits', 'someTimeStep',(1, 1, 1),(12, 31, 24)]]
            else:
                indexList.append(len(list))
                
            return indexList, listInfo

    ## read epw file
    def epwLocation(self, epw_file):
        epwfile = open(epw_file,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        while 1>0: #remove empty cells from the end of the list if any
            try: float(csheadline[-1]); break
            except: csheadline.pop()
        locName = ''
        for hLine in range(1,4):
            if csheadline[hLine] != '-':
                locName = locName + csheadline[hLine] + '_'
        locName = locName[:-1]
        lat = csheadline[-4]
        lngt = csheadline[-3]
        timeZone = csheadline[-2]
        elev = csheadline[-1].strip()
        locationString = "Site:Location,\n" + \
            locName + ',\n' + \
            lat+',      !Latitude\n' + \
            lngt+',     !Longitude\n' + \
            timeZone+',     !Time Zone\n' + \
            elev + ';       !Elevation'
        epwfile.close
        return locName, lat, lngt, timeZone, elev, locationString

    def decomposeLocation(self, location):
        locationStr = location.split('\n')
        newLocStr = ""
        #clean the idf file
        for line in locationStr:
            if '!' in line:
                line = line.split('!')[0]
                newLocStr  = newLocStr + line.replace(" ", "")
            else:
                newLocStr  = newLocStr + line
        
        newLocStr = newLocStr.replace(';', "")
        site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
        
        return locationName, float(latitude), float(longitude), float(timeZone), float(elevation)

    def separateHeader(self, inputList):
        num = []; str = []
        for item in inputList:
            try: num.append(float(item))
            except: str.append(item)
        return num, str
    
    def depthData(self,groundtemp,depthdataposition):
        """ This function takes two arguements the list of the ground temp data and the index which defines what 
        depth the data is @. THe purpose is to replace 'Depth' seen in the groundTempData function 
        with depth at which the temperatures are in the epw in meters 
        """
       
        for count, i in enumerate(groundtemp):
            if i == 'Depth':
                groundtemp[count] = 'Ground temperature at ' + str(depthdataposition) + ' m' 
            else:
                pass
    
    strToBeFoundgt = 'key:location/Depth temp @ (m)/units/frequency/startsAt/endsAt' ## String for GroundTempData function
    
    def groundTempData(self, epw_file, location = 'Somewhere!', Depth = 'Not entered!'):
        
        """ This function reads the ground temperature data from an epw file, and then converts it to a list of floats 
            the list of floats is then subsequently re-arranaged by using the function depthData so that the depth below ground to which the 
            ground temperature data corresponds to is the 2nd item in the list of all the ground temperature data.
        """
        
        
        epwfile = open(epw_file,"r")
        
        groundtemp1st = [self.strToBeFoundgt, location, 'Depth', 'C', 'Monthly', (1, 1, 1), (12, 31, 24)];
        groundtemp2nd = [self.strToBeFoundgt, location, 'Depth' ,  'C', 'Monthly', (1, 1, 1), (12, 31, 24)];
        groundtemp3rd = [self.strToBeFoundgt, location, 'Depth' ,  'C', 'Monthly', (1, 1, 1), (12, 31, 24)];

        lnum = 1 # Line number
        
        with epwfile as i:
            for line in i: 
                if lnum == 3:
                    noData = False
                    groundtemp = epwfile.readline().split(',') ## Adding line from epw to file as a string then splitting it along , this line in the epw contains groundtemp data
                    
                    self.groundtemp = groundtemp
                    
                    def stringtoFloat(sequence): # stringtoFloattion that converts strings to floats, if not possible it passes
                    	strings = []
                    	seq = [] # line 18 - data = CSV.Branch(month_-1) creates grasshoppers own List[object] this does not contain a remove method'
                    	# therefore in line 4 6 and 7 we must add the data to a python list to be able to use the function
                    	for item in sequence:
                    		seq.append(item)
                    	for i in range(len(seq)):
                    		try:
                    			seq[i] = float(seq[i])
                    		except:
                    			strings.append(seq[i])
                    	for x in strings:
                    		seq.remove(x)
                    	return seq
                    
                    if noData == False:
                        groundtemp1st.extend(stringtoFloat(groundtemp[6:18])) ## Need to use func and not just float as it is a list using float() won't work
                        groundtemp2nd.extend(stringtoFloat(groundtemp[22:34]))
                        groundtemp3rd.extend(stringtoFloat(groundtemp[38:50]))
                        
                        self.depthData(groundtemp1st,float(groundtemp[2])) ## Referring to the depthData function 
                        try: self.depthData(groundtemp2nd,float(groundtemp[18])) ## In each groundtemp list changing 'Depth' index to each datasets corresponding depth in the epw
                        except: pass
                        try: self.depthData(groundtemp3rd,float(groundtemp[34]))
                        except: pass
                    
                else:
                    pass
                lnum += 1
                
        return groundtemp1st,groundtemp2nd,groundtemp3rd
    
    def printgroundTempData(self,groundtemp):
                    
        try: print 'Ground temperature data contains monthly average temperatures at ' + groundtemp[1] + ' different depths ' + groundtemp[2] + ' meters (1st) ' + groundtemp[18]+ ' meters (2nd) '+ groundtemp[34]+' meters (3rd) respectively'
        except:
            if groundtemp[1] == '':
                print 'No ground temperatures found in weather file.'
                noData = True
            else: print 'Ground temperature data contains monthly average temperatures at ' + groundtemp[1] + ' different depths ' + groundtemp[2] + ' meters'
        
    
    strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
    
    def epwDataReader(self, epw_file, location = 'Somewhere!'):
        # weather data
        modelYear = [self.strToBeFound, location, 'Year', 'Year', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dbTemp = [self.strToBeFound, location, 'Dry Bulb Temperature', 'C', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dewPoint = [self.strToBeFound, location, 'Dew Point Temperature', 'C', 'Hourly', (1, 1, 1), (12, 31, 24)];
        RH = [self.strToBeFound, location, 'Relative Humidity', '%', 'Hourly', (1, 1, 1), (12, 31, 24)];
        windSpeed = [self.strToBeFound, location, 'Wind Speed', 'm/s', 'Hourly', (1, 1, 1), (12, 31, 24)];
        windDir = [self.strToBeFound, location, 'Wind Direction', 'degrees', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dirRad = [self.strToBeFound, location, 'Direct Normal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        difRad = [self.strToBeFound, location, 'Diffuse Horizontal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        glbRad = [self.strToBeFound, location, 'Global Horizontal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dirIll = [self.strToBeFound, location, 'Direct Normal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        difIll = [self.strToBeFound, location, 'Diffuse Horizontal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        glbIll = [self.strToBeFound, location, 'Global Horizontal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        cloudCov = [self.strToBeFound, location, 'Total Cloud Cover', 'tenth', 'Hourly', (1, 1, 1), (12, 31, 24)];
        rainDepth = [self.strToBeFound, location, 'Liquid Precipitation Depth', 'mm', 'Hourly', (1, 1, 1), (12, 31, 24)];
        barPress = [self.strToBeFound, location, 'Barometric Pressure', 'Pa', 'Hourly', (1, 1, 1), (12, 31, 24)];
        epwfile = open(epw_file,"r")
        lnum = 1 # line number
        for line in epwfile:
            if lnum > 8:
                modelYear.append(float(line.split(',')[0]))
                dbTemp.append(float(line.split(',')[6]))
                dewPoint.append(float(line.split(',')[7]))
                RH.append(float(line.split(',')[8]))
                barPress.append(float(line.split(',')[9]))
                windSpeed.append(float(line.split(',')[21]))
                windDir.append(float(line.split(',')[20]))
                dirRad.append(float(line.split(',')[14]))
                difRad.append(float(line.split(',')[15]))
                glbRad.append(float(line.split(',')[13]))
                dirIll.append(float(line.split(',')[17]))
                difIll.append(float(line.split(',')[18]))
                glbIll.append(float(line.split(',')[16]))
                cloudCov.append(float(line.split(',')[22]))
                try:
                    if float(line.split(',')[33])!=999: rainDepth.append(float(line.split(',')[33]))
                    else: rainDepth.append(0.0)
                except: pass
            lnum += 1
        return dbTemp, dewPoint, RH, windSpeed, windDir, dirRad, difRad, glbRad, dirIll, difIll, glbIll, cloudCov, rainDepth, barPress, modelYear
    
    ##### Start of Gencumulative Sky
    def removeBlank(self, str):
        newStr = ''
        chars = [' ', ',', '.', '-', '   ', '    ', '\\', '/']
        for c in str:
            if c in chars: newStr = newStr + '_'
            else: newStr = newStr + c
        return newStr
    
    def removeBlankLight(self, str):
        newStr = ''
        chars = [' ', ',', '.', '-', '   ', '    ']
        for c in str:
            if c in chars: newStr = newStr + '_'
            else: newStr = newStr + c
        return newStr
    
    def copyFile(self, inputFile, copyFullpath):
        if not os.path.isfile(copyFullpath): shutil.copyfile(inputFile, copyFullpath)
        return copyFullpath
        
    def genCumSkyStr(self, runningPeriod, subWorkingDir, workingDir, newLocName, lat, lngt, timeZone):
        # read running period
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(runningPeriod)
        
        # sun modes: +s1 is "smeared sun" approach, and +s2 use "binned sun" approach
        # read this paper for more information:
        # http://plea-arch.net/PLEA/ConferenceResources/PLEA2004/Proceedings/p1153final.pdf
        sunModes = ['+s1']
        batchStr = workingDir[0:2] + "\ncd " + subWorkingDir + "\n"
        for sunMode in sunModes:
            calFileName = subWorkingDir + "\\" + newLocName + '_' + sunMode[-1] + '.cal'
            reportFileName = subWorkingDir + "\\" + newLocName + '_' + sunMode[-1] + '_report.txt' 
            newLine = workingDir + "\GenCumulativeSky " + sunMode + \
                " -a " + lat + \
                " -o " + `-1 * float(lngt)` + \
                " -m " + `-15* float(timeZone)` + \
                " -p -E -time " + `stHour` + " " + `endHour` + \
                " -date " + `stMonth` + " " + `stDay` + \
                " " + `endMonth` + " " + `endDay` + \
                " " + subWorkingDir + "\\" + newLocName + '.epw' + \
                " 1> " + calFileName + \
                " 2> " + reportFileName + "\n"
            batchStr = batchStr + newLine
        batchStr = batchStr + 'cd\\'
        return batchStr
    
    def readCalFile(self, calFileName):
        # this functions comes from trial and error
        # Even though I figured out how to read it for GenCummulativeSky,
        # I still don't underestand the structure of a cal file 100%
        try:
            calRes = open(calFileName, "r")
            lines = calRes.readlines()
            segNum = [30, 30, 24, 24, 18, 12, 6, 1]
            strConv = [0.0435, 0.0416, 0.0474, 0.0407, 0.0429, 0.0445, 0.0455, 0.0344] #steradians conversion
            result = []
            for rowNum in range(7):
                countLine = 0
                for l in range(len(lines)):
                    if lines[l][:4] == 'row'+`rowNum`:
                        for ll in range(l+1,l+1+segNum[rowNum]):
                            result.append (strConv[rowNum] * float(lines[ll][0:-2]))
            for l in range(len(lines)):
                if lines[l][:4] == 'row7':
                    result.append(strConv[7] * float(lines[l][15:-5]))
                calRes.close()
            return result
        except:
            print "There is an error in the result file" #+ \
                    #"\nCheck the report file at " + reportFileName + \
                    #"\n\nEmail me at (sadeghipour@gmail.com) if you couldn't solve the problem."
            return -1
    
    def printReportFile(self, reportFileName):
        try:
            reportFile = open(reportFileName, "r")
            SUH = []; lineCount = 0
            for line in reportFile:
                if lineCount == 0:
                    print line[:-1] + "."
                    for ch in line:
                        try: num = int(ch); SUH.append(num)
                        except: pass
                    break
            #sunUpHours = 0; numCount = 0
            #for num in SUH:
            #    sunUpHours = sunUpHours + num * (10 ** (len(SUH) - numCount -1))
            #    numCount += 1
            #reportFile.close()
            #return sunUpHours 
        except:
            print "There is no report file!!"
            return -1
            
    #### End of Gencumulative Sky
    
    def generateSkyGeo(self, cenPt, skyType, scale):
        """
        This script is based of the Treganza sky
        skyType:
            0 is Tregenza Sky with 145 + 1 patches
            1 is Reinhart Sky with 577 + 3 patches
        # number of segments in each row of the sky
        # 15 rows - total 580
        """
        
        originalNumSeg = [30, 30, 24, 24, 18, 12, 6]
        
        if skyType==0:
            numSeg = originalNumSeg + [1]
        else:
            numSeg =[]
            for numOfSeg in originalNumSeg:
                for i in range(skyType+1):
                    numSeg.append(numOfSeg * (skyType+1))
            numSeg = numSeg + [1]
        
        # rotation line axis
        lineVector = rc.Geometry.Vector3d.ZAxis
        lineVector.Reverse()
        lineAxis = rc.Geometry.Line(cenPt, lineVector)
        
        # base plane to draw the arcs
        basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.XAxis)
        baseVector = rc.Geometry.Vector3d.YAxis
        
        
        # 29 is the total number of devisions 14 + 1 + 14
        eachSegVerticalAngle = (math.pi)/ (2 * len(numSeg) - 1)/2
        
        skyPatches = []
        for row in range(len(numSeg)):
            # create the base arc
            stPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector)
            
            if row == len(numSeg)-1:
                eachSegVerticalAngle = eachSegVerticalAngle/2
                
            baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
            midPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
            
            baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
            endPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
            
            baseArc = rc.Geometry.Arc(stPt, midPt, endPt).ToNurbsCurve()
            
            # create the row
            numOfSeg = numSeg[row]
            angleDiv = 2 * math.pi / numOfSeg
            
            for patchNum in range(numOfSeg):
                start_angle = (patchNum * angleDiv) -(angleDiv/2)
                end_angle = ((patchNum + 1) * angleDiv) - (angleDiv/2)
                patch = rc.Geometry.RevSurface.Create(baseArc, lineAxis, start_angle, end_angle)
                skyPatches.append(patch.ToBrep())
                
        return skyPatches
    
    # Tregenza Sky Dome
    def generateTregenzaSkyGeo(self, cenPt, scale):
        patches = []; baseArcs = []; Pts = [];
        numSeg = [30, 30, 24, 24, 18, 12, 6, 1]
        # draw the base arc
        basePlane = rs.PlaneFromNormal(cenPt,(1,0,0))
        mainArc = rs.AddArc(basePlane, 100 * scale , 90)
        startPt = rs.CurveStartPoint(mainArc)
        endPt = rs.CurveEndPoint(mainArc)
        Pts.append(startPt)
    
        # base curves
        for angle in rs.frange(5.75,90, 5.75):
            rotatedPt = rs.RotateObject(rs.AddPoint(startPt[0],startPt[1],startPt[2]), cenPt, angle, (1,0,0), True)
            Pts.append(rotatedPt)
        Pts.append(endPt)
    
        for i in range(0,16,2):
            arc = rs.AddArc3Pt(Pts[0+i], Pts[2+i], Pts[1+i])
            baseArcs.append(arc)
    
        assert len(baseArcs) == 8
        revAx = rs.AddLine(cenPt,endPt)
        for j in range(len(baseArcs)):
            incDeg = (360/numSeg[j])/2
            rotationDeg = -(360/numSeg[j])
            startArc = rs.RotateObject(baseArcs[j], cenPt, incDeg, rs.VectorCreate(endPt,cenPt), False)
            for num in range(numSeg[j]):
                patches.append(rs.AddRevSrf(startArc, revAx, rotationDeg + (rotationDeg * num), (rotationDeg * num)))
        
        patchesInRC = [rs.coercesurface(patch) for patch in patches]
        
        return patchesInRC

    
    def genRadRoseArrows(self, movingVectors, radResult, cenPt, sc, internalSc = 0.2, arrowHeadScale = 1):
        radArrows = []; vecNum = 0
        
        for vec in movingVectors:
            movingVec = (sc* internalSc * vec * radResult[vecNum])
            ptMoveDis = movingVec.Length * 0.1 * internalSc * arrowHeadScale 
            
            arrowEndpt = rc.Geometry.Point3d.Add(cenPt, movingVec)
            baseLine = rc.Geometry.LineCurve(cenPt, arrowEndpt)
            basePt = baseLine.PointAt(baseLine.DivideByCount(4, True)[-2])
            
            ptMovingVec_right = rc.Geometry.Vector3d(vec.X, vec.Y, vec.Z)
            ptMovingVec_right.Rotate(math.radians(90), rc.Geometry.Vector3d.ZAxis)
            ptMovingVec_right.Unitize()
            ptMovingVec_right = rc.Geometry.Vector3d.Multiply(ptMoveDis, ptMovingVec_right)
            rightPt = rc.Geometry.Point3d.Add(basePt, ptMovingVec_right)
            
            ptMovingVec_right.Reverse()
            leftPt = rc.Geometry.Point3d.Add(basePt, ptMovingVec_right)
            
            
            tempMesh = rc.Geometry.Mesh()
            tempMesh.Vertices.Add(cenPt) #0
            tempMesh.Vertices.Add(rightPt) #1
            tempMesh.Vertices.Add(arrowEndpt) #2
            tempMesh.Vertices.Add(leftPt) #3
            tempMesh.Faces.AddFace(0, 1, 2, 3)
            
            
            radArrows.append(tempMesh)
            vecNum += 1
        
        return radArrows
    
    def getReinhartPatchesNormalVectors(self):
        ReinhartPatchesNormalVectors = [
        (0.0,0.998533,0.054139),(0.104375,0.993063,0.054139),(0.207607,0.976713,0.054139),
    (0.308564,0.949662,0.054139),(0.40614,0.912206,0.054139),(0.499267,0.864755,0.054139),
    (0.586923,0.807831,0.054139),(0.668149,0.742055,0.054139),(0.742055,0.668149,0.054139),
    (0.807831,0.586923,0.054139),(0.864755,0.499267,0.054139),(0.912206,0.40614,0.054139),
    (0.949662,0.308564,0.054139),(0.976713,0.207607,0.054139),(0.993063,0.104375,0.054139),
    (0.998533,0.0,0.054139),(0.993063,-0.104375,0.054139),(0.976713,-0.207607,0.054139),
    (0.949662,-0.308564,0.054139),(0.912206,-0.40614,0.054139),(0.864755,-0.499267,0.054139),
    (0.807831,-0.586923,0.054139),(0.742055,-0.668149,0.054139),(0.668149,-0.742055,0.054139),
    (0.586923,-0.807831,0.054139),(0.499267,-0.864755,0.054139),(0.40614,-0.912206,0.054139),
    (0.308564,-0.949662,0.054139),(0.207607,-0.976713,0.054139),(0.104375,-0.993063,0.054139),
    (0.0,-0.998533,0.054139),(-0.104375,-0.993063,0.054139),(-0.207607,-0.976713,0.054139),
    (-0.308564,-0.949662,0.054139),(-0.40614,-0.912206,0.054139),(-0.499267,-0.864755,0.054139),
    (-0.586923,-0.807831,0.054139),(-0.668149,-0.742055,0.054139),(-0.742055,-0.668149,0.054139),
    (-0.807831,-0.586923,0.054139),(-0.864755,-0.499267,0.054139),(-0.912206,-0.40614,0.054139),
    (-0.949662,-0.308564,0.054139),(-0.976713,-0.207607,0.054139),(-0.993063,-0.104375,0.054139),
    (-0.998533,0.0,0.054139),(-0.993063,0.104375,0.054139),(-0.976713,0.207607,0.054139),
    (-0.949662,0.308564,0.054139),(-0.912206,0.40614,0.054139),(-0.864755,0.499267,0.054139),
    (-0.807831,0.586923,0.054139),(-0.742055,0.668149,0.054139),(-0.668149,0.742055,0.054139),
    (-0.586923,0.807831,0.054139),(-0.499267,0.864755,0.054139),(-0.40614,0.912206,0.054139),
    (-0.308564,0.949662,0.054139),(-0.207607,0.976713,0.054139),(-0.104375,0.993063,0.054139),
    (0.0,0.986827,0.161782),(0.103151,0.981421,0.161782),(0.205173,0.965262,0.161782),
    (0.304946,0.938528,0.161782),(0.401379,0.901511,0.161782),(0.493413,0.854617,0.161782),
    (0.580042,0.798359,0.161782),(0.660316,0.733355,0.161782),(0.733355,0.660316,0.161782),
    (0.798359,0.580042,0.161782),(0.854617,0.493413,0.161782),(0.901511,0.401379,0.161782),
    (0.938528,0.304946,0.161782),(0.965262,0.205173,0.161782),(0.981421,0.103151,0.161782),
    (0.986827,0.0,0.161782),(0.981421,-0.103151,0.161782),(0.965262,-0.205173,0.161782),
    (0.938528,-0.304946,0.161782),(0.901511,-0.401379,0.161782),(0.854617,-0.493413,0.161782),
    (0.798359,-0.580042,0.161782),(0.733355,-0.660316,0.161782),(0.660316,-0.733355,0.161782),
    (0.580042,-0.798359,0.161782),(0.493413,-0.854617,0.161782),(0.401379,-0.901511,0.161782),
    (0.304946,-0.938528,0.161782),(0.205173,-0.965262,0.161782),(0.103151,-0.981421,0.161782),
    (0.0,-0.986827,0.161782),(-0.103151,-0.981421,0.161782),(-0.205173,-0.965262,0.161782),
    (-0.304946,-0.938528,0.161782),(-0.401379,-0.901511,0.161782),(-0.493413,-0.854617,0.161782),
    (-0.580042,-0.798359,0.161782),(-0.660316,-0.733355,0.161782),(-0.733355,-0.660316,0.161782),
    (-0.798359,-0.580042,0.161782),(-0.854617,-0.493413,0.161782),(-0.901511,-0.401379,0.161782),
    (-0.938528,-0.304946,0.161782),(-0.965262,-0.205173,0.161782),(-0.981421,-0.103151,0.161782),
    (-0.986827,0.0,0.161782),(-0.981421,0.103151,0.161782),(-0.965262,0.205173,0.161782),
    (-0.938528,0.304946,0.161782),(-0.901511,0.401379,0.161782),(-0.854617,0.493413,0.161782),
    (-0.798359,0.580042,0.161782),(-0.733355,0.660316,0.161782),(-0.660316,0.733355,0.161782),
    (-0.580042,0.798359,0.161782),(-0.493413,0.854617,0.161782),(-0.401379,0.901511,0.161782),
    (-0.304946,0.938528,0.161782),(-0.205173,0.965262,0.161782),(-0.103151,0.981421,0.161782),
    (0.0,0.96355,0.267528),(0.100718,0.958272,0.267528),(0.200333,0.942494,0.267528),
    (0.297753,0.91639,0.267528),(0.391911,0.880247,0.267528),(0.481775,0.834459,0.267528),
    (0.56636,0.779528,0.267528),(0.644741,0.716057,0.267528),(0.716057,0.644741,0.267528),
    (0.779528,0.56636,0.267528),(0.834459,0.481775,0.267528),(0.880247,0.391911,0.267528),
    (0.91639,0.297753,0.267528),(0.942494,0.200333,0.267528),(0.958272,0.100718,0.267528),
    (0.96355,0.0,0.267528),(0.958272,-0.100718,0.267528),(0.942494,-0.200333,0.267528),
    (0.91639,-0.297753,0.267528),(0.880247,-0.391911,0.267528),(0.834459,-0.481775,0.267528),
    (0.779528,-0.56636,0.267528),(0.716057,-0.644741,0.267528),(0.644741,-0.716057,0.267528),
    (0.56636,-0.779528,0.267528),(0.481775,-0.834459,0.267528),(0.391911,-0.880247,0.267528),
    (0.297753,-0.91639,0.267528),(0.200333,-0.942494,0.267528),(0.100718,-0.958272,0.267528),
    (0.0,-0.96355,0.267528),(-0.100718,-0.958272,0.267528),(-0.200333,-0.942494,0.267528),
    (-0.297753,-0.91639,0.267528),(-0.391911,-0.880247,0.267528),(-0.481775,-0.834459,0.267528),
    (-0.56636,-0.779528,0.267528),(-0.644741,-0.716057,0.267528),(-0.716057,-0.644741,0.267528),
    (-0.779528,-0.56636,0.267528),(-0.834459,-0.481775,0.267528),(-0.880247,-0.391911,0.267528),
    (-0.91639,-0.297753,0.267528),(-0.942494,-0.200333,0.267528),(-0.958272,-0.100718,0.267528),
    (-0.96355,0.0,0.267528),(-0.958272,0.100718,0.267528),(-0.942494,0.200333,0.267528),
    (-0.91639,0.297753,0.267528),(-0.880247,0.391911,0.267528),(-0.834459,0.481775,0.267528),
    (-0.779528,0.56636,0.267528),(-0.716057,0.644741,0.267528),(-0.644741,0.716057,0.267528),
    (-0.56636,0.779528,0.267528),(-0.481775,0.834459,0.267528),(-0.391911,0.880247,0.267528),
    (-0.297753,0.91639,0.267528),(-0.200333,0.942494,0.267528),(-0.100718,0.958272,0.267528),
    (0.0,0.928977,0.370138),(0.097105,0.923888,0.370138),(0.193145,0.908676,0.370138),
    (0.28707,0.883509,0.370138),(0.377849,0.848662,0.370138),(0.464488,0.804517,0.370138),
    (0.546039,0.751558,0.370138),(0.621607,0.690364,0.370138),(0.690364,0.621607,0.370138),
    (0.751558,0.546039,0.370138),(0.804517,0.464488,0.370138),(0.848662,0.377849,0.370138),
    (0.883509,0.28707,0.370138),(0.908676,0.193145,0.370138),(0.923888,0.097105,0.370138),
    (0.928977,0.0,0.370138),(0.923888,-0.097105,0.370138),(0.908676,-0.193145,0.370138),
    (0.883509,-0.28707,0.370138),(0.848662,-0.377849,0.370138),(0.804517,-0.464488,0.370138),
    (0.751558,-0.546039,0.370138),(0.690364,-0.621607,0.370138),(0.621607,-0.690364,0.370138),
    (0.546039,-0.751558,0.370138),(0.464488,-0.804517,0.370138),(0.377849,-0.848662,0.370138),
    (0.28707,-0.883509,0.370138),(0.193145,-0.908676,0.370138),(0.097105,-0.923888,0.370138),
    (0.0,-0.928977,0.370138),(-0.097105,-0.923888,0.370138),(-0.193145,-0.908676,0.370138),
    (-0.28707,-0.883509,0.370138),(-0.377849,-0.848662,0.370138),(-0.464488,-0.804517,0.370138),
    (-0.546039,-0.751558,0.370138),(-0.621607,-0.690364,0.370138),(-0.690364,-0.621607,0.370138),
    (-0.751558,-0.546039,0.370138),(-0.804517,-0.464488,0.370138),(-0.848662,-0.377849,0.370138),
    (-0.883509,-0.28707,0.370138),(-0.908676,-0.193145,0.370138),(-0.923888,-0.097105,0.370138),
    (-0.928977,0.0,0.370138),(-0.923888,0.097105,0.370138),(-0.908676,0.193145,0.370138),
    (-0.883509,0.28707,0.370138),(-0.848662,0.377849,0.370138),(-0.804517,0.464488,0.370138),
    (-0.751558,0.546039,0.370138),(-0.690364,0.621607,0.370138),(-0.621607,0.690364,0.370138),
    (-0.546039,0.751558,0.370138),(-0.464488,0.804517,0.370138),(-0.377849,0.848662,0.370138),
    (-0.28707,0.883509,0.370138),(-0.193145,0.908676,0.370138),(-0.097105,0.923888,0.370138),
    (0.0,0.883512,0.468408),(0.115321,0.875953,0.468408),(0.22867,0.853407,0.468408),
    (0.338105,0.816259,0.468408),(0.441756,0.765144,0.468408),(0.537848,0.700937,0.468408),
    (0.624737,0.624737,0.468408),(0.700937,0.537848,0.468408),(0.765144,0.441756,0.468408),
    (0.816259,0.338105,0.468408),(0.853407,0.22867,0.468408),(0.875953,0.115321,0.468408),
    (0.883512,0.0,0.468408),(0.875953,-0.115321,0.468408),(0.853407,-0.22867,0.468408),
    (0.816259,-0.338105,0.468408),(0.765144,-0.441756,0.468408),(0.700937,-0.537848,0.468408),
    (0.624737,-0.624737,0.468408),(0.537848,-0.700937,0.468408),(0.441756,-0.765144,0.468408),
    (0.338105,-0.816259,0.468408),(0.22867,-0.853407,0.468408),(0.115321,-0.875953,0.468408),
    (0.0,-0.883512,0.468408),(-0.115321,-0.875953,0.468408),(-0.22867,-0.853407,0.468408),
    (-0.338105,-0.816259,0.468408),(-0.441756,-0.765144,0.468408),(-0.537848,-0.700937,0.468408),
    (-0.624737,-0.624737,0.468408),(-0.700937,-0.537848,0.468408),(-0.765144,-0.441756,0.468408),
    (-0.816259,-0.338105,0.468408),(-0.853407,-0.22867,0.468408),(-0.875953,-0.115321,0.468408),
    (-0.883512,0.0,0.468408),(-0.875953,0.115321,0.468408),(-0.853407,0.22867,0.468408),
    (-0.816259,0.338105,0.468408),(-0.765144,0.441756,0.468408),(-0.700937,0.537848,0.468408),
    (-0.624737,0.624737,0.468408),(-0.537848,0.700937,0.468408),(-0.441756,0.765144,0.468408),
    (-0.338105,0.816259,0.468408),(-0.22867,0.853407,0.468408),(-0.115321,0.875953,0.468408),
    (0.0,0.827689,0.561187),(0.108035,0.820608,0.561187),(0.214222,0.799486,0.561187),
    (0.316743,0.764685,0.561187),(0.413844,0.7168,0.561187),(0.503865,0.65665,0.561187),
    (0.585265,0.585265,0.561187),(0.65665,0.503865,0.561187),(0.7168,0.413844,0.561187),
    (0.764685,0.316743,0.561187),(0.799486,0.214222,0.561187),(0.820608,0.108035,0.561187),
    (0.827689,0.0,0.561187),(0.820608,-0.108035,0.561187),(0.799486,-0.214222,0.561187),
    (0.764685,-0.316743,0.561187),(0.7168,-0.413844,0.561187),(0.65665,-0.503865,0.561187),
    (0.585265,-0.585265,0.561187),(0.503865,-0.65665,0.561187),(0.413844,-0.7168,0.561187),
    (0.316743,-0.764685,0.561187),(0.214222,-0.799486,0.561187),(0.108035,-0.820608,0.561187),
    (0.0,-0.827689,0.561187),(-0.108035,-0.820608,0.561187),(-0.214222,-0.799486,0.561187),
    (-0.316743,-0.764685,0.561187),(-0.413844,-0.7168,0.561187),(-0.503865,-0.65665,0.561187),
    (-0.585265,-0.585265,0.561187),(-0.65665,-0.503865,0.561187),(-0.7168,-0.413844,0.561187),
    (-0.764685,-0.316743,0.561187),(-0.799486,-0.214222,0.561187),(-0.820608,-0.108035,0.561187),
    (-0.827689,0.0,0.561187),(-0.820608,0.108035,0.561187),(-0.799486,0.214222,0.561187),
    (-0.764685,0.316743,0.561187),(-0.7168,0.413844,0.561187),(-0.65665,0.503865,0.561187),
    (-0.585265,0.585265,0.561187),(-0.503865,0.65665,0.561187),(-0.413844,0.7168,0.561187),
    (-0.316743,0.764685,0.561187),(-0.214222,0.799486,0.561187),(-0.108035,0.820608,0.561187),
    (0.0,0.762162,0.647386),(0.099482,0.755642,0.647386),(0.197262,0.736192,0.647386),
    (0.291667,0.704146,0.647386),(0.381081,0.660052,0.647386),(0.463975,0.604664,0.647386),
    (0.53893,0.53893,0.647386),(0.604664,0.463975,0.647386),(0.660052,0.381081,0.647386),
    (0.704146,0.291667,0.647386),(0.736192,0.197262,0.647386),(0.755642,0.099482,0.647386),
    (0.762162,0.0,0.647386),(0.755642,-0.099482,0.647386),(0.736192,-0.197262,0.647386),
    (0.704146,-0.291667,0.647386),(0.660052,-0.381081,0.647386),(0.604664,-0.463975,0.647386),
    (0.53893,-0.53893,0.647386),(0.463975,-0.604664,0.647386),(0.381081,-0.660052,0.647386),
    (0.291667,-0.704146,0.647386),(0.197262,-0.736192,0.647386),(0.099482,-0.755642,0.647386),
    (0.0,-0.762162,0.647386),(-0.099482,-0.755642,0.647386),(-0.197262,-0.736192,0.647386),
    (-0.291667,-0.704146,0.647386),(-0.381081,-0.660052,0.647386),(-0.463975,-0.604664,0.647386),
    (-0.53893,-0.53893,0.647386),(-0.604664,-0.463975,0.647386),(-0.660052,-0.381081,0.647386),
    (-0.704146,-0.291667,0.647386),(-0.736192,-0.197262,0.647386),(-0.755642,-0.099482,0.647386),
    (-0.762162,0.0,0.647386),(-0.755642,0.099482,0.647386),(-0.736192,0.197262,0.647386),
    (-0.704146,0.291667,0.647386),(-0.660052,0.381081,0.647386),(-0.604664,0.463975,0.647386),
    (-0.53893,0.53893,0.647386),(-0.463975,0.604664,0.647386),(-0.381081,0.660052,0.647386),
    (-0.291667,0.704146,0.647386),(-0.197262,0.736192,0.647386),(-0.099482,0.755642,0.647386),
    (0.0,0.687699,0.725995),(0.089763,0.681816,0.725995),(0.17799,0.664267,0.725995),
    (0.263171,0.635351,0.725995),(0.34385,0.595565,0.725995),(0.418645,0.545589,0.725995),
    (0.486277,0.486277,0.725995),(0.545589,0.418645,0.725995),(0.595565,0.34385,0.725995),
    (0.635351,0.263171,0.725995),(0.664267,0.17799,0.725995),(0.681816,0.089763,0.725995),
    (0.687699,0.0,0.725995),(0.681816,-0.089763,0.725995),(0.664267,-0.17799,0.725995),
    (0.635351,-0.263171,0.725995),(0.595565,-0.34385,0.725995),(0.545589,-0.418645,0.725995),
    (0.486277,-0.486277,0.725995),(0.418645,-0.545589,0.725995),(0.34385,-0.595565,0.725995),
    (0.263171,-0.635351,0.725995),(0.17799,-0.664267,0.725995),(0.089763,-0.681816,0.725995),
    (0.0,-0.687699,0.725995),(-0.089763,-0.681816,0.725995),(-0.17799,-0.664267,0.725995),
    (-0.263171,-0.635351,0.725995),(-0.34385,-0.595565,0.725995),(-0.418645,-0.545589,0.725995),
    (-0.486277,-0.486277,0.725995),(-0.545589,-0.418645,0.725995),(-0.595565,-0.34385,0.725995),
    (-0.635351,-0.263171,0.725995),(-0.664267,-0.17799,0.725995),(-0.681816,-0.089763,0.725995),
    (-0.687699,0.0,0.725995),(-0.681816,0.089763,0.725995),(-0.664267,0.17799,0.725995),
    (-0.635351,0.263171,0.725995),(-0.595565,0.34385,0.725995),(-0.545589,0.418645,0.725995),
    (-0.486277,0.486277,0.725995),(-0.418645,0.545589,0.725995),(-0.34385,0.595565,0.725995),
    (-0.263171,0.635351,0.725995),(-0.17799,0.664267,0.725995),(-0.089763,0.681816,0.725995),
    (0.0,0.605174,0.796093),(0.105087,0.59598,0.796093),(0.206982,0.568678,0.796093),
    (0.302587,0.524096,0.796093),(0.388998,0.46359,0.796093),(0.46359,0.388998,0.796093),
    (0.524096,0.302587,0.796093),(0.568678,0.206982,0.796093),(0.59598,0.105087,0.796093),
    (0.605174,0.0,0.796093),(0.59598,-0.105087,0.796093),(0.568678,-0.206982,0.796093),
    (0.524096,-0.302587,0.796093),(0.46359,-0.388998,0.796093),(0.388998,-0.46359,0.796093),
    (0.302587,-0.524096,0.796093),(0.206982,-0.568678,0.796093),(0.105087,-0.59598,0.796093),
    (0.0,-0.605174,0.796093),(-0.105087,-0.59598,0.796093),(-0.206982,-0.568678,0.796093),
    (-0.302587,-0.524096,0.796093),(-0.388998,-0.46359,0.796093),(-0.46359,-0.388998,0.796093),
    (-0.524096,-0.302587,0.796093),(-0.568678,-0.206982,0.796093),(-0.59598,-0.105087,0.796093),
    (-0.605174,0.0,0.796093),(-0.59598,0.105087,0.796093),(-0.568678,0.206982,0.796093),
    (-0.524096,0.302587,0.796093),(-0.46359,0.388998,0.796093),(-0.388998,0.46359,0.796093),
    (-0.302587,0.524096,0.796093),(-0.206982,0.568678,0.796093),(-0.105087,0.59598,0.796093),
    (0.0,0.515554,0.856857),(0.089525,0.507721,0.856857),(0.17633,0.484462,0.856857),
    (0.257777,0.446483,0.856857),(0.331392,0.394937,0.856857),(0.394937,0.331392,0.856857),
    (0.446483,0.257777,0.856857),(0.484462,0.17633,0.856857),(0.507721,0.089525,0.856857),
    (0.515554,0.0,0.856857),(0.507721,-0.089525,0.856857),(0.484462,-0.17633,0.856857),
    (0.446483,-0.257777,0.856857),(0.394937,-0.331392,0.856857),(0.331392,-0.394937,0.856857),
    (0.257777,-0.446483,0.856857),(0.17633,-0.484462,0.856857),(0.089525,-0.507721,0.856857),
    (0.0,-0.515554,0.856857),(-0.089525,-0.507721,0.856857),(-0.17633,-0.484462,0.856857),
    (-0.257777,-0.446483,0.856857),(-0.331392,-0.394937,0.856857),(-0.394937,-0.331392,0.856857),
    (-0.446483,-0.257777,0.856857),(-0.484462,-0.17633,0.856857),(-0.507721,-0.089525,0.856857),
    (-0.515554,0.0,0.856857),(-0.507721,0.089525,0.856857),(-0.484462,0.17633,0.856857),
    (-0.446483,0.257777,0.856857),(-0.394937,0.331392,0.856857),(-0.331392,0.394937,0.856857),
    (-0.257777,0.446483,0.856857),(-0.17633,0.484462,0.856857),(-0.089525,0.507721,0.856857),
    (0.0,0.419889,0.907575),(0.108675,0.405582,0.907575),(0.209945,0.363635,0.907575),
    (0.296906,0.296906,0.907575),(0.363635,0.209945,0.907575),(0.405582,0.108675,0.907575),
    (0.419889,0.0,0.907575),(0.405582,-0.108675,0.907575),(0.363635,-0.209945,0.907575),
    (0.296906,-0.296906,0.907575),(0.209945,-0.363635,0.907575),(0.108675,-0.405582,0.907575),
    (0.0,-0.419889,0.907575),(-0.108675,-0.405582,0.907575),(-0.209945,-0.363635,0.907575),
    (-0.296906,-0.296906,0.907575),(-0.363635,-0.209945,0.907575),(-0.405582,-0.108675,0.907575),
    (-0.419889,0.0,0.907575),(-0.405582,0.108675,0.907575),(-0.363635,0.209945,0.907575),
    (-0.296906,0.296906,0.907575),(-0.209945,0.363635,0.907575),(-0.108675,0.405582,0.907575),
    (0.0,0.319302,0.947653),(0.082641,0.308422,0.947653),(0.159651,0.276523,0.947653),
    (0.22578,0.22578,0.947653),(0.276523,0.159651,0.947653),(0.308422,0.082641,0.947653),
    (0.319302,0.0,0.947653),(0.308422,-0.082641,0.947653),(0.276523,-0.159651,0.947653),
    (0.22578,-0.22578,0.947653),(0.159651,-0.276523,0.947653),(0.082641,-0.308422,0.947653),
    (0.0,-0.319302,0.947653),(-0.082641,-0.308422,0.947653),(-0.159651,-0.276523,0.947653),
    (-0.22578,-0.22578,0.947653),(-0.276523,-0.159651,0.947653),(-0.308422,-0.082641,0.947653),
    (-0.319302,0.0,0.947653),(-0.308422,0.082641,0.947653),(-0.276523,0.159651,0.947653),
    (-0.22578,0.22578,0.947653),(-0.159651,0.276523,0.947653),(-0.082641,0.308422,0.947653),
    (0.0,0.21497,0.976621),(0.107485,0.18617,0.976621),(0.18617,0.107485,0.976621),
    (0.21497,0.0,0.976621),(0.18617,-0.107485,0.976621),(0.107485,-0.18617,0.976621),
    (0.0,-0.21497,0.976621),(-0.107485,-0.18617,0.976621),(-0.18617,-0.107485,0.976621),
    (-0.21497,0.0,0.976621),(-0.18617,0.107485,0.976621),(-0.107485,0.18617,0.976621),
    (0.0,0.108119,0.994138),(0.05406,0.093634,0.994138),(0.093634,0.05406,0.994138),
    (0.108119,0.0,0.994138),(0.093634,-0.05406,0.994138),(0.05406,-0.093634,0.994138),
    (0.0,-0.108119,0.994138),(-0.05406,-0.093634,0.994138),(-0.093634,-0.05406,0.994138),
    (-0.108119,0.0,0.994138),(-0.093634,0.05406,0.994138),(-0.05406,0.093634,0.994138),
    (0.0,0.0,1.0)]
        
        return ReinhartPatchesNormalVectors
    
    TregenzaPatchesNormalVectors = [
    (0.0,0.994522,0.104528),(0.206773,0.972789,0.104528),(0.404508,0.908541,0.104528),
    (0.584565,0.804585,0.104528),(0.739074,0.665465,0.104528),(0.861281,0.497261,0.104528),
    (0.945847,0.307324,0.104528),(0.989074,0.103956,0.104528),(0.989074,-0.103956,0.104528),
    (0.945847,-0.307324,0.104528),(0.861281,-0.497261,0.104528),(0.739074,-0.665465,0.104528),
    (0.584565,-0.804585,0.104528),(0.404508,-0.908541,0.104528),(0.206773,-0.972789,0.104528),
    (0.0,-0.994522,0.104528),(-0.206773,-0.972789,0.104528),(-0.404508,-0.908541,0.104528),
    (-0.584565,-0.804585,0.104528),(-0.739074,-0.665465,0.104528),(-0.861281,-0.497261,0.104528),
    (-0.945847,-0.307324,0.104528),(-0.989074,-0.103956,0.104528),(-0.989074,0.103956,0.104528),
    (-0.945847,0.307324,0.104528),(-0.861281,0.497261,0.104528),(-0.739074,0.665465,0.104528),
    (-0.584565,0.804585,0.104528),(-0.404508,0.908541,0.104528),(-0.206773,0.972789,0.104528),
    (0.0,0.951057,0.309017),(0.197736,0.930274,0.309017),(0.38683,0.868833,0.309017),
    (0.559017,0.769421,0.309017),(0.706773,0.636381,0.309017),(0.823639,0.475528,0.309017),
    (0.904508,0.293893,0.309017),(0.945847,0.099412,0.309017),(0.945847,-0.099412,0.309017),
    (0.904508,-0.293893,0.309017),(0.823639,-0.475528,0.309017),(0.706773,-0.636381,0.309017),
    (0.559017,-0.769421,0.309017),(0.38683,-0.868833,0.309017),(0.197736,-0.930274,0.309017),
    (0.0,-0.951057,0.309017),(-0.197736,-0.930274,0.309017),(-0.38683,-0.868833,0.309017),
    (-0.559017,-0.769421,0.309017),(-0.706773,-0.636381,0.309017),(-0.823639,-0.475528,0.309017),
    (-0.904508,-0.293893,0.309017),(-0.945847,-0.099412,0.309017),(-0.945847,0.099412,0.309017),
    (-0.904508,0.293893,0.309017),(-0.823639,0.475528,0.309017),(-0.706773,0.636381,0.309017),
    (-0.559017,0.769421,0.309017),(-0.38683,0.868833,0.309017),(-0.197736,0.930274,0.309017),
    (0.0,0.866025,0.5),(0.224144,0.836516,0.5),(0.433013,0.75,0.5),(0.612372,0.612372,0.5),
    (0.75,0.433013,0.5),(0.836516,0.224144,0.5),(0.866025,0.0,0.5),(0.836516,-0.224144,0.5),
    (0.75,-0.433013,0.5),(0.612372,-0.612372,0.5),(0.433013,-0.75,0.5),(0.224144,-0.836516,0.5),
    (0.0,-0.866025,0.5),(-0.224144,-0.836516,0.5),(-0.433013,-0.75,0.5),(-0.612372,-0.612372,0.5),
    (-0.75,-0.433013,0.5),(-0.836516,-0.224144,0.5),(-0.866025,0.0,0.5),(-0.836516,0.224144,0.5),
    (-0.75,0.433013,0.5),(-0.612372,0.612372,0.5),(-0.433013,0.75,0.5),(-0.224144,0.836516,0.5),
    (0.0,0.743145,0.669131),(0.19234,0.717823,0.669131),(0.371572,0.643582,0.669131),(0.525483,0.525483,0.669131),
    (0.643582,0.371572,0.669131),(0.717823,0.19234,0.669131),(0.743145,0.0,0.669131),(0.717823,-0.19234,0.669131),
    (0.643582,-0.371572,0.669131),(0.525483,-0.525483,0.669131),(0.371572,-0.643582,0.669131),
    (0.19234,-0.717823,0.669131),(0.0,-0.743145,0.669131),(-0.19234,-0.717823,0.669131),
    (-0.371572,-0.643582,0.669131),(-0.525483,-0.525483,0.669131),(-0.643582,-0.371572,0.669131),
    (-0.717823,-0.19234,0.669131),(-0.743145,0.0,0.669131),(-0.717823,0.19234,0.669131),
    (-0.643582,0.371572,0.669131),(-0.525483,0.525483,0.669131),(-0.371572,0.643582,0.669131),
    (-0.19234,0.717823,0.669131),(0.0,0.587785,0.809017),(0.201034,0.552337,0.809017),
    (0.377821,0.45027,0.809017),(0.509037,0.293893,0.809017),(0.578855,0.102068,0.809017),
    (0.578855,-0.102068,0.809017),(0.509037,-0.293893,0.809017),(0.377821,-0.45027,0.809017),
    (0.201034,-0.552337,0.809017),(0.0,-0.587785,0.809017),(-0.201034,-0.552337,0.809017),
    (-0.377821,-0.45027,0.809017),(-0.509037,-0.293893,0.809017),(-0.578855,-0.102068,0.809017),
    (-0.578855,0.102068,0.809017),(-0.509037,0.293893,0.809017),(-0.377821,0.45027,0.809017),
    (-0.201034,0.552337,0.809017),(0.0,0.406737,0.913545),(0.203368,0.352244,0.913545),
    (0.352244,0.203368,0.913545),(0.406737,0.0,0.913545),(0.352244,-0.203368,0.913545),
    (0.203368,-0.352244,0.913545),(0.0,-0.406737,0.913545),(-0.203368,-0.352244,0.913545),
    (-0.352244,-0.203368,0.913545),(-0.406737,0.0,0.913545),(-0.352244,0.203368,0.913545),
    (-0.203368,0.352244,0.913545),(0.0,0.207912,0.978148),(0.180057,0.103956,0.978148),
    (0.180057,-0.103956,0.978148),(0.0,-0.207912,0.978148),(-0.180057,-0.103956,0.978148),
    (-0.180057,0.103956,0.978148),(0.0,0.0,1)]

    def celsiusToFahrenheit(self, C):
        return (C*9/5)+32
    
    def fahrenheitToCelsius(self, F):
        return (5/9)*(F-32)


class Sunpath(object):
    """
    The sun-path Class is a Python version of RADIANCE sun-path script by Greg Ward. RADIANCE source code can be accessed at:
    http://www.radiance-online.org/download-install/CVS%20source%20code
    The difference of the results with NREL version is less than 1 degree
    """
    def __init__(self):
        pass
    
    def initTheClass(self, latitude, northAngle = 0, cenPt = rc.Geometry.Point3d.Origin, scale = 100, longtitude = 0, timeZone = 0):
        self.solLat = math.radians(float(latitude));
        self.s_longtitude =  math.radians(longtitude) #2.13; # site longtitude (radians)
        self.s_meridian = math.radians(timeZone * 15) #2.13 #.0944; # standard meridian (radians)
        self. angle2North = northAngle
        self.basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.ZAxis)
        self.cenPt = cenPt
        self.scale = scale
        self.timeZone = timeZone
    
    #This part is written by Trygve Wastvedt (Trygve.Wastvedt@gmail.com).
    def solInitOutput(self, month, day, hour, solarTime = False):
        year = 2015
        self.time = hour
        
        a = 1 if (month < 3) else 0
        y = year + 4800 - a
        m = month + 12*a - 3
        self.julianDay = day + math.floor((153*m + 2)/5) + 59
        
        self.julianDay += (self.time - self.timeZone)/24.0  + 365*y + math.floor(y/4) \
            - math.floor(y/100) + math.floor(y/400) - 32045.5 - 59
        
        julianCentury = (self.julianDay - 2451545) / 36525
        #degrees
        geomMeanLongSun = (280.46646 + julianCentury * (36000.76983 + julianCentury*0.0003032)) % 360
        #degrees
        geomMeanAnomSun = 357.52911 + julianCentury*(35999.05029 - 0.0001537*julianCentury)
        eccentOrbit = 0.016708634 - julianCentury*(0.000042037 + 0.0000001267*julianCentury)
        sunEqOfCtr = math.sin(math.radians(geomMeanAnomSun))*(1.914602 - julianCentury*(0.004817+0.000014*julianCentury)) + \
            math.sin(math.radians(2*geomMeanAnomSun))*(0.019993-0.000101*julianCentury) + \
            math.sin(math.radians(3*geomMeanAnomSun))*0.000289
        #degrees
        sunTrueLong = geomMeanLongSun + sunEqOfCtr
        #AUs
        sunTrueAnom = geomMeanAnomSun + sunEqOfCtr
        #AUs
        sunRadVector = (1.000001018*(1 - eccentOrbit**2))/ \
            (1 + eccentOrbit*math.cos(math.radians(sunTrueLong)))
        #degrees
        sunAppLong = sunTrueLong - 0.00569 - 0.00478*math.sin(math.radians(125.04-1934.136*julianCentury))
        #degrees
        meanObliqEcliptic = 23 + (26 + ((21.448 - julianCentury*(46.815 + \
            julianCentury*(0.00059 - julianCentury*0.001813))))/60)/60
        #degrees
        obliqueCorr = meanObliqEcliptic + 0.00256*math.cos(math.radians(125.04 - 1934.136*julianCentury))
        #degrees
        sunRightAscen = math.degrees(math.atan2(math.cos(math.radians(obliqueCorr))* \
            math.sin(math.radians(sunAppLong)), math.cos(math.radians(sunAppLong))))
        #RADIANS
        self.solDec = math.asin(math.sin(math.radians(obliqueCorr))*math.sin(math.radians(sunAppLong)))
        
        varY = math.tan(math.radians(obliqueCorr/2))*math.tan(math.radians(obliqueCorr/2))
        #minutes
        eqOfTime = 4*math.degrees(varY*math.sin(2*math.radians(geomMeanLongSun)) \
            - 2*eccentOrbit*math.sin(math.radians(geomMeanAnomSun)) \
            + 4*eccentOrbit*varY*math.sin(math.radians(geomMeanAnomSun))*math.cos(2*math.radians(geomMeanLongSun)) \
            - 0.5*(varY**2)*math.sin(4*math.radians(geomMeanLongSun)) \
            - 1.25*(eccentOrbit**2)*math.sin(2*math.radians(geomMeanAnomSun)))
        #hours
        if solarTime == False:
            self.solTime = ((self.time*60 + eqOfTime + 4*math.degrees(self.s_longtitude) - 60*self.timeZone) % 1440)/60
        else: self.solTime = self.time
        
        #degrees
        hourAngle = (self.solTime*15 + 180) if (self.solTime*15 < 0) else (self.solTime*15 - 180)
        #RADIANS
        self.zenith = math.acos(math.sin(self.solLat)*math.sin(self.solDec) \
            + math.cos(self.solLat)*math.cos(self.solDec)*math.cos(math.radians(hourAngle)))
        self.solAlt = (math.pi/2) - self.zenith
        
        if hourAngle == 0.0 or hourAngle == -180.0 or hourAngle == 180.0:
            if self.solDec < self.solLat: self.solAz = math.pi
            else: self.solAz = 0.0
        else:
            self.solAz = ((math.acos(((math.sin(self.solLat)*math.cos(self.zenith)) \
                - math.sin(self.solDec))/(math.cos(self.solLat)*math.sin(self.zenith))) + math.pi) % (2*math.pi)) \
                if (hourAngle > 0) else \
                    ((3*math.pi - math.acos(((math.sin(self.solLat)*math.cos(self.zenith)) \
                    - math.sin(self.solDec))/(math.cos(self.solLat)*math.sin(self.zenith)))) % (2*math.pi))
    
    def sunReverseVectorCalc(self):
        basePoint = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin,rc.Geometry.Vector3f(0,1,0))
        basePoint = rc.Geometry.Point(basePoint)
        basePoint.Rotate(self.solAlt, rc.Geometry.Vector3d.XAxis, rc.Geometry.Point3d.Origin)
        basePoint.Rotate(-(self.solAz - self.angle2North), rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
        sunVector = rc.Geometry.Vector3d(basePoint.Location - rc.Geometry.Point3d.Origin)
        sunVector.Unitize()
        
        return sunVector
    
    def sunPosPt(self, sunScale = 1):
        #print 'altitude is:', math.degrees(self.solAlt), 'and azimuth is:', math.degrees(self.solAz)
        basePoint = rc.Geometry.Point3d.Add(self.cenPt,rc.Geometry.Vector3f(0,self.scale,0))
        basePoint = rc.Geometry.Point(basePoint)
        basePoint.Rotate(self.solAlt, rc.Geometry.Vector3d.XAxis, self.cenPt)
        basePoint.Rotate(-(self.solAz - self.angle2North), rc.Geometry.Vector3d.ZAxis, self.cenPt)
        sunVector = rc.Geometry.Vector3d(self.cenPt - basePoint.Location)
        sunVector.Unitize()
        
        raduis = 3 * sunScale
        sunSphere = rc.Geometry.Sphere(basePoint.Location, raduis)
        sunSphereMesh = rc.Geometry.Mesh.CreateFromSphere(sunSphere, 10, 10)
        return sunSphereMesh, sunVector, basePoint.Location

    def drawDailyPath(self, month, day):
        # find the sun position for midnight, noon - 10 min, noon + 10 min!
        hours = [0, 11.9, 12.1]
        sunP = []
        validCircle =  False
        for hour in hours:
            self.solInitOutput(month, day, hour)
            sunPos = self.sunPosPt()[2]
            sunP.append(sunPos)
            if sunPos.Z > self.cenPt.Z: validCircle = True
        if validCircle:
            # draw the circle base on these three points
            circle = rc.Geometry.Circle(*sunP)
            # intersect with the plan
            intersection = rc.Geometry.Intersect.Intersection.PlaneCircle(self.basePlane, circle)
        
            #if intersection draw the new curve for intersections and noon
            if intersection[1] != intersection[2]:
                startPt = circle.PointAt(intersection[1])
                endPt = circle.PointAt(intersection[2])
                midPt = sunP[1]
                return rc.Geometry.Arc(startPt, midPt, endPt)
            else:
                # add to check to be above the plane
                return circle
        else:
                pass

    def drawSunPath(self, solarTime = False):
        # draw daily curves for 21st of all the months
        
        monthlyCrvs = []
        for m in range(1,13):
            crv = self.drawDailyPath(m, 21)
            if crv: monthlyCrvs.append(crv)
        
        # draw hourly curves for each of hours for 1st and 21st of all month
        hourlyCrvs = []
        days = [1, 7, 14, 21]
        sunP = []; selHours = []
        if math.degrees(self.solLat)>0: month = 6
        else: month = 12
        
        # find the hours that the sun is up
        for hour in range(0,25):
            self.solInitOutput(month, 21, hour, solarTime)
            if self.sunPosPt()[2].Z > self.cenPt.Z: selHours.append(hour)
        
        sunPsolarTimeL = []
        hourlyCrvsSolarTime = []
        for hour in selHours:
            for day in days:
                sunP = []
                for month in range(1,13):
                    self.solInitOutput(month, day, hour, solarTime)
                    sunP.append(self.sunPosPt()[2])
            sunP.append(sunP[0])
            sunPsolarTime = [sunP[11], (sunP[0]+sunP[10])/2, (sunP[1]+sunP[9])/2, (sunP[2]+sunP[8])/2, (sunP[3]+sunP[7])/2, (sunP[4]+sunP[6])/2, sunP[5]]
            sunPsolarTimeL.append(sunPsolarTime)
            knotStyle = rc.Geometry.CurveKnotStyle.UniformPeriodic
            crv = rc.Geometry.Curve.CreateInterpolatedCurve(sunP, 3, knotStyle)
            intersectionEvents = rc.Geometry.Intersect.Intersection.CurvePlane(crv, self.basePlane, sc.doc.ModelAbsoluteTolerance)
            crvSolarTime = rc.Geometry.Curve.CreateInterpolatedCurve(sunPsolarTime, 3, knotStyle)
            
            try:
                if len(intersectionEvents) != 0:
                    crvDomain = crv.Domain
                    crv1 = rc.Geometry.Curve.Trim(crv, intersectionEvents[0].ParameterA, intersectionEvents[1].ParameterA)
                    crv2 = rc.Geometry.Curve.Trim(crv, intersectionEvents[1].ParameterA, intersectionEvents[0].ParameterA)
                    # calculate the bounding box to find thr center
                    
                    pt1 = ResultVisualization().calculateBB([crv1])[1]
                    pt2 = ResultVisualization().calculateBB([crv2])[1] 
                    
                    if pt1.Z > pt2.Z: crv = crv1
                    else: crv = crv2
            except: pass
            
            if crv: hourlyCrvs.append(crv)
            if crvSolarTime: hourlyCrvsSolarTime.append(crvSolarTime)
        
        return monthlyCrvs, hourlyCrvs, sunPsolarTimeL, hourlyCrvsSolarTime
        
        
    def drawBaseLines(self):
        circle1 = rc.Geometry.Circle(self.basePlane, self.scale)
        circle2 = rc.Geometry.Circle(self.basePlane, 1.03 * self.scale)
        lines= [] # will fix this part later. circles and lines will have different graphics
        lines.append(circle1.ToNurbsCurve())
        lines.append(circle2.ToNurbsCurve())
        # prepare direction lines
        movingVec = rc.Geometry.Vector3d.YAxis
        movingVec.Rotate(self.angle2North, rc.Geometry.Vector3d.ZAxis)
        shortNLineStart = rc.Geometry.Point3d.Add(self.cenPt, movingVec * 0.97 * self.scale)
        shortNLineEnd = rc.Geometry.Point3d.Add(self.cenPt, movingVec * 1.07 * self.scale)
        
        for i in range(4):
            northLine = rc.Geometry.Line(self.cenPt, movingVec, 1.1 * self.scale)
            shortNorthLine = rc.Geometry.Line(shortNLineStart, shortNLineEnd)
            xf = rc.Geometry.Transform.Rotation(PI/2 * i, rc.Geometry.Vector3d.ZAxis, self.cenPt)
            shortxf = rc.Geometry.Transform.Rotation(PI/2 * i + PI/4, rc.Geometry.Vector3d.ZAxis, self.cenPt)
            northLine.Transform(xf)
            shortNorthLine.Transform(shortxf)
            lines.append(northLine.ToNurbsCurve())
            lines.append(shortNorthLine.ToNurbsCurve())
        
        return lines


class Vector:
    
    def __init__(self, items):
        self.v = items
    
    def dot(self, u):
        if (len(self.v) == len(u.v)):
            t = 0
            for i,j in zip(self.v, u.v):
                t += i*j
            return t
        else:
            return None
    
    def __add__(self, b):
        v = []
        for i,j in zip(self.v, b.v):
            v.append(i+j)
        return Vector(v)
    
    def __sub__(self, b):
        v = []
        for i, v in zip(self.v, b.v):
            v.append(i-j)
        return Vector(v)
    
    def __mul__(self, other):
        return self.__class__(self.v).__imul__(other)
    
    def __rmul__(self, other):
        # The __rmul__ is called in scalar * vector case; it's commutative.
        return self.__class__(self.v).__imul__(other)
    
    def __imul__(self, other):
        '''Vectors can be multipled by a scalar. Two 3d vectors can cross.'''
        if isinstance(other, Vector):
            self.v = self.cross(other).v
        else:
            self.v = [i * other for i in self.v]
        return self


class Sun:
    pass


class Coeff:
    A = None
    B = None
    C = None
    D = None
    E = None


class Sky:
    def __init__(self):
        pass
    
    def createSky(self, doy, year, hour, timeZone, latitude, longitude, turbidity):
        self.doy = doy
        self.year = year
        self.hour = hour
        self.timeZone = timeZone
        self.latitude = latitude
        self.longitude = longitude
        self.turbidity = turbidity
        
        self.sun = Sun()
        
        self.setTime()
        
        self.setSunPosition()
        
        self.setZenitalAbsolutes()
        
        self.setCoefficents()
    
    def info(self):
        print(  "doy: {0}\n"
                "julian day: {9}\n"
                "year: {10}\n"
                "time: {1}\n"
                "solar time: {2}\n"
                "latitude: {3}\n"
                "longitude: {4}\n"
                "turbidity: {5}\n"
                "sun azimuth: {6}\n"
                "sun zenith: {7}\n"
                "sun declination: {8}\n" \
                .format(self.doy, self.time, self.sun.time, self.latitude, \
                self.longitude, self.turbidity, math.degrees(self.sun.azimuth), math.degrees(self.sun.zenith), \
                math.degrees(self.sun.declination), self.julianDay, self.year))
    
    def setZenitalAbsolutes(self):
        Yz = (4.0453*self.turbidity - 4.9710) \
            * math.tan((4/9 - self.turbidity /120) * (math.pi - 2*self.sun.zenith)) \
            - 0.2155*self.turbidity + 2.4192
        Y0 = (4.0453*self.turbidity - 4.9710) \
            * math.tan((4/9 - self.turbidity /120) * (math.pi)) \
            - 0.2155*self.turbidity + 2.4192
        self.Yz = Yz/Y0
     
        z3 = self.sun.zenith ** 3
        z2 = self.sun.zenith ** 2
        z = self.sun.zenith
        T_vec = Vector([self.turbidity ** 2, self.turbidity, 1])
     
        x = Vector([0.00166 * z3 - 0.00375 * z2 + 0.00209 * z,
            -0.02903 * z3 + 0.06377 * z2 - 0.03202 * z + 0.00394,
            0.11693 * z3 - 0.21196 * z2 + 0.06052 * z + 0.25886])
        self.xz = T_vec.dot(x)
        
        y = Vector([0.00275 * z3 - 0.00610 * z2 + 0.00317 * z,
            -0.04214 * z3 + 0.08970 * z2 - 0.04153 * z + 0.00516,
            0.15346 * z3 - 0.26756 * z2 + 0.06670 * z + 0.26688])
        self.yz = T_vec.dot(y)
     
    def setCoefficents(self):
        #A: darkening or brightening of the horizon
        #B: luminance gradient near the horizon
        #C: relative intensity of the circumsolar region
        #D: width of the circumsolar region
        #E: relative backscattered light
        
        #values derived by 
        self.coeffsY = Coeff()
        self.coeffsY.A = 0.1787 * self.turbidity - 1.4630
        self.coeffsY.B = -0.3554 * self.turbidity + 0.4275
        self.coeffsY.C = -0.0227 * self.turbidity + 5.3251
        self.coeffsY.D = 0.1206 * self.turbidity - 2.5771
        self.coeffsY.E = -0.0670 * self.turbidity + 0.3703
     
        self.coeffsx = Coeff()
        self.coeffsx.A = -0.0193 * self.turbidity - 0.2592
        self.coeffsx.B = -0.0665 * self.turbidity + 0.0008
        self.coeffsx.C = -0.0004 * self.turbidity + 0.2125
        self.coeffsx.D = -0.0641 * self.turbidity - 0.8989
        self.coeffsx.E = -0.0033 * self.turbidity + 0.0452
     
        self.coeffsy = Coeff()
        self.coeffsy.A = -0.0167 * self.turbidity - 0.2608
        self.coeffsy.B = -0.0950 * self.turbidity + 0.0092
        self.coeffsy.C = -0.0079 * self.turbidity + 0.2102
        self.coeffsy.D = -0.0441 * self.turbidity - 1.6537
        self.coeffsy.E = -0.0109 * self.turbidity + 0.0529
    
    def perez(self, zen, g, coeffs):
        return (1 + coeffs.A*math.exp(coeffs.B/math.cos(zen))) * \
        (1 + coeffs.C*math.exp(coeffs.D*g) + coeffs.E*(math.cos(g) ** 2))
    
    def YxyToXYZ(self, vec):
        Y = vec.v[0]
        x = vec.v[1]
        y = vec.v[2]
        
        X = x/y*Y
        Z = (1-x-y)/y*Y
        
        return Vector([X, Y, Z])
    
    def YxyToRGB(self, vec):
        [X,Y,Z] = self.YxyToXYZ(vec).v
        
        return Vector([3.2406 * X - 1.5372 * Y - 0.4986 * Z, \
            -0.9689 * X + 1.8758 * Y + 0.0415 * Z, \
            0.0557 * X - 0.2040 * Y + 1.0570 * Z])
    
    def gamma(self, zenith, azimuth):
        return math.acos(math.sin(self.sun.zenith)*math.sin(zenith)*math.cos(azimuth-self.sun.azimuth)+math.cos(self.sun.zenith)*math.cos(zenith))
    
    def sunlight(self):
        optMass = 1/(math.cos(self.sun.zenith) + 0.15*(98.885 - self.sun.zenith)**(-1.253))
        
        #constants
        a = 1.3 #wavelength exponent (sunsky: suggested by Angstrom?)
        w = 2 #(sunsky)
        l = 35 #ozone_thickness (sunsky)
        
        turbCoeff = 0.04608*self.turbidity - 0.04586 #sunsky: approximation
        
        trans_rayleigh = math.exp(-0.008735*wavelength**(-4.08*optMass))
        
        trans_aerosol = math.exp(-turbCoeff*wavelength**(-a*optMass))
        
        trans_ozone = math.exp(-k_o*l*optMass)
        
        trans_gass = math.exp(-1.41*k_g*optMass / (1 + 118.93*k_g*optMass)**0.45)
        
        trans_vapor = math.exp(-0.2385*k_wa*w*optMass / (1 + 20.07*k_wa*w*optMass)**0.45)
    
    def setTime(self):
        self.time = self.hour
        
        self.julianDay = self.doy
        y = self.year + 4800
        
        self.julianDay += (self.time - self.timeZone)/24.0  + 365*y + math.floor(y/4) \
            - math.floor(y/100) + math.floor(y/400) - 32045.5 - 59
    
    def setSunPosition(self):
        julianCentury = (self.julianDay - 2451545) / 36525
        #degrees
        geomMeanLongSun = (280.46646 + julianCentury * (36000.76983 + julianCentury*0.0003032)) % 360
        #degrees
        geomMeanAnomSun = 357.52911 + julianCentury*(35999.05029 - 0.0001537*julianCentury)
        eccentOrbit = 0.016708634 - julianCentury*(0.000042037 + 0.0000001267*julianCentury)
        sunEqOfCtr = math.sin(math.radians(geomMeanAnomSun))*(1.914602 - julianCentury*(0.004817+0.000014*julianCentury)) + \
            math.sin(math.radians(2*geomMeanAnomSun))*(0.019993-0.000101*julianCentury) + \
            math.sin(math.radians(3*geomMeanAnomSun))*0.000289
        #degrees
        sunTrueLong = geomMeanLongSun + sunEqOfCtr
        #AUs
        sunTrueAnom = geomMeanAnomSun + sunEqOfCtr
        #AUs
        sunRadVector = (1.000001018*(1 - eccentOrbit**2))/ \
            (1 + eccentOrbit*math.cos(math.radians(sunTrueLong)))
        #degrees
        sunAppLong = sunTrueLong - 0.00569 - 0.00478*math.sin(math.radians(125.04-1934.136*julianCentury))
        #degrees
        meanObliqEcliptic = 23 + (26 + ((21.448 - julianCentury*(46.815 + \
            julianCentury*(0.00059 - julianCentury*0.001813))))/60)/60
        #degrees
        obliqueCorr = meanObliqEcliptic + 0.00256*math.cos(math.radians(125.04 - 1934.136*julianCentury))
        #degrees
        sunRightAscen = math.degrees(math.atan2(math.cos(math.radians(obliqueCorr))* \
            math.sin(math.radians(sunAppLong)), math.cos(math.radians(sunAppLong))))
        #RADIANS
        self.sun.declination = math.asin(math.sin(math.radians(obliqueCorr))*math.sin(math.radians(sunAppLong)))
        
        varY = math.tan(math.radians(obliqueCorr/2))*math.tan(math.radians(obliqueCorr/2))
        #minutes
        eqOfTime = 4*math.degrees(varY*math.sin(2*math.radians(geomMeanLongSun)) \
            - 2*eccentOrbit*math.sin(math.radians(geomMeanAnomSun)) \
            + 4*eccentOrbit*varY*math.sin(math.radians(geomMeanAnomSun))*math.cos(2*math.radians(geomMeanLongSun)) \
            - 0.5*(varY**2)*math.sin(4*math.radians(geomMeanLongSun)) \
            - 1.25*(eccentOrbit**2)*math.sin(2*math.radians(geomMeanAnomSun)))
        #hours
        self.sun.time = ((self.time*60 + eqOfTime + 4*self.longitude - 60*self.timeZone) % 1440)/60
        #degrees
        hourAngle = (self.sun.time*15 + 180) if (self.sun.time*15 < 0) else (self.sun.time*15 - 180)
        #RADIANS
        self.sun.zenith = math.acos(math.sin(math.radians(self.latitude))*math.sin(self.sun.declination) \
            + math.cos(math.radians(self.latitude))*math.cos(self.sun.declination)*math.cos(math.radians(hourAngle)))
        #degrees
        atmosphRefrac = 0 if (self.sun.zenith < 0.087) else \
            (58.1/math.tan(math.pi/2 - self.sun.zenith) \
            - 0.07/(math.tan(math.pi/2 - self.sun.zenith))**3 \
            + 0.000086/(math.tan(math.pi/2 - self.sun.zenith))**5)/3600 \
            if (self.sun.zenith < 1.484) else \
                (1735 + (90-math.degrees(self.sun.zenith)) \
                *(-518.2 + (90-math.degrees(self.sun.zenith)) \
                *(103.4+(90-math.degrees(self.sun.zenith)) \
                *(-12.79+(90-math.degrees(self.sun.zenith))*0.711))))/3600 \
                if (self.sun.zenith < -1.581) else \
                    (-20.772/math.tan(math.pi/2 - self.sun.zenith))/3600
        #RADIANS
        self.sun.zenithCorr = self.sun.zenith - math.radians(atmosphRefrac)
        #RADIANS cw from N
        self.sun.azimuth = ((math.acos(((math.sin(math.radians(self.latitude))*math.cos(self.sun.zenith)) \
            - math.sin(self.sun.declination))/(math.cos(math.radians(self.latitude))*math.sin(self.sun.zenith))) + math.pi) % (2*math.pi)) \
            if (hourAngle > 0) else \
                ((3*math.pi - math.acos(((math.sin(math.radians(self.latitude))*math.cos(self.sun.zenith)) \
                - math.sin(self.sun.declination))/(math.cos(math.radians(self.latitude))*math.sin(self.sun.zenith)))) % (2*math.pi))
    
    def calcSkyColor(self, azimuth, zenith):
        gamma = self.gamma(zenith, azimuth)
        zenith = min(zenith, math.pi)
        Yp = self.Yz * self.perez(zenith, gamma, self.coeffsY) / self.perez(0, self.sun.zenith, self.coeffsY)
        xp = self.xz * self.perez(zenith, gamma, self.coeffsx) / self.perez(0, self.sun.zenith, self.coeffsx)
        yp = self.yz * self.perez(zenith, gamma, self.coeffsy) / self.perez(0, self.sun.zenith, self.coeffsy)
        
        return Vector([Yp, xp, yp])
    
    def calcLightColor(self):
        nightColor = Vector([0.2, 0.2, 0.5])
        
        if (self.sun.zenith > math.pi/2):
            return self.YxyToRGB(nightColor)
        
        Ys = self.Yz * self.perez(self.sun.zenith, 0, self.coeffsY) / self.perez(0, self.sun.zenith, self.coeffsY)
        xs = self.xz * self.perez(self.sun.zenith, 0, self.coeffsx) / self.perez(0, self.sun.zenith, self.coeffsx)
        ys = self.yz * self.perez(self.sun.zenith, 0, self.coeffsy) / self.perez(0, self.sun.zenith, self.coeffsy)
        dayColor = self.YxyToRGB(Vector([Ys, xs, ys]))
        
        interpolation = max(0, min(1, (self.sun.zenith - math.pi/2 + 0.2) / 0.2))
        return interpolation * nightColor + (1 - interpolation) * dayColor
    
    def calcFullSky(self, res):
        import ghpythonlib.components as ghcomp
        self.fullSky = []
        self.fullSkyXYZ = []
        for j in range(4*res):
            az = j/(4*res) * 2*math.pi
            for i in range(res+1):
                zen = (res-i)/res * math.pi/2
                color = self.YxyToXYZ(self.calcSkyColor(az, zen))
                self.fullSkyXYZ.append(str(color.v[0]) + ", " + str(color.v[1]) + ", " + str(color.v[2]))
                self.fullSky.append(ghcomp.ColourXYZ(1, *color.v))
        
        return self.fullSky, self.fullSkyXYZ
    
    def calcSkyAvg(self, res):
        self.colorAvg = Vector([0, 0, 0])
        fac = 1/(4 * res**2)
        for j in range(4*res):
            az = j/(4*res) * 2*math.pi
            for i in range(res):
                zen = (res-i)/res * math.pi/2
                self.colorAvg = self.colorAvg + (self.calcSkyColor(az, zen) * fac)
        
        return self.colorAvg


class MeshPreparation(object):
    
    def joinMesh(self, meshList):
        joinedMesh = rc.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh
    
    def parallel_makeSurfaceMesh(self, brep, gridSize):
        ## mesh breps
        def makeMeshFromSrf(i, inputBrep):
            try:
                mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)
                inputBrep.Dispose()
            except:
                print 'Error in converting Brep to Mesh...'
                pass

        # prepare bulk list for each surface
        mesh = [None] * len(brep)

        # set-up mesh parameters for each surface based on surface size
        aspectRatio = 1
        meshParam = rc.Geometry.MeshingParameters.Default
        rc.Geometry.MeshingParameters.MaximumEdgeLength.__set__(meshParam, (gridSize))
        rc.Geometry.MeshingParameters.MinimumEdgeLength.__set__(meshParam, (gridSize))
        rc.Geometry.MeshingParameters.GridAspectRatio.__set__(meshParam, aspectRatio)
    
        ## Call the mesh function
        if 1 < 0: #parallel: # for some reason parallel meshing gives error
            tasks.Parallel.ForEach(xrange(len(brep)),makeMeshFromSrf)
        else:
            for i in range(len(mesh)):
                makeMeshFromSrf(i, brep[i])

        meshGeometries = mesh
        
        return meshGeometries
    
    def parallel_makeContextMesh(self, brep):
        ## mesh breps
        def makeMeshFromSrf(i, inputBrep):
            try:
                mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)
                inputBrep.Dispose()
            except:
                print 'Error in converting Brep to Mesh...'
                pass
                
        # prepare bulk list for each surface
        mesh = [None] * len(brep)

        # set-up mesh parameters for each surface based on surface size
        meshParam = rc.Geometry.MeshingParameters.Default #Coarse
        rc.Geometry.MeshingParameters.GridMaxCount.__set__(meshParam, 1)
        rc.Geometry.MeshingParameters.SimplePlanes.__set__(meshParam, True)
        rc.Geometry.MeshingParameters.GridAmplification.__set__(meshParam, 1.5)
    
        ## Call the mesh function
        if 1 < 0: #parallel: # for some reason parallel meshing gives error
            tasks.Parallel.ForEach(xrange(len(brep)),makeMeshFromSrf)
        else:
            for i in range(len(mesh)):
                makeMeshFromSrf(i, brep[i])

        meshGeometries = mesh
        return meshGeometries

    def parallel_testPointCalculator(self, analysisSrfs, disFromBase, parallel = True):
        # Mesh functions should be modified and be written interrelated as a class
        movingDis = disFromBase
    
        # preparing bulk lists
        testPoint = [[]] * len(analysisSrfs)
        srfNormals = [[]] * len(analysisSrfs)
        meshSrfCen = [[]] * len(analysisSrfs)
        meshSrfArea = [[]] * len(analysisSrfs)
        
        srfCount = 0
        for srf in analysisSrfs:
            testPoint[srfCount] = range(srf.Faces.Count)
            srfNormals[srfCount] = range(srf.Faces.Count)
            meshSrfCen[srfCount] = range(srf.Faces.Count)
            meshSrfArea[srfCount] = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                analysisSrfs[i].FaceNormals.ComputeFaceNormals()
                analysisSrfs[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(analysisSrfs[i].Faces.Count):
                    srfNormals[i][face] = (analysisSrfs[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = analysisSrfs[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                    tempMesh = rc.Geometry.Mesh()
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].A]) #0
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].B]) #1
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].C]) #2
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].D]) #3
                    tempMesh.Faces.AddFace(0, 1, 3, 2)
                    massData = rc.Geometry.AreaMassProperties.Compute(tempMesh)
                    meshSrfArea[i][face] = massData.Area
                    massData.Dispose()
                    tempMesh.Dispose()
                    
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(analysisSrfs)),srfPtCalculator)
        else:
            for i in range(len(analysisSrfs)):
                srfPtCalculator(i)
    
        return testPoint, srfNormals, meshSrfArea
    
    def meshFromPoints(self, u, v, pts, meshColors=None):
        # creates a mesh from grid of points
        mesh = rc.Geometry.Mesh()
        if (meshColors == None) or (len(meshColors) == 0):
            for i,pt in enumerate(pts):
                mesh.Vertices.Add(pt)
        else:
            for i,pt in enumerate(pts):
                mesh.Vertices.Add(pt)
                mesh.VertexColors.Add(meshColors[i])
        for i in range(1,u):
            for k in range(1,v):
                mesh.Faces.AddFace(k-1+(i-1)*v, k-1+i*v, k-1+i*v+1, k-1+(i-1)*v+1)
        
        return mesh


class RunAnalysisInsideGH(object):
    #
    def calRadRoseRes(self, tiltedRoseVectors, TregenzaPatchesNormalVectors, genCumSkyResult, testPoint = rc.Geometry.Point3d.Origin, bldgMesh = [], groundRef = 0):
        radResult = []; sunUpHours = 1
        for vec in tiltedRoseVectors:
            radiation = 0; groundRadiation = 0; patchNum = 0;
            for patchVec in TregenzaPatchesNormalVectors:
                vecAngle = rs.VectorAngle(patchVec, vec)
                
                if  vecAngle < 90:
                    check = 1
                    
                    if bldgMesh!=[]:
                        #calculate intersection
                        ray = rc.Geometry.Ray3d(testPoint, rc.Geometry.Vector3d(*patchVec)) # generate the ray
                        if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0;
                    
                    if check == 1:
                        radiation = radiation + genCumSkyResult[patchNum] * math.cos(math.radians(vecAngle))
                        groundRadiation = groundRadiation + genCumSkyResult[patchNum] * math.cos(math.radians(vecAngle)) * (groundRef/100) * 0.5
                        #radchk.append((vecAngle))
                patchNum += 1
            # print radiation, groundRadiation 
            radResult.append((groundRadiation + radiation)/sunUpHours)
        return radResult
    
    def parallel_radCalculator(self, testPts, testVec, meshSrfArea, bldgMesh,
                                contextMesh, parallel, cumSkyResult, TregenzaPatches,
                                conversionFac, contextHeight = 2200000000000000,
                                northVector = rc.Geometry.Vector3d.YAxis):
        # preparing bulk lists
        # create an empty dictionary for each point
        intersectionMtx = {}
        for pp in range(len(testPts)): intersectionMtx[pp] = {}
            
        radiation = [0] * len(testPts)
        groundRadiation = [0] * len(testPts)
        radResult = [0] * len(testPts)
        groundRef = 30
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        # Converting vectors to Rhino 3D Vectors
        sunUpHours = cumSkyResult [-1]
        TregenzaVectors = []
        for vector in TregenzaPatches: TregenzaVectors.append(rc.Geometry.Vector3d(*vector))
        
        angle = rc.Geometry.Vector3d.VectorAngle(northVector, YAxis)
        if northVector.X > 0 : angle = -angle
        
        if angle != 0: [vec.Rotate(angle, ZAxis) for vec in TregenzaVectors]
        PI = math.pi
        
        try:
            def srfRadCalculator(i):
                patchNum = 0
                for patchVec in TregenzaVectors:
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(patchVec, testVec[i]) # calculate the angle between the surface and sky patch
                    
                    intersectionMtx[i][patchNum] = {'isIntersect' : 0,
                                                    'vecAngle' : vecAngle}
                    
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break!! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], patchVec) # generate the ray
                        
                        if bldgMesh!=None:
                            #for bldg in bldgMesh: # bldgMesh is all joined as one mesh
                            if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0;
                        
                        if check != 0 and contextMesh!=None: #and testPts[i].Z < contextHeight:
                            #for bldg in contextMesh:
                            if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh,ray) >= 0.0: check = 0;
                        
                        if check != 0:
                            radiation[i] = radiation[i] + (cumSkyResult[patchNum] * math.cos(vecAngle))
                            intersectionMtx[i][patchNum] =  {'isIntersect' : 1, 'vecAngle' : vecAngle}
                            # print groundRadiation
                            groundRadiation[i] = 0 #groundRadiation[i] + cumSkyResult[patchNum] * math.cos(vecAngle) * (groundRef/100) * 0.5
                    patchNum += 1
                
                radResult[i] = (groundRadiation[i] + radiation[i]) #/sunUpHours
        
        except:
            #print 'Error in Radiation calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)),srfRadCalculator)
            else:
                for i in range(len(testPts)):
                    srfRadCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'Radiation study time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total radiation
        totalRadiation = 0;
        for r in range(len(testPts)):
            totalRadiation = totalRadiation + (radResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        return radResult, totalRadiation, intersectionMtx
    
    
    def parallel_sunlightHoursCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, sunVectors, conversionFac, northVector, timeStep = 1):
        # preparing bulk lists
        sunlightHours = [0] * len(testPts)
        sunlightHoursResult = [0] * len(testPts)
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        PI = math.pi
        
        
        # Converting vectors to Rhino 3D Vectors
        sunV = [];
        sunVectorCount = 0;
        for vector in sunVectors:
            if vector[2] < 0: print "Sun vector " + `sunVectorCount + 1` + " removed since it represents a vector with negative Z!" 
            else: sunV.append(rc.Geometry.Vector3d(vector))
            sunVectorCount =+ 1
            
        angle = rc.Geometry.Vector3d.VectorAngle(northVector, YAxis)
        if northVector.X > 0 : angle = -angle
        # print math.degrees(angle)
        if angle != 0: [vec.Rotate(angle, ZAxis) for vec in sunV]
        
        sunVisibility = []
        for pt in testPts: sunVisibility.append(range(len(sunV)))
        
        try:
            def sunlightHoursCalculator(i):
                for vectorCount, vector in enumerate(sunV):
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    check = 0
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], vector) # generate the ray
                        
                        if bldgMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0
                        if check != 0 and contextMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh,ray) >= 0.0: check = 0
                        
                        if check != 0:
                            sunlightHours[i] += 1/timeStep
                        
                    sunVisibility[i][vectorCount] = check
                
                sunlightHoursResult[i] = sunlightHours[i] # This is stupid but I'm tired to change it now...
        except:
            #print 'Error in Sunligh Hours calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            # calling the function
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)), sunlightHoursCalculator)
            else:
                for i in range(len(testPts)):
                    sunlightHoursCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'Sunlight hours calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total sunlight hours
        totalSLH = 0;
        for r in range(len(testPts)):
            totalSLH = totalSLH + (sunlightHoursResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        
        return sunlightHoursResult, totalSLH, sunVisibility
    
    
    def parallel_viewCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, viewPoints, viewPtsWeights, conversionFac):
        
        # preparing bulk lists
        view = [0] * len(testPts)
        viewResult = [0] * len(testPts)
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        PI = math.pi
        
        targetViewsCount  = len(viewPoints)
        ptImportance = []
        for ptCount in range(targetViewsCount):
            try:
                
                if viewPtsWeights[ptCount] == 0:
                    ptImportance.append(100/targetViewsCount)
                else:
                    ptImportance.append(viewPtsWeights[ptCount]*100)
            except:
                ptImportance.append(100/targetViewsCount)
        
        
        viewVector = []
        
        ptVisibility = []
        for pt in testPts: ptVisibility.append(range(len(viewPoints)))
        
        try:
            def viewCalculator(i):
                for ptCount, viewPt in enumerate(viewPoints):
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vector = rc.Geometry.Vector3d(viewPt - testPts[i])
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    check = 0
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        line = rc.Geometry.Line(testPts[i], viewPt)
                        
                        if bldgMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshLine(bldgMesh, line)[1] != None: check = 0
                        if check != 0 and contextMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshLine(contextMesh, line)[1] != None: check = 0
                        
                        if check != 0:
                            view[i] += ptImportance[ptCount]
                        
                    ptVisibility[i][ptCount] = check
                viewResult[i] = view[i] # This is stupid but I'm tired to change it now...
                
                if viewResult[i] > 100: viewResult[i] = 100
        except Exception, e:
            # print `e`
            # print 'Error in View calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            # calling the function
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)), viewCalculator)
            else:
                for i in range(len(testPts)):
                    viewCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'View calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # average view
        averageView = sum(viewResult)/len(viewResult)
            
        return viewResult, averageView, ptVisibility
        

class ExportAnalysis2Radiance(object):
    pass
        

class ResultVisualization(object):
    # This wasn't agood idea since multiple studies have different Bounding boxes
    def __init__(self):
        self.BoundingBoxPar = None
        self.monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.gradientLibrary = {
        0: [System.Drawing.Color.FromArgb(75, 107, 169), System.Drawing.Color.FromArgb(115, 147, 202), System.Drawing.Color.FromArgb(170, 200, 247), System.Drawing.Color.FromArgb(193, 213, 208), System.Drawing.Color.FromArgb(245, 239, 103), System.Drawing.Color.FromArgb(252, 230, 74), System.Drawing.Color.FromArgb(239, 156, 21), System.Drawing.Color.FromArgb(234, 123, 0), System.Drawing.Color.FromArgb(234, 74, 0), System.Drawing.Color.FromArgb(234, 38, 0)],
        1: [System.Drawing.Color.FromArgb(49,54,149), System.Drawing.Color.FromArgb(69,117,180), System.Drawing.Color.FromArgb(116,173,209), System.Drawing.Color.FromArgb(171,217,233), System.Drawing.Color.FromArgb(224,243,248), System.Drawing.Color.FromArgb(255,255,191), System.Drawing.Color.FromArgb(254,224,144), System.Drawing.Color.FromArgb(253,174,97), System.Drawing.Color.FromArgb(244,109,67), System.Drawing.Color.FromArgb(215,48,39), System.Drawing.Color.FromArgb(165,0,38)],
        2: [System.Drawing.Color.FromArgb(4,25,145), System.Drawing.Color.FromArgb(7,48,224), System.Drawing.Color.FromArgb(7,88,255), System.Drawing.Color.FromArgb(1,232,255), System.Drawing.Color.FromArgb(97,246,156), System.Drawing.Color.FromArgb(166,249,86), System.Drawing.Color.FromArgb(254,244,1), System.Drawing.Color.FromArgb(255,121,0), System.Drawing.Color.FromArgb(239,39,0), System.Drawing.Color.FromArgb(138,17,0)],
        3: [System.Drawing.Color.FromArgb(255,20,147), System.Drawing.Color.FromArgb(240,47,145), System.Drawing.Color.FromArgb(203,117,139), System.Drawing.Color.FromArgb(160,196,133), System.Drawing.Color.FromArgb(132,248,129), System.Drawing.Color.FromArgb(124,253,132), System.Drawing.Color.FromArgb(96,239,160), System.Drawing.Color.FromArgb(53,217,203), System.Drawing.Color.FromArgb(15,198,240), System.Drawing.Color.FromArgb(0,191,255)],
        4: [System.Drawing.Color.FromArgb(0,13,255), System.Drawing.Color.FromArgb(0,41,234), System.Drawing.Color.FromArgb(0,113,181), System.Drawing.Color.FromArgb(0,194,122), System.Drawing.Color.FromArgb(0,248,82), System.Drawing.Color.FromArgb(8,247,75), System.Drawing.Color.FromArgb(64,191,58), System.Drawing.Color.FromArgb(150,105,32), System.Drawing.Color.FromArgb(225,30,9), System.Drawing.Color.FromArgb(255,0,0)],
        5: [System.Drawing.Color.FromArgb(55,55,55), System.Drawing.Color.FromArgb(235,235,235)],
        6: [System.Drawing.Color.FromArgb(0,0,255), System.Drawing.Color.FromArgb(53,0,202), System.Drawing.Color.FromArgb(107,0,148), System.Drawing.Color.FromArgb(160,0,95), System.Drawing.Color.FromArgb(214,0,41), System.Drawing.Color.FromArgb(255,12,0), System.Drawing.Color.FromArgb(255,66,0), System.Drawing.Color.FromArgb(255,119,0), System.Drawing.Color.FromArgb(255,173,0), System.Drawing.Color.FromArgb(255,226,0), System.Drawing.Color.FromArgb(255,255,0)],
        7: [System.Drawing.Color.FromArgb(0,0,0), System.Drawing.Color.FromArgb(110,0,153), System.Drawing.Color.FromArgb(255,0,0), System.Drawing.Color.FromArgb(255,255,102), System.Drawing.Color.FromArgb(255,255,255)],
        8: [System.Drawing.Color.FromArgb(0,136,255), System.Drawing.Color.FromArgb(200,225,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,230,230), System.Drawing.Color.FromArgb(255,0,0)],
        9: [System.Drawing.Color.FromArgb(0,136,255), System.Drawing.Color.FromArgb(67,176,255), System.Drawing.Color.FromArgb(134,215,255), System.Drawing.Color.FromArgb(174,228,255), System.Drawing.Color.FromArgb(215,242,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,243,243), System.Drawing.Color.FromArgb(255,0,0)],
        10: [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,0,0)],
        11: [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(0,136,255)],
        12: [System.Drawing.Color.FromArgb(5,48,97), System.Drawing.Color.FromArgb(33,102,172), System.Drawing.Color.FromArgb(67,147,195), System.Drawing.Color.FromArgb(146,197,222), System.Drawing.Color.FromArgb(209,229,240), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(253,219,199), System.Drawing.Color.FromArgb(244,165,130), System.Drawing.Color.FromArgb(214,96,77), System.Drawing.Color.FromArgb(178,24,43), System.Drawing.Color.FromArgb(103,0,31)],
        13: [System.Drawing.Color.FromArgb(5,48,97), System.Drawing.Color.FromArgb(33,102,172), System.Drawing.Color.FromArgb(67,147,195), System.Drawing.Color.FromArgb(146,197,222), System.Drawing.Color.FromArgb(209,229,240), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(244,165,130), System.Drawing.Color.FromArgb(178,24,43)],
        14: [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(253,219,199), System.Drawing.Color.FromArgb(244,165,130), System.Drawing.Color.FromArgb(214,96,77), System.Drawing.Color.FromArgb(178,24,43), System.Drawing.Color.FromArgb(103,0,31)],
        15: [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(209,229,240), System.Drawing.Color.FromArgb(146,197,222), System.Drawing.Color.FromArgb(67,147,195), System.Drawing.Color.FromArgb(33,102,172), System.Drawing.Color.FromArgb(5,48,97)],
        16: [System.Drawing.Color.FromArgb(0,0,0), System.Drawing.Color.FromArgb(255,255,255)],
        17: [System.Drawing.Color.FromArgb(0,16,120), System.Drawing.Color.FromArgb(38,70,160), System.Drawing.Color.FromArgb(5,180,222), System.Drawing.Color.FromArgb(16,180,109), System.Drawing.Color.FromArgb(59,183,35), System.Drawing.Color.FromArgb(143,209,19), System.Drawing.Color.FromArgb(228,215,29), System.Drawing.Color.FromArgb(246,147,17), System.Drawing.Color.FromArgb(243,74,0), System.Drawing.Color.FromArgb(255,0,0)],
        18: [System.Drawing.Color.FromArgb(69,92,166), System.Drawing.Color.FromArgb(66,128,167), System.Drawing.Color.FromArgb(62,176,168), System.Drawing.Color.FromArgb(78,181,137), System.Drawing.Color.FromArgb(120,188,59), System.Drawing.Color.FromArgb(139,184,46), System.Drawing.Color.FromArgb(197,157,54), System.Drawing.Color.FromArgb(220,144,57), System.Drawing.Color.FromArgb(228,100,59), System.Drawing.Color.FromArgb(233,68,60)],
        19: [System.Drawing.Color.FromArgb(153,153,153), System.Drawing.Color.FromArgb(100,149,237), System.Drawing.Color.FromArgb(104,152,231), System.Drawing.Color.FromArgb(115,159,214), System.Drawing.Color.FromArgb(132,171,188), System.Drawing.Color.FromArgb(154,186,155), System.Drawing.Color.FromArgb(178,202,119), System.Drawing.Color.FromArgb(201,218,82), System.Drawing.Color.FromArgb(223,233,49), System.Drawing.Color.FromArgb(240,245,23), System.Drawing.Color.FromArgb(251,252,6), System.Drawing.Color.FromArgb(255,255,0)]
        }
    
    def readRunPeriod(self, runningPeriod, p = True, full = True):
        if not runningPeriod or runningPeriod[0]==None:
            runningPeriod = ((1, 1, 1),(12, 31, 24))
            
        stMonth = runningPeriod [0][0]; stDay = runningPeriod [0][1]; stHour = runningPeriod [0][2];
        endMonth = runningPeriod [1][0]; endDay = runningPeriod [1][1]; endHour = runningPeriod [1][2];
        
        if p:
            startDay = self.hour2Date(self.date2Hour(stMonth, stDay, stHour))
            startHour = startDay.split(' ')[-1]
            startDate = startDay.Replace(startHour, "")[:-1]
            
            endingDay = self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            endingHour = endingDay.split(' ')[-1]
            endingDate = endingDay.Replace(endingHour, "")[:-1]
            
            if full:
                print 'Analysis period is from', startDate, 'to', endingDate
                print 'Between hours ' + startHour + ' and ' + endingHour
            
            else: print startDay, ' - ', endingDay
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    
    def colorMesh(self, colors, meshList, unweld = True):
        
        joinedMesh = rc.Geometry.Mesh()
        try:
            for face in range(meshList[0].Faces.Count):
                joinedMesh.Append(meshList[0].Faces[face]) #join the mesh
        except:
            try:
                for face in meshList: joinedMesh.Append(face)
            except:
                joinedMesh.Append(meshList)
        
        if unweld: joinedMesh.Unweld(0, False)
        
        
        if joinedMesh.Faces.Count == 0:
            print "Invalid Mesh!"
            return -1
            
        try:
            assert joinedMesh.Faces.Count == len(colors)
        except:
            print 'number of mesh:' + `joinedMesh.Faces.Count` + ' != number of values:' + `len(colors)`
            return -1
            
        # make a monotonemesh
        joinedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
        #color the mesh based on the results
        for srfCount in range (joinedMesh.Faces.Count):
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].A] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].B] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].C] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].D] = colors[srfCount]
        return joinedMesh
    
    def gradientColor(self, values, lowB, highB, colors):
        if highB == 'max': highB = max(values)
        if lowB == 'min': lowB = min(values)
        
        # this function inputs values, and custom colors and outputs gradient colors
        def parNum(num, lowB, highB):
            """This function normalizes all the values"""
            if num > highB: numP = 1
            elif num < lowB: numP = 0
            elif highB == lowB: numP = 0
            else: numP = (num - lowB)/(highB - lowB)
            return numP

        def calColor(valueP, rangeMinP, rangeMaxP, minColor, maxColor):
            # range is between 0 and 1
            rangeP = rangeMaxP - rangeMinP
            red = round(((valueP - rangeMinP)/rangeP) * (maxColor.R - minColor.R) + minColor.R)
            blue = round(((valueP - rangeMinP)/rangeP) * (maxColor.B - minColor.B) + minColor.B)
            green = round(((valueP - rangeMinP)/rangeP) * (maxColor.G - minColor.G) + minColor.G) 
            color = System.Drawing.Color.FromArgb(red, green, blue)
            return color
        
        numofColors = len(colors)
        colorBounds = rs.frange(0, 1, round(1/(numofColors-1),6))
        if len(colorBounds) != numofColors: colorBounds.append(1)
        colorBounds = [round(x,3) for x in colorBounds]
        
        numP = []
        for num in values: numP.append(parNum(num, lowB, highB))
            
        colorTemp = []
        for num in numP:
            for i in range(numofColors):
                if  colorBounds[i] <= num <= colorBounds[i + 1]:
                    colorTemp.append(calColor(num, colorBounds[i], colorBounds[i+1], colors[i], colors[i+1]))
                    break
        color = colorTemp
        return color
    
    def calculateBB(self, geometries, restricted = False):
        bbox = None
        plane = rc.Geometry.Plane.WorldXY
        if geometries:
            flattenGeo = []
            for geometry in geometries:
                #print geometry
                if isinstance(geometry, list):
                    # geometry = list(chain.from_iterable(geometry)) # it gives me errors for
                    [flattenGeo.append(g) for g in geometry]
                    #geometry = flatten
                else:
                    flattenGeo.append(geometry)
                #print flattenGeo
                for geo in flattenGeo:
                    if(bbox==None ): bbox = geo.GetBoundingBox(restricted)
                    else: bbox = rc.Geometry.BoundingBox.Union( bbox, geo.GetBoundingBox(restricted))
                
        minZPt = bbox.Corner(False, True, True)
        maxZPt = bbox.Corner(False, True, False)
        titleBasePt = bbox.Corner(True, True, True)
        BBXlength = titleBasePt.DistanceTo(minZPt)
        BBYlength = titleBasePt.DistanceTo(bbox.Corner(True, False, True))
        BBZlength = titleBasePt.DistanceTo(bbox.Corner(True, True, False))
        CENTERPoint = (bbox.Corner(False, True, True) + bbox.Corner( True, False, False))/2
        
        # this is just here because I'm using it in number of components and I don't want to go and fix them right now.
        # else it doesn't make sense to store the parameters in this Class
        self.BoundingBoxPar = minZPt, BBXlength, BBYlength, BBZlength, CENTERPoint, titleBasePt, maxZPt
        
        return minZPt, CENTERPoint, maxZPt
    
    def createLegend(self, results, lowB, highB, numOfSeg, legendTitle, BoundingBoxP, legendBasePoint, legendScale = 1, font = None, textSize = None, fontBold = False):
        if numOfSeg: numOfSeg = int(numOfSeg)
        if highB == 'max': highB = max(results)
        if lowB == 'min': lowB = min(results)
        if legendBasePoint == None: basePt = BoundingBoxP[0]
        else: basePt = legendBasePoint
            
        BBYlength = BoundingBoxP[2]
        
        def legend(basePt, legendHeight, legendWidth, numofSeg):
            basePt = rc.Geometry.Point3d.Add(basePt, rc.Geometry.Vector3f(legendWidth, 0, 0))
            numPt = int(4 + 2 * (numOfSeg - 1))
            # make the point list
            ptList = []
            for pt in range(numPt):
                point = rc.Geometry.Point3d(basePt[0] + (pt%2) * legendWidth, basePt[1] + int(pt/2) * legendHeight, basePt[2])
                ptList.append(point)
    
            meshVertices = ptList; textPt = []
            legendSrf = rc.Geometry.Mesh()
            for segNum in  range(numOfSeg):
                # generate the surface
                mesh = rc.Geometry.Mesh()
                mesh.Vertices.Add(meshVertices[segNum * 2]) #0
                mesh.Vertices.Add(meshVertices[segNum * 2 + 1]) #1
                mesh.Vertices.Add(meshVertices[segNum * 2 + 2]) #2
                mesh.Vertices.Add(meshVertices[segNum * 2 + 3]) #3
                mesh.Faces.AddFace(0, 1, 3, 2)
                legendSrf.Append(mesh)
                
                pt = rc.Geometry.Point3d(meshVertices[segNum * 2 + 1].X + textSize*0.5, meshVertices[segNum * 2 + 1].Y, meshVertices[segNum * 2 + 1].Z)
                textPt.append(pt)
            pt = rc.Geometry.Point3d(meshVertices[-1].X + textSize*0.5, meshVertices[-1].Y, meshVertices[-1].Z)
            textPt.append(pt) # one more point for legend title
            
            return legendSrf, textPt
        
        # check for user input
        if font == None:
            font = 'Verdana'
        legendHeight = legendWidth = (BBYlength/10) * legendScale
        if  textSize == None:
            textSize = (legendHeight/3) * legendScale
        
        # numbers
        # rs.frange(0, 1, round(1/(numofColors-1),6))
        try:
            numbers = rs.frange(lowB, highB, round((highB - lowB) / (numOfSeg -1), 6))
        except:
            if highB - lowB < 10**(-12):
                numbers = [lowB]; numOfSeg = 1
            else:
                numbers = [lowB, lowB + ((highB-lowB)/4), lowB + ((highB-lowB)/2), lowB + (3*(highB-lowB)/4), highB]; numOfSeg = 5
        ###
        if len(numbers) < numOfSeg: numbers.append(highB)
        elif len(numbers) > numOfSeg: numbers = numbers[:-1]
        numbersStr = [("%.2f" % x) for x in numbers]
        numbersStr[0] = "<=" + numbersStr[0]
        numbersStr[-1] = numbersStr[-1] + "<="
        numbersStr.append(legendTitle)
        numbers.append(legendTitle)
        
        # mesh surfaces and legend text
        legendSrf, textPt = legend(basePt, legendHeight, legendWidth, numOfSeg)
        
        numbersCrv = self.text2srf(numbersStr, textPt, font, textSize, fontBold)
        
        return legendSrf, numbers, numbersCrv, textPt, textSize
    
    def openLegend(self, legendRes):
        if len(legendRes)!=0:
            meshAndCrv = []
            meshAndCrv.append(legendRes[0])
            [meshAndCrv.append(c) for c in legendRes[1]]
            return meshAndCrv
        else: return -1
        
    def textJustificationEnumeration(self, justificationIndex):
        #justificationIndices:
        # 0 - bottom left (default)
        # 1 - bottom center
        # 2 - bottom right
        # 3 - middle left
        # 4 - center
        # 5 - middle right
        # 6 - top left
        # 7 - top middle
        # 8 - top right
        constantsList  = [0, 2, 4, 131072, 131074, 131076, 262144, 262146, 262148]
        try:
            justificationConstant = constantsList[justificationIndex]
        except:
            # if 0 < justificationIndex > 8
            justificationConstant = 0
        textJustification = System.Enum.ToObject(rc.Geometry.TextJustification, justificationConstant)
        return textJustification
    
    def text2crv(self, text, textPt, font = 'Verdana', textHeight = 20, justificationIndex = 0):
        # Thanks to Giulio Piacentino for his version of text to curve
        textCrvs = []
        textJustification = self.textJustificationEnumeration(justificationIndex)
        for n in range(len(text)):
            plane = rc.Geometry.Plane(textPt[n], rc.Geometry.Vector3d(0,0,1))
            if type(text[n]) is not str:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText(`text[n]`, plane, textHeight, font, True, False, textJustification)
            else:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText( text[n], plane, textHeight, font, True, False, textJustification)
                
            postText = rc.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crv = TG.Explode()
            textCrvs.append(crv)
            rc.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
        return textCrvs
    
    def text2srf(self, text, textPt, font = 'Verdana', textHeight = 20, bold = False, plane = None, justificationIndex = 0):
        # Thanks to Giulio Piacentino for his version of text to curve
        textSrfs = []
        textJustification = self.textJustificationEnumeration(justificationIndex)
        planeCheck = False
        for n in range(len(text)):
            if plane == None or planeCheck == True:
                plane = rc.Geometry.Plane(textPt[n], rc.Geometry.Vector3d(0,0,1))
                planeCheck = True
            if type(text[n]) is not str:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText(`text[n]`, plane, textHeight, font, bold, False, textJustification)
            else:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText( text[n], plane, textHeight, font, bold, False, textJustification)
                
            postText = rc.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crvs = TG.Explode()
            
            # join the curves
            joindCrvs = rc.Geometry.Curve.JoinCurves(crvs)
            
            # create the surface
            srfs = rc.Geometry.Brep.CreatePlanarBreps(joindCrvs)
            
            
            extraSrfCount = 0
            # = generate 2 surfaces
            if "=" in text[n]: extraSrfCount += -1
            if ":" in text[n]: extraSrfCount += -1
            
            if srfs:
                if len(text[n].strip()) != len(srfs) + extraSrfCount:
                    # project the curves to the place in case number of surfaces
                    # doesn't match the text
                    projectedCrvs = []
                    for crv in joindCrvs:
                        projectedCrvs.append(rc.Geometry.Curve.ProjectToPlane(crv, plane))
                    srfs = rc.Geometry.Brep.CreatePlanarBreps(projectedCrvs)
                
                #Mesh the surfcaes.
                meshSrfs = []
                for srf in srfs:
                    srf.Flip()
                    meshSrf = rc.Geometry.Mesh.CreateFromBrep(srf, rc.Geometry.MeshingParameters.Coarse)[0]
                    meshSrf.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
                    meshSrfs.append(meshSrf)
                
                textSrfs.append(meshSrfs)
            
            #if len(text[n].strip()) == len(srfs)+ extraSrfCount:
            #    textSrfs.append(srfs)
            #else:
            #print len(text[n])
            #print len(text[n].strip())
            #print len(srfs)+ extraSrfCount
            #print extraSrfCount
            #textSrfs.append(projectedCrvs)
                
            rc.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
            
        return textSrfs
    
    def createTitle(self, listInfo, boundingBoxPar, legendScale = 1, Heading = None, shortVersion = False, font = None, fontSize = None, fontBold = False):
        #Define a function to create surfaces from input curves.
        
        if Heading==None: Heading = listInfo[0][2] + ' (' + listInfo[0][3] + ')' + ' - ' + listInfo[0][4]
        
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod((listInfo[0][5], listInfo[0][6]), False)
        
        period = `stDay`+ ' ' + self.monthList[stMonth-1] + ' ' + `stHour` + ':00' + \
                 " - " + `endDay`+ ' ' + self.monthList[endMonth-1] + ' ' + `endHour` + ':00'
        
        if shortVersion: titleStr = '\n' + Heading
        else: titleStr = '\n' + Heading + '\n' + listInfo[0][1] + '\n' + period
        
        if font == None: font = 'Veranda'
        
        if fontSize == None: fontSize = (boundingBoxPar[2]/30) * legendScale
        
        titlebasePt = boundingBoxPar[-2]
        
        titleTextSrf = self.text2srf([titleStr], [titlebasePt], font, fontSize, fontBold)
        
        return titleTextSrf, titleStr, titlebasePt

    def compassCircle(self, cenPt = rc.Geometry.Point3d.Origin, northVector = rc.Geometry.Vector3d.YAxis, radius = 200, angles = range(0,360,30), xMove = 
                        10, centerLine = False):
        baseCircle = rc.Geometry.Circle(cenPt, radius).ToNurbsCurve()
        outerCircle = rc.Geometry.Circle(cenPt, 1.02*radius).ToNurbsCurve()
        
        xMove = 0.03*radius
        
        def drawLine(cenPt, vector, radius, mainLine = False, xMove = 5):
            stPtRatio = 1
            endPtRatio = 1.08
            textPtRatio = endPtRatio + 0.08
            if mainLine: endPtRatio = 1.15; textPtRatio = 1.17
            stPt = rc.Geometry.Point3d.Add(cenPt, stPtRatio * radius * vector)
            if centerLine: stPt = cenPt
            endPt = rc.Geometry.Point3d.Add(cenPt, endPtRatio * radius * vector)
            textBasePt = rc.Geometry.Point3d.Add(cenPt, textPtRatio * radius * vector)
            
            if not mainLine: textBasePt = rc.Geometry.Point3d(textBasePt.X-xMove, textBasePt.Y-(xMove/4), textBasePt.Z)
            else: textBasePt = rc.Geometry.Point3d(textBasePt.X-(xMove/2), textBasePt.Y-(xMove/2), textBasePt.Z)
            
            return rc.Geometry.Line(stPt, endPt).ToNurbsCurve(), textBasePt, baseCircle, outerCircle
        
        lines = []; textBasePts = []
        mainAngles = [0, 90, 180, 270]
        mainText = ['N', 'E', 'S', 'W']
        altText1 = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        altText2 = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        compassText = []
        for angle in angles:
            mainLine = False
            if angle in mainAngles: mainLine = True
            vector = rc.Geometry.Vector3d(northVector)
            vector.Rotate(-math.radians(angle), rc.Geometry.Vector3d.ZAxis)
            line, basePt, baseCircle, outerCircle = drawLine(cenPt, vector, radius, mainLine, xMove)
            if len(angles) != 8 and len(angles) != 16:
                if mainLine == True: compassText.append(mainText[mainAngles.index(angle)])
                else: compassText.append(str(int(angle)))
            
            textBasePts.append(basePt)
            lines.append(line)
        
        if len(angles) == 8: compassText = altText1
        if len(angles) == 16: compassText = altText2
        
        lines.append(baseCircle)
        lines.append(outerCircle)
        return lines, textBasePts, compassText
    
    
    def setupLayers(self, result = 'No result', parentLayerName = 'LADYBUG', projectName = 'Option',
                        studyLayerName = 'RADIATION_KWH', CheckTheName = True,
                        OrientationStudy = False, rotationAngle = 0, l = 0):
                            
            # studyLayerName is actually component name
            # project name will be city name for sun-path, radRose , etc.
            # OrientationStudy for result layer name
            
            layerT = rc.RhinoDoc.ActiveDoc.Layers #layer table
            
            # Add Parent layer properties
            parentLayer = rc.DocObjects.Layer()
            parentLayer.Name = parentLayerName
            parentLayer.IsVisible = True
            parentLayer.Color =  System.Drawing.Color.Pink
            
            # Add Parent layer if it's not already created
            parentLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, parentLayerName, True)
            if parentLayerIndex < 0: parentLayerIndex = layerT.Add(parentLayer)
        
            # Make Study Folder
            studyLayer = rc.DocObjects.Layer()
            studyLayer.Name = studyLayerName
            studyLayer.Color =  System.Drawing.Color.Yellow
            studyLayer.IsVisible = True
            studyLayer.ParentLayerId = layerT[parentLayerIndex].Id
            studyLayerPath = parentLayer.Name + '::' + studyLayer.Name
            # Add The layer if it's not already created
            studyLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, studyLayerPath, True)
            if studyLayerIndex < 0: studyLayerIndex = layerT.Add(studyLayer)
            
            # make a sub-layer for current project
            if projectName: layerName = str(projectName)
            else: layerName = 'Option'
            
            if rc.DocObjects.Layer.IsValidName(layerName) != True:
                print 'The layer name: ' +  `layerName` + ' is not a valid layer name.'
                return
                #layerIndex = 0; newLayerIndex = layerIndex;
            else:
                layerPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l`
                layerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                if CheckTheName:
                    while layerIndex > 0: # if layer existed rename the layer
                        l = l + 1
                        layerPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l`
                        layerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                        
                # creat the new sub layer for each geometry
                nLayer = rc.DocObjects.Layer()
                nLayer.Name = layerName + '_' + `l`
                nLayer.IsVisible = False
                nLayer.ParentLayerId = layerT[studyLayerIndex].Id
                # nLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, nLayer.Name, True)
                
                nLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                if nLayerIndex < 0: nLayerIndex = layerT.Add(nLayer)
                # study = 1; # do it once in a rotation study
                # add layer for
                newLayer = rc.DocObjects.Layer()
                if OrientationStudy:
                    newLayer.Name = ("%.3f" % (result)) + '<-' + layerName + '_' + `l` +'_Angle '+ `rotationAngle`
                else:
                    try: newLayer.Name = ("%.3f" % (result)) + '<-Result for '+ layerName + '_' + `l`
                    except: newLayer.Name = result
                        
                newLayerFullPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l` + '::' + newLayer.Name
                newLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, newLayerFullPath, True)
                # newLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, newLayer.Name, True)
                if newLayerIndex < 0:
                    newLayer.IsVisible = True
                    newLayer.ParentLayerId = layerT[nLayerIndex].Id
                    newLayerIndex = layerT.Add(newLayer)
                
            return newLayerIndex, l
    
    def bakeObjects(self, newLayerIndex, testGeomety, legendGeometry, legendText, textPt, textSize, fontName = 'Verdana', crvs = None):
            attr = rc.DocObjects.ObjectAttributes()
            attr.LayerIndex = newLayerIndex
            attr.ColorSource = rc.DocObjects.ObjectColorSource.ColorFromObject
            attr.PlotColorSource = rc.DocObjects.ObjectPlotColorSource.PlotColorFromObject
            try:
                for mesh in testGeomety: rc.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh, attr)
            except:
                rc.RhinoDoc.ActiveDoc.Objects.AddMesh(testGeomety, attr)
            
            rc.RhinoDoc.ActiveDoc.Objects.AddMesh(legendGeometry, attr)
            if crvs != None:
                for crv in crvs:
                    try:
                        rc.RhinoDoc.ActiveDoc.Objects.AddCurve(crv, attr)
                    except:
                        # This is for breps surfaces as I changed curves to surfaces now
                        try: rc.RhinoDoc.ActiveDoc.Objects.AddBrep(crv, attr)
                        except: rc.RhinoDoc.ActiveDoc.Objects.AddMesh(crv, attr)
            for text in range(len(legendText)):
                plane = rc.Geometry.Plane(textPt[text], rc.Geometry.Vector3d(0,0,1))
                if type(legendText[text]) is not str: legendText[text] = ("%.2f" % legendText[text])
                rc.RhinoDoc.ActiveDoc.Objects.AddText(legendText[text], plane, textSize, fontName, False, False, attr)
                
                # end of the script


class ComfortModels(object):
    
    def comfPMVElevatedAirspeed(self, ta, tr, vel, rh, met, clo, wme):
        #This function accepts any input conditions (including low air speeds) but will return accurate values if the airspeed is above (>0.15m/s).
        #The function will return the following:
        #pmv : Predicted mean vote
        #ppd : Percent predicted dissatisfied [%]
        #ta_adj: Air temperature adjusted for air speed [C]
        #cooling_effect : The difference between the air temperature and adjusted air temperature [C]
        #set: The Standard Effective Temperature [C] (see below)
        
        r = []
        set = self.comfPierceSET(ta, tr, vel, rh, met , clo, wme)
        stillAirThreshold = 0.15
        
        #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function 
        def utilSecant(a, b, epsilon):
            # root-finding only
            res = []
            def fn(t):
                return (set - self.comfPierceSET(ta-t, tr-t, stillAirThreshold, rh, met, clo, wme));
            f1 = fn(a)
            if abs(f1) <= epsilon: res.append(a)
            else:
                f2 = fn(b)
                if abs(f2) <= epsilon: res.append(b)
                else:
                    count = range(100)
                    for i in count:
                        if (b - a) != 0 and (f2 - f1) != 0:
                            slope = (f2 - f1) / (b - a)
                            c = b - f2/slope
                            f3 = fn(c)
                            if abs(f3) < epsilon:
                                res.append(c)
                            a = b
                            b = c
                            f1 = f2
                            f2 = f3
                res.append('NaN')
            
            return res[0]
        
        #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function definition.
        def utilBisect(a, b, epsilon, target):
            def fn(t):
                return (set - self.comfPierceSET(ta-t, tr-t, stillAirThreshold, rh, met, clo, wme))
            while abs(b - a) > (2 * epsilon):
                midpoint = (b + a) / 2
                a_T = fn(a)
                b_T = fn(b)
                midpoint_T = fn(midpoint)
                if (a_T - target) * (midpoint_T - target) < 0: b = midpoint
                elif (b_T - target) * (midpoint_T - target) < 0: a = midpoint
                else: return -999
            return midpoint
        
        
        if vel <= stillAirThreshold:
            pmv, ppd = self.comfPMV(ta, tr, vel, rh, met, clo, wme)
            ta_adj = ta
            ce = 0
        else:
            ce_l = 0
            ce_r = 40
            eps = 0.001  # precision of ce
            
            ce = utilSecant(ce_l, ce_r, eps)
            if ce == 'NaN':
                ce = utilBisect(ce_l, ce_r, eps, 0)
            
            pmv, ppd = self.comfPMV(ta - ce, tr - ce, stillAirThreshold, rh, met, clo, wme)
            ta_adj = ta - ce
            tr_adj = tr - ce
        
        r.append(pmv)
        r.append(ppd)
        r.append(set)
        r.append(ta_adj)
        r.append(ce)
        
        return r
    
    
    def comfPMV(self, ta, tr, vel, rh, met, clo, wme):
        #returns [pmv, ppd]
        #ta, air temperature (C)
        #tr, mean radiant temperature (C)
        #vel, relative air velocity (m/s)
        #rh, relative humidity (%) Used only this way to input humidity level
        #met, metabolic rate (met)
        #clo, clothing (clo)
        #wme, external work, normally around 0 (met)
        
        pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))
        
        icl = 0.155 * clo #thermal insulation of the clothing in M2K/W
        m = met * 58.15 #metabolic rate in W/M2
        w = wme * 58.15 #external work in W/M2
        mw = m - w #internal heat production in the human body
        if (icl <= 0.078): fcl = 1 + (1.29 * icl)
        else: fcl = 1.05 + (0.645 * icl)
        
        #heat transf. coeff. by forced convection
        hcf = 12.1 * math.sqrt(vel)
        taa = ta + 273
        tra = tr + 273
        tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)
    
        p1 = icl * fcl
        p2 = p1 * 3.96
        p3 = p1 * 100
        p4 = p1 * taa
        p5 = (308.7 - 0.028 * mw) + (p2 * math.pow(tra / 100, 4))
        xn = tcla / 100
        xf = tcla / 50
        eps = 0.00015
        
        n = 0
        while abs(xn - xf) > eps:
            xf = (xf + xn) / 2
            hcn = 2.38 * math.pow(abs(100.0 * xf - taa), 0.25)
            if (hcf > hcn):
                hc = hcf
            else:
                hc = hcn
            xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
            n += 1
            if (n > 150):
                print 'Max iterations exceeded'
                return 1
            
        
        tcl = 100 * xn - 273
        
        #heat loss diff. through skin 
        hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)
        #heat loss by sweating
        if mw > 58.15:
            hl2 = 0.42 * (mw - 58.15)
        else:
            hl2 = 0
        #latent respiration heat loss 
        hl3 = 1.7 * 0.00001 * m * (5867 - pa)
        #dry respiration heat loss
        hl4 = 0.0014 * m * (34 - ta)
        #heat loss by radiation  
        hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
        #heat loss by convection
        hl6 = fcl * hc * (tcl - ta)
        
        ts = 0.303 * math.exp(-0.036 * m) + 0.028
        pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
        ppd = 100.0 - 95.0 * math.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0))
        
        r = []
        r.append(pmv)
        r.append(ppd)
        
        return r
    
    
    def comfPierceSET(self, ta, tr, vel, rh, met, clo, wme):
        #Function to find the saturation vapor pressure, used frequently throughtout the comfPierceSET function.
        def findSaturatedVaporPressureTorr(T):
            #calculates Saturated Vapor Pressure (Torr) at Temperature T  (C)
            return math.exp(18.6686 - 4030.183 / (T + 235.0))
        
        #Key initial variables.
        VaporPressure = (rh * findSaturatedVaporPressureTorr(ta)) / 100
        AirVelocity = max(vel, 0.1)
        KCLO = 0.25
        BODYWEIGHT = 69.9
        BODYSURFACEAREA = 1.8258
        METFACTOR = 58.2
        SBC = 0.000000056697 # Stefan-Boltzmann constant (W/m2K4)
        CSW = 170
        CDIL = 120
        CSTR = 0.5
        
        TempSkinNeutral = 33.7 #setpoint (neutral) value for Tsk
        TempCoreNeutral = 36.49 #setpoint value for Tcr
        TempBodyNeutral = 36.49 #setpoint for Tb (.1*TempSkinNeutral + .9*TempCoreNeutral)
        SkinBloodFlowNeutral = 6.3 #neutral value for SkinBloodFlow
    
        #INITIAL VALUES - start of 1st experiment
        TempSkin = TempSkinNeutral
        TempCore = TempCoreNeutral
        SkinBloodFlow = SkinBloodFlowNeutral
        MSHIV = 0.0
        ALFA = 0.1
        ESK = 0.1 * met
        
        #Start new experiment here (for graded experiments)
        #UNIT CONVERSIONS (from input variables)
        
        p = 101325.0 / 1000 # This variable is the pressure of the atmosphere in kPa and was taken from the psychrometrics.js file of the CBE comfort tool.
        
        PressureInAtmospheres = p * 0.009869
        LTIME = 60
        TIMEH = LTIME / 60.0
        RCL = 0.155 * clo
        #AdjustICL(RCL, Conditions);  TH: I don't think this is used in the software
        
        FACL = 1.0 + 0.15 * clo #% INCREASE IN BODY SURFACE AREA DUE TO CLOTHING
        LR = 2.2 / PressureInAtmospheres #Lewis Relation is 2.2 at sea level
        RM = met * METFACTOR
        M = met * METFACTOR
        
        if clo <= 0:
            WCRIT = 0.38 * pow(AirVelocity, -0.29)
            ICL = 1.0
        else:
            WCRIT = 0.59 * pow(AirVelocity, -0.08)
            ICL = 0.45
        
        CHC = 3.0 * pow(PressureInAtmospheres, 0.53)
        CHCV = 8.600001 * pow((AirVelocity * PressureInAtmospheres), 0.53)
        CHC = max(CHC, CHCV)
        
        #initial estimate of Tcl
        CHR = 4.7
        CTC = CHR + CHC
        RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
        TOP = (CHR * tr + CHC * ta) / CTC
        TCL = TOP + (TempSkin - TOP) / (CTC * (RA + RCL))
    
        # ========================  BEGIN ITERATION
        #
        # Tcl and CHR are solved iteratively using: H(Tsk - To) = CTC(Tcl - To),
        # where H = 1/(Ra + Rcl) and Ra = 1/Facl*CTC
        
        TCL_OLD = TCL
        TIME = range(LTIME)
        flag = True
        for TIM in TIME:
            if flag == True:
                while abs(TCL - TCL_OLD) > 0.01:
                    TCL_OLD = TCL
                    CHR = 4.0 * SBC * pow(((TCL + tr) / 2.0 + 273.15), 3.0) * 0.72
                    CTC = CHR + CHC
                    RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
                    TOP = (CHR * tr + CHC * ta) / CTC
                    TCL = (RA * TempSkin + RCL * TOP) / (RA + RCL)
            flag = False
            DRY = (TempSkin - TOP) / (RA + RCL)
            HFCS = (TempCore - TempSkin) * (5.28 + 1.163 * SkinBloodFlow)
            ERES = 0.0023 * M * (44.0 - VaporPressure)
            CRES = 0.0014 * M * (34.0 - ta)
            SCR = M - HFCS - ERES - CRES - wme
            SSK = HFCS - DRY - ESK
            TCSK = 0.97 * ALFA * BODYWEIGHT
            TCCR = 0.97 * (1 - ALFA) * BODYWEIGHT
            DTSK = (SSK * BODYSURFACEAREA) / (TCSK * 60.0)# //deg C per minute
            DTCR = SCR * BODYSURFACEAREA / (TCCR * 60.0)# //deg C per minute
            TempSkin = TempSkin + DTSK
            TempCore = TempCore + DTCR
            TB = ALFA * TempSkin + (1 - ALFA) * TempCore
            SKSIG = TempSkin - TempSkinNeutral
            WARMS = (SKSIG > 0) * SKSIG
            COLDS = ((-1.0 * SKSIG) > 0) * (-1.0 * SKSIG)
            CRSIG = (TempCore - TempCoreNeutral)
            WARMC = (CRSIG > 0) * CRSIG
            COLDC = ((-1.0 * CRSIG) > 0) * (-1.0 * CRSIG)
            BDSIG = TB - TempBodyNeutral
            WARMB = (BDSIG > 0) * BDSIG
            COLDB = ((-1.0 * BDSIG) > 0) * (-1.0 * BDSIG)
            SkinBloodFlow = (SkinBloodFlowNeutral + CDIL * WARMC) / (1 + CSTR * COLDS)
            if SkinBloodFlow > 90.0: SkinBloodFlow = 90.0
            if SkinBloodFlow < 0.5: SkinBloodFlow = 0.5
            REGSW = CSW * WARMB * math.exp(WARMS / 10.7)
            if REGSW > 500.0: REGSW = 500.0
            ERSW = 0.68 * REGSW
            REA = 1.0 / (LR * FACL * CHC) #evaporative resistance of air layer
            RECL = RCL / (LR * ICL) #evaporative resistance of clothing (icl=.45)
            EMAX = (findSaturatedVaporPressureTorr(TempSkin) - VaporPressure) / (REA + RECL)
            PRSW = ERSW / EMAX
            PWET = 0.06 + 0.94 * PRSW
            EDIF = PWET * EMAX - ERSW
            ESK = ERSW + EDIF
            if PWET > WCRIT:
                PWET = WCRIT
                PRSW = WCRIT / 0.94
                ERSW = PRSW * EMAX
                EDIF = 0.06 * (1.0 - PRSW) * EMAX
                ESK = ERSW + EDIF
            if EMAX < 0:
                EDIF = 0
                ERSW = 0
                PWET = WCRIT
                PRSW = WCRIT
                ESK = EMAX
            ESK = ERSW + EDIF
            MSHIV = 19.4 * COLDS * COLDC
            M = RM + MSHIV
            ALFA = 0.0417737 + 0.7451833 / (SkinBloodFlow + .585417)
        
        
        #Define new heat flow terms, coeffs, and abbreviations
        STORE = M - wme - CRES - ERES - DRY - ESK #rate of body heat storage
        HSK = DRY + ESK #total heat loss from skin
        RN = M - wme #net metabolic heat production
        ECOMF = 0.42 * (RN - (1 * METFACTOR))
        if ECOMF < 0.0: ECOMF = 0.0 #from Fanger
        EREQ = RN - ERES - CRES - DRY
        EMAX = EMAX * WCRIT
        HD = 1.0 / (RA + RCL)
        HE = 1.0 / (REA + RECL)
        W = PWET
        PSSK = findSaturatedVaporPressureTorr(TempSkin)
        #Definition of ASHRAE standard environment... denoted "S"
        CHRS = CHR
        if met < 0.85:
            CHCS = 3.0
        else:
            CHCS = 5.66 * pow((met - 0.85), 0.39)
            if CHCS < 3.0: CHCS = 3.0
        
        CTCS = CHCS + CHRS
        RCLOS = 1.52 / ((met - wme / METFACTOR) + 0.6944) - 0.1835
        RCLS = 0.155 * RCLOS
        FACLS = 1.0 + KCLO * RCLOS
        FCLS = 1.0 / (1.0 + 0.155 * FACLS * CTCS * RCLOS)
        IMS = 0.45
        ICLS = IMS * CHCS / CTCS * (1 - FCLS) / (CHCS / CTCS - FCLS * IMS)
        RAS = 1.0 / (FACLS * CTCS)
        REAS = 1.0 / (LR * FACLS * CHCS)
        RECLS = RCLS / (LR * ICLS)
        HD_S = 1.0 / (RAS + RCLS)
        HE_S = 1.0 / (REAS + RECLS)
        
        #SET* (standardized humidity, clo, Pb, and CHC)
        #determined using Newton's iterative solution
        #FNERRS is defined in the GENERAL SETUP section above
        
        DELTA = .0001
        dx = 100.0
        X_OLD = TempSkin - HSK / HD_S #lower bound for SET
        while abs(dx) > .01:
            ERR1 = (HSK - HD_S * (TempSkin - X_OLD) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr(X_OLD)))
            ERR2 = (HSK - HD_S * (TempSkin - (X_OLD + DELTA)) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr((X_OLD + DELTA))))
            X = X_OLD - DELTA * ERR1 / (ERR2 - ERR1)
            dx = X - X_OLD
            X_OLD = X
        
        return X
    
    
    def calcBalTemp(self, initialGuess, windSpeed, relHumid, metRate, cloLevel, exWork):
        balTemper = initialGuess
        delta = 3
        while abs(delta) > 0.01:
            delta, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(balTemper, balTemper, windSpeed, relHumid, metRate, cloLevel, exWork)
            balTemper = balTemper - delta
        return balTemper
    
    
    def calcComfRange(self, initialGuessUp, initialGuessDown, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork, targetPPD):
        upTemper = initialGuessUp
        upDelta = 3
        if targetPPD == 10.0: targetPMV = 0.5
        elif targetPPD == 6.0: targetPMV = 0.220
        elif targetPPD == 15.0: targetPMV = 0.690
        elif targetPPD == 20.0: targetPMV = 0.84373
        elif targetPPD < 5.0: targetPMV = 0.0001
        else:
            #Use Rhino's geometry functions to compute a target pmv
            def pmvCrv(pmv):
                return 100.0 - 95.0 * math.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0))
            
            distribPts = []
            startPMV = 0
            for pmvCount in range(20):
                distribPts.append(rc.Geometry.Point3d(startPMV, pmvCrv(startPMV), 0))
                startPMV += 0.25
            distribCrv = rc.Geometry.Curve.CreateInterpolatedCurve(distribPts, 3)
            testLine = rc.Geometry.LineCurve(rc.Geometry.Point3d(0, targetPPD, 0), rc.Geometry.Point3d(5, targetPPD, 0))
            intersectPts = rc.Geometry.Intersect.Intersection.CurveCurve(distribCrv, testLine, sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAbsoluteTolerance)
            targetPMV = intersectPts[0].PointA.X
        
        while abs(upDelta) > 0.01:
            pmv, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(upTemper, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork)
            upDelta = targetPMV - pmv
            upTemper = upTemper + upDelta
        
        if initialGuessDown == None:
            downTemper = upTemper - 6
        else: downTemper = initialGuessDown
        downDelta = 3
        while abs(downDelta) > 0.01:
            pmv, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(downTemper, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork)
            downDelta = -targetPMV - pmv
            downTemper = downTemper + downDelta
        
        return upTemper, downTemper
    
    
    def comfAdaptiveComfortASH55(self, ta, tr, runningMean, vel, eightyOrNinety, levelOfConditioning = 0):
        # Define the variables that will be used throughout the calculation.
        r = []
        coolingEffect = 0
        if eightyOrNinety == True: offset = 3.5
        else: offset = 2.5
        to = (ta + tr) / 2
        # See if the running mean temperature is between 10 C and 33.5 C (the range where the adaptive model is supposed to be used).
        if runningMean >= 10.0 and runningMean <= 33.5:
            
            if (vel >= 0.6 and to >= 25):
                # calculate cooling effect of elevated air speed
                # when top > 25 degC.
                if vel < 0.9: coolingEffect = 1.2
                elif  vel < 1.2: coolingEffect = 1.8
                elif vel > 1.2: coolingEffect = 2.2
                else: pass
            
            #Figure out the relation between comfort and outdoor temperature depending on the level of conditioning.
            if levelOfConditioning == 0: tComf = 0.31 * runningMean + 17.8
            elif levelOfConditioning == 1: tComf = 0.09 * runningMean + 22.6
            else: tComf = ((0.09*levelOfConditioning)+(0.31*(1-levelOfConditioning))) * runningMean + ((22.6*levelOfConditioning)+(17.8*(1-levelOfConditioning)))
            
            tComfLower = tComf - offset
            tComfUpper = tComf + offset + coolingEffect
            r.append(tComf)
            r.append(to - tComf)
            r.append(tComfLower)
            r.append(tComfUpper)
            
            # See if the conditions are comfortable.
            if to > tComfLower and to < tComfUpper:
                # compliance
                acceptability = True
            else:
                # nonCompliance
                acceptability = False
            r.append(acceptability)
            
            # Append a number to the result list to show whether the values are too hot, too cold, or comfortable.
            if acceptability == True: r.append(0)
            elif to > tComfUpper: r.append(1)
            else: r.append(-1)
            
        elif runningMean < 10.0:
            # The prevailing temperature is too cold for the adaptive standard but we will use some correlations from adaptive-style surveys of conditioned buildings to give a good guess.
            if levelOfConditioning == 0: tComf = 24.024 + (0.295*(runningMean - 22.0)) * math.exp((-1)*(((runningMean-22)/(33.941125))*((runningMean-22)/(33.941125))))
            else:
                conditOffset = 2.6*levelOfConditioning
                tComf = conditOffset+ 24.024 + (0.295*(runningMean - 22.0)) * math.exp((-1)*(((runningMean-22)/(33.941125))*((runningMean-22)/(33.941125))))
            
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            if acceptability == True: condit = 0
            elif to > tComfUpper: condit = 1
            else: condit = -1 
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, condit]
            r.extend(outputs)
        else:
            # The prevailing temperature is too hot for the adaptive method.  This should usually not happen for climates on today's earth but it might be possible in the future with global warming. For this case, we will just use the adaptive model at its hottest limit.
            if (vel >= 0.6 and to >= 25):
                if vel < 0.9: coolingEffect = 1.2
                elif  vel < 1.2: coolingEffect = 1.8
                elif vel > 1.2: coolingEffect = 2.2
                else: pass
            if levelOfConditioning == 0: tComf = 0.31 * 33.5 + 17.8
            else: tComf = ((0.09*levelOfConditioning)+(0.31*(1-levelOfConditioning))) * 33.5 + ((22.6*levelOfConditioning)+(17.8*(1-levelOfConditioning)))
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset + coolingEffect
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            if acceptability == True: condit = 0
            elif to > tComfUpper: condit = 1
            else: condit = -1 
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, condit]
            r.extend(outputs)
        
        return r
    
    def comfAdaptiveComfortEN15251(self, ta, tr, runningMean, vel, comfortClass, levelOfConditioning = 0):
        # Define the variables that will be used throughout the calculation.
        r = []
        coolingEffect = 0
        if comfortClass == 1: offset = 2
        elif comfortClass == 2: offset = 3
        else: offset = 4
        to = (ta + tr) / 2
        
        # See if the running mean temperature is between 10 C and 30.0 C (the range where the adaptive model is supposed to be used).
        if runningMean >= 10.0 and runningMean <= 30.0:
            if (vel >= 0.2 and to >= 25):
                # calculate cooling effect of elevated air speed
                # when top > 25 degC.
                coolingEffect = 1.7856 * math.log(vel) + 2.9835
            
            if levelOfConditioning == 0: tComf = 0.33 * runningMean + 18.8
            elif levelOfConditioning == 1: tComf = 0.09 * runningMean + 22.6
            else: tComf = ((0.09*levelOfConditioning)+(0.33*(1-levelOfConditioning))) * runningMean + ((22.6*levelOfConditioning)+(18.8*(1-levelOfConditioning)))
            
            if runningMean > 15:
                tComfLower = tComf - offset
                tComfUpper = tComf + offset + coolingEffect
            elif runningMean > 12.73 and runningMean < 15 and levelOfConditioning == 0:
                tComfLow = 23.75
                tComfLower = tComfLow - offset
                tComfUpper = tComf + offset + coolingEffect
            elif levelOfConditioning != 0:
                tComfLower = tComf - offset
                tComfUpper = tComf + offset + coolingEffect
                #tComfLow = 23.75 - (0.25*levelOfConditioning)
            else:
                tComfLow = 23.75
                tComfLower = tComfLow - offset
                if comfortClass == 1: tComfUpper = tComf + offset
                else: tComfUpper = tComf + offset + coolingEffect
            
            r.append(tComf)
            r.append(to - tComf)
            r.append(tComfLower)
            r.append(tComfUpper)
            
            # See if the conditions are comfortable.
            if to > tComfLower and to < tComfUpper:
                # compliance
                acceptability = True
            else:
                # nonCompliance
                acceptability = False
            r.append(acceptability)
            
            # Append a number to the result list to show whether the values are too hot, too cold, or comfortable.
            if acceptability == True: r.append(0)
            elif to > tComfUpper: r.append(1)
            else: r.append(-1)
            
        elif runningMean < 10.0:
            # The prevailing temperature is too cold for the adaptive standard but we will use some correlations from adaptive-style surveys of conditioned buildings to give a good guess.
            if levelOfConditioning == 0: tComf = 25.224 + (0.295*(runningMean - 22.0)) * math.exp((-1)*(((runningMean-22)/(33.941125))*((runningMean-22)/(33.941125))))
            else:
                conditOffset = 1.4*levelOfConditioning
                tComf = conditOffset + 25.224 + (0.295*(runningMean - 22.0)) * math.exp((-1)*(((runningMean-22)/(33.941125))*((runningMean-22)/(33.941125))))
            
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            if acceptability == True: condit = 0
            elif to > tComfUpper: condit = 1
            else: condit = -1 
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, condit]
            r.extend(outputs)
        else:
            # The prevailing temperature is too hot for the adaptive method.  This should usually not happen for climates on today's earth but it might be possible in the future with global warming. For this case, we will just use the adaptive model at its hottest limit.
            if (vel >= 0.2 and to >= 25):
                # calculate cooling effect of elevated air speed
                # when top > 25 degC.
                coolingEffect = 1.7856 * math.log(vel) + 2.9835
            if levelOfConditioning == 0: tComf = 0.33 * 30.0 + 18.8
            else: tComf = ((0.09*levelOfConditioning)+(0.33*(1-levelOfConditioning))) * 30.0 + ((22.6*levelOfConditioning)+(18.8*(1-levelOfConditioning)))
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset + coolingEffect
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            if acceptability == True: condit = 0
            elif to > tComfUpper: condit = 1
            else: condit = -1 
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, condit]
            r.extend(outputs)
        
        return r
    
    
    def comfUTCI(self, Ta, Tmrt, va, RH):
        # Define a function to change the RH to water saturation vapor pressure in hPa
        def es(ta):
            g = [-2836.5744, -6028.076559, 19.54263612, -0.02737830188, 0.000016261698, (7.0229056*(10**(-10))), (-1.8680009*(10**(-13)))]      
            tk = ta + 273.15 # air temp in K
            es = 2.7150305 * math.log(tk)
            for count, i in enumerate(g):
                es = es + (i * (tk**(count-2)))
            es = math.exp(es)*0.01	# convert Pa to hPa
            return es
        
        #Do a series of checks to be sure that the input values are within the bounds accepted by the model.
        check = True
        if Ta < -50.0 or Ta > 50.0: check = False
        else: pass
        if Tmrt-Ta < -30.0 or Tmrt-Ta > 70.0: check = False
        else: pass
        if va < 0.5: va = 0.5
        elif va > 17: va = 17
        else: pass
        
        #If everything is good, run the data through the model below to get the UTCI.
        #This is a python version of the UTCI_approx function, Version a 0.002, October 2009
        #Ta: air temperature, degree Celsius
        #ehPa: water vapour presure, hPa=hecto Pascal
        #Tmrt: mean radiant temperature, degree Celsius
        #va10m: wind speed 10 m above ground level in m/s
        
        if check == True:
            ehPa = es(Ta) * (RH/100.0)
            D_Tmrt = Tmrt - Ta
            Pa = ehPa/10.0  # convert vapour pressure to kPa
            
            
            UTCI_approx = Ta + \
            (0.607562052) + \
            (-0.0227712343) * Ta + \
            (8.06470249*(10**(-4))) * Ta * Ta + \
            (-1.54271372*(10**(-4))) * Ta * Ta * Ta + \
            (-3.24651735*(10**(-6))) * Ta * Ta * Ta * Ta + \
            (7.32602852*(10**(-8))) * Ta * Ta * Ta * Ta * Ta + \
            (1.35959073*(10**(-9))) * Ta * Ta * Ta * Ta * Ta * Ta + \
            (-2.25836520) * va + \
            (0.0880326035) * Ta * va + \
            (0.00216844454) * Ta * Ta * va + \
            (-1.53347087*(10**(-5))) * Ta * Ta * Ta * va + \
            (-5.72983704*(10**(-7))) * Ta * Ta * Ta * Ta * va + \
            (-2.55090145*(10**(-9))) * Ta * Ta * Ta * Ta * Ta * va + \
            (-0.751269505) * va * va + \
            (-0.00408350271) * Ta * va * va + \
            (-5.21670675*(10**(-5))) * Ta * Ta * va * va + \
            (1.94544667*(10**(-6))) * Ta * Ta * Ta * va * va + \
            (1.14099531*(10**(-8))) * Ta * Ta * Ta * Ta * va * va + \
            (0.158137256) * va * va * va + \
            (-6.57263143*(10**(-5))) * Ta * va * va * va + \
            (2.22697524*(10**(-7))) * Ta * Ta * va * va * va + \
            (-4.16117031*(10**(-8))) * Ta * Ta * Ta * va * va * va + \
            (-0.0127762753) * va * va * va * va + \
            (9.66891875*(10**(-6))) * Ta * va * va * va * va + \
            (2.52785852*(10**(-9))) * Ta * Ta * va * va * va * va + \
            (4.56306672*(10**(-4))) * va * va * va * va * va + \
            (-1.74202546*(10**(-7))) * Ta * va * va * va * va * va + \
            (-5.91491269*(10**(-6))) * va * va * va * va * va * va + \
            (0.398374029) * D_Tmrt + \
            (1.83945314*(10**(-4))) * Ta * D_Tmrt + \
            (-1.73754510*(10**(-4))) * Ta * Ta * D_Tmrt + \
            (-7.60781159*(10**(-7))) * Ta * Ta * Ta * D_Tmrt + \
            (3.77830287*(10**(-8))) * Ta * Ta * Ta * Ta * D_Tmrt + \
            (5.43079673*(10**(-10))) * Ta * Ta * Ta * Ta * Ta * D_Tmrt + \
            (-0.0200518269) * va * D_Tmrt + \
            (8.92859837*(10**(-4))) * Ta * va * D_Tmrt + \
            (3.45433048*(10**(-6))) * Ta * Ta * va * D_Tmrt + \
            (-3.77925774*(10**(-7))) * Ta * Ta * Ta * va * D_Tmrt + \
            (-1.69699377*(10**(-9))) * Ta * Ta * Ta * Ta * va * D_Tmrt + \
            (1.69992415*(10**(-4))) * va*va*D_Tmrt + \
            ( -4.99204314*(10**(-5)) ) * Ta*va*va*D_Tmrt + \
            ( 2.47417178*(10**(-7)) ) * Ta*Ta*va*va*D_Tmrt + \
            ( 1.07596466*(10**(-8)) ) * Ta*Ta*Ta*va*va*D_Tmrt + \
            ( 8.49242932*(10**(-5)) ) * va*va*va*D_Tmrt + \
            ( 1.35191328*(10**(-6)) ) * Ta*va*va*va*D_Tmrt + \
            ( -6.21531254*(10**(-9)) ) * Ta*Ta*va*va*va*D_Tmrt + \
            ( -4.99410301*(10**(-6)) ) * va*va*va*va*D_Tmrt + \
            ( -1.89489258*(10**(-8)) ) * Ta*va*va*va*va*D_Tmrt + \
            ( 8.15300114*(10**(-8)) ) * va*va*va*va*va*D_Tmrt + \
            ( 7.55043090*(10**(-4)) ) * D_Tmrt*D_Tmrt + \
            ( -5.65095215*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt + \
            ( -4.52166564*(10**(-7)) ) * Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 2.46688878*(10**(-8)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 2.42674348*(10**(-10)) ) * Ta*Ta*Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 1.54547250*(10**(-4)) ) * va*D_Tmrt*D_Tmrt + \
            ( 5.24110970*(10**(-6)) ) * Ta*va*D_Tmrt*D_Tmrt + \
            ( -8.75874982*(10**(-8)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt + \
            ( -1.50743064*(10**(-9)) ) * Ta*Ta*Ta*va*D_Tmrt*D_Tmrt + \
            ( -1.56236307*(10**(-5)) ) * va*va*D_Tmrt*D_Tmrt + \
            ( -1.33895614*(10**(-7)) ) * Ta*va*va*D_Tmrt*D_Tmrt + \
            ( 2.49709824*(10**(-9)) ) * Ta*Ta*va*va*D_Tmrt*D_Tmrt + \
            ( 6.51711721*(10**(-7)) ) * va*va*va*D_Tmrt*D_Tmrt + \
            ( 1.94960053*(10**(-9)) ) * Ta*va*va*va*D_Tmrt*D_Tmrt + \
            ( -1.00361113*(10**(-8)) ) * va*va*va*va*D_Tmrt*D_Tmrt + \
            ( -1.21206673*(10**(-5)) ) * D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -2.18203660*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 7.51269482*(10**(-9)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 9.79063848*(10**(-11)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.25006734*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -1.81584736*(10**(-9)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -3.52197671*(10**(-10)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -3.36514630*(10**(-8)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.35908359*(10**(-10)) ) * Ta*va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.17032620*(10**(-10)) ) * va*va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -1.30369025*(10**(-9)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.13908461*(10**(-10)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 9.22652254*(10**(-12)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -5.08220384*(10**(-9)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -2.24730961*(10**(-11)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.17139133*(10**(-10)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 6.62154879*(10**(-10)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.03863260*(10**(-13)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.95087203*(10**(-12)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -4.73602469*(10**(-12))) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 5.12733497) * Pa + \
            ( -0.312788561) * Ta*Pa + \
            ( -0.0196701861 ) * Ta*Ta*Pa + \
            ( 9.99690870*(10**(-4)) ) * Ta*Ta*Ta*Pa + \
            ( 9.51738512*(10**(-6)) ) * Ta*Ta*Ta*Ta*Pa + \
            ( -4.66426341*(10**(-7)) ) * Ta*Ta*Ta*Ta*Ta*Pa + \
            ( 0.548050612 ) * va*Pa + \
            ( -0.00330552823) * Ta*va*Pa + \
            ( -0.00164119440 ) * Ta*Ta*va*Pa + \
            ( -5.16670694*(10**(-6)) ) * Ta*Ta*Ta*va*Pa + \
            ( 9.52692432*(10**(-7)) ) * Ta*Ta*Ta*Ta*va*Pa + \
            ( -0.0429223622 ) * va*va*Pa + \
            ( 0.00500845667 ) * Ta*va*va*Pa + \
            ( 1.00601257*(10**(-6)) ) * Ta*Ta*va*va*Pa + \
            ( -1.81748644*(10**(-6)) ) * Ta*Ta*Ta*va*va*Pa + \
            ( -1.25813502*(10**(-3)) ) * va*va*va*Pa + \
            ( -1.79330391*(10**(-4)) ) * Ta*va*va*va*Pa + \
            ( 2.34994441*(10**(-6)) ) * Ta*Ta*va*va*va*Pa + \
            ( 1.29735808*(10**(-4)) ) * va*va*va*va*Pa + \
            ( 1.29064870*(10**(-6)) ) * Ta*va*va*va*va*Pa + \
            ( -2.28558686*(10**(-6)) ) * va*va*va*va*va*Pa + \
            ( -0.0369476348 ) * D_Tmrt*Pa + \
            ( 0.00162325322 ) * Ta*D_Tmrt*Pa + \
            ( -3.14279680*(10**(-5)) ) * Ta*Ta*D_Tmrt*Pa + \
            ( 2.59835559*(10**(-6)) ) * Ta*Ta*Ta*D_Tmrt*Pa + \
            ( -4.77136523*(10**(-8)) ) * Ta*Ta*Ta*Ta*D_Tmrt*Pa + \
            ( 8.64203390*(10**(-3)) ) * va*D_Tmrt*Pa + \
            ( -6.87405181*(10**(-4)) ) * Ta*va*D_Tmrt*Pa + \
            ( -9.13863872*(10**(-6)) ) * Ta*Ta*va*D_Tmrt*Pa + \
            ( 5.15916806*(10**(-7)) ) * Ta*Ta*Ta*va*D_Tmrt*Pa + \
            ( -3.59217476*(10**(-5)) ) * va*va*D_Tmrt*Pa + \
            ( 3.28696511*(10**(-5)) ) * Ta*va*va*D_Tmrt*Pa + \
            ( -7.10542454*(10**(-7)) ) * Ta*Ta*va*va*D_Tmrt*Pa + \
            ( -1.24382300*(10**(-5)) ) * va*va*va*D_Tmrt*Pa + \
            ( -7.38584400*(10**(-9)) ) * Ta*va*va*va*D_Tmrt*Pa + \
            ( 2.20609296*(10**(-7)) ) * va*va*va*va*D_Tmrt*Pa + \
            ( -7.32469180*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa + \
            ( -1.87381964*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt*Pa + \
            ( 4.80925239*(10**(-6)) ) * Ta*Ta*D_Tmrt*D_Tmrt*Pa + \
            ( -8.75492040*(10**(-8)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt*Pa + \
            ( 2.77862930*(10**(-5)) ) * va*D_Tmrt*D_Tmrt*Pa + \
            ( -5.06004592*(10**(-6)) ) * Ta*va*D_Tmrt*D_Tmrt*Pa + \
            ( 1.14325367*(10**(-7)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt*Pa + \
            ( 2.53016723*(10**(-6)) ) * va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -1.72857035*(10**(-8)) ) * Ta*va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -3.95079398*(10**(-8)) ) * va*va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -3.59413173*(10**(-7)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 7.04388046*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.89309167*(10**(-8)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -4.79768731*(10**(-7)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 7.96079978*(10**(-9)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 1.62897058*(10**(-9)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 3.94367674*(10**(-8)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.18566247*(10**(-9)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 3.34678041*(10**(-10)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.15606447*(10**(-10)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -2.80626406 ) * Pa*Pa + \
            ( 0.548712484 ) * Ta*Pa*Pa + \
            ( -0.00399428410 ) * Ta*Ta*Pa*Pa + \
            ( -9.54009191*(10**(-4)) ) * Ta*Ta*Ta*Pa*Pa + \
            ( 1.93090978*(10**(-5)) ) * Ta*Ta*Ta*Ta*Pa*Pa + \
            ( -0.308806365 ) * va*Pa*Pa + \
            ( 0.0116952364 ) * Ta*va*Pa*Pa + \
            ( 4.95271903*(10**(-4)) ) * Ta*Ta*va*Pa*Pa + \
            ( -1.90710882*(10**(-5)) ) * Ta*Ta*Ta*va*Pa*Pa + \
            ( 0.00210787756 ) * va*va*Pa*Pa + \
            ( -6.98445738*(10**(-4)) ) * Ta*va*va*Pa*Pa + \
            ( 2.30109073*(10**(-5)) ) * Ta*Ta*va*va*Pa*Pa + \
            ( 4.17856590*(10**(-4)) ) * va*va*va*Pa*Pa + \
            ( -1.27043871*(10**(-5)) ) * Ta*va*va*va*Pa*Pa + \
            ( -3.04620472*(10**(-6)) ) * va*va*va*va*Pa*Pa + \
            ( 0.0514507424 ) * D_Tmrt*Pa*Pa + \
            ( -0.00432510997 ) * Ta*D_Tmrt*Pa*Pa + \
            ( 8.99281156*(10**(-5)) ) * Ta*Ta*D_Tmrt*Pa*Pa + \
            ( -7.14663943*(10**(-7)) ) * Ta*Ta*Ta*D_Tmrt*Pa*Pa + \
            ( -2.66016305*(10**(-4)) ) * va*D_Tmrt*Pa*Pa + \
            ( 2.63789586*(10**(-4)) ) * Ta*va*D_Tmrt*Pa*Pa + \
            ( -7.01199003*(10**(-6)) ) * Ta*Ta*va*D_Tmrt*Pa*Pa + \
            ( -1.06823306*(10**(-4)) ) * va*va*D_Tmrt*Pa*Pa + \
            ( 3.61341136*(10**(-6)) ) * Ta*va*va*D_Tmrt*Pa*Pa + \
            ( 2.29748967*(10**(-7)) ) * va*va*va*D_Tmrt*Pa*Pa + \
            ( 3.04788893*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -6.42070836*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 1.16257971*(10**(-6)) ) * Ta*Ta*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 7.68023384*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -5.47446896*(10**(-7)) ) * Ta*va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -3.59937910*(10**(-8)) ) * va*va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -4.36497725*(10**(-6)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 1.68737969*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 2.67489271*(10**(-8)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 3.23926897*(10**(-9)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -0.0353874123 ) * Pa*Pa*Pa + \
            ( -0.221201190 ) * Ta*Pa*Pa*Pa + \
            ( 0.0155126038 ) * Ta*Ta*Pa*Pa*Pa + \
            ( -2.63917279*(10**(-4)) ) * Ta*Ta*Ta*Pa*Pa*Pa + \
            ( 0.0453433455 ) * va*Pa*Pa*Pa + \
            ( -0.00432943862 ) * Ta*va*Pa*Pa*Pa + \
            ( 1.45389826*(10**(-4)) ) * Ta*Ta*va*Pa*Pa*Pa + \
            ( 2.17508610*(10**(-4)) ) * va*va*Pa*Pa*Pa + \
            ( -6.66724702*(10**(-5)) ) * Ta*va*va*Pa*Pa*Pa + \
            ( 3.33217140*(10**(-5)) ) * va*va*va*Pa*Pa*Pa + \
            ( -0.00226921615 ) * D_Tmrt*Pa*Pa*Pa + \
            ( 3.80261982*(10**(-4)) ) * Ta*D_Tmrt*Pa*Pa*Pa + \
            ( -5.45314314*(10**(-9)) ) * Ta*Ta*D_Tmrt*Pa*Pa*Pa + \
            ( -7.96355448*(10**(-4)) ) * va*D_Tmrt*Pa*Pa*Pa + \
            ( 2.53458034*(10**(-5)) ) * Ta*va*D_Tmrt*Pa*Pa*Pa + \
            ( -6.31223658*(10**(-6)) ) * va*va*D_Tmrt*Pa*Pa*Pa + \
            ( 3.02122035*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( -4.77403547*(10**(-6)) ) * Ta*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( 1.73825715*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( -4.09087898*(10**(-7)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( 0.614155345 ) * Pa*Pa*Pa*Pa + \
            ( -0.0616755931 ) * Ta*Pa*Pa*Pa*Pa + \
            ( 0.00133374846 ) * Ta*Ta*Pa*Pa*Pa*Pa + \
            ( 0.00355375387 ) * va*Pa*Pa*Pa*Pa + \
            ( -5.13027851*(10**(-4)) ) * Ta*va*Pa*Pa*Pa*Pa + \
            ( 1.02449757*(10**(-4)) ) * va*va*Pa*Pa*Pa*Pa + \
            ( -0.00148526421 ) * D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -4.11469183*(10**(-5)) ) * Ta*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -6.80434415*(10**(-6)) ) * va*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -9.77675906*(10**(-6)) ) * D_Tmrt*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( 0.0882773108 ) * Pa*Pa*Pa*Pa*Pa + \
            ( -0.00301859306 ) * Ta*Pa*Pa*Pa*Pa*Pa + \
            ( 0.00104452989 ) * va*Pa*Pa*Pa*Pa*Pa + \
            ( 2.47090539*(10**(-4)) ) * D_Tmrt*Pa*Pa*Pa*Pa*Pa + \
            ( 0.00148348065 ) * Pa*Pa*Pa*Pa*Pa*Pa
            
            if UTCI_approx > 9 and UTCI_approx < 26: comfortable = 1
            else: comfortable = 0
            
            if UTCI_approx <= -13.0:
                stressRange = -3
                stressVal = -1
            elif UTCI_approx > -13.0 and UTCI_approx <= 0.0:
                stressRange = -2
                stressVal = -1
            elif UTCI_approx > 0.0 and UTCI_approx <= 9.0:
                stressRange = -1
                stressVal = -1
            elif UTCI_approx > 9.0 and UTCI_approx <= 26.0:
                stressRange = 0
                stressVal = 0
            elif UTCI_approx > 26.0 and UTCI_approx <= 28.0:
                stressRange = 1
                stressVal = 1
            elif UTCI_approx > 28.0 and UTCI_approx <= 32.0:
                stressRange = 2
                stressVal = 1
            else:
                stressRange = 3
                stressVal = 1
            
        else:
            UTCI_approx = None
            comfortable = None
            stressVal = None
            stressRange = None
        
        return UTCI_approx, comfortable, stressRange, stressVal
    
    
    def calcVapPressHighAccuracy(self, TKelvin):
        #Calculate saturation vapor pressure above freezing
        Sigma = []
        for item in TKelvin:
            if item >= 273:
                Sigma.append(1-(item/647.096))
            else:
                Sigma.append(0)
        
        ExpressResult = []
        for item in Sigma:
            ExpressResult.append(((item)*(-7.85951783))+((item**1.5)*1.84408259)+((item**3)*(-11.7866487))+((item**3.5)*22.6807411)+((item**4)*(-15.9618719))+((item**7.5)*1.80122502))
        
        CritTemp = []
        for item in TKelvin:
            CritTemp.append(647.096/item)
        
        Exponent = [a*b for a,b in zip(CritTemp,ExpressResult)]
        
        Power = []
        for item in Exponent:
            Power.append(math.exp(item))
        
        SatPress1 = []
        for item in Power:
            if item != 1:
                SatPress1.append(item*22064000)
            else:
                SatPress1.append(0)
        
        #Calculate saturation vapor pressure below freezing
        Theta = []
        for item in TKelvin:
            if item < 273:
                Theta.append(item/273.16)
            else:
                Theta.append(1)
        
        Exponent2 = []
        for x in Theta:
            Exponent2.append(((1-(x**(-1.5)))*(-13.928169))+((1-(x**(-1.25)))*34.707823))
        
        Power = []
        for item in Exponent2:
            Power.append(math.exp(item))
        
        SatPress2 = []
        for item in Power:
            if item != 1:
                SatPress2.append(item*611.657)
            else:
                SatPress2.append(0)
        
        #Combine into final saturation vapor pressure
        saturationPressure = [a+b for a,b in zip(SatPress1,SatPress2)]
        
        return saturationPressure
    
    def calcHumidRatio(self, airTemp, relHumid, barPress):
        #Convert Temperature to Kelvin
        TKelvin = []
        for item in airTemp:
            TKelvin.append(item+273)
        
        saturationPressure = self.calcVapPressHighAccuracy(TKelvin)
        
        #Calculate hourly water vapor pressure
        DecRH = []
        for item in relHumid:
            DecRH.append(item*0.01)
        
        partialPressure = [a*b for a,b in zip(DecRH,saturationPressure)]
        
        #Calculate hourly humidity ratio
        PressDiffer = [a-b for a,b in zip(barPress,partialPressure)]
        
        Constant = []
        for item in partialPressure:
            Constant.append(item*0.621991)
        
        humidityRatio = [a/b for a,b in zip(Constant,PressDiffer)]
        
        #Calculate hourly enthalpy
        EnVariable1 = []
        for item in humidityRatio:
            EnVariable1.append(1.01+(1.89*item))
        
        EnVariable2 = [a*b for a,b in zip(EnVariable1,airTemp)]
        
        EnVariable3 = []
        for item in humidityRatio:
            EnVariable3.append(2500*item)
        
        EnVariable4 = [a+b for a,b in zip(EnVariable2,EnVariable3)]
        
        enthalpy = []
        for x in EnVariable4:
            if x >= 0:
                enthalpy.append(x)
            else:
                enthalpy.append(0)
        
        #Return all of the results
        return humidityRatio, enthalpy, partialPressure, saturationPressure
    
    
    def calcRelHumidFromHumidRatio(self, absHumid, barPress, temperature):
        #Calculate the partial pressure of water in the atmostphere.
        Pw = (absHumid*1000*barPress)/(621.9907 + (absHumid*1000))
        
        #Convert Temperature to Kelvin
        TKelvin = temperature + 273
        #Calculate saturation pressure.
        Pws = self.calcVapPressHighAccuracy([TKelvin])[0]
        
        #Calculate the relative humidity.
        relHumid = (Pw/Pws)*100
        
        return relHumid
    
    
    def calcTempFromEnthalpy(self, enthalpy, absHumid):
        airTemp =(enthalpy - 2.5*(absHumid*1000))/(1.01 + (0.00189*absHumid*1000))
        return airTemp
    
    
    def outlineCurve(self, curve):
        solidBrep = rc.Geometry.Brep.CreatePlanarBreps([curve])[0]
        try:
            offsetCrv = curve.OffsetOnSurface(solidBrep.Faces[0], 0.25, sc.doc.ModelAbsoluteTolerance)[0]
            finalBrep = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])
        except:
            finalBrep = solidBrep
            warning = "Creating an outline of one of the comfort or strategy curves failed.  Component will return a solid brep."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
        return finalBrep
    
    
    def getSeatedMannequinData(self):
        seatedData = [[(-0.0495296, 0.284129, 0.450062), (-0.0495296, 0.284129, 0.973663), (-0.175068, 0.166825, 0.973663), (-0.175068, 0.166825, 0.38225)],
        [(0.0495296, 0.284129, 0.450062), (0.0495296, 0.284129, 0.973663), (-0.0495296, 0.284129, 0.973663), (-0.0495296, 0.284129, 0.450062)],
        [(0.0495296, 0.284129, 0.973663), (0.0495296, 0.284129, 0.450062), (0.175068, 0.166825, 0.38225), (0.175068, 0.166825, 0.973663)],
        [(-0.165339, 0.096853, 0.60115), (-0.120896, -0.222765, 0.60115), (-0.120896, -0.222765, 0.38225), (-0.175068, 0.166825, 0.38225)],
        [(-0.165339, 0.096853, 0.789205), (-0.165339, 0.096853, 0.60115), (-0.175068, 0.166825, 0.902163)],
        [(-0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.902163), (-0.165339, 0.096853, 0.60115)],
        [(0.165339, 0.096853, 0.60115), (0.120896, -0.222765, 0.60115), (0.120896, -0.222765, 0.38225), (0.175068, 0.166825, 0.38225)],
        [(0.165339, 0.096853, 0.789205), (0.165339, 0.096853, 0.60115), (0.175068, 0.166825, 0.902163)],
        [(0.175068, 0.166825, 0.38225), (0.175068, 0.166825, 0.902163), (0.165339, 0.096853, 0.60115)],
        [(0.120896, -0.222765, 0.60115), (0.120896, -0.222765, 0.0715), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.222765, 0.60115)],
        [(-0.120896, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.0715), (-0.120896, -0.222765, 0.0715)],
        [(0.0223678, -0.132523, 0.38225), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.222765, 0.60115)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.382764, -4.51028e-17), (0.0223678, -0.382764, 0.0715)],
        [(0.0223678, -0.382764, -4.51028e-17), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.132523, -4.51028e-17)],
        [(0.0223678, -0.132523, 0.38225), (0.0223678, 0.0529662, 0.60115), (0.0223678, 0.0529662, 0.38225)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.132523, 0.38225), (0.0223678, -0.132523, -4.51028e-17)],
        [(0.0223678, -0.222765, 0.60115), (0.0223678, 0.0529662, 0.60115), (0.0223678, -0.132523, 0.38225)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.382764, 0.0715), (-0.0223678, -0.382764, -3.1225e-17)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.0715)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.382764, -3.1225e-17), (-0.0223678, -0.132523, -3.1225e-17)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.132523, -3.1225e-17), (-0.0223678, -0.132523, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225), (-0.0223678, 0.0529662, 0.60115)],
        [(-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.60115)],
        [(-0.120896, -0.382764, 0.0715), (-0.120896, -0.382764, -3.29597e-17), (-0.120896, -0.222765, 0.0715)],
        [(-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.222765, 0.0715), (-0.120896, -0.382764, -3.29597e-17)],
        [(-0.120896, -0.222765, 0.38225), (-0.120896, -0.222765, 0.0715), (-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.132523, 0.38225)],
        [(0.120896, -0.382764, 0.0715), (0.120896, -0.382764, -4.51028e-17), (0.120896, -0.222765, 0.0715)],
        [(0.120896, -0.132523, -4.51028e-17), (0.120896, -0.222765, 0.0715), (0.120896, -0.382764, -4.51028e-17)],
        [(0.120896, -0.222765, 0.38225), (0.120896, -0.222765, 0.0715), (0.120896, -0.132523, -4.51028e-17), (0.120896, -0.132523, 0.38225)],
        [(0.0223678, 0.0529662, 0.38225), (0.0223678, 0.0529662, 0.973663), (-0.0223678, 0.0529662, 0.973663), (-0.0223678, 0.0529662, 0.38225)],
        [(-0.0495296, 0.284129, 0.450062), (0.0495296, 0.284129, 0.450062), (0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, -0.132523, 0.0715), (-0.120896, -0.132523, 0.0715), (-0.120896, -0.132523, 0.38225)],
        [(-0.120896, -0.222765, 0.0715), (-0.120896, -0.382764, 0.0715), (-0.0223678, -0.382764, 0.0715), (-0.0223678, -0.222765, 0.0715)],
        [(-0.0223678, -0.382764, -3.1225e-17), (-0.120896, -0.382764, -3.29597e-17), (-0.120896, -0.132523, -3.29597e-17), (-0.0223678, -0.132523, -3.1225e-17)],
        [(-0.0223678, -0.132523, 0.0715), (-0.0223678, -0.132523, -3.1225e-17), (-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.132523, 0.0715)],
        [(-0.0223678, -0.382764, 0.0715), (-0.120896, -0.382764, 0.0715), (-0.120896, -0.382764, -3.29597e-17), (-0.0223678, -0.382764, -3.1225e-17)],
        [(0.0223678, -0.132523, 0.0715), (0.0223678, -0.132523, 0.38225), (0.120896, -0.132523, 0.38225), (0.120896, -0.132523, 0.0715)],
        [(-0.175068, 0.166825, 0.38225), (-0.120896, -0.222765, 0.38225), (-0.120896, -0.132523, 0.38225)],
        [(-0.175068, 0.166825, 0.38225), (-0.120896, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225), (-0.120896, -0.132523, 0.38225)],
        [(0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.38225), (-0.0223678, 0.0529662, 0.38225), (0.0223678, 0.0529662, 0.38225)],
        [(0.175068, 0.166825, 0.38225), (0.0223678, 0.0529662, 0.38225), (0.120896, -0.132523, 0.38225)],
        [(0.0223678, -0.132523, 0.38225), (0.120896, -0.132523, 0.38225), (0.0223678, 0.0529662, 0.38225)],
        [(0.120896, -0.222765, 0.38225), (0.175068, 0.166825, 0.38225), (0.120896, -0.132523, 0.38225)],
        [(0.165339, 0.096853, 0.60115), (0.0223678, 0.0529662, 0.60115), (0.0223678, -0.222765, 0.60115), (0.120896, -0.222765, 0.60115)],
        [(-0.120896, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.60115), (-0.0223678, 0.0529662, 0.60115), (-0.165339, 0.096853, 0.60115)],
        [(0.165339, 0.096853, 0.60115), (0.165339, 0.096853, 0.973663), (0.0223678, 0.0529662, 0.973663), (0.0223678, 0.0529662, 0.60115)],
        [(0.232207, 0.15888, 0.902163), (0.175068, 0.166825, 0.902163), (0.175068, 0.166825, 0.973663), (0.232207, 0.15888, 0.973663)],
        [(0.232207, 0.15888, 0.973663), (0.222478, 0.0889078, 0.973663), (0.165339, 0.096853, 0.973663), (0.175068, 0.166825, 0.973663)],
        [(0.206606, -0.025235, 0.728104), (0.206606, -0.180522, 0.728104), (0.209127, -0.180873, 0.694807), (0.211569, 0.0104553, 0.662556)],
        [(0.153842, 0.0141721, 0.655729), (0.151455, -0.172853, 0.687256), (0.148959, -0.172506, 0.720232), (0.148959, -0.0209489, 0.720232)],
        [(0.206606, -0.025235, 0.728104), (0.148959, -0.0209489, 0.720232), (0.148959, -0.172506, 0.720232), (0.206606, -0.180522, 0.728104)],
        [(0.153842, 0.0141721, 0.655729), (0.151455, -0.172853, 0.687256), (0.209127, -0.180873, 0.694807), (0.211569, 0.0104553, 0.662556)],
        [(0.209127, -0.180873, 0.694807), (0.151455, -0.172853, 0.687256), (0.139503, -0.258806, 0.687256), (0.197175, -0.266825, 0.694807)],
        [(0.151455, -0.172853, 0.687256), (0.148959, -0.172506, 0.720232), (0.137007, -0.258459, 0.720232), (0.139503, -0.258806, 0.687256)],
        [(0.148959, -0.172506, 0.720232), (0.206606, -0.180522, 0.728104), (0.194654, -0.266475, 0.728104), (0.137007, -0.258459, 0.720232)],
        [(0.197175, -0.266825, 0.694807), (0.194654, -0.266475, 0.728104), (0.206606, -0.180522, 0.728104), (0.209127, -0.180873, 0.694807)],
        [(0.197175, -0.266825, 0.694807), (0.194654, -0.266475, 0.728104), (0.137007, -0.258459, 0.720232), (0.139503, -0.258806, 0.687256)],
        [(0.232207, 0.15888, 0.902163), (0.211569, 0.0104553, 0.662556), (0.153842, 0.0141721, 0.655729), (0.175068, 0.166825, 0.902163)],
        [(0.222478, 0.0889078, 0.973663), (0.206606, -0.025235, 0.728104), (0.211569, 0.0104553, 0.662556)],
        [(0.232207, 0.15888, 0.973663), (0.222478, 0.0889078, 0.973663), (0.232207, 0.15888, 0.902163)],
        [(0.211569, 0.0104553, 0.662556), (0.232207, 0.15888, 0.902163), (0.222478, 0.0889078, 0.973663)],
        [(0.165339, 0.096853, 0.973663), (0.148959, -0.0209489, 0.720232), (0.153842, 0.0141721, 0.655729), (0.165339, 0.096853, 0.789205)],
        [(0.165339, 0.096853, 0.973663), (0.148959, -0.0209489, 0.720232), (0.206606, -0.025235, 0.728104), (0.222478, 0.0889078, 0.973663)],
        [(-0.232207, 0.15888, 0.902163), (-0.175068, 0.166825, 0.902163), (-0.175068, 0.166825, 0.973663), (-0.232207, 0.15888, 0.973663)],
        [(-0.175068, 0.166825, 0.973663), (-0.165339, 0.096853, 0.973663), (-0.222478, 0.0889078, 0.973663), (-0.232207, 0.15888, 0.973663)],
        [(-0.206606, -0.025235, 0.728104), (-0.206606, -0.180522, 0.728104), (-0.209127, -0.180873, 0.694807), (-0.211569, 0.0104553, 0.662556)],
        [(-0.153842, 0.0141721, 0.655729), (-0.151455, -0.172853, 0.687256), (-0.148959, -0.172506, 0.720232), (-0.148959, -0.0209489, 0.720232)],
        [(-0.206606, -0.025235, 0.728104), (-0.148959, -0.0209489, 0.720232), (-0.148959, -0.172506, 0.720232), (-0.206606, -0.180522, 0.728104)],
        [(-0.153842, 0.0141721, 0.655729), (-0.151455, -0.172853, 0.687256), (-0.209127, -0.180873, 0.694807), (-0.211569, 0.0104553, 0.662556)],
        [(-0.209127, -0.180873, 0.694807), (-0.151455, -0.172853, 0.687256), (-0.139503, -0.258806, 0.687256), (-0.197175, -0.266825, 0.694807)],
        [(-0.151455, -0.172853, 0.687256), (-0.148959, -0.172506, 0.720232), (-0.137007, -0.258459, 0.720232), (-0.139503, -0.258806, 0.687256)],
        [(-0.148959, -0.172506, 0.720232), (-0.206606, -0.180522, 0.728104), (-0.194654, -0.266475, 0.728104), (-0.137007, -0.258459, 0.720232)],
        [(-0.197175, -0.266825, 0.694807), (-0.194654, -0.266475, 0.728104), (-0.206606, -0.180522, 0.728104), (-0.209127, -0.180873, 0.694807)],
        [(-0.197175, -0.266825, 0.694807), (-0.194654, -0.266475, 0.728104), (-0.137007, -0.258459, 0.720232), (-0.139503, -0.258806, 0.687256)],
        [(-0.232207, 0.15888, 0.902163), (-0.211569, 0.0104553, 0.662556), (-0.153842, 0.0141721, 0.655729), (-0.175068, 0.166825, 0.902163)],
        [(-0.222478, 0.0889078, 0.973663), (-0.206606, -0.025235, 0.728104), (-0.211569, 0.0104553, 0.662556)],
        [(-0.232207, 0.15888, 0.973663), (-0.222478, 0.0889078, 0.973663), (-0.232207, 0.15888, 0.902163)],
        [(-0.211569, 0.0104553, 0.662556), (-0.232207, 0.15888, 0.902163), (-0.222478, 0.0889078, 0.973663)],
        [(-0.153842, 0.0141721, 0.655729), (-0.165339, 0.096853, 0.789205), (-0.165339, 0.096853, 0.973663), (-0.148959, -0.0209489, 0.720232)],
        [(-0.165339, 0.096853, 0.973663), (-0.148959, -0.0209489, 0.720232), (-0.206606, -0.025235, 0.728104), (-0.222478, 0.0889078, 0.973663)],
        [(-0.0495296, 0.284129, 0.973663), (-0.0369027, 0.229597, 1.00290), (0.0369027, 0.229597, 1.00290), (0.0495296, 0.284129, 0.973663)],
        [(0.0564241, 0.229597, 0.994861), (0.0564241, 0.166825, 1.02253), (0.175068, 0.166825, 0.973663)],
        [(0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 0.994861), (0.0495296, 0.284129, 0.973663)],
        [(0.175068, 0.166825, 0.973663), (0.0495296, 0.284129, 0.973663), (0.0564241, 0.229597, 0.994861)],
        [(0.175068, 0.166825, 0.973663), (0.0564241, 0.166825, 1.02253), (0.0564241, 0.131926, 1.02053), (0.165339, 0.096853, 0.973663)],
        [(0.0564241, 0.118717, 1.01150), (0.0223678, 0.118717, 1.01865), (0.0223678, 0.0529662, 0.973663)],
        [(0.0564241, 0.131926, 1.02053), (0.0564241, 0.118717, 1.01150), (0.165339, 0.096853, 0.973663)],
        [(0.0223678, 0.0529662, 0.973663), (0.165339, 0.096853, 0.973663), (0.0564241, 0.118717, 1.01150)],
        [(0.0223678, 0.0529662, 0.973663), (0.0223678, 0.118717, 1.01865), (-0.0223678, 0.118717, 1.01865), (-0.0223678, 0.0529662, 0.973663)],
        [(-0.165339, 0.096853, 0.60115), (-0.0223678, 0.0529662, 0.60115), (-0.0223678, 0.0529662, 0.973663), (-0.165339, 0.096853, 0.973663)],
        [(-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.131926, 1.02053), (-0.165339, 0.096853, 0.973663)],
        [(-0.0223678, 0.118717, 1.01865), (-0.0564241, 0.118717, 1.01150), (-0.0223678, 0.0529662, 0.973663)],
        [(-0.165339, 0.096853, 0.973663), (-0.0223678, 0.0529662, 0.973663), (-0.0564241, 0.118717, 1.01150)],
        [(-0.175068, 0.166825, 0.973663), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.131926, 1.02053), (-0.165339, 0.096853, 0.973663)],
        [(-0.0564241, 0.229597, 0.994861), (-0.0564241, 0.166825, 1.02253), (-0.175068, 0.166825, 0.973663)],
        [(-0.0369027, 0.229597, 1.00290), (-0.0564241, 0.229597, 0.994861), (-0.0495296, 0.284129, 0.973663)],
        [(-0.175068, 0.166825, 0.973663), (-0.0495296, 0.284129, 0.973663), (-0.0564241, 0.229597, 0.994861)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.382764, 0.0715), (0.120896, -0.382764, 0.0715), (0.120896, -0.222765, 0.0715)],
        [(0.0223678, -0.132523, -4.51028e-17), (0.120896, -0.132523, -4.51028e-17), (0.120896, -0.382764, -4.51028e-17), (0.0223678, -0.382764, -4.51028e-17)],
        [(0.120896, -0.132523, 0.0715), (0.120896, -0.132523, -4.51028e-17), (0.0223678, -0.132523, -4.51028e-17), (0.0223678, -0.132523, 0.0715)],
        [(0.0223678, -0.382764, -4.51028e-17), (0.120896, -0.382764, -4.51028e-17), (0.120896, -0.382764, 0.0715), (0.0223678, -0.382764, 0.0715)],
        [(-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.118717, 1.0945), (-0.0223678, 0.118717, 1.01865)],
        [(-0.0564241, 0.118717, 1.0945), (0.0564241, 0.118717, 1.0945), (0.0223678, 0.118717, 1.01865), (-0.0223678, 0.118717, 1.01865)],
        [(0.0564241, 0.118717, 1.01150), (0.0223678, 0.118717, 1.01865), (0.0564241, 0.118717, 1.0945)],
        [(0.0564241, 0.118717, 1.01150), (0.0564241, 0.118717, 1.0945), (0.0564241, 0.131926, 1.02053)],
        [(0.0564241, 0.166825, 1.02253), (0.0564241, 0.131926, 1.02053), (0.0564241, 0.118717, 1.0945)],
        [(0.0564241, 0.229597, 0.994861), (0.0564241, 0.166825, 1.02253), (0.0564241, 0.229597, 1.0945)],
        [(0.0564241, 0.118717, 1.0945), (0.0564241, 0.229597, 1.0945), (0.0564241, 0.166825, 1.02253)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.229597, 0.994861), (-0.0369027, 0.229597, 1.00290)],
        [(-0.0369027, 0.229597, 1.00290), (0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 1.0945), (-0.0564241, 0.229597, 1.0945)],
        [(0.0564241, 0.229597, 1.0945), (0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 0.994861)],
        [(-0.0709703, 0.229597, 1.0945), (0.0709703, 0.229597, 1.0945), (0.0709703, 0.264736, 1.23032), (-0.0709703, 0.264736, 1.23032)],
        [(-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.229597, 1.3112), (0.0709703, 0.229597, 1.3112), (0.0709703, 0.264736, 1.23032)],
        [(0.0709703, 0.264736, 1.23032), (0.0709703, 0.107585, 1.0945), (0.0709703, 0.107585, 1.3112)],
        [(0.0709703, 0.107585, 1.0945), (0.0709703, 0.264736, 1.23032), (0.0709703, 0.229597, 1.0945)],
        [(0.0709703, 0.229597, 1.3112), (0.0709703, 0.264736, 1.23032), (0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.229597, 1.0945)],
        [(-0.0709703, 0.229597, 1.3112), (-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.107585, 1.3112), (-0.0394345, 0.0843967, 1.24231), (0.0394345, 0.0843967, 1.24231), (0.0709703, 0.107585, 1.3112)],
        [(0.0394345, 0.0843967, 1.24231), (0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.24231)],
        [(0.0709703, 0.229597, 1.3112), (0.0709703, 0.107585, 1.3112), (-0.0709703, 0.107585, 1.3112), (-0.0709703, 0.229597, 1.3112)],
        [(-0.0709703, 0.107585, 1.3112), (-0.0394345, 0.0843967, 1.24231), (-0.0394345, 0.0843967, 1.0945), (-0.0709703, 0.107585, 1.0945)],
        [(0.0709703, 0.107585, 1.0945), (0.0394345, 0.0843967, 1.0945), (0.0394345, 0.0843967, 1.24231), (0.0709703, 0.107585, 1.3112)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.118717, 1.0945), (-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.229597, 1.0945)],
        [(-0.0394345, 0.0843967, 1.0945), (-0.0709703, 0.107585, 1.0945), (-0.0564241, 0.118717, 1.0945)],
        [(-0.0564241, 0.118717, 1.0945), (0.0564241, 0.118717, 1.0945), (0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.0945)],
        [(0.0564241, 0.118717, 1.0945), (0.0564241, 0.229597, 1.0945), (0.0709703, 0.229597, 1.0945), (0.0709703, 0.107585, 1.0945)],
        [(0.0709703, 0.107585, 1.0945), (0.0394345, 0.0843967, 1.0945), (0.0564241, 0.118717, 1.0945)],
        [(-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.131926, 1.02053)],
        [(-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.131926, 1.02053)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.229597, 0.994861)],
        [(-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.229597, 1.0945)]]
        
        return seatedData
    
    def getStandingMannequinData(self):
        standingData = [[(0.171916, -0.047394, 1.00065), (0.171916, -0.047394, 1.36994), (0.172486, -0.0875496, 1.06244)],
        [(0.228398, -0.0483948, 1.00065), (0.196123, -0.118413, 0.759271), (0.228968, -0.0885504, 1.06244)],
        [(0.228968, -0.0885504, 1.06244), (0.196885, -0.172085, 0.783852), (0.196123, -0.118413, 0.759271)],
        [(0.197285, -0.200214, 0.687691), (0.174081, -0.199803, 0.687691), (0.173681, -0.171674, 0.783852), (0.196885, -0.172085, 0.783852)],
        [(0.196522, -0.146542, 0.66311), (0.196123, -0.118413, 0.759271), (0.172919, -0.118002, 0.759271), (0.173318, -0.146131, 0.66311)],
        [(0.173681, -0.171674, 0.783852), (0.172919, -0.118002, 0.759271), (0.173318, -0.146131, 0.66311), (0.174081, -0.199803, 0.687691)],
        [(0.174081, -0.199803, 0.687691), (0.173318, -0.146131, 0.66311), (0.196522, -0.146542, 0.66311), (0.197285, -0.200214, 0.687691)],
        [(0.196123, -0.118413, 0.759271), (0.196522, -0.146542, 0.66311), (0.197285, -0.200214, 0.687691), (0.196885, -0.172085, 0.783852)],
        [(0.196123, -0.118413, 0.759271), (0.228398, -0.0483948, 1.00065), (0.171916, -0.047394, 1.00065), (0.172919, -0.118002, 0.759271)],
        [(0.228968, -0.0885504, 1.06244), (0.172486, -0.0875496, 1.06244), (0.173681, -0.171674, 0.783852), (0.196885, -0.172085, 0.783852)],
        [(0.171916, -0.047394, 1.00065), (0.172919, -0.118002, 0.759271), (0.173681, -0.171674, 0.783852), (0.172486, -0.0875496, 1.06244)],
        [(0.228398, -0.0483948, 1.00065), (0.228398, -0.0483948, 1.36994), (0.228968, -0.0885504, 1.06244)],
        [(0.227417, 0.0206151, 1.36994), (0.228398, -0.0483948, 1.36994), (0.227417, 0.0206151, 1.30002)],
        [(0.228398, -0.0483948, 1.36994), (0.227417, 0.0206151, 1.30002), (0.228398, -0.0483948, 1.00065)],
        [(0.171916, -0.047394, 1.36994), (0.228398, -0.0483948, 1.36994), (0.228968, -0.0885504, 1.06244), (0.172486, -0.0875496, 1.06244)],
        [(0.171916, -0.047394, 1.00065), (0.170935, 0.0216159, 1.30002), (0.227417, 0.0206151, 1.30002), (0.228398, -0.0483948, 1.00065)],
        [(0.227417, 0.0206151, 1.36994), (0.170935, 0.0216159, 1.36994), (0.170935, 0.0216159, 1.30002), (0.227417, 0.0206151, 1.30002)],
        [(0.227417, 0.0206151, 1.36994), (0.170935, 0.0216159, 1.36994), (0.171916, -0.047394, 1.36994), (0.228398, -0.0483948, 1.36994)],
        [(0.170935, 0.0216159, 1.36994), (0.170935, 0.0216159, 0.791631), (0.0198005, 0.138854, 0.791631), (0.0198005, 0.138854, 1.36994)],
        [(0.171916, -0.047394, 1.36994), (0.0230087, -0.0869583, 1.36994), (0.0230087, -0.0869583, 0.791631), (0.171916, -0.047394, 0.791631)],
        [(0.170935, 0.0216159, 1.30002), (0.170935, 0.0216159, 0.791631), (0.171916, -0.047394, 0.791631), (0.171916, -0.047394, 1.00065)],
        [(-0.227379, -0.0403189, 1.00065), (-0.193098, -0.111516, 0.759271), (-0.226809, -0.0804746, 1.06244)],
        [(-0.226809, -0.0804746, 1.06244), (-0.192336, -0.165189, 0.783852), (-0.193098, -0.111516, 0.759271)],
        [(-0.191936, -0.193318, 0.687691), (-0.168732, -0.193729, 0.687691), (-0.169132, -0.1656, 0.783852), (-0.192336, -0.165189, 0.783852)],
        [(-0.193098, -0.111516, 0.759271), (-0.169894, -0.111928, 0.759271), (-0.169495, -0.140056, 0.66311), (-0.192698, -0.139645, 0.66311)],
        [(-0.169132, -0.1656, 0.783852), (-0.169894, -0.111928, 0.759271), (-0.169495, -0.140056, 0.66311), (-0.168732, -0.193729, 0.687691)],
        [(-0.168732, -0.193729, 0.687691), (-0.169495, -0.140056, 0.66311), (-0.192698, -0.139645, 0.66311), (-0.191936, -0.193318, 0.687691)],
        [(-0.193098, -0.111516, 0.759271), (-0.192698, -0.139645, 0.66311), (-0.191936, -0.193318, 0.687691), (-0.192336, -0.165189, 0.783852)],
        [(-0.169894, -0.111928, 0.759271), (-0.170897, -0.0413197, 1.00065), (-0.227379, -0.0403189, 1.00065), (-0.193098, -0.111516, 0.759271)],
        [(-0.226809, -0.0804746, 1.06244), (-0.170327, -0.0814754, 1.06244), (-0.169132, -0.1656, 0.783852), (-0.192336, -0.165189, 0.783852)],
        [(-0.169894, -0.111928, 0.759271), (-0.170897, -0.0413197, 1.00065), (-0.170327, -0.0814754, 1.06244), (-0.169132, -0.1656, 0.783852)],
        [(-0.227379, -0.0403189, 1.00065), (-0.227379, -0.0403189, 1.36994), (-0.226809, -0.0804746, 1.06244)],
        [(-0.22836, 0.028691, 1.36994), (-0.227379, -0.0403189, 1.36994), (-0.22836, 0.028691, 1.30002)],
        [(-0.227379, -0.0403189, 1.36994), (-0.22836, 0.028691, 1.30002), (-0.227379, -0.0403189, 1.00065)],
        [(-0.170327, -0.0814754, 1.06244), (-0.170897, -0.0413197, 1.36994), (-0.227379, -0.0403189, 1.36994), (-0.226809, -0.0804746, 1.06244)],
        [(-0.170897, -0.0413197, 1.00065), (-0.171878, 0.0276902, 1.30002), (-0.22836, 0.028691, 1.30002), (-0.227379, -0.0403189, 1.00065)],
        [(-0.22836, 0.028691, 1.36994), (-0.171878, 0.0276902, 1.36994), (-0.171878, 0.0276902, 1.30002), (-0.22836, 0.028691, 1.30002)],
        [(-0.22836, 0.028691, 1.36994), (-0.171878, 0.0276902, 1.36994), (-0.170897, -0.0413197, 1.36994), (-0.227379, -0.0403189, 1.36994)],
        [(-0.170327, -0.0814754, 1.06244), (-0.170897, -0.0413197, 1.36994), (-0.170897, -0.0413197, 1.00065)],
        [(-0.171878, 0.0276902, 1.30002), (-0.171878, 0.0276902, 0.791631), (-0.170897, -0.0413197, 0.791631), (-0.170897, -0.0413197, 1.00065)],
        [(-0.11609, -0.166736, 0.069916), (-0.11831, -0.0104408, 0.069916), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.11831, -0.0104408, 0.069916), (-0.119563, 0.0777126, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.11831, -0.0104408, 0.069916), (-0.119563, 0.0777126, 0.373781), (-0.119563, 0.0777126, -1.43982e-16)],
        [(-0.119563, 0.0777126, 0.373781), (-0.11831, -0.0104408, 0.373781), (-0.11831, -0.0104408, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.118424, -0.0146354, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16), (0.118424, -0.0146354, 0.069916)],
        [(0.118424, -0.0146354, 0.373781), (0.117172, 0.073518, 0.373781), (0.118424, -0.0146354, 0.069916)],
        [(0.118424, -0.0146354, 0.069916), (0.117172, 0.073518, 0.373781), (0.117172, 0.073518, -1.5786e-16)],
        [(-0.119563, 0.0777126, 0.373781), (-0.0230953, 0.0760034, 0.373781), (-0.0230953, 0.0760034, 0.069916), (-0.119563, 0.0777126, 0.069916)],
        [(-0.11831, -0.0104408, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0196224, -0.168445, 0.069916), (-0.11609, -0.166736, 0.069916)],
        [(-0.119563, 0.0777126, -1.43982e-16), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0196224, -0.168445, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.119563, 0.0777126, -1.43982e-16), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0230953, 0.0760034, 0.069916), (-0.119563, 0.0777126, 0.069916)],
        [(-0.11609, -0.166736, 0.069916), (-0.0196224, -0.168445, 0.069916), (-0.0196224, -0.168445, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(0.117172, 0.073518, 0.069916), (0.0207045, 0.0752273, 0.069916), (0.0207045, 0.0752273, 0.373781), (0.117172, 0.073518, 0.373781)],
        [(0.118424, -0.0146354, 0.069916), (0.0219569, -0.0129262, 0.069916), (0.0241775, -0.169221, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.0241775, -0.169221, -1.5786e-16), (0.0207045, 0.0752273, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16)],
        [(0.117172, 0.073518, 0.069916), (0.0207045, 0.0752273, 0.069916), (0.0207045, 0.0752273, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16)],
        [(0.120645, -0.170931, -1.5786e-16), (0.0241775, -0.169221, -1.5786e-16), (0.0241775, -0.169221, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(-0.0196224, -0.168445, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0196224, -0.168445, -1.43982e-16)],
        [(-0.0218429, -0.0121501, 0.069916), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0196224, -0.168445, -1.43982e-16)],
        [(-0.0218429, -0.0121501, 0.373781), (-0.0230953, 0.0760034, 0.373781), (-0.0218429, -0.0121501, 0.069916)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0218429, -0.0121501, 0.069916)],
        [(0.0241775, -0.169221, -1.5786e-16), (0.0219569, -0.0129262, 0.069916), (0.0241775, -0.169221, 0.069916)],
        [(0.0241775, -0.169221, -1.5786e-16), (0.0207045, 0.0752273, -1.5786e-16), (0.0219569, -0.0129262, 0.069916)],
        [(0.0207045, 0.0752273, 0.373781), (0.0219569, -0.0129262, 0.069916), (0.0207045, 0.0752273, -1.5786e-16)],
        [(0.0207045, 0.0752273, 0.373781), (0.0219569, -0.0129262, 0.373781), (0.0219569, -0.0129262, 0.069916)],
        [(-0.11831, -0.0104408, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0218429, -0.0121501, 0.373781), (-0.11831, -0.0104408, 0.373781)],
        [(0.118424, -0.0146354, 0.373781), (0.0219569, -0.0129262, 0.373781), (0.0219569, -0.0129262, 0.069916), (0.118424, -0.0146354, 0.069916)],
        [(-0.037937, -0.0551831, 1.4881), (-0.0550476, -0.0213627, 1.4881), (-0.069135, -0.0319849, 1.4881)],
        [(-0.0708283, 0.0872035, 1.4881), (-0.0550476, -0.0213627, 1.4881), (-0.0565864, 0.0869511, 1.4881)],
        [(-0.069135, -0.0319849, 1.4881), (-0.0708283, 0.0872035, 1.4881), (-0.0550476, -0.0213627, 1.4881)],
        [(-0.037937, -0.0551831, 1.4881), (0.0554401, -0.0233204, 1.4881), (-0.0550476, -0.0213627, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0554401, -0.0233204, 1.4881), (0.0392822, -0.0565513, 1.4881)],
        [(0.0539013, 0.0849934, 1.4881), (0.0554401, -0.0233204, 1.4881), (0.0681432, 0.084741, 1.4881)],
        [(0.0554401, -0.0233204, 1.4881), (0.0681432, 0.084741, 1.4881), (0.0698365, -0.0344473, 1.4881)],
        [(0.0392822, -0.0565513, 1.4881), (-0.037937, -0.0551831, 1.4881), (0.0554401, -0.0233204, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0698365, -0.0344473, 1.7), (0.0392822, -0.0565513, 1.63263), (0.0392822, -0.0565513, 1.4881)],
        [(-0.037937, -0.0551831, 1.4881), (-0.037937, -0.0551831, 1.63263), (-0.069135, -0.0319849, 1.7), (-0.069135, -0.0319849, 1.4881)],
        [(-0.0708283, 0.0872035, 1.7), (-0.069135, -0.0319849, 1.7), (0.0698365, -0.0344473, 1.7), (0.0681432, 0.084741, 1.7)],
        [(0.0392822, -0.0565513, 1.63263), (-0.037937, -0.0551831, 1.63263), (-0.037937, -0.0551831, 1.4881), (0.0392822, -0.0565513, 1.4881)],
        [(0.0392822, -0.0565513, 1.63263), (-0.037937, -0.0551831, 1.63263), (-0.069135, -0.0319849, 1.7), (0.0698365, -0.0344473, 1.7)],
        [(-0.069135, -0.0319849, 1.7), (-0.071316, 0.12153, 1.62091), (-0.069135, -0.0319849, 1.4881)],
        [(-0.069135, -0.0319849, 1.4881), (-0.0708283, 0.0872035, 1.4881), (-0.071316, 0.12153, 1.62091)],
        [(-0.071316, 0.12153, 1.62091), (-0.0708283, 0.0872035, 1.7), (-0.069135, -0.0319849, 1.7)],
        [(0.0698365, -0.0344473, 1.7), (0.0676555, 0.119067, 1.62091), (0.0698365, -0.0344473, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0681432, 0.084741, 1.4881), (0.0676555, 0.119067, 1.62091)],
        [(0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.7), (0.0698365, -0.0344473, 1.7)],
        [(-0.0708283, 0.0872035, 1.7), (-0.071316, 0.12153, 1.62091), (0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.7)],
        [(-0.0708283, 0.0872035, 1.4881), (-0.071316, 0.12153, 1.62091), (0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0217036, -0.0219535, 1.41393), (-0.0550476, -0.0213627, 1.40694)],
        [(-0.0217036, -0.0219535, 1.41393), (0.0220962, -0.0227296, 1.41393), (-0.0550476, -0.0213627, 1.4881)],
        [(0.0554401, -0.0233204, 1.40694), (0.0220962, -0.0227296, 1.41393), (0.0554401, -0.0233204, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (0.0220962, -0.0227296, 1.41393), (0.0554401, -0.0233204, 1.4881)],
        [(0.0220962, -0.0227296, 1.41393), (0.0230087, -0.0869583, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0217036, -0.0219535, 1.41393)],
        [(0.0230087, -0.0869583, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0207911, -0.0861823, 0.791631), (0.0230087, -0.0869583, 0.791631)],
        [(-0.170897, -0.0413197, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0207911, -0.0861823, 0.791631), (-0.170897, -0.0413197, 0.791631)],
        [(-0.0550476, -0.0213627, 1.40694), (-0.0207911, -0.0861823, 1.36994), (-0.0217036, -0.0219535, 1.41393)],
        [(-0.0550476, -0.0213627, 1.40694), (-0.170897, -0.0413197, 1.36994), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.0207911, -0.0861823, 1.36994), (-0.0550476, -0.0213627, 1.40694), (-0.170897, -0.0413197, 1.36994)],
        [(0.0554401, -0.0233204, 1.40694), (0.0230087, -0.0869583, 1.36994), (0.0220962, -0.0227296, 1.41393)],
        [(0.0552568, -0.0104165, 1.41577), (0.0554401, -0.0233204, 1.40694), (0.171916, -0.047394, 1.36994)],
        [(0.0230087, -0.0869583, 1.36994), (0.0554401, -0.0233204, 1.40694), (0.171916, -0.047394, 1.36994)],
        [(0.0198005, 0.138854, 1.36994), (-0.0239993, 0.13963, 1.36994), (-0.0239993, 0.13963, 0.791631), (0.0198005, 0.138854, 0.791631)],
        [(-0.171878, 0.0276902, 1.36994), (-0.171878, 0.0276902, 0.791631), (-0.0239993, 0.13963, 0.791631), (-0.0239993, 0.13963, 1.36994)],
        [(-0.0565864, 0.0869511, 1.4881), (-0.0565864, 0.0869511, 1.39853), (0.0539013, 0.0849934, 1.39853), (0.0539013, 0.0849934, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0552309, -0.00845877, 1.41577), (-0.0550476, -0.0213627, 1.40694)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0557152, 0.0256319, 1.41773), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.0565864, 0.0869511, 1.39853), (-0.0557152, 0.0256319, 1.41773), (-0.0565864, 0.0869511, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0565864, 0.0869511, 1.4881), (-0.0557152, 0.0256319, 1.41773)],
        [(-0.0239993, 0.13963, 1.36994), (-0.0565864, 0.0869511, 1.39853), (0.0539013, 0.0849934, 1.39853), (0.0198005, 0.138854, 1.36994)],
        [(-0.170897, -0.0413197, 0.791631), (-0.11831, -0.0104408, 0.373781), (-0.119563, 0.0777126, 0.373781), (-0.171878, 0.0276902, 0.791631)],
        [(-0.170897, -0.0413197, 0.791631), (-0.11831, -0.0104408, 0.373781), (-0.0207911, -0.0861823, 0.791631)],
        [(-0.11831, -0.0104408, 0.373781), (-0.0207911, -0.0861823, 0.791631), (-0.0218429, -0.0121501, 0.373781)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0239993, 0.13963, 0.791631), (-0.119563, 0.0777126, 0.373781)],
        [(-0.0239993, 0.13963, 0.791631), (-0.119563, 0.0777126, 0.373781), (-0.171878, 0.0276902, 0.791631)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0239993, 0.13963, 0.791631), (-0.0207911, -0.0861823, 0.791631), (-0.0218429, -0.0121501, 0.373781)],
        [(0.171916, -0.047394, 0.791631), (0.118424, -0.0146354, 0.373781), (0.117172, 0.073518, 0.373781), (0.170935, 0.0216159, 0.791631)],
        [(0.171916, -0.047394, 0.791631), (0.118424, -0.0146354, 0.373781), (0.0230087, -0.0869583, 0.791631)],
        [(0.118424, -0.0146354, 0.373781), (0.0230087, -0.0869583, 0.791631), (0.0219569, -0.0129262, 0.373781)],
        [(0.0207045, 0.0752273, 0.373781), (0.0198005, 0.138854, 0.791631), (0.117172, 0.073518, 0.373781)],
        [(0.0198005, 0.138854, 0.791631), (0.117172, 0.073518, 0.373781), (0.170935, 0.0216159, 0.791631)],
        [(0.0207045, 0.0752273, 0.373781), (0.0198005, 0.138854, 0.791631), (0.0230087, -0.0869583, 0.791631), (0.0219569, -0.0129262, 0.373781)],
        [(0.0230087, -0.0869583, 0.791631), (0.0198005, 0.138854, 0.791631), (-0.0239993, 0.13963, 0.791631), (-0.0207911, -0.0861823, 0.791631)],
        [(-0.0565864, 0.0869511, 1.39853), (-0.171878, 0.0276902, 1.36994), (-0.0557152, 0.0256319, 1.41773)],
        [(-0.0239993, 0.13963, 1.36994), (-0.0565864, 0.0869511, 1.39853), (-0.171878, 0.0276902, 1.36994)],
        [(0.0539013, 0.0849934, 1.39853), (0.170935, 0.0216159, 1.36994), (0.0547724, 0.0236742, 1.41773)],
        [(0.0198005, 0.138854, 1.36994), (0.0539013, 0.0849934, 1.39853), (0.170935, 0.0216159, 1.36994)],
        [(0.0554401, -0.0233204, 1.40694), (0.0552568, -0.0104165, 1.41577), (0.0554401, -0.0233204, 1.4881)],
        [(0.0552568, -0.0104165, 1.41577), (0.0547724, 0.0236742, 1.41773), (0.0554401, -0.0233204, 1.4881)],
        [(0.0539013, 0.0849934, 1.4881), (0.0547724, 0.0236742, 1.41773), (0.0539013, 0.0849934, 1.39853)],
        [(0.0547724, 0.0236742, 1.41773), (0.0539013, 0.0849934, 1.4881), (0.0554401, -0.0233204, 1.4881)],
        [(-0.170897, -0.0413197, 1.36994), (-0.0557152, 0.0256319, 1.41773), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.171878, 0.0276902, 1.36994), (-0.0557152, 0.0256319, 1.41773), (-0.170897, -0.0413197, 1.36994)],
        [(0.0552568, -0.0104165, 1.41577), (0.0547724, 0.0236742, 1.41773), (0.171916, -0.047394, 1.36994)],
        [(0.170935, 0.0216159, 1.36994), (0.0547724, 0.0236742, 1.41773), (0.171916, -0.047394, 1.36994)]]
        
        return standingData
    
    def getSeatedMannequinSimple(self):
        seatedData = [[(-0.0709703, 0.229597, 1.01605), (0.0709703, 0.229597, 1.01605), (0.0709703, 0.284129, 1.01605), (-0.0709703, 0.284129, 1.01605)],
        [(-0.0709703, 0.107585, 1.01605), (-0.0709703, 0.0529662, 1.01605), (0.0709703, 0.0529662, 1.01605), (0.0709703, 0.107585, 1.01605)],
        [(0.0709703, 0.284129, 1.01605), (0.0709703, 0.0529662, 1.01605), (0.175068, 0.0529662, 1.01605), (0.175068, 0.284129, 1.01605)],
        [(-0.0709703, 0.284129, 1.01605), (-0.175068, 0.284129, 1.01605), (-0.175068, 0.0529662, 1.01605), (-0.0709703, 0.0529662, 1.01605)],
        [(-0.175068, -0.132523, -1.85037e-17), (0.175068, -0.132523, -1.85037e-17), (0.175068, -0.132523, 0.38225), (-0.175068, -0.132523, 0.38225)],
        [(0.175068, 0.284129, 1.01605), (-0.175068, 0.284129, 1.01605), (-0.175068, 0.284129, 0.38225), (0.175068, 0.284129, 0.38225)],
        [(-0.0709703, 0.107585, 1.3112), (0.0709703, 0.107585, 1.3112), (0.0709703, 0.229597, 1.3112), (-0.0709703, 0.229597, 1.3112)],
        [(-0.0709703, 0.107585, 1.01605), (-0.0709703, 0.107585, 1.3112), (0.0709703, 0.107585, 1.3112), (0.0709703, 0.107585, 1.01605)],
        [(0.0709703, 0.229597, 1.3112), (0.0709703, 0.229597, 1.01605), (0.0709703, 0.107585, 1.01605), (0.0709703, 0.107585, 1.3112)],
        [(0.0709703, 0.229597, 1.01605), (0.0709703, 0.229597, 1.3112), (-0.0709703, 0.229597, 1.3112), (-0.0709703, 0.229597, 1.01605)],
        [(-0.0709703, 0.107585, 1.3112), (-0.0709703, 0.107585, 1.01605), (-0.0709703, 0.229597, 1.01605), (-0.0709703, 0.229597, 1.3112)],
        [(-0.175068, -0.222765, 0.60115), (0.175068, -0.222765, 0.60115), (0.175068, 0.0529662, 0.60115), (-0.175068, 0.0529662, 0.60115)],
        [(0.175068, -0.222765, 0.60115), (0.175068, -0.222765, 0.0715), (-0.175068, -0.222765, 0.0715), (-0.175068, -0.222765, 0.60115)],
        [(0.175068, -0.222765, 0.0715), (0.175068, -0.382764, 0.0715), (-0.175068, -0.382764, 0.0715), (-0.175068, -0.222765, 0.0715)],
        [(0.175068, -0.132523, 0.38225), (0.175068, 0.284129, 0.38225), (-0.175068, 0.284129, 0.38225), (-0.175068, -0.132523, 0.38225)],
        [(0.175068, -0.132523, -1.85037e-17), (0.175068, -0.382764, 0.0), (-0.175068, -0.382764, 0.0), (-0.175068, -0.132523, -1.85037e-17)],
        [(-0.175068, -0.382764, 0.0715), (-0.175068, -0.382764, 0.0), (0.175068, -0.382764, 0.0), (0.175068, -0.382764, 0.0715)],
        [(-0.175068, 0.0529662, 1.01605), (0.175068, 0.0529662, 1.01605), (0.175068, 0.0529662, 0.60115), (-0.175068, 0.0529662, 0.60115)],
        [(0.175068, -0.382764, 0.0715), (0.175068, -0.382764, 0.0), (0.175068, -0.222765, -1.38778e-17), (0.175068, -0.222765, 0.0715)],
        [(0.175068, -0.132523, -1.85037e-17), (0.175068, -0.222765, -1.38778e-17), (0.175068, -0.222765, 0.38225), (0.175068, -0.132523, 0.38225)],
        [(0.175068, 0.284129, 0.60115), (0.175068, -0.222765, 0.60115), (0.175068, -0.222765, 0.38225), (0.175068, 0.284129, 0.38225)],
        [(0.175068, 0.0529662, 1.01605), (0.175068, 0.0529662, 0.60115), (0.175068, 0.284129, 0.60115), (0.175068, 0.284129, 1.01605)],
        [(-0.175068, -0.382764, 0.0715), (-0.175068, -0.382764, 0.0), (-0.175068, -0.222765, -1.38778e-17), (-0.175068, -0.222765, 0.0715)],
        [(-0.175068, -0.132523, -1.85037e-17), (-0.175068, -0.222765, -1.38778e-17), (-0.175068, -0.222765, 0.38225), (-0.175068, -0.132523, 0.38225)],
        [(-0.175068, 0.284129, 0.60115), (-0.175068, -0.222765, 0.60115), (-0.175068, -0.222765, 0.38225), (-0.175068, 0.284129, 0.38225)],
        [(-0.175068, 0.0529662, 1.01605), (-0.175068, 0.0529662, 0.60115), (-0.175068, 0.284129, 0.60115), (-0.175068, 0.284129, 1.01605)]]
        
        return seatedData
    
    def getStandingMannequinSimple(self):
        standingData = [[(0.0629122, 0.0872035, 1.39853), (0.0629122, 0.111924, 1.39853), (-0.0721542, 0.111924, 1.39853), (-0.0721542, 0.0872035, 1.39853)],
        [(-0.0721542, 0.111924, 1.39853), (-0.175068, 0.111924, 1.39853), (-0.175068, -0.0816051, 1.39853), (-0.0721542, -0.0816051, 1.39853)],
        [(-0.0721542, -0.0542619, 1.39853), (-0.0721542, -0.0816051, 1.39853), (0.0629122, -0.0816051, 1.39853), (0.0629122, -0.0542619, 1.39853)],
        [(0.0629122, 0.111924, 1.39853), (0.0629122, -0.0816051, 1.39853), (0.175068, -0.0816051, 1.39853), (0.175068, 0.111924, 1.39853)],
        [(0.175068, 0.111924, 1.39853), (-0.175068, 0.111924, 1.39853), (-0.175068, 0.111924, 1.38778e-17), (0.175068, 0.111924, 1.38778e-17)],
        [(-0.0721542, -0.0542619, 1.7), (0.0629122, -0.0542619, 1.7), (0.0629122, 0.0872035, 1.7), (-0.0721542, 0.0872035, 1.7)],
        [(-0.0721542, -0.0542619, 1.39853), (-0.0721542, -0.0542619, 1.7), (0.0629122, -0.0542619, 1.7), (0.0629122, -0.0542619, 1.39853)],
        [(0.0629122, 0.0872035, 1.7), (0.0629122, 0.0872035, 1.39853), (0.0629122, -0.0542619, 1.39853), (0.0629122, -0.0542619, 1.7)],
        [(0.0629122, 0.0872035, 1.39853), (0.0629122, 0.0872035, 1.7), (-0.0721542, 0.0872035, 1.7), (-0.0721542, 0.0872035, 1.39853)],
        [(-0.0721542, -0.0542619, 1.7), (-0.0721542, -0.0542619, 1.39853), (-0.0721542, 0.0872035, 1.39853), (-0.0721542, 0.0872035, 1.7)],
        [(-0.175068, -0.0816051, 0.069916), (0.175068, -0.0816051, 0.069916), (0.175068, -0.170931, 0.069916), (-0.175068, -0.170931, 0.069916)],
        [(0.175068, 0.111924, 1.38778e-17), (0.175068, -0.170931, 0.0), (-0.175068, -0.170931, 0.0), (-0.175068, 0.111924, 1.38778e-17)],
        [(-0.175068, -0.170931, 0.069916), (-0.175068, -0.170931, 0.0), (0.175068, -0.170931, 0.0), (0.175068, -0.170931, 0.069916)],
        [(0.175068, -0.0816051, 0.069916), (0.175068, -0.0816051, 0.734223), (-0.175068, -0.0816051, 0.734223), (-0.175068, -0.0816051, 0.069916)],
        [(-0.175068, -0.0816051, 1.39853), (0.175068, -0.0816051, 1.39853), (0.175068, -0.0816051, 0.734223), (-0.175068, -0.0816051, 0.734223)],
        [(0.175068, -0.170931, 0.069916), (0.175068, -0.170931, 0.0), (0.175068, -0.0816051, 1.38778e-17), (0.175068, -0.0816051, 0.069916)],
        [(0.175068, 0.111924, 0.734223), (0.175068, -0.0816051, 0.734223), (0.175068, -0.0816051, 1.38778e-17), (0.175068, 0.111924, 1.38778e-17)],
        [(0.175068, -0.0816051, 1.39853), (0.175068, -0.0816051, 0.734223), (0.175068, 0.111924, 0.734223), (0.175068, 0.111924, 1.39853)],
        [(-0.175068, -0.0816051, 1.39853), (-0.175068, -0.0816051, 0.734223), (-0.175068, 0.111924, 0.734223), (-0.175068, 0.111924, 1.39853)],
        [(-0.175068, 0.111924, 0.734223), (-0.175068, -0.0816051, 0.734223), (-0.175068, -0.0816051, 1.38778e-17), (-0.175068, 0.111924, 1.38778e-17)],
        [(-0.175068, -0.170931, 0.069916), (-0.175068, -0.170931, 0.0), (-0.175068, -0.0816051, 1.38778e-17), (-0.175068, -0.0816051, 0.069916)]]
        
        return standingData
    
    
    def splineSit(self, az, alt):
        spline_sit = [[0.3633120000000002, 0.3710234325333335, 0.37785920426666686, 0.3838607835428574, 0.3890696387047621, 0.3935272380952383, 0.3972750500571431, 0.40035454293333356, 0.40280718506666674, 0.40467444480000014, 0.40599779047619067, 0.40681869043809543, 0.4071786130285716, 0.4071190265904764, 0.4066813994666668, 0.4059072000000002, 0.4048378965333334, 0.40351495740952387, 0.4019798509714287, 0.4002740455619049, 0.39843900952380956, 0.3965162112, 0.3945471189333334, 0.39257320106666665, 0.39063592594285723, 0.388776761904762, 0.3870371772952382, 0.3854586404571429, 0.38408261973333346, 0.3829505834666667, 0.382104, 0.3815688533333333, 0.38130919009523817, 0.38127357257142863, 0.38141056304761906, 0.38166872380952377, 0.3819966171428572, 0.38234280533333337, 0.38265585066666674, 0.3828843154285715, 0.38297676190476193, 0.38288175238095246, 0.3825478491428573, 0.3819236144761906, 0.3809576106666667, 0.3795984000000001, 0.3778097109333334, 0.37561593660952397, 0.37305663634285724, 0.3701713694476191, 0.36699969523809534, 0.36358117302857146, 0.3599553621333334, 0.3561618218666668, 0.3522401115428573, 0.3482297904761905, 0.3441704179809525, 0.3401015533714287, 0.33606275596190494, 0.3320935850666667, 0.32823360000000007, 0.3245135573333335, 0.3209290026666667, 0.31746667885714297, 0.31411332876190484, 0.31085569523809536, 0.30768052114285727, 0.30457454933333333, 0.30152452266666674, 0.29851718400000005, 0.29553927619047626, 0.2925775420952382, 0.2896187245714286, 0.28664956647619055, 0.2836568106666667, 0.2806272000000001, 0.2775474773333334, 0.27440438552380964, 0.2711846674285715, 0.26787506590476196, 0.26446232380952384, 0.26093318400000004, 0.25727438933333335, 0.25347268266666667, 0.2495148068571429, 0.2453875047619048, 0.24107751923809528, 0.2365715931428572, 0.23185646933333334, 0.22691889066666665, 0.2217456],
        [0.3635516686308318, 0.3713916538667092, 0.37833067218338234, 0.3844113499702241, 0.3896763136166074, 0.39416818951190524, 0.3979296040454903, 0.40100318360673604, 0.40343155458501495, 0.40525734336970004, 0.4065231763501645, 0.407271679915781, 0.40754548045592237, 0.407387204359962, 0.4068394780172725, 0.40594492781722685, 0.4047461801491979, 0.40328586140255873, 0.40160659796668224, 0.3997510162309412, 0.39776174258470903, 0.395681403417358, 0.3935526251182618, 0.39141803407679243, 0.38932025668232373, 0.3873019193242281, 0.3854056483918785, 0.3836740702746482, 0.3821498113619099, 0.38087549804303633, 0.3798937567074009, 0.37923177058093294, 0.3788549502357898, 0.37871326308068465, 0.3787566765243321, 0.37893515797544536, 0.37919867484273856, 0.3794971945349253, 0.3797806844607193, 0.37999911202883435, 0.3801024446479848, 0.38004064972688373, 0.37976369467424526, 0.3792215468987832, 0.37836417380921117, 0.3771415428142431, 0.37551789478282177, 0.3735145644248065, 0.371167159910285, 0.36851128940934574, 0.3655825610920767, 0.36241658312856617, 0.35904896368890216, 0.3555153109431727, 0.35185123306146604, 0.3480923382138703, 0.3442742345704738, 0.3404325303013645, 0.3366028335766304, 0.3328207525663597, 0.3291218954406409, 0.32553402865802006, 0.3220535518308777, 0.3186690228600522, 0.31536899964638243, 0.3121420400907071, 0.30897670209386446, 0.30586154355669365, 0.30278512238003313, 0.2997359964647212, 0.2967027237115971, 0.29367386202149887, 0.2906379692952655, 0.28758360343373573, 0.284499322337748, 0.28137368390814105, 0.27819524604575346, 0.2749525666514238, 0.27163420362599083, 0.26822871487029315, 0.26472465828516945, 0.2611105917714582, 0.25737507322999825, 0.2535066605616283, 0.24949391166718665, 0.24532538444751228, 0.24098963680344368, 0.23647522663581952, 0.2317707118454784, 0.22686465033325895, 0.2217456],
        [0.36379128664838806, 0.37175420486260496, 0.3787926457872141, 0.3849502995879878, 0.39027085643069814, 0.394798006481117, 0.3985754399050171, 0.40164684686817015, 0.4040559175363485, 0.40584634207532405, 0.40706181065086944, 0.40774601342875655, 0.4079426405747574, 0.4076953822546444, 0.4070479286341897, 0.4060439698791653, 0.40472719615534314, 0.4031412976284961, 0.40132996446439584, 0.39933688682881446, 0.39720575488752424, 0.39498025880629745, 0.39270408875090596, 0.3904209348871223, 0.38817448738071836, 0.38600843639746657, 0.3839664721031387, 0.38209228466350714, 0.3804295642443441, 0.37902200101142164, 0.37791328513051187, 0.377131710567987, 0.37664398649261904, 0.3764014258737796, 0.3763553416808408, 0.37645704688317416, 0.3766578544501519, 0.37690907735114565, 0.3771620285555274, 0.3773680210326688, 0.37747836775194205, 0.37744438168271865, 0.37721737579437076, 0.37674866305627025, 0.37598955643778853, 0.374891368908298, 0.37341884554970356, 0.3715904598940439, 0.36943811758589035, 0.36699372426981525, 0.3642891855903905, 0.36135640719218753, 0.3582272947197785, 0.3549337538177349, 0.35150769013062866, 0.34798100930303194, 0.34438561697951625, 0.34075341880465354, 0.3371163204230154, 0.3335062274791738, 0.3299550456177007, 0.3264877427187179, 0.32310153560454674, 0.3197867033330592, 0.3165335249621265, 0.31333227954962034, 0.3101732461534123, 0.30704670383137406, 0.3039429316413772, 0.30085220864129325, 0.29776481388899384, 0.29467102644235055, 0.291561125359235, 0.28842538969751863, 0.28525409851507305, 0.2820375308697701, 0.27876596581948115, 0.2754296824220778, 0.2720189597354317, 0.26852407681741447, 0.2649353127258976, 0.26124294651875274, 0.2574372572538513, 0.25350852398906515, 0.24944702578226569, 0.2452430416913247, 0.24088685077411354, 0.23636873208850395, 0.2316789646923674, 0.22680782764357552, 0.2217456],
        [0.3640284713821885, 0.37210901742512636, 0.3792432870376541, 0.3854759446368346, 0.39085165463973115, 0.3954150814634067, 0.3992108895249247, 0.4022837432413479, 0.4046783070297398, 0.40643924530716347, 0.40761122249068216, 0.4082389029973585, 0.40836695124425615, 0.4080400316484381, 0.4073028086269675, 0.4061999465969074, 0.4047761099753209, 0.40307596317927147, 0.4011441706258218, 0.39902539673203546, 0.39676430591497536, 0.39440556259170473, 0.3919938311792866, 0.38957377609478416, 0.3871900617552606, 0.384887352577779, 0.3827103129794026, 0.3807036073771945, 0.3789119001882177, 0.3773798558295354, 0.376152138718211, 0.37525806880345514, 0.37466558816307144, 0.3743272944070103, 0.37419578514522295, 0.37422365798766033, 0.37436351054427336, 0.3745679404250133, 0.37478954523983044, 0.37498092259867644, 0.375094670111502, 0.3750833853882578, 0.3748996660388955, 0.37449610967336555, 0.3738253139016188, 0.37283987633360666, 0.3715050361615932, 0.3698365989070961, 0.36786301167394636, 0.3656127215659749, 0.36311417568701276, 0.36039582114089097, 0.3574861050314405, 0.3544134744624923, 0.3512063765378774, 0.3478932583614266, 0.34450256703697096, 0.341062749668342, 0.33760225335936994, 0.3341495252138859, 0.3307330123357215, 0.32737507183758485, 0.32407370086769716, 0.32082080658315676, 0.317608296141062, 0.31442807669851186, 0.31127205541260466, 0.30813213944043893, 0.30500023593911363, 0.30186825206572665, 0.29872809497737723, 0.2955716718311636, 0.29239088978418415, 0.28917765599353784, 0.28592387761632293, 0.2826214618096382, 0.279262315730582, 0.2758383465362532, 0.2723414613837501, 0.2687635674301712, 0.2650965718326152, 0.2613323817481808, 0.2574629043339663, 0.25348004674707053, 0.24937571614459197, 0.245141819683629, 0.24077026452128036, 0.23625295781464464, 0.23158180672082024, 0.22674871839690586, 0.22174560000000001],
        [0.36426084016175264, 0.3724540234583791, 0.37968075789419353, 0.38598659735745017, 0.3914170957364031, 0.39601780691930644, 0.3998342847944143, 0.40291208324998157, 0.4052967561742617, 0.40703385745550924, 0.4081689409819785, 0.40874756064192347, 0.40881527032359827, 0.40841762391525754, 0.4076001753051551, 0.40640847838154515, 0.40488808703268236, 0.40308455514682034, 0.4010434366122137, 0.3988102853171165, 0.39643065514978304, 0.39395009999846725, 0.3914141737514237, 0.3888684302969063, 0.3863584235231697, 0.3839297073184677, 0.3816278355710546, 0.37949836216918476, 0.37758684100111223, 0.37593882595509115, 0.37459987091937585, 0.37360024079629706, 0.372909044544492, 0.37248010213667415, 0.3722672335455568, 0.37222425874385423, 0.3723049977042795, 0.3724632703995463, 0.37265289680236824, 0.37282769688545914, 0.3729414906215325, 0.37294809798330175, 0.3728013389434807, 0.3724550334747829, 0.3718630015499217, 0.3709790631416111, 0.3697689395461055, 0.3682459573538239, 0.3664353444787258, 0.3643623288347711, 0.3620521383359198, 0.3595300008961315, 0.3568211444293662, 0.35395079684958336, 0.3509441860707433, 0.34782654000680535, 0.3446230865717295, 0.341359053679476, 0.33805966924400377, 0.33475016117927325, 0.33145575739924404, 0.32819638833677894, 0.3249707945003513, 0.32177241891733777, 0.31859470461511463, 0.31543109462105856, 0.31227503196254586, 0.3091199596669528, 0.30595932076165616, 0.3027865582740321, 0.29959511523145743, 0.2963784346613082, 0.29312995959096094, 0.28984313304779225, 0.28651139805917836, 0.28312819765249586, 0.2796869748551213, 0.27618117269443077, 0.27260423419780094, 0.2689496023926081, 0.2652107203062291, 0.26138103096603993, 0.2574539773994171, 0.25342300263373735, 0.2492815496963769, 0.245023061614712, 0.2406409814161195, 0.23612875212797554, 0.23147981677765664, 0.22668761839253934, 0.22174559999999996],
        [0.36448601031660033, 0.372787154866469, 0.3801032203163244, 0.3864805699905205, 0.3919655672134106, 0.39660457530934856, 0.400443957602688, 0.4035300774177828, 0.4059092980789863, 0.40762798291065244, 0.4087324952371351, 0.4092691983827877, 0.40928445567196364, 0.4088246304290172, 0.4079360859783017, 0.4066651856441708, 0.4050582927509785, 0.40316177062307823, 0.4010219825848238, 0.3986852919605688, 0.3961980620746671, 0.3936066562514721, 0.39095743781533765, 0.3882967700906174, 0.3856710164016652, 0.38312654007283453, 0.3807097044284793, 0.3784668727929528, 0.376444408490609, 0.37468867484580165, 0.37324603518288446, 0.37214762205547225, 0.3713636449342262, 0.37084908251906823, 0.3705589135099208, 0.370448116606706, 0.3704716705093463, 0.3705845539177637, 0.3707417455318807, 0.3708982240516193, 0.3710089681769021, 0.37102895660765084, 0.37091316804378816, 0.3706165811852362, 0.3700941747319172, 0.36930092738375336, 0.3682030286308554, 0.3668115111240874, 0.36514861830450185, 0.363236593613151, 0.3610976804910878, 0.3587541223793645, 0.35622816271903357, 0.3535420449511474, 0.3507180125167586, 0.34777830885691985, 0.34474517741268323, 0.3416408616251016, 0.33848760493522717, 0.3353076507841127, 0.33212324261281045, 0.32895206453845793, 0.3257935633825323, 0.3226426266425955, 0.31949414181620994, 0.31634299640093744, 0.31318407789434005, 0.31001227379398, 0.30682247159741954, 0.3036095588022205, 0.3003684229059451, 0.2970939514061552, 0.2937810318004131, 0.29042455158628094, 0.2870193982613205, 0.2835604593230942, 0.28004262226916404, 0.27646077459709206, 0.2728098038044402, 0.26908459738877094, 0.2652800428476459, 0.2613910276786275, 0.2574124393792776, 0.25333916544715857, 0.2491660933798323, 0.24488811067486083, 0.24050010482980644, 0.23599696334223103, 0.23137357370969677, 0.22662482342976567, 0.22174559999999996],
        [0.3647015991762512, 0.37310634355350175, 0.3805088362635386, 0.3869561747767318, 0.3924954565634508, 0.39717377909406604, 0.401038239838947, 0.40413593626846384, 0.4065139658529863, 0.4082194260628845, 0.40929941436852835, 0.4098010282402875, 0.40977136514853185, 0.40925752256363174, 0.40830659795595636, 0.4069656887958764, 0.4052818925537612, 0.4033023066999809, 0.4010740287049054, 0.39864415603890446, 0.3960597861723481, 0.3933680165756062, 0.39061594471904876, 0.38785066807304547, 0.3851192841079665, 0.3824688902941816, 0.37994658410206056, 0.3775994630019735, 0.3754746244642902, 0.37361916595938055, 0.3720801849576146, 0.3708896080899403, 0.37001867862961907, 0.3694234690104899, 0.36906005166639244, 0.3688844990311661, 0.3688528835386503, 0.3689212776226842, 0.36904575371710724, 0.36918238425575906, 0.3692872416724786, 0.36931639840110575, 0.3692259268754795, 0.3689718995294396, 0.3685103887968251, 0.3677974671114755, 0.3667997763434575, 0.36552623610774715, 0.36399633545554744, 0.36222956343806173, 0.3602454091064932, 0.3580633615120452, 0.3557029097059206, 0.35318354273932295, 0.3505247496634555, 0.3477460195295211, 0.34486684138872326, 0.34190670429226533, 0.3388850972913503, 0.3358215094371813, 0.3327354297809619, 0.32964247276477987, 0.32654275439426284, 0.3234325160659231, 0.32030799917627306, 0.31716544512182526, 0.3140010952990918, 0.3108111911045853, 0.3075919739348181, 0.3043396851863023, 0.30105056625555043, 0.29772085853907515, 0.2943468034333884, 0.29092464233500276, 0.2874506166404305, 0.2839209677461842, 0.2803319370487759, 0.2766797659447184, 0.27296069583052374, 0.2691709681027044, 0.2653068241577726, 0.26136450539224093, 0.2573402532026217, 0.25323030898542737, 0.24903091413717013, 0.2447383100543624, 0.24034873813351662, 0.23585843977114515, 0.23126365636376017, 0.22656062930787438, 0.22174559999999996],
        [0.36490522407022485, 0.3734095214235831, 0.3808957676953275, 0.3874117239567694, 0.39300515127922014, 0.3977238107339907, 0.4016154633923925, 0.40472787032573676, 0.4071087926053342, 0.40880599130249623, 0.4098672274885345, 0.4103402622347595, 0.4102728566124828, 0.4097127716930155, 0.4087077685476686, 0.4073056082477537, 0.4055540518645816, 0.4035008604694636, 0.40119379513371095, 0.3986806169286349, 0.39600908692554637, 0.3932269661957568, 0.3903820158105772, 0.3875219968413188, 0.38469467035929295, 0.3819477974358106, 0.3793291391421829, 0.37688645654972136, 0.374667510729737, 0.3727200627535407, 0.37109187369244406, 0.3698155944086608, 0.36886343492801577, 0.36819249506723645, 0.3677598746430501, 0.36752267347218465, 0.3674379913713675, 0.3674629281573259, 0.36755458364678756, 0.3676700576564799, 0.3677664500031305, 0.3678008605034668, 0.3677303889742165, 0.36751213523210674, 0.36710319909386513, 0.3664606803762195, 0.3655516556115267, 0.36438310819466346, 0.36297199823613574, 0.3613352858464499, 0.3594899311361122, 0.3574528942156286, 0.35524113519550554, 0.352871614186249, 0.3503612912983653, 0.34772712664236055, 0.3449860803287411, 0.3421551124680132, 0.3392511831706829, 0.3362912525472563, 0.3332922807082399, 0.3302679853379025, 0.32721911441556567, 0.32414317349431326, 0.3210376681272296, 0.31790010386739886, 0.3147279862679052, 0.31151882088183275, 0.30827011326226567, 0.30497936896228806, 0.30164409353498406, 0.29826179253343815, 0.29482997151073426, 0.29134613601995646, 0.28780779161418907, 0.2842124438465164, 0.2805575982700222, 0.276840760437791, 0.27305943590290666, 0.2692111302184536, 0.26529334893751594, 0.26130359761317773, 0.25723938179852324, 0.25309820704663666, 0.24887757891060205, 0.24457500294350362, 0.2401879846984255, 0.235714029728452, 0.23115064358666707, 0.226495331826155, 0.22174559999999996],
        [0.3650945023280412, 0.37369462038081847, 0.38126217657118283, 0.3878455297713198, 0.3934930388534155, 0.39825306268965577, 0.40217396015222634, 0.4053040901133132, 0.40769181144510214, 0.409385483019779, 0.4104334637095298, 0.41088411238654016, 0.4107857879229959, 0.4101868491910831, 0.4091356550629874, 0.4076805644108948, 0.405869936106991, 0.403752129023462, 0.4013755020324938, 0.39878841400627185, 0.39603922381698214, 0.39317629033681073, 0.39024797243794335, 0.38730262899256573, 0.38438861887286396, 0.3815543009510236, 0.37884803409923085, 0.37631817718967125, 0.37401308909453085, 0.37198112868599537, 0.37027065483625077, 0.36891497652059335, 0.36788720312676165, 0.36714539414560493, 0.3666476090679719, 0.36635190738471224, 0.3662163485866746, 0.3661989921647079, 0.3662578976096616, 0.36635112441238454, 0.36643673206372596, 0.3664727800545349, 0.36641732787566045, 0.36622843501795166, 0.3658641609722575, 0.36528256522942726, 0.36445113936267765, 0.3633751032746965, 0.3620691089505398, 0.3605478083752627, 0.3588258535339209, 0.3569178964115702, 0.354838588993266, 0.35260258326406413, 0.3502245312090202, 0.3477190848131895, 0.34510089606162814, 0.34238461693939143, 0.339584899431535, 0.33671639552311466, 0.3337937571991859, 0.33082897457998395, 0.32782339032646374, 0.32477568523475925, 0.321684540101005, 0.3185486357213353, 0.3153666528918845, 0.31213727240878675, 0.30885917506817673, 0.30553104166618855, 0.30215155299895646, 0.29871938986261504, 0.2952332330532987, 0.29169176336714125, 0.28809366160027755, 0.28443760854884165, 0.2807222850089681, 0.2769463717767911, 0.27310854964844483, 0.26920749942006394, 0.26524190188778257, 0.2612104378477351, 0.25711178809605606, 0.2529446334288795, 0.24870765464233982, 0.24439953253257135, 0.2400189478957085, 0.2355645815278857, 0.23103511422523704, 0.226429226783897, 0.22174559999999988],
        [0.36526705127921977, 0.373959572329314, 0.3816062248505963, 0.3882559044610688, 0.39395750677873376, 0.39875992742159333, 0.40271206200765003, 0.4058628061549059, 0.40826105548136293, 0.40995570560502403, 0.41099565214389083, 0.4114297907159658, 0.4113070169392512, 0.41067622643174917, 0.4095863148114619, 0.4080861776963918, 0.40622471070454114, 0.40405080945391186, 0.4016133695625064, 0.3989612866483271, 0.3961434563293759, 0.3932087742236553, 0.39020613594916753, 0.38718443712391465, 0.3841925733658991, 0.3812794402931231, 0.37849393352358857, 0.37588494867529815, 0.37350138136625377, 0.3713921272144578, 0.3696060818379127, 0.3681771499346976, 0.3670792725232022, 0.3662713997018928, 0.3657124815692362, 0.3653614682236988, 0.3651773097637474, 0.3651189562878486, 0.36514535789446867, 0.3652154646820747, 0.36528822674913297, 0.36532259419411034, 0.3652775171154731, 0.36511194561168814, 0.36478482978122184, 0.36425511972254104, 0.3634907005245253, 0.3624951972377073, 0.36128116990303266, 0.3598611785614468, 0.35824778325389584, 0.3564535440213251, 0.35449102090468043, 0.35237277394490757, 0.3501113631829521, 0.3477193486597595, 0.34520929041627574, 0.3425937484934463, 0.33988528293221715, 0.33709645377353353, 0.3342398210583416, 0.33132581281318224, 0.3283563290069798, 0.3253311375942542, 0.3222500065295246, 0.3191127037673114, 0.31591899726213385, 0.31266865496851204, 0.30936144484096567, 0.3059971348340143, 0.302575492902178, 0.2990962869999763, 0.29555928508192914, 0.29196425510255586, 0.2883109650163767, 0.28459918277791113, 0.28082867634167885, 0.27699921366219993, 0.27311056269399386, 0.26916249139158055, 0.26515476770947954, 0.2610871596022108, 0.25695943502429386, 0.2527713619302488, 0.24852270827459527, 0.24421324201185277, 0.23984273109654125, 0.23541094348318048, 0.23091764712629015, 0.22636260998039007, 0.22174559999999993],
        [0.36542048825328016, 0.37420230917317526, 0.38192607449305976, 0.38864116026670237, 0.39439694254787144, 0.3992427973903361, 0.40322810084786487, 0.4064022289742263, 0.4088145578231891, 0.41051446344852205, 0.41155132190399374, 0.411974509243373, 0.4118334015204281, 0.411177374788928, 0.41005580510264134, 0.4085180685153368, 0.4066135410807828, 0.40439159885274845, 0.4019016178850019, 0.3991929742313122, 0.396315043945448, 0.39331720308117757, 0.3902488276922702, 0.387159293832494, 0.38409797755561775, 0.38111425491541046, 0.37825750196564045, 0.37557709476007656, 0.3731224093524873, 0.37094282179664123, 0.36908770814630754, 0.3675915101599333, 0.3664289324146825, 0.36555974519239726, 0.3649437187749206, 0.36454062344409494, 0.36431022948176267, 0.36421230716976655, 0.364206626789949, 0.36425295862415263, 0.36431107295421994, 0.36434074006199363, 0.3643017302293162, 0.3641538137380304, 0.3638567608699781, 0.36337034190700274, 0.3626628120246842, 0.3617363659735557, 0.3606016833978872, 0.3592694439419495, 0.35775032725001316, 0.3560550129663488, 0.3541941807352268, 0.352178510200918, 0.35001868100769273, 0.34772537279982146, 0.3453092652215752, 0.34278103791722403, 0.340151370531039, 0.33743094270729007, 0.33463043409024834, 0.33175887235965523, 0.3288186773371369, 0.3258106168797908, 0.322735458844714, 0.3195939710890039, 0.3163869214697578, 0.31311507784407294, 0.3097792080690468, 0.3063800800017764, 0.3029184614993593, 0.2993951204188923, 0.2958108246174734, 0.2921663419521993, 0.2884624402801675, 0.28469988745847546, 0.2808794513442202, 0.2770018997944991, 0.27306800066640935, 0.2690785218170485, 0.26503423110351354, 0.26093589638290193, 0.256784285512311, 0.25258016634883795, 0.24832430674958011, 0.24401747457163472, 0.23966043767209907, 0.23525396390807052, 0.23079882113664624, 0.22629577721492367, 0.2217456],
        [0.3655524305797423, 0.3744207628165078, 0.3822198874580647, 0.388999609428906, 0.3948097336535254, 0.3997000650564163, 0.4037204085620722, 0.4069205690949865, 0.4093503515796527, 0.4110595609405644, 0.41209800210221514, 0.41251547998909804, 0.4123617995257065, 0.4116867656365344, 0.41054018324607494, 0.40897185727882157, 0.40703159265926775, 0.4047691943119072, 0.40223446716123307, 0.399477216131739, 0.39654724614791836, 0.3934943621342645, 0.39036836901527117, 0.38721907171543163, 0.38409627515923944, 0.38104978427118796, 0.3781294039757708, 0.37538493919748117, 0.37286619486081274, 0.37062297589025883, 0.3687050872103131, 0.36714745270525967, 0.36592547209854764, 0.3649996640734158, 0.3643305473131036, 0.3638786405008507, 0.36360446231989657, 0.36346853145348046, 0.36343136658484193, 0.36345348639722025, 0.36349540957385507, 0.36351765479798537, 0.36348074075285125, 0.36334518612169175, 0.36307150958774637, 0.36262022983425446, 0.36195994679076954, 0.3610915853721022, 0.36002415173937663, 0.3587666520537174, 0.35732809247624914, 0.3557174791680962, 0.35394381829038296, 0.3520161160042341, 0.34994337847077406, 0.3477346118511271, 0.3453988223064179, 0.34294501599777083, 0.34038219908631057, 0.3377193777331612, 0.33496555809944767, 0.33212852554156064, 0.3292111821969576, 0.3262152093983622, 0.32314228847849835, 0.31999410077008983, 0.31677232760586044, 0.3134786503185339, 0.31011475024083424, 0.3066823087054851, 0.30318300704521023, 0.2996185265927337, 0.2959905486807792, 0.29230075464207034, 0.2885508258093312, 0.28474244351528544, 0.28087728909265697, 0.2769570438741695, 0.2729833891925468, 0.2689580063805128, 0.26488257677079136, 0.26075878169610606, 0.2565883024891808, 0.2523728204827396, 0.24811401700950608, 0.24381357340220403, 0.2394731709935574, 0.23509449111628983, 0.23067921510312517, 0.22622902428678726, 0.22174559999999996],
        [0.36566049558812563, 0.3746128651634175, 0.38248582570510264, 0.389329564188366, 0.3951942675883921, 0.4001301228803664, 0.4041873170394736, 0.4074160370408988, 0.40986646985982644, 0.41158880247144247, 0.4126332218509309, 0.41304991497347715, 0.4128890688142661, 0.4122008703484826, 0.41103550655131177, 0.40944316439793826, 0.4074740308635474, 0.40517829292332386, 0.40260613755245267, 0.3998077517261188, 0.3968333224195074, 0.393733036607803, 0.39055708126619093, 0.387355643369856, 0.38417890989398323, 0.3810770678137574, 0.3781003041043635, 0.3752988057409867, 0.37272275969881175, 0.3704223529530235, 0.3684477724788073, 0.36683437307963673, 0.36555818087214287, 0.3645803898012449, 0.3638621938118629, 0.3633647868489163, 0.3630493628573252, 0.3628771157820087, 0.36280923956788697, 0.3628069281598796, 0.36283137550290606, 0.36284377554188624, 0.36280532222173995, 0.3626772094873865, 0.3624206312837459, 0.3619967815557379, 0.3613745777503955, 0.36055383132320706, 0.3595420772317739, 0.35834685043369763, 0.3569756858865801, 0.3554361185480226, 0.353735683375627, 0.35188191532699487, 0.3498823493597278, 0.3477445204314273, 0.3454759634996951, 0.34308421352213275, 0.34057680545634184, 0.33796127425992406, 0.3352451548904809, 0.33243514468105656, 0.3295345904664647, 0.32654600145696155, 0.3234718868628032, 0.3203147558942459, 0.317077117761546, 0.3137614816749592, 0.31037035684474235, 0.30690625248115116, 0.3033716777944419, 0.29976914199487087, 0.2961011542926942, 0.2923702238981681, 0.2885788600215485, 0.28472957187309206, 0.28082486866305467, 0.27686725960169245, 0.2728592538992618, 0.2688033607660188, 0.26470208941221957, 0.26055794904812046, 0.25637344888397756, 0.25215109813004694, 0.24789340599658505, 0.24360288169384783, 0.2392820344320916, 0.23493337342157258, 0.23055940787254675, 0.22616264699527047, 0.22174559999999996],
        [0.36574230060794993, 0.37477654811801026, 0.3827220511936657, 0.3896293367857683, 0.39554893184516887, 0.40053136332271916, 0.4046271581692707, 0.4078868433356749, 0.4103609457727831, 0.41209999243144685, 0.41315451026251776, 0.4135750262168472, 0.4134120672452865, 0.41271616029868735, 0.411537832327901, 0.409927610283779, 0.4079360211171727, 0.40561359177893386, 0.40301084921991387, 0.4001783203909639, 0.3971665322429357, 0.39402601172668056, 0.3908072857930501, 0.3875608813928957, 0.3843373254770688, 0.381187144996421, 0.3781608669018036, 0.3753090181440682, 0.37268212567406606, 0.37033071644264876, 0.36830531740066796, 0.3666416667920238, 0.36531634803281354, 0.3642911558321826, 0.36352788489927684, 0.36298832994324237, 0.36263428567322487, 0.36242754679837025, 0.36232990802782417, 0.36230316407073276, 0.3623091096362416, 0.3623095394334965, 0.36226624817164366, 0.36214103055982866, 0.3618956813071972, 0.3614919951228953, 0.36089917783117725, 0.3601160797167308, 0.359148962179352, 0.35800408661883704, 0.35668771443498215, 0.35520610702758343, 0.35356552579643713, 0.3517722321413392, 0.34983248746208595, 0.34775255315847364, 0.34553869063029824, 0.34319716127735606, 0.3407342264994432, 0.3381561476963556, 0.3354691862678898, 0.332679102100301, 0.32978964902568136, 0.32680407936258193, 0.32372564542955407, 0.32055759954514934, 0.31730319402791873, 0.31396568119641355, 0.31054831336918537, 0.3070543428647852, 0.30348702200176436, 0.29984960309867426, 0.29614533847406616, 0.29237748044649114, 0.28854928133450075, 0.2846639934566463, 0.28072486913147865, 0.27673516067754955, 0.27269812041341, 0.2686170006576116, 0.2644950537287054, 0.26033553194524267, 0.25614168762577477, 0.251916773088853, 0.24766404065302866, 0.24338674263685303, 0.2390881313588773, 0.2347714591376529, 0.230439978291731, 0.2260969411396629, 0.22174559999999996],
        [0.3657954629687349, 0.37490974358439133, 0.38292672588324556, 0.38989723946179855, 0.39587211391655197, 0.4009021788440069, 0.40503826384066477, 0.4083311985030269, 0.41083181242759453, 0.4125909352108691, 0.41365939644935196, 0.4140880257395443, 0.41392765267794757, 0.4132291068610629, 0.4120432178853918, 0.4104208153474355, 0.4084127288436954, 0.40606978797067284, 0.40344282232486905, 0.40058266150278543, 0.39754013510092323, 0.3943660727157838, 0.39111130394386845, 0.3878266583816787, 0.3845629656257156, 0.3813710552724805, 0.3783017569184749, 0.3754059001602, 0.3727343145941572, 0.3703378298168477, 0.36826727542477294, 0.3665587293513805, 0.36518926287790476, 0.36412119562252554, 0.3633168472034235, 0.36273853723877886, 0.36234858534677206, 0.3621093111455833, 0.36198303425339307, 0.3619320742883817, 0.36191875086872954, 0.36190538361261676, 0.3618542921382242, 0.3617277960637316, 0.3614882150073197, 0.3610978685871688, 0.3605262199607295, 0.35977130644253386, 0.35883830888638407, 0.35773240814608254, 0.35645878507543166, 0.3550226205282337, 0.353429095358291, 0.3516833904194058, 0.3497906865653805, 0.3477561646500173, 0.3455850055271186, 0.34328239005048694, 0.3408534990739243, 0.338303513451233, 0.33563761403621584, 0.33286077012145177, 0.32997710475462977, 0.32699052942221607, 0.3239049556106763, 0.3207242948064766, 0.31745245849608295, 0.31409335816596123, 0.3106509053025776, 0.3071290113923979, 0.3035315879218883, 0.29986254637751447, 0.29612579824574253, 0.2923252550130387, 0.2884648281658686, 0.28454842919069856, 0.2805799695739941, 0.27656336080222177, 0.27250251436184714, 0.26840134173933633, 0.26426375442115524, 0.26009366389377, 0.25589498164364655, 0.2516716191572508, 0.24742748792104877, 0.24316649942150648, 0.23889256514508983, 0.23460959657826497, 0.23032150520749764, 0.22603220251925396, 0.2217456],
        [0.3658176000000002, 0.37501038346666693, 0.3830980117333335, 0.39013158445714313, 0.3961622012952383, 0.40124096190476216, 0.4054189659428575, 0.40874731306666695, 0.4112771029333336, 0.41305943520000027, 0.41414540952380985, 0.41458612556190505, 0.4144326829714289, 0.4137361814095242, 0.41254772053333355, 0.4109184000000003, 0.4088993194666668, 0.40654157859047635, 0.40389627702857167, 0.4010145144380954, 0.3979473904761906, 0.3947460048000001, 0.3914614570666667, 0.3881448469333333, 0.384847274057143, 0.38161983809523814, 0.3785136387047619, 0.3755797755428572, 0.3728693482666667, 0.3704334565333334, 0.36832319999999996, 0.3665749562666667, 0.36516621470476196, 0.3640597426285714, 0.363218307352381, 0.3626046761904763, 0.3621816164571429, 0.3619118954666667, 0.3617582805333334, 0.3616835389714287, 0.36165043809523817, 0.36162174521904766, 0.3615602276571431, 0.3614286527238098, 0.36118978773333354, 0.3608064000000002, 0.36024817706666695, 0.3595124873904764, 0.35860361965714316, 0.3575258625523811, 0.35628350476190496, 0.35488083497142875, 0.35332214186666694, 0.35161171413333353, 0.34975384045714314, 0.34775280952380966, 0.3456129100190478, 0.34333843062857156, 0.3409336600380954, 0.33840288693333337, 0.3357504000000002, 0.33298052106666687, 0.3300977045333335, 0.3271064379428573, 0.32401120883809525, 0.3208165047619049, 0.3175268132571428, 0.3141466218666666, 0.31068041813333336, 0.30713268960000006, 0.30350792380952385, 0.29981060830476186, 0.29604523062857147, 0.29221627832380953, 0.28832823893333326, 0.28438560000000007, 0.2803928490666667, 0.2763544736761905, 0.2722749613714286, 0.26815879969523804, 0.2640104761904762, 0.25983447839999996, 0.25563529386666667, 0.2514174101333333, 0.24718531474285715, 0.2429434952380952, 0.23869643916190478, 0.2344486340571429, 0.23020456746666662, 0.22596872693333328, 0.2217456],
        [0.3658063290312653, 0.37507639966894224, 0.3832340707034214, 0.3903306840124875, 0.39641758147392475, 0.40154610496551735, 0.40576759636505, 0.4091333975503069, 0.41169485039907244, 0.41350329678913117, 0.4146100785982675, 0.41506653770426566, 0.41492401598491, 0.41423385531798507, 0.4130473975812752, 0.41141598465256474, 0.409390958409638, 0.4070236607302797, 0.40436543349227394, 0.4014676185734051, 0.39838155785145785, 0.3951585932042162, 0.3918500665094648, 0.38850731964498786, 0.3851816944885701, 0.38192453291799566, 0.37878717681104884, 0.3758209680455143, 0.3730772484991761, 0.3706073600498189, 0.3684626445752271, 0.3666797430468414, 0.3652364928107301, 0.36409603030661725, 0.3632214919742273, 0.3625760142532846, 0.3621227335835138, 0.361824786404639, 0.3616453091563849, 0.3615474382784756, 0.3614943102106358, 0.36144906139258975, 0.36137482826406186, 0.3612347472647767, 0.36099195483445834, 0.36060958741283156, 0.36005752207660424, 0.359332598450419, 0.3584383967959021, 0.35737849737467964, 0.3561564804483782, 0.35477592627862375, 0.3532404151270427, 0.35155352725526123, 0.3497188429249055, 0.347739942397602, 0.3456204059349767, 0.3433638137986562, 0.3409737462502664, 0.33845378355143374, 0.33580750596378445, 0.33303872725810396, 0.33015219524181466, 0.3271528912314984, 0.3240457965437365, 0.32083589249511085, 0.31752816040220283, 0.3141275815815942, 0.3106391373498668, 0.30706780902360203, 0.3034185779193816, 0.2996964253537871, 0.29590633264340027, 0.29205328110480255, 0.2881422520545756, 0.28417822680930155, 0.2801661866855613, 0.27611111299993696, 0.27201798706901, 0.267891790209362, 0.2637375037375748, 0.2595601089702299, 0.25536458722390887, 0.2511559198151936, 0.24693908806066545, 0.24271907327690614, 0.23850085678049737, 0.2342894198880208, 0.2300897439160578, 0.22590681018119035, 0.22174559999999996],
        [0.3657592673920502, 0.37510572409532345, 0.3833330647530013, 0.39049285036851805, 0.3966366419453079, 0.4018160004868051, 0.40608248699644406, 0.409487662477659, 0.412083087933884, 0.4139203243685535, 0.41505093278510174, 0.41552647418696287, 0.4153985095775711, 0.41471859996036076, 0.41353830633876615, 0.4119091897162214, 0.40988281109616076, 0.4075107314820186, 0.40484451187722925, 0.4019357132852267, 0.3988358967094454, 0.39559662315331945, 0.3922694536202832, 0.3889059491137709, 0.3855576706372169, 0.3822761791940553, 0.37911303578772027, 0.3761198014216461, 0.3733480370992673, 0.3708493038240178, 0.36867516259933203, 0.366862485200865, 0.36538938649315483, 0.3642192921129605, 0.3633156276970406, 0.36264181888215447, 0.362161291305061, 0.36183747060251886, 0.36163378241128713, 0.3615136523681246, 0.36144050610979045, 0.3613777692730433, 0.36128886749464245, 0.3611372264113464, 0.36088627165991427, 0.36049942887710507, 0.35994672791815646, 0.35922461551222196, 0.3583361426069341, 0.35728436014992515, 0.3560723190888278, 0.3547030703712741, 0.35317966494489667, 0.35150515375732777, 0.34968258775620004, 0.3477150178891457, 0.3456054951037972, 0.3433570703477872, 0.34097279456874763, 0.3384557187143112, 0.3358088937321103, 0.33303576101792143, 0.3301413237600967, 0.3271309755951326, 0.3240101101595254, 0.3207841210897715, 0.3174584020223671, 0.31403834659380847, 0.31052934844059243, 0.30693680119921485, 0.30326609850617214, 0.29952263399796064, 0.2957118013110767, 0.2918389940820167, 0.28790960594727694, 0.2839290305433539, 0.2799026615067436, 0.2758358924739426, 0.27173411708144707, 0.2676027289657535, 0.26344712176335805, 0.2592726891107572, 0.2550848246444473, 0.25088892200092466, 0.24669037481668557, 0.24249457672822627, 0.23830692137204326, 0.2341328023846328, 0.22997761340249118, 0.22584674806211483, 0.22174559999999996],
        [0.36567403241187457, 0.37509628864991595, 0.3833931558415643, 0.3906163957659202, 0.3968177702020844, 0.40204904092915783, 0.4063619697262412, 0.40980831837243514, 0.41243984864684036, 0.4143083223285579, 0.41546550119668857, 0.41596314703033277, 0.41585302160859144, 0.4151868867105654, 0.41401650411535534, 0.41239363560206216, 0.4103700429497863, 0.40799748793762863, 0.40532773234469033, 0.4024125379500716, 0.3993036665328737, 0.3960528798721969, 0.39271193974714225, 0.3893326079368105, 0.3859666462203025, 0.3826658163767187, 0.37948188018516027, 0.3764665994247275, 0.37367173587452157, 0.371149051313643, 0.36895030752119273, 0.36711257823769644, 0.36561418504938104, 0.36441876150389796, 0.363489941148899, 0.362791357532036, 0.3622866442009608, 0.3619394347033247, 0.36171336258677983, 0.3615720613989778, 0.36147916468757035, 0.36139830600020917, 0.3612931188845461, 0.3611272368882329, 0.36086429355892097, 0.36046792244426246, 0.35990826751893806, 0.3591815144657458, 0.3582903593945123, 0.3572374984150647, 0.35602562763722984, 0.3546574431708348, 0.3531356411257066, 0.35146291761167214, 0.3496419687385583, 0.347675490616192, 0.3455661793544003, 0.3433167310630104, 0.3409298418518489, 0.3384082078307428, 0.3357545251095193, 0.33297199466827687, 0.330065836968202, 0.32704177734075285, 0.32390554111738734, 0.32066285362956365, 0.3173194402087398, 0.313881026186374, 0.31035333689392436, 0.3067420976628489, 0.3030530338246057, 0.2992918707106529, 0.2954643336524486, 0.291576147981451, 0.287633039029118, 0.283640732126908, 0.27960495260627866, 0.27553142579868845, 0.27142587703559523, 0.2672940316484574, 0.26314161496873273, 0.25897435232787946, 0.2547979690573557, 0.2506181904886196, 0.24644074195312923, 0.2422713487823426, 0.23811573630771787, 0.23397962986071313, 0.22986875477278654, 0.2257888363753961, 0.22174559999999996],
        [0.3655482414202579, 0.37504602523682573, 0.3834125059286025, 0.3906996324453803, 0.3969593537369513, 0.402243618753108, 0.40660437644364267, 0.4100935757583472, 0.4127631656470142, 0.4146650950594359, 0.4158513129454043, 0.416373768254712, 0.416284409937151, 0.41563518694251367, 0.4144780482205921, 0.41286494272117874, 0.4108478193940657, 0.4084786271890454, 0.40580931505591006, 0.4028918319444516, 0.3997781268044629, 0.3965201485857355, 0.39316984623806217, 0.3897791687112349, 0.38640006495504625, 0.3830844839192883, 0.3798843745537531, 0.37685168580823314, 0.37403836663252066, 0.3714963659764077, 0.3692776327896869, 0.36741941766629554, 0.3659001777767541, 0.3646836719357272, 0.36373365895788057, 0.3630138976578795, 0.3624881468503893, 0.3621201653500753, 0.3618737119716028, 0.36171254552963716, 0.3616004248388437, 0.3615011087138877, 0.3613783559694347, 0.3611959254201499, 0.3609175758806985, 0.360507066165746, 0.35993461380656416, 0.3591962712008507, 0.35829454946290956, 0.3572319597070447, 0.3560110130475607, 0.3546342205987613, 0.3531040934749507, 0.3514231427904328, 0.3495938796595121, 0.34761881519649224, 0.3455004605156776, 0.3432413267313722, 0.34084392495788024, 0.3383107663095055, 0.3356443619005525, 0.33284780053132834, 0.32992648174615363, 0.32688638277535215, 0.3237334808492478, 0.3204737531981643, 0.3171131770524253, 0.31365772964235494, 0.31011338819827683, 0.3064861299505149, 0.30278193212939286, 0.29900677196523445, 0.29516662668836363, 0.29126747352910415, 0.28731528971777986, 0.2833160524847146, 0.2792757390602319, 0.27520032667465594, 0.27109579255831034, 0.2669681139415189, 0.26282326805460554, 0.2586672321278939, 0.2545059833917079, 0.25034549907637144, 0.24619175641220814, 0.2420507326295419, 0.23792840495869658, 0.23383075062999586, 0.22976374687376366, 0.22573337092032375, 0.22174559999999996],
        [0.36537951174671995, 0.3749528657601584, 0.38338927697360736, 0.390740872647584, 0.3970597800426053, 0.4023981264191882, 0.40680803903784996, 0.4103416451591075, 0.41305107204347785, 0.41498844695147824, 0.4162058971436256, 0.41675554988043706, 0.41668953242242934, 0.4160599720301199, 0.41491899596402565, 0.4133187314846636, 0.41131130585255066, 0.40894884632820416, 0.4062834801721411, 0.4033673346448784, 0.4002525370069332, 0.39699121451882247, 0.39363549444106327, 0.3902375040341727, 0.38684937055866786, 0.3835232212750657, 0.3803111834438833, 0.3772653843256377, 0.37443795118084605, 0.3718810112700253, 0.3696466918536925, 0.3677723989956221, 0.36623665397261923, 0.3650032568647455, 0.36403600775206346, 0.3632987067146352, 0.3627551538325231, 0.36236914918578905, 0.3621044928544956, 0.3619249849187046, 0.36179442545847856, 0.36167661455387945, 0.36153535228496975, 0.3613344387318114, 0.3610376739744664, 0.3606088580929976, 0.3600182397086493, 0.3592618616073971, 0.3583422151163989, 0.35726179156281274, 0.35602308227379675, 0.3546285785765087, 0.3530807717981068, 0.35138215326574906, 0.3495352143065934, 0.3475424462477977, 0.34540634041652024, 0.343129388139919, 0.34071408074515164, 0.3381629095593766, 0.3354783659097519, 0.3326635509292339, 0.32972400497397436, 0.3266658782059237, 0.3234953207870322, 0.32021848287925014, 0.316841514644528, 0.3133705662448158, 0.3098117878420643, 0.3061713295982235, 0.30245534167524396, 0.2986699742350758, 0.2948213774396695, 0.29091570145097523, 0.2869590964309434, 0.28295771254152463, 0.27891769994466875, 0.2748452088023264, 0.2707463892764478, 0.2666273915289833, 0.2624943657218832, 0.25835346201709797, 0.2542108305765778, 0.2500726215622731, 0.24594498513613422, 0.2418340714601113, 0.23774603069615485, 0.23368701300621525, 0.2296631685522426, 0.2256806474961874, 0.2217456],
        [0.36516546072078043, 0.3748147421240195, 0.3833216309360707, 0.39073842861321734, 0.39711743661174287, 0.40251095638793083, 0.40697128939806465, 0.4105507370984279, 0.4133016009453039, 0.41527618239497627, 0.41652678290372847, 0.41710570392784413, 0.41706524692360625, 0.4164577133472989, 0.41533540465520496, 0.41375062230360843, 0.4117556677487925, 0.4094028424470406, 0.4067444478546365, 0.4038327854278634, 0.400720156623005, 0.3974588628963445, 0.39410120570416574, 0.3906994865027517, 0.3873060067483865, 0.383973067897353, 0.38075297140593506, 0.37769801873041603, 0.3748605113270794, 0.3722927506522086, 0.3700470381620872, 0.3681609177346355, 0.36661290293432147, 0.3653667497472499, 0.36438621415952566, 0.36363505215725345, 0.3630770197265383, 0.36267587285348485, 0.36239536752419804, 0.36219925972478256, 0.36205130544134323, 0.361915260659985, 0.3617548813668128, 0.3615339235479311, 0.36121614318944495, 0.3607652962774593, 0.3601516181528083, 0.35937126157524546, 0.35842685865925344, 0.35732104151931526, 0.35605644226991395, 0.3546356930255322, 0.3530614259006531, 0.35133627300975934, 0.34946286646733404, 0.34744383838785964, 0.34528182088581966, 0.3429794460756965, 0.3405393460719735, 0.33796415298913307, 0.33525649894165854, 0.33241961818415106, 0.3294591535316868, 0.3263813499394602, 0.32319245236266586, 0.31989870575649826, 0.31650635507615177, 0.31302164527682114, 0.30945082131370094, 0.3058001281419855, 0.30207581071686945, 0.2982841139935473, 0.29443128292721366, 0.29052356247306305, 0.28656719758628996, 0.28256843322208886, 0.2785335143356543, 0.27446868588218093, 0.2703801928168632, 0.26627428009489557, 0.26215719267147275, 0.25803517550178906, 0.2539144735410392, 0.24980133174441768, 0.24570199506711898, 0.24162270846433762, 0.23756971689126818, 0.23354926530310519, 0.2295675986550431, 0.22563096190227647, 0.22174559999999996],
        [0.36490370567195896, 0.3746295862325151, 0.38320772977548423, 0.3906906125829662, 0.39713071093706104, 0.4025805011198684, 0.4070924594134882, 0.4107190621000203, 0.41351278546156456, 0.4155261057802211, 0.41681149933808953, 0.41742144241726975, 0.4174084112998614, 0.41682488226796477, 0.41572333160367947, 0.4141562355891054, 0.41217607050634236, 0.4098353126374904, 0.4071864382646491, 0.4042819236699186, 0.40117424513539873, 0.3979158789431892, 0.39455930137538997, 0.3911569887141007, 0.3877614172414216, 0.38442506323945247, 0.3812004029902928, 0.37813991277604286, 0.37529606887880235, 0.3727213475806711, 0.370468225163749, 0.36857436939229526, 0.3670182139592065, 0.3657633840395379, 0.36477350480834525, 0.3640122014406845, 0.3634430991116113, 0.36302982299618103, 0.36273599826944963, 0.3625252501064727, 0.36236120368230584, 0.3622074841720049, 0.36202771675062556, 0.36178552659322327, 0.3614445388748538, 0.36096837877057303, 0.36032722206665585, 0.3595174469942561, 0.3585419823957462, 0.3574037571134994, 0.3561056999898888, 0.35465073986728723, 0.3530418055880675, 0.3512818259946027, 0.3493737299292657, 0.34732044623442954, 0.3451249037524671, 0.34279003132575153, 0.34031875779665544, 0.33771401200755197, 0.33497872280081425, 0.3321163746182383, 0.32913267429931414, 0.3260338842829551, 0.3228262670080744, 0.3195160849135854, 0.3161096004384013, 0.31261307602143534, 0.309032774101601, 0.3053749571178113, 0.3016458875089799, 0.2978518277140197, 0.2939990401718442, 0.2900937873213666, 0.28614233160150016, 0.2821509354511583, 0.27812586130925415, 0.274073371614701, 0.26999972880641226, 0.2659111953233011, 0.26181403360428074, 0.2577145060882647, 0.2536188752141661, 0.24953340342089828, 0.24546435314737441, 0.24141798683250792, 0.23740056691521194, 0.2334183558344, 0.2294776160289851, 0.22558460993788065, 0.22174559999999996],
        [0.3645918639297753, 0.3743953299897505, 0.3830457354513395, 0.39059573679751663, 0.3970979905112563, 0.4026051530755333, 0.4071698809733221, 0.4108448306875969, 0.4136826587013327, 0.4157360214975038, 0.4170575755590848, 0.4176999773690504, 0.41771588341037463, 0.41715795016603247, 0.4160788341189982, 0.41453119175224656, 0.41256767954875184, 0.4102409539914888, 0.4076036715634319, 0.40470848874755566, 0.4016080620268345, 0.39835504788424314, 0.395002102802756, 0.3916018832653477, 0.3882070457549927, 0.3848702467546655, 0.3816441427473407, 0.3785813902159928, 0.3757346456435964, 0.3731565655131258, 0.3708998063075559, 0.3690021494775612, 0.36744187634461917, 0.3661823931979064, 0.3651871063266005, 0.36441942201987865, 0.3638427465669183, 0.3634204862568963, 0.3631160473789902, 0.36289283622237717, 0.36271425907623456, 0.36254372222973963, 0.36234463197206945, 0.36208039459240154, 0.36171441637991275, 0.36121010362378086, 0.3605375243778069, 0.3596933937542893, 0.3586810886301502, 0.3575039858823122, 0.3561654623876976, 0.35466889502322885, 0.3530176606658281, 0.351215136192418, 0.34926469847992064, 0.3471697244052585, 0.3449335908453542, 0.3425596746771298, 0.3400513527775078, 0.3374120020234104, 0.3346449992917602, 0.33175419255365307, 0.32874531415687885, 0.325624567543401, 0.3223981561551831, 0.3190722834341884, 0.3156531528223805, 0.3121469677617228, 0.30855993169417884, 0.3048982480617119, 0.3011681203062856, 0.29737575186986337, 0.29352734619440857, 0.28962910672188463, 0.2856872368942552, 0.2817079401534837, 0.27769741994153335, 0.27366187970036776, 0.26960752287195044, 0.2655405528982448, 0.2614671732212142, 0.25739358728282213, 0.2533259985250322, 0.24927061038980775, 0.24523362631911222, 0.24122124975490905, 0.23723968413916172, 0.23329513291383375, 0.22939379952088843, 0.22554188740228934, 0.22174559999999993],
        [0.36422755282374913, 0.37410990529983185, 0.38283380992312843, 0.39045211349755443, 0.3970176628270258, 0.40258330471545833, 0.4072018859667678, 0.4109262533848699, 0.4138092537736806, 0.4159037339371157, 0.41726254067909113, 0.4179385208035224, 0.41798452111432555, 0.41745338841541624, 0.41639796951071056, 0.41487111120412395, 0.41292566029957234, 0.41061446360097165, 0.40799036791223775, 0.40510622003728614, 0.402014866780033, 0.39876915494439374, 0.3954219313342846, 0.3920260427536212, 0.3886343360063193, 0.3852996578962947, 0.3820748552274632, 0.37901277480374085, 0.3761662634290433, 0.3735881679072861, 0.37133133504238547, 0.36943365349939294, 0.367873179387905, 0.366613010678653, 0.36561624534236953, 0.36484598134978635, 0.3642653166716356, 0.3638373492786493, 0.36352517714155963, 0.36329189823109836, 0.3631006105179977, 0.3629144119729898, 0.3626964005668064, 0.3624096742701799, 0.3620173310538419, 0.36148246888852487, 0.3607749980138761, 0.3598920777452057, 0.3588376796667387, 0.3576157753627004, 0.35623033641731655, 0.35468533441481237, 0.35298474093941307, 0.3511325275753439, 0.3491326659068306, 0.34698912751809824, 0.34470588399337204, 0.3422869069168778, 0.33973616787284056, 0.33705763844548536, 0.3342552902190383, 0.33133344431255374, 0.3282978199844041, 0.32515448602779135, 0.32190951123591743, 0.31856896440198434, 0.31513891431919394, 0.31162542978074803, 0.3080345795798487, 0.3043724325096977, 0.30064505736349717, 0.29685852293444875, 0.29301889801575454, 0.2891322514006164, 0.28520465188223615, 0.2812421682538159, 0.27725086930855736, 0.27323682383966263, 0.26920610064033346, 0.2651647685037719, 0.2611188962231798, 0.257074552591759, 0.2530378064027115, 0.2490147264492393, 0.24501138152454416, 0.2410338404218281, 0.23708817193429294, 0.23318044485514064, 0.22931672797757302, 0.22550309009479222, 0.2217456],
        [0.3638083896834, 0.3737712440668646, 0.3825701151503425, 0.3902580549237657, 0.39688811537706603, 0.4025133485001757, 0.4071868062830267, 0.41096154071555097, 0.41389060378768056, 0.41602704748934777, 0.4174239238104843, 0.41813428474102243, 0.4182111822708938, 0.41770766839003076, 0.41667679508836525, 0.4151716143558294, 0.41324517818235496, 0.4109505385578742, 0.40834074747231913, 0.40546885691562184, 0.402387918877714, 0.399150985348528, 0.3958111083179958, 0.3924213397760492, 0.3890347317126206, 0.3857043361176416, 0.38248320498104466, 0.3794243902927615, 0.37658094404272435, 0.3740059182208649, 0.3717523648171156, 0.3698582769667499, 0.3683014123864089, 0.36704446993807477, 0.36605014848373, 0.36528114688535757, 0.36470016400493954, 0.36426989870445864, 0.36395304984589727, 0.363712316291238, 0.36351039690246334, 0.36330999054155577, 0.3630737960704978, 0.36276451235127205, 0.3623448382458609, 0.36177747261624693, 0.36103211590247836, 0.36010647485686537, 0.35900525780978426, 0.3577331730916111, 0.35629492903272203, 0.35469523396349295, 0.35293879621430013, 0.35103032411551954, 0.3489745259975273, 0.34677611019069954, 0.3444397850254121, 0.34197025883204146, 0.33937223994096344, 0.3366504366825542, 0.3338095573871897, 0.3308545022170978, 0.3277909386619124, 0.32462472604311887, 0.32136172368220284, 0.31800779090064996, 0.31456878701994573, 0.3110505713615754, 0.3074590032470248, 0.3037999419977794, 0.3000792469353248, 0.29630277738114635, 0.2924763926567297, 0.2886059520835603, 0.28469731498312384, 0.28075634067690575, 0.27678888848639155, 0.27280081773306675, 0.2687979877384169, 0.26478625782392756, 0.2607714873110843, 0.2567595355213725, 0.25275626177627786, 0.24876752539728586, 0.24479918570588205, 0.24085710202355187, 0.2369471336717809, 0.23307513997205476, 0.22924698024585877, 0.22546851381467872, 0.2217456],
        [0.36333199183824766, 0.37337727819495453, 0.38225281309247344, 0.39001187331683607, 0.39670773565407375, 0.40239367689021793, 0.40712297381130025, 0.4109489032033522, 0.41392474185240524, 0.41610376654449105, 0.41753925406564096, 0.41828448120188655, 0.4183927247392591, 0.4179172614637904, 0.416911368161512, 0.41542832161845505, 0.41352139862065124, 0.41124387595413225, 0.4086490304049294, 0.40579013875907416, 0.4027204778025981, 0.39949332432153284, 0.3961619551019097, 0.39277964692976014, 0.38939967659111596, 0.3860753208720086, 0.38285985655846916, 0.3798065604365296, 0.37696870929222126, 0.3743995799115756, 0.37215244908062417, 0.37026541538859165, 0.3687158646374763, 0.3674660044324689, 0.36647804237876064, 0.3657141860815427, 0.36513664314600647, 0.36470762117734273, 0.36438932778074296, 0.3641439705613981, 0.36393375712449955, 0.36372089507523814, 0.3634675920188054, 0.36313605556039213, 0.36268849330518965, 0.36208711285838924, 0.3613013509712281, 0.36032956097912894, 0.35917732536356034, 0.357850226605991, 0.35635384718789004, 0.3546937695907259, 0.35287557629596744, 0.35090484978508346, 0.3487871725395427, 0.34652812704081376, 0.3441332957703657, 0.34160826120966725, 0.3389586058401869, 0.33618991214339355, 0.3333077626007561, 0.3303177385894436, 0.3272254170694266, 0.3240363738963767, 0.32075618492596475, 0.3173904260138622, 0.3139446730157399, 0.3104245017872693, 0.3068354881841216, 0.30318320806196775, 0.2994732372764791, 0.29571115168332673, 0.29190252713818193, 0.28805293949671573, 0.2841679646145994, 0.2802531783475042, 0.2763141565511011, 0.2723564750810614, 0.26838570979305626, 0.26440743654275695, 0.26042723118583444, 0.25645066957796014, 0.25248332757480507, 0.2485307810320405, 0.24459860580533754, 0.2406923777503674, 0.2368176727228012, 0.23298006657831022, 0.22918513517256553, 0.2254384543612384, 0.2217456],
        [0.3627959766178118, 0.37292593958820736, 0.38188006570901295, 0.3897118809174517, 0.39647491115074557, 0.4022226823461176, 0.4070087204407902, 0.41088655137198576, 0.4139097010769271, 0.41613169549283685, 0.4176060605569374, 0.4183863222064513, 0.4185260063786013, 0.41807863901060993, 0.4170977460396997, 0.415636853403093, 0.41374948703801256, 0.4114891728816811, 0.40890943687132114, 0.40606380494415506, 0.4030058030374057, 0.39978895708829537, 0.39646679303404675, 0.39309283681188245, 0.38972061435902516, 0.38640365161269724, 0.38319547451012126, 0.38014960898851996, 0.3773195809851157, 0.3747589164371312, 0.37252114128178915, 0.37064446427387804, 0.3691058254384525, 0.36786684761813265, 0.366889153655539, 0.3661343663932921, 0.36556410867401246, 0.3651400033403203, 0.3648236732348364, 0.3645767412001809, 0.36436083007897446, 0.36413756271383757, 0.3638685619473906, 0.36351545062225393, 0.3630398515810481, 0.3624033876663937, 0.36157517614774054, 0.36055431200185667, 0.3593473846323398, 0.35796098344278726, 0.356401697836797, 0.3546761172179665, 0.3527908309898932, 0.35075242855617467, 0.3485674993204087, 0.34624263268619265, 0.34378441805712434, 0.3411994448368012, 0.33849430242882084, 0.33567558023678074, 0.3327498676642788, 0.32972352575174857, 0.32660200208696966, 0.3233905158945578, 0.32009428639912857, 0.31671853282529777, 0.31326847439768113, 0.3097493303408943, 0.3061663198795531, 0.3025246622382733, 0.29882957664167054, 0.29508628231436035, 0.2912999984809587, 0.28747594436608126, 0.28361933919434384, 0.2797354021903619, 0.27582935257875135, 0.27190640958412793, 0.26797179243110725, 0.26403072034430514, 0.2600884125483372, 0.25615008826781926, 0.252220966727367, 0.2483062671515962, 0.24441120876512248, 0.24054101079256157, 0.23670089245852927, 0.23289607298764126, 0.22913177160451315, 0.22541320753376082, 0.2217456],
        [0.3621979613516122, 0.37241516015072873, 0.3814500349594529, 0.3893563899662983, 0.39618802935977865, 0.4019987573284071, 0.4068423780606976, 0.41077269574516356, 0.4138435145703186, 0.4161086387246761, 0.41762187239674986, 0.41843701977505326, 0.41860788504810004, 0.4181882724044035, 0.4172319860324773, 0.4157928301208352, 0.41392460885799015, 0.4116811264324565, 0.40911618703274727, 0.40628359484737625, 0.40323715406485683, 0.40003066887370264, 0.3967179434624273, 0.3933527820195443, 0.3899889887335674, 0.3866803677930098, 0.3834807233863851, 0.3804438597022072, 0.3776235809289893, 0.3750736912552451, 0.3728479948694881, 0.37098481913156844, 0.3694605840866827, 0.3682362329513634, 0.3672727089421434, 0.366530955275556, 0.365971915168134, 0.36555653183641, 0.36524574849691727, 0.3650005083661885, 0.36478175466075646, 0.3645504305971545, 0.36426747939191517, 0.36389384426157145, 0.3633904684226561, 0.3627182950917022, 0.36184606435963, 0.360773703814909, 0.35950893792039557, 0.3580594911389467, 0.3564330879334192, 0.3546374527666698, 0.35268031010155515, 0.3505693844009319, 0.3483124001276571, 0.3459170817445872, 0.3433911537145791, 0.34074234050048957, 0.3379783665651753, 0.3351069563714928, 0.33213583438229927, 0.3290722360261711, 0.32592144059456446, 0.32268823834465526, 0.3193774195336197, 0.31599377441863374, 0.3125420932568735, 0.3090271663055148, 0.3054537838217339, 0.3018267360627067, 0.29815081328560933, 0.29443080574761776, 0.29067150370590794, 0.286877697417656, 0.28305417714003805, 0.27920573313022995, 0.2753371556454078, 0.2714532349427476, 0.26755876127942546, 0.2636585249126174, 0.25975731609949926, 0.2558599250972473, 0.2519711421630375, 0.248095757554046, 0.2442385615274486, 0.2404043443404214, 0.23659789625014047, 0.23282400751378185, 0.22908746838852154, 0.2253930691315356, 0.2217456],
        [0.36153556336916837, 0.3718428717866244, 0.3809608828032846, 0.3889437127040621, 0.39584547777386925, 0.40172029429761913, 0.40662227856022426, 0.41060554684659767, 0.413724215441652, 0.4160324006303001, 0.41758421869745493, 0.4184337859280289, 0.41863521860693487, 0.41824263301908593, 0.41731014544939443, 0.4158918721827734, 0.4140419295041355, 0.4118144336983938, 0.4092635010504606, 0.40644324784524916, 0.40340779036767205, 0.40021124490264176, 0.3969077277350716, 0.393551355149874, 0.390196243431962, 0.38689650886624805, 0.3837062677376452, 0.380679636331066, 0.3778707309314235, 0.3753336678236302, 0.37312256329259913, 0.3712758754706225, 0.369769429879512, 0.3685633938884581, 0.367617934866652, 0.3668932201832848, 0.3663494172075472, 0.3659466933086304, 0.36564521585572524, 0.36540515221802267, 0.36518666976471376, 0.3649499358649894, 0.36465511788804067, 0.36426238320305837, 0.36373189917923343, 0.3630238331857571, 0.3621064885345116, 0.36098071230814616, 0.3596554875320009, 0.3581397972314162, 0.3564426244317329, 0.35457295215829115, 0.3525397634364314, 0.3503520412914941, 0.3480187687488198, 0.3455489288337487, 0.3429515045716215, 0.34023547898777856, 0.3374098351075601, 0.33448355595630685, 0.33146562455935924, 0.3283642417348689, 0.32518447947223356, 0.32193062755366214, 0.3186069757613636, 0.315217813877547, 0.3117674316844211, 0.3082601189641952, 0.304700165499078, 0.30109186107127867, 0.29743949546300624, 0.29374735845646927, 0.2900197398338772, 0.2862609293774388, 0.28247521686936305, 0.278666892091859, 0.2748402448271355, 0.2709995648574017, 0.26714914196486644, 0.2632932659317387, 0.2594362265402275, 0.2555823135725418, 0.2517358168108906, 0.24790102603748293, 0.24408223103452767, 0.24028372158423383, 0.23650978746881035, 0.23276471847046626, 0.22905280437141054, 0.22537833495385207, 0.2217456],
        [0.3608064000000001, 0.3712070064000001, 0.3804107712, 0.38847216137142876, 0.3954456438857144, 0.4013856857142859, 0.40634675382857166, 0.41038331520000015, 0.4135498368, 0.4159007856000001, 0.4174906285714287, 0.4183738326857143, 0.4186048649142858, 0.41823819222857156, 0.41732828160000013, 0.4159296000000001, 0.4140966144, 0.41188379177142853, 0.40934559908571433, 0.40653650331428565, 0.40351097142857145, 0.40032347039999994, 0.39702846719999996, 0.3936804287999999, 0.3903338221714286, 0.3870431142857143, 0.38386277211428577, 0.3808472626285713, 0.37805105279999995, 0.37552860959999995, 0.3733344, 0.3715070287999999, 0.3700216521142857, 0.36883756388571426, 0.3679140580571428, 0.36721042857142855, 0.36668596937142867, 0.3662999744, 0.3660117376000001, 0.3657805529142858, 0.3655657142857143, 0.3653265156571429, 0.36502225097142876, 0.36461221417142875, 0.3640556992000001, 0.36331200000000013, 0.36234892160000004, 0.3611683133714287, 0.35978053577142877, 0.3581959492571429, 0.3564249142857143, 0.3544777913142858, 0.3523649408000001, 0.35009672320000007, 0.3476834989714287, 0.3451356285714286, 0.3424634724571429, 0.3396773910857143, 0.33678774491428576, 0.33380489439999994, 0.33073920000000007, 0.32759991520000004, 0.32439186559999994, 0.3211187698285714, 0.3177843465142857, 0.3143923142857143, 0.3109463917714286, 0.3074502975999999, 0.30390775039999995, 0.3003224688, 0.29669817142857147, 0.2930385769142857, 0.2893474038857143, 0.28562837097142857, 0.2818851968, 0.2781216000000001, 0.2743412992, 0.27054801302857145, 0.2667454601142857, 0.2629373590857143, 0.2591274285714286, 0.25531938719999997, 0.2515169536, 0.24772384640000003, 0.2439437842285715, 0.2401804857142858, 0.23643766948571432, 0.23271905417142863, 0.22902835840000005, 0.2253693008, 0.2217456],
        [0.36000898644410734, 0.3705061942857695, 0.3797983961835745, 0.3879404510861126, 0.3949872179419737, 0.4009935556997478, 0.4060143233080251, 0.4101043797153955, 0.4133185838704489, 0.41571179472177566, 0.4173388712179656, 0.4182546723076088, 0.4185140569392953, 0.41817188406161526, 0.41728301262315837, 0.41590230157251495, 0.4140846098582747, 0.41188479642902825, 0.4093577202333651, 0.40655824021987547, 0.40354121533714943, 0.40036150453377695, 0.39707396675834794, 0.3937334609594527, 0.3903948460856812, 0.3871129810856233, 0.3839427249078692, 0.3809389365010088, 0.37815647481363224, 0.37565019879432954, 0.3734749673916906, 0.37166955049834755, 0.3702083617830998, 0.36904972585878904, 0.3681519673382564, 0.36747341083434365, 0.36697238095989226, 0.3666072023277436, 0.36633619955073926, 0.3661176972417205, 0.365910020013529, 0.3656714924790061, 0.36536043925099354, 0.3649351849423325, 0.3643540541658646, 0.36357537153443137, 0.3625663824481051, 0.3613300154558831, 0.35987811989399326, 0.3582225450986635, 0.3563751404061219, 0.35434775515259653, 0.3521522386743154, 0.3498004403075065, 0.347304209388398, 0.34467539525321755, 0.34192584723819364, 0.3390674146795541, 0.3361119469135267, 0.33307129327633983, 0.32995730310422156, 0.32678036413277417, 0.3235450176950982, 0.32025434352366877, 0.3169114213509609, 0.3135193309094496, 0.31008115193160984, 0.3065999641499166, 0.30307884729684514, 0.29952088110487035, 0.2959291453064672, 0.29230671963411087, 0.2886566838202762, 0.2849821175974382, 0.2812861006980721, 0.277571712854653, 0.2738420337996555, 0.2701001432655549, 0.2663491209848263, 0.26259204668994457, 0.2588320001133848, 0.255072060987622, 0.2513153090451311, 0.2475648240183874, 0.2438236856398657, 0.24009497364204105, 0.23638176775738848, 0.23268714771838317, 0.2290141932574998, 0.22536598410721378, 0.22174559999999993],
        [0.35914542938341143, 0.3697418593020776, 0.3791245900859178, 0.38734890847394154, 0.39447010120515835, 0.40054345501857724, 0.4056242566532078, 0.40976779284805936, 0.4130293503421412, 0.4154642158744628, 0.41712767618403346, 0.4180750180098626, 0.4183615280909595, 0.4180424931663334, 0.41717319997499386, 0.41580893525595014, 0.4140049857482115, 0.4118166381907875, 0.40929917932268756, 0.40650789588292086, 0.40349807461049675, 0.4003250022444247, 0.3970439655237139, 0.3937102511873738, 0.390379145974414, 0.38710593662384346, 0.38394590987467153, 0.38095435246590814, 0.378186551136562, 0.37569779262564285, 0.3735433636721599, 0.3717622154230615, 0.37032795665705326, 0.3691978605607791, 0.3683292003208832, 0.36767924912401057, 0.3672052801568047, 0.36686456660591027, 0.36661438165797167, 0.3664119984996331, 0.3662146903175387, 0.365979730298333, 0.3656643916286603, 0.36522594749516485, 0.3646216710844908, 0.3638088355832828, 0.36275407382841723, 0.3614614572577014, 0.35994441695917395, 0.3582163840208746, 0.3562907895308425, 0.3541810645771169, 0.35190064024773704, 0.34946294763074215, 0.34688141781417176, 0.3441694818860648, 0.34134057093446063, 0.3384081160473987, 0.33538554831291817, 0.3322862988190581, 0.32912379865385816, 0.3259096378006092, 0.32264804182360995, 0.31934139518241084, 0.31599208233656234, 0.3126024877456151, 0.30917499586911956, 0.305711991166626, 0.3022158580976852, 0.29868898112184744, 0.29513374469866344, 0.2915525332876833, 0.287947731348458, 0.28432172334053774, 0.2806768937234731, 0.2770156269568145, 0.27334030750011246, 0.2696533198129175, 0.2659570483547801, 0.26225387758525076, 0.2585461919638799, 0.25483637595021813, 0.2511268140038158, 0.24741989058422365, 0.2437179901509919, 0.24002349716367127, 0.23633879608181202, 0.23266627136496487, 0.22900830747268008, 0.2253672888645083, 0.22174560000000004],
        [0.3582187333703139, 0.368916123697877, 0.37839071931342305, 0.3866982630377716, 0.3938944976917418, 0.4000351660961536, 0.4051760110718263, 0.4093727754395796, 0.41268120202023273, 0.41515703363460543, 0.41685601310351733, 0.41783388324778764, 0.41814638688823613, 0.41784926684568224, 0.4169982659409454, 0.41564912699484546, 0.4138575928282012, 0.41167940626183297, 0.40917031011656, 0.4063860472132018, 0.4033823603725779, 0.4002149924155076, 0.3969396861628107, 0.3936121844353067, 0.39028823005381513, 0.3870235658391553, 0.38387393461214697, 0.38089507919360965, 0.37814274240436263, 0.37567266706522556, 0.3735405959970181, 0.37178567430122533, 0.3703806562019951, 0.3692816982041409, 0.3684449568124763, 0.36782658853181477, 0.3673827498669699, 0.3670695973227551, 0.3668432874039839, 0.36665997661546995, 0.3664758214620268, 0.3662469784484677, 0.36592960407960656, 0.3654798548602566, 0.36485388729523116, 0.36400785788934426, 0.36290774445492174, 0.36155881003434087, 0.3599761389774913, 0.3581748156342626, 0.35616992435454486, 0.35397654948822765, 0.3516097753852006, 0.3490846863953535, 0.34641636686857624, 0.3436199011547583, 0.3407103736037896, 0.3377028685655601, 0.33461247038995906, 0.3314542634268764, 0.3282433320262021, 0.32499252085997454, 0.3217057158888283, 0.31838456339554655, 0.31503070966291263, 0.31164580097371, 0.3082314836107219, 0.3047894038567315, 0.3013212079945224, 0.29782854230687766, 0.2943130530765809, 0.2907763865864152, 0.2872201891191639, 0.2836461069576105, 0.2800557863845381, 0.27645087368273025, 0.27283301513496994, 0.2692038570240408, 0.2655650456327261, 0.26191822724380903, 0.258265048140073, 0.2546071546043013, 0.2509461929192773, 0.24728380936778427, 0.24362165023260557, 0.2399613617965245, 0.23630459034232437, 0.23265298215278857, 0.22900818351070032, 0.22537184069884306, 0.22174560000000001],
        [0.3572319029572163, 0.368031109722121, 0.377598150272484, 0.3859892442804586, 0.39326061141819846, 0.399468471357857, 0.4046690437715878, 0.4089185483315441, 0.41227320470987977, 0.4147892325787481, 0.41652285161030267, 0.4175302814766969, 0.4178677418500842, 0.4175914524026182, 0.4167576328064525, 0.4154225027337405, 0.41364228185663543, 0.4114731898472912, 0.40897144637786115, 0.4061932711204986, 0.40319488374735724, 0.4000325039305907, 0.396762351342352, 0.3934406456547951, 0.39012360654007333, 0.3868674536703403, 0.3837284067177493, 0.38076268535445384, 0.3780265092526077, 0.375576098084364, 0.3734676715218764, 0.37174057785992237, 0.3703666798837751, 0.3693009690013313, 0.3684984366204882, 0.3679140741491428, 0.3675028729951922, 0.3672198245665332, 0.367019920271063, 0.3668581515166785, 0.3666895097112768, 0.36646898626275487, 0.3661515725790098, 0.36569226006793865, 0.36504604013743813, 0.36416790419540573, 0.36302314304160405, 0.3616182450432599, 0.35996999795946566, 0.3580951895493142, 0.356010607571898, 0.3537330397863097, 0.3512792739516419, 0.3486660978269869, 0.3459102991714378, 0.34302866574408686, 0.3400379853040266, 0.3369550456103499, 0.3337966344221492, 0.33057953949851693, 0.3273205485985461, 0.32403379796733994, 0.3207228177940466, 0.317388486753825, 0.31403168352183436, 0.3106532867732334, 0.30725417518318127, 0.30383522742683705, 0.30039732217935955, 0.29694133811590806, 0.2934681539116413, 0.28997864824171843, 0.2864736997812986, 0.2829541872055404, 0.27942098918960323, 0.27587498440864594, 0.2723170515378276, 0.268748069252307, 0.2651689162272434, 0.26158047113779587, 0.2579836126591232, 0.2543792194663844, 0.25076817023473863, 0.24715134363934482, 0.243529618355362, 0.23990387305794916, 0.2362749864222653, 0.23264383712346948, 0.22901130383672055, 0.22537826523717777, 0.2217456],
        [0.3561879426965204, 0.3670889396237624, 0.3767482493694938, 0.38522258170485896, 0.392568646401002, 0.3988431532290672, 0.40410281196019887, 0.40840433236554124, 0.4118044242162385, 0.41435979728343514, 0.4161271613382752, 0.41716322615190277, 0.4175247014954624, 0.4172682971400983, 0.4164507228569545, 0.4151286884171755, 0.41335890359190536, 0.41119807815228865, 0.4087029218694692, 0.40593014451459153, 0.4029364558587997, 0.3997785656732383, 0.39651318372905114, 0.39319701979738275, 0.3898867836493775, 0.3866391850561794, 0.38351093378893264, 0.38055873961878167, 0.37783931231687057, 0.3754093616543438, 0.37332559740234555, 0.3716275768262363, 0.3702862471682427, 0.36925540316480704, 0.3684888395523722, 0.3679403510673809, 0.36756373244627594, 0.3673127784254998, 0.3671412837414953, 0.36700304313070525, 0.36685185132957204, 0.36664150307453885, 0.36632579310204794, 0.3658585161485423, 0.3651934669504644, 0.36428444024425716, 0.3630960183024493, 0.3616359335419161, 0.3599227059156179, 0.35797485537651574, 0.35581090187757086, 0.3534493653717443, 0.3509087658119968, 0.34820762315128934, 0.345364457342583, 0.34239778833883866, 0.3393261360930174, 0.3361680205580803, 0.3329419616869881, 0.3296664794327017, 0.32636009374818253, 0.32303825377917483, 0.3197041254425583, 0.31635780384799567, 0.31299938410515, 0.3096289613236847, 0.30624663061326235, 0.3028524870835463, 0.29944662584419945, 0.29602914200488506, 0.2926001306752659, 0.28915968696500527, 0.285707905983766, 0.2822448828412112, 0.2787707126470039, 0.27528549051080736, 0.27178931154228436, 0.26828227085109796, 0.26476446354691147, 0.26123598473938764, 0.2576969295381896, 0.25414739305298045, 0.2505874703934232, 0.24701725666918103, 0.24343684698991677, 0.23984633646529357, 0.23624582020497445, 0.23263539331862254, 0.22901515091590072, 0.22538518810647218, 0.22174559999999996],
        [0.35508985714062774, 0.36609173565175407, 0.3758423830108461, 0.3843990048138287, 0.39181880665662655, 0.3981589941351642, 0.40347677284536687, 0.40782934838315904, 0.41127392634446536, 0.4138677123252108, 0.4156679119213202, 0.41673173072871805, 0.4171163743433293, 0.41687904836107864, 0.41607695837789066, 0.4147673099896906, 0.4130073087924026, 0.41085416038195194, 0.40836507035426295, 0.40559724430526073, 0.4026078878308699, 0.3994542065270152, 0.39619340598962155, 0.39288269181461355, 0.38957926959791594, 0.3863403449354536, 0.3832231234231512, 0.38028481065693354, 0.3775826122327253, 0.3751737337464513, 0.37311538079403633, 0.3714473219272506, 0.3701395775212473, 0.3691447309070246, 0.36841536541558095, 0.3679040643779152, 0.36756341112502533, 0.36734598898791015, 0.3672043812975679, 0.36709117138499714, 0.3669589425811964, 0.36676027821716406, 0.36644776162389864, 0.3659739761323986, 0.36529150507366226, 0.3643529317786884, 0.3631221189514435, 0.3616080467877674, 0.3598309748564682, 0.3578111627263539, 0.35556886996623255, 0.35312435614491233, 0.3504978808312011, 0.347709703593907, 0.3447800840018381, 0.34172928162380234, 0.338577556028608, 0.3353451667850629, 0.33205237346197525, 0.3287194356281529, 0.32536661285240426, 0.32201067295194924, 0.31865441673765654, 0.31529715326880736, 0.3119381916046824, 0.3085768408045629, 0.30521240992772936, 0.30184420803346307, 0.2984715441810448, 0.2950937274297555, 0.2917100668388761, 0.2883198714676876, 0.2849224503754708, 0.2815171126215067, 0.2781031672650762, 0.2746799233654604, 0.2712466899819399, 0.26780277617379594, 0.26434749100030924, 0.26088014352076083, 0.2574000427944316, 0.25390649788060243, 0.2503988178385544, 0.24687631172756846, 0.24333828860692536, 0.23978405753590606, 0.2362129275737916, 0.23262420777986284, 0.22901720721340066, 0.22539123493368607, 0.2217456],
        [0.35394065084193965, 0.3650416200550486, 0.3748819176029341, 0.38351924311022373, 0.3910112962015457, 0.3974157765015279, 0.4027903836347984, 0.4071928172259851, 0.41068077689971616, 0.4133119622806196, 0.41514407299332323, 0.4162348086624552, 0.4166418689126433, 0.41642295336851565, 0.4156357616547003, 0.4143379933958251, 0.41258734821651805, 0.4104415257414074, 0.4079582255951209, 0.40519514740228646, 0.4022099907875323, 0.3990604553754863, 0.3958042407907766, 0.39249904665803087, 0.3892025726018774, 0.3859725182469441, 0.3828665832178588, 0.37994246713924973, 0.3772578696357448, 0.37487049033197206, 0.37283802885255934, 0.3712004638900487, 0.3699268904086384, 0.36896868244044073, 0.36827721401756763, 0.36780385917213154, 0.3674999919362447, 0.3673169863420191, 0.36720621642156714, 0.367119056207001, 0.36700687973043283, 0.36682106102397477, 0.3665129741197394, 0.36603399304983847, 0.36533549184638436, 0.3643688445414894, 0.36309719370257143, 0.3615307560382718, 0.3596915167925373, 0.35760146120931485, 0.3552825745325517, 0.35275684200619456, 0.3500462488741905, 0.3471727803804864, 0.34415842176902933, 0.34102515828376606, 0.33779497516864393, 0.33448985766760964, 0.33113179102461016, 0.3277427604835924, 0.32434475128850354, 0.3209558401421322, 0.31757846958263475, 0.3142111736070093, 0.3108524862122541, 0.30750094139536716, 0.3041550731533468, 0.30081341548319096, 0.29747450238189804, 0.29413686784646603, 0.29079904587389316, 0.28745957046117754, 0.2841169756053173, 0.2807697953033106, 0.27741656355215555, 0.2740558143488505, 0.27068608169039343, 0.2673058995737824, 0.26391380199601583, 0.26050832295409165, 0.2570879964450081, 0.2536513564657632, 0.2501969370133554, 0.24672327208478262, 0.24322889567704306, 0.23971234178713485, 0.23617214441205628, 0.23260683754880532, 0.22901495519438017, 0.22539503134577898, 0.22174559999999996],
        [0.35274332835285815, 0.36394071508259945, 0.3738682195521511, 0.38258402609690034, 0.3901463190522335, 0.396613282753538, 0.4020431015362005, 0.4064939597356079, 0.4100240416871474, 0.4126915317262057, 0.4145546141881698, 0.4156714734084267, 0.41610029372236307, 0.4158992594653661, 0.41512655497282247, 0.4138403645801193, 0.41209887262264344, 0.40996026343578185, 0.40748272135492136, 0.40472443071544895, 0.40174357585275156, 0.39859834110221604, 0.39534691079922946, 0.3920474692791786, 0.3887582008774504, 0.38553728992943187, 0.3824429207705099, 0.3795332777360712, 0.376866545161503, 0.3745009073821921, 0.3724945487335254, 0.3708876534417139, 0.36964840529626564, 0.36872698797751197, 0.368073585165785, 0.36763838054141645, 0.3673715577847383, 0.3672233005760821, 0.36714379259578, 0.3670832175241638, 0.36699175904156506, 0.36681960082831583, 0.36651692656474794, 0.36603391993119316, 0.36532076460798313, 0.3643276442754501, 0.36301699126981885, 0.36140023255088705, 0.35950104373434566, 0.35734310043588535, 0.3549500782711973, 0.35234565285597214, 0.3495534998059008, 0.3465972947366742, 0.3435007132639833, 0.3402874310035187, 0.3369811235709714, 0.3336054665820324, 0.3301841356523924, 0.32674080639774217, 0.323299154433773, 0.3198785400061937, 0.31648106188078606, 0.3131045034533507, 0.3097466481196876, 0.30640527927559685, 0.303078180316879, 0.2997631346393339, 0.29645792563876205, 0.29316033671096353, 0.2898681512517385, 0.2865791526568872, 0.2832911243222099, 0.28000184964350666, 0.27670911201657783, 0.27341069483722363, 0.2701043815012442, 0.2667879554044397, 0.26345919994261047, 0.26011589851155653, 0.2567558345070783, 0.2533767913249758, 0.24997655236104938, 0.24655290101109925, 0.24310362067092559, 0.23962649473632847, 0.2361193066031082, 0.23257983966706508, 0.22900587732399913, 0.2253952029697107, 0.22174559999999996],
        [0.3515008942257845, 0.3627911429833592, 0.37280265526489087, 0.38159408327671435, 0.38922407922516394, 0.39575129531657444, 0.40123438375728, 0.40573199675361543, 0.40930278651191504, 0.4120054052385136, 0.41389850513974535, 0.4150407384219452, 0.41549075729144724, 0.41530721395458625, 0.4145487606176967, 0.4132740494871131, 0.41154173276916994, 0.4094104626702016, 0.406938891396543, 0.40418567115452825, 0.4012094541504922, 0.3980688925907691, 0.39482263868169365, 0.3915293446296002, 0.3882476626408235, 0.3850362449216979, 0.38195374367855806, 0.3790588111177383, 0.37641009944557324, 0.37406626086839745, 0.3720859475925454, 0.37050954130933, 0.3693043416499782, 0.368419377730695, 0.3678036786676858, 0.3674062735771558, 0.3671761915753103, 0.3670624617783542, 0.3670141133024931, 0.3669801752639321, 0.36690967677887637, 0.3667516469635312, 0.3664551149341017, 0.3659691098067933, 0.3652426606978111, 0.3642247967233605, 0.36287726036717094, 0.3612126475830711, 0.35925626769241376, 0.3570334300165518, 0.35456944387683825, 0.35188961859462603, 0.34901926349126794, 0.345983687888117, 0.3428082011065261, 0.33951811246784813, 0.3361387312934361, 0.33269536690464296, 0.32921332862282143, 0.3257179257693245, 0.3222344676655053, 0.31878355720060314, 0.315366971535404, 0.31198178139858057, 0.3086250575188054, 0.30529387062475116, 0.3019852914450903, 0.2986963907084954, 0.29542423914363936, 0.2921659074791944, 0.28891846644383323, 0.2856789867662285, 0.28244453917505286, 0.27921219439897854, 0.27597902316667866, 0.27274209620682544, 0.26949848424809153, 0.26624525801914956, 0.2629794882486721, 0.2596982456653319, 0.2563986009978013, 0.253077624974753, 0.24973238832485967, 0.24635996177679384, 0.24295741605922808, 0.23952182190083493, 0.23605025003028704, 0.23253977117625704, 0.22898745606741744, 0.22539037543244086, 0.22174559999999996],
        [0.35021635301312054, 0.3615950260062806, 0.37168659114754654, 0.3805501441525221, 0.38824478073681096, 0.39482959661601696, 0.4003636875057439, 0.40490614912159545, 0.4085160771791753, 0.41125256739408733, 0.4131747154819355, 0.41434161715832324, 0.41481236813885447, 0.41464606413913285, 0.41390180087476225, 0.4126386740613463, 0.41091577941448887, 0.40879221264979354, 0.40632706948286434, 0.4035794456293049, 0.40060843680471897, 0.39747313872471024, 0.39423264710488265, 0.39094605766083973, 0.3876724661081855, 0.3844709681625236, 0.38140065953945773, 0.3785206359545917, 0.37588999312352916, 0.37356782676187394, 0.37161323258523005, 0.3700667782199802, 0.36889491893562576, 0.36804558191244663, 0.36746669433072315, 0.3671061833707359, 0.36691197621276495, 0.3668320000370906, 0.36681418202399324, 0.36680644935375306, 0.3667567292066504, 0.3666129487629656, 0.3663230352029789, 0.3658349157069706, 0.36509651745522087, 0.3640557676280103, 0.36267374970861316, 0.36096417239228196, 0.3589539006772622, 0.3566697995618008, 0.3541387340441436, 0.35138756912253727, 0.3484431697952276, 0.34533240106046126, 0.34208212791648435, 0.3387192153615431, 0.335270528393884, 0.3317629320117531, 0.3282232912133969, 0.32467847099706115, 0.32115533636099286, 0.3176756763818302, 0.3142409764497818, 0.3108476460334482, 0.3074920946014304, 0.30417073162232916, 0.3008799665647453, 0.29761620889727947, 0.29437586808853267, 0.2911553536071055, 0.287951074921599, 0.2847594415006137, 0.2815768628127505, 0.27839974832661024, 0.27522450751079375, 0.2720475498339016, 0.26886528476453475, 0.2656741217712941, 0.2624704703227802, 0.2592507398875941, 0.2560113399343364, 0.25274867993160793, 0.24945916934800955, 0.24613921765214206, 0.24278523431260618, 0.23939362879800272, 0.2359608105769325, 0.2324831891179964, 0.22895717388979497, 0.22537917436092927, 0.22174559999999996],
        [0.3488927092672677, 0.3603544864003168, 0.3705213936065115, 0.37945293822717957, 0.3872086276036485, 0.3938479690772457, 0.3994304699892991, 0.40401563768113613, 0.4076629794940843, 0.4104320027694717, 0.41238221484862553, 0.41357312307287364, 0.41406423478354315, 0.41391505732196215, 0.4131850980294582, 0.4119338642473587, 0.4102208633169915, 0.4081056025796839, 0.40564758937676393, 0.40290633104955864, 0.3999413349393964, 0.396812108387604, 0.39357815873550966, 0.3902989933244406, 0.3870341194957249, 0.3838430445906897, 0.3807852759506627, 0.37792032091697164, 0.3753076868309441, 0.37300688103390767, 0.37107741086719, 0.369560014900748, 0.3684203566190576, 0.36760533073522317, 0.3670618319623499, 0.36673675501354275, 0.3665769946019066, 0.3665294454405463, 0.3665410022425669, 0.3665585597210733, 0.3665290125891704, 0.3663992555599632, 0.3661161833465566, 0.3656266906620555, 0.36487767221956485, 0.36381602273218955, 0.3624022080081311, 0.3606509782359772, 0.3585906546994116, 0.3562495586821186, 0.35365601146778214, 0.3508383343400865, 0.3478248485827155, 0.3446438754793534, 0.34132373631368423, 0.33789275236939204, 0.33437924493016086, 0.33081153527967483, 0.327217944701618, 0.3236267944796744, 0.32006640589752827, 0.3165596822063446, 0.3131078545272126, 0.30970673594870257, 0.306352139559385, 0.3030398784478302, 0.2997657657026082, 0.2965256144122896, 0.29331523766544476, 0.2901304485506437, 0.28696706015645684, 0.2838208855714547, 0.2806877378842074, 0.27756343018328533, 0.27444377555725874, 0.271324587094698, 0.2682016778841733, 0.2650708610142552, 0.2619279495735138, 0.25876875665051946, 0.25558909533384255, 0.2523847787120534, 0.24915161987372222, 0.24588543190741946, 0.24258202790171532, 0.23923722094518013, 0.23584682412638427, 0.23240665053389803, 0.22891251325629164, 0.22536022538213552, 0.22174559999999993],
        [0.3475329675406277, 0.35907164641442074, 0.36930842904817945, 0.3783031950035431, 0.3861158238421502, 0.3928061951256405, 0.39843418841565265, 0.4030596832738258, 0.40674255926179875, 0.4095426959412109, 0.4115199728737011, 0.4127342696209086, 0.4132454657444722, 0.4131134408060311, 0.41239807436722414, 0.4111592459896905, 0.40945683523506926, 0.40735072166499947, 0.40490078484112024, 0.40216690432507035, 0.3992089596784891, 0.39608683046301535, 0.39286039624028823, 0.38958953657194684, 0.3863341310196303, 0.38315405914497747, 0.38010920050962743, 0.3772594346752192, 0.37466464120339193, 0.37238469965578463, 0.3704794895940363, 0.3689899020787173, 0.3678808741661235, 0.3670983544114817, 0.3665882913700191, 0.3662966335969628, 0.3661693296475396, 0.3661523280769767, 0.36619157744050124, 0.3662330262933399, 0.36622262319072013, 0.3661063166878687, 0.36583005534001284, 0.3653397877023795, 0.3645814623301956, 0.36350102777868837, 0.3620583839797101, 0.36026923637161506, 0.3581632417693825, 0.3557700569879919, 0.35311933884242297, 0.35024074414765516, 0.3471639297186677, 0.34391855237044033, 0.3405342689179523, 0.3370407361761833, 0.3334676109601127, 0.32984455008472, 0.32620121036498484, 0.32256724861588626, 0.31897232165240424, 0.3154403593306158, 0.3119723836709899, 0.30856368973509307, 0.305209572584492, 0.30190532728075337, 0.2986462488854437, 0.29542763246012965, 0.29224477306637814, 0.2890929657657555, 0.28596750561982853, 0.2828636876901637, 0.27977680703832797, 0.27670215872588766, 0.2736350378144095, 0.2705707393654603, 0.26750455844060655, 0.26443179010141493, 0.261347729409452, 0.2582476714262846, 0.25512691121347914, 0.25198074383260244, 0.24880446434522105, 0.24559336781290173, 0.242342749297211, 0.23904790385971555, 0.23570412656198206, 0.23230671246557708, 0.22885095663206725, 0.22533215412301938, 0.2217456],
        [0.3461401323856021, 0.3577486282975451, 0.3680490638789435, 0.3771016439844682, 0.3849665734687905, 0.391704057186581, 0.3973742999925113, 0.402037506741252, 0.4057538822874742, 0.40858363148584914, 0.4105869591910477, 0.411824070257741, 0.41235516954059986, 0.4122404618942957, 0.4115401521734992, 0.41031444523288146, 0.40862354592711353, 0.4065276591108667, 0.40408698963881173, 0.4013617423656196, 0.39841212214596167, 0.3952983338345087, 0.3920805822859318, 0.38881907235490193, 0.38557400889609034, 0.38240559676416797, 0.37937404081380566, 0.3765395458996747, 0.37396231687644593, 0.3717025585987906, 0.36982047592137957, 0.3683570904809711, 0.36727669104267274, 0.36652438315367875, 0.36604527236118345, 0.36578446421238187, 0.3656870642544681, 0.3656981780346368, 0.3657629111000825, 0.3658263689979997, 0.36583365727558287, 0.36572988148002644, 0.36546014715852526, 0.3649695598582735, 0.36420322512646564, 0.36310624851029644, 0.36163802633733544, 0.3598151180566532, 0.3576683738976953, 0.3552286440899073, 0.35252677886273504, 0.3495936284456239, 0.3464600430680198, 0.34315687295936814, 0.33971496834911485, 0.3361651794667054, 0.33253835654158526, 0.32886534980320054, 0.3251770094809965, 0.32150418580441864, 0.3178777290029131, 0.3143224924111136, 0.3108393417844069, 0.3074231459833687, 0.3040687738685738, 0.30077109430059784, 0.29752497614001594, 0.2943252882474035, 0.2911668994833357, 0.28804467870838774, 0.2849534947831351, 0.28188821656815277, 0.2788437129240164, 0.27581485271130085, 0.2727965047905818, 0.26978353802243427, 0.2667708212674336, 0.2637532233861551, 0.260725613239174, 0.25768285968706556, 0.25461983159040513, 0.2515313978097679, 0.24841242720572923, 0.24525778863886438, 0.24206235096974865, 0.2388209830589572, 0.2355285537670654, 0.23217993195464856, 0.2287699864822818, 0.22529358621054046, 0.2217456],
        [0.34471720835459224, 0.3563875542986427, 0.3667446645051968, 0.3758490146728114, 0.3837610805000426, 0.39054133768544724, 0.3962502619275819, 0.4009483289250028, 0.40469601437626695, 0.4075537939799306, 0.4095821434345504, 0.41084153843868293, 0.41139245469088487, 0.41129536788971244, 0.4106107537337223, 0.4093990879214713, 0.40772084615151544, 0.40563650412241187, 0.40320653753271674, 0.4004914220809868, 0.3975516334657786, 0.3944476473856485, 0.39123993953915337, 0.3879889856248493, 0.3847552613412934, 0.38159924238704196, 0.37858140446065136, 0.37576222326067843, 0.3732021744856796, 0.3709617338342114, 0.3691013770048305, 0.36766223083459293, 0.3666080267145547, 0.3658831471742705, 0.36543197474329586, 0.36519889195118604, 0.36512828132749625, 0.3651645254017817, 0.3652520067035976, 0.3653351077624993, 0.3653582111080418, 0.36526569926978064, 0.3650019547772712, 0.36451136016006824, 0.36373829794772733, 0.3626271506698036, 0.36113688379499237, 0.35928479454854956, 0.3571027630948703, 0.35462266959835076, 0.35187639422338673, 0.3488958171343737, 0.34571281849570745, 0.34235927847178366, 0.3388670772269981, 0.33526809492574644, 0.3315942117324245, 0.3278773078114279, 0.3241492633271523, 0.32044195844399365, 0.3167872733263475, 0.31321086610430715, 0.3097135067707569, 0.30628974328427827, 0.3029341236034529, 0.29964119568686276, 0.2964055074930893, 0.29322160698071437, 0.29008404210831973, 0.2869873608344869, 0.28392611111779764, 0.2808948409168337, 0.2778880981901769, 0.2749004308964088, 0.271926386994111, 0.2689605144418655, 0.2659973611982538, 0.26303147522185766, 0.26005740447125875, 0.25706969690503884, 0.25406290048177954, 0.2510315631600627, 0.24797023289846987, 0.244873457655583, 0.24173578538998353, 0.23855176406025325, 0.23531594162497393, 0.23202286604272732, 0.22866708527209487, 0.2252431472716585, 0.22174559999999993],
        [0.34326720000000016, 0.35499054666666685, 0.36539659733333346, 0.3745460365714288, 0.38249954895238114, 0.38931781904761925, 0.3950615314285716, 0.39979137066666687, 0.4035680213333333, 0.40645216800000006, 0.40850449523809534, 0.40978568761904777, 0.4103564297142858, 0.4102774060952382, 0.4096093013333334, 0.40841280000000013, 0.4067485866666667, 0.40467734590476195, 0.40225976228571436, 0.3995565203809524, 0.39662830476190475, 0.3935358, 0.39033969066666657, 0.3871006613333332, 0.38387939657142855, 0.3807365809523809, 0.3777328990476191, 0.3749290354285715, 0.3723856746666667, 0.3701635013333333, 0.3683232, 0.36690597386666657, 0.3658751006476191, 0.3651743766857143, 0.36474759832380954, 0.36453856190476186, 0.3644910637714286, 0.3645489002666666, 0.36465586773333336, 0.36475576251428576, 0.3647923809523809, 0.36470951939047613, 0.36445097417142863, 0.3639605416380953, 0.36318201813333334, 0.3620592000000001, 0.36055070506666675, 0.3586744371047621, 0.35646312137142866, 0.3539494831238095, 0.35116624761904763, 0.34814614011428574, 0.34492188586666667, 0.3415262101333333, 0.3379918381714287, 0.33435149523809526, 0.3306379065904762, 0.32688379748571433, 0.32312189318095236, 0.3193849189333333, 0.3157056, 0.3121102650666667, 0.30859965653333327, 0.3051681202285714, 0.30181000198095237, 0.29851964761904753, 0.29529140297142853, 0.2921196138666665, 0.28899862613333327, 0.2859227855999999, 0.2828864380952381, 0.2798839294476189, 0.27690960548571425, 0.27395781203809516, 0.2710228949333332, 0.2680991999999999, 0.2651810730666666, 0.2622628599619047, 0.25933890651428565, 0.2564035585523809, 0.2534511619047618, 0.2504760623999999, 0.24747260586666656, 0.24443513813333323, 0.24135800502857135, 0.23823555238095234, 0.23506212601904755, 0.23183207177142856, 0.22853973546666662, 0.22517946293333327, 0.22174559999999996],
        [0.3417924899923059, 0.3535593269525238, 0.36400601831240453, 0.3731933898967771, 0.38118226753047035, 0.3880334770383138, 0.39380784424513593, 0.3985661949757659, 0.4023693550550331, 0.40527815030776604, 0.4073534065587942, 0.4086559496329465, 0.40924660535505153, 0.40918619954993884, 0.4085355580424373, 0.40735550665737585, 0.40570687121958343, 0.4036504775538894, 0.40124715148512263, 0.3985577188381119, 0.39564300543768666, 0.3925638371086757, 0.3893810396759081, 0.3861554389642126, 0.38294786079841886, 0.37981913100335535, 0.3768300754038513, 0.3740415198247357, 0.37151429009083764, 0.3693092120269862, 0.36748711145801005, 0.3660892364814668, 0.3650785242858255, 0.3643983343322838, 0.36399202608203923, 0.36380295899628917, 0.3637744925362315, 0.3638499861630631, 0.36397279933798193, 0.3640862915221854, 0.36413382217687107, 0.3640587507632362, 0.3638044367424786, 0.3633142395757956, 0.3625315187243847, 0.36139963364944355, 0.35987694551471877, 0.35798182229415326, 0.3557476336642397, 0.35320774930147014, 0.35039553888233727, 0.3473443720833331, 0.34408761858095027, 0.34065864805168083, 0.3370908301720173, 0.3334175346184518, 0.3296721310674769, 0.3258879891955848, 0.32209847867926794, 0.3183369691950186, 0.31463683041932905, 0.3110249158049128, 0.3075020139093675, 0.304062397066512, 0.30070033761016507, 0.2974101078741453, 0.294185980192272, 0.2910222268983633, 0.2879131203262384, 0.2848529328097161, 0.281835936682615, 0.27885640427875397, 0.275908607931952, 0.27298681997602736, 0.27008531274479936, 0.26719835857208657, 0.26432022979170783, 0.2614451987374819, 0.25856753774322755, 0.25568151914276366, 0.25278141526990877, 0.24986149845848205, 0.24691604104230197, 0.24393931535518754, 0.2409255937309574, 0.23786914850343047, 0.23476425200642537, 0.23160517657376098, 0.22838619453925604, 0.22510157823672947, 0.22174559999999993],
        [0.34029297347430465, 0.35209401391493533, 0.36257324156209403, 0.3717915577197168, 0.3798098636917391, 0.3866890607820968, 0.39249005029472567, 0.3972737335335612, 0.4011010118025393, 0.40403278640559576, 0.4061299586466663, 0.40745342982968663, 0.4080641012585921, 0.40802287423731887, 0.4073906500698024, 0.4062283300599787, 0.40459681551178334, 0.402557007729152, 0.4001698080160204, 0.3974961176763245, 0.3945968380139997, 0.39153287033298173, 0.3883651159372066, 0.38515447613060966, 0.3819618522171272, 0.37884814550069446, 0.37587425728524726, 0.37310108887472127, 0.37058954157305246, 0.36840051668417634, 0.36659491551202866, 0.3652140002920344, 0.3642204769855758, 0.36355741248552376, 0.36316787368474956, 0.3629949274761248, 0.3629816407525206, 0.36307108040680813, 0.36320631333185877, 0.36333040642054365, 0.3633864265657341, 0.3633174406603014, 0.36306651559711695, 0.36257671826905175, 0.36179111556897714, 0.36065277438976456, 0.35911988709500936, 0.35721114793120545, 0.3549603766155705, 0.3524013928653224, 0.3495680163976792, 0.34649406692985896, 0.34321336417907927, 0.3397597278625581, 0.3361669776975135, 0.33246893340116346, 0.32869941469072567, 0.3248922412834184, 0.3210812328964592, 0.3173002092470661, 0.31358299005245716, 0.3099568122267728, 0.30642258147184387, 0.30297462068642417, 0.29960725276926703, 0.2963148006191261, 0.29309158713475486, 0.289931935214907, 0.2868301677583358, 0.28378060766379526, 0.28077757783003854, 0.2778154011558193, 0.2748884005398911, 0.27199089888100736, 0.269117219077922, 0.2662616840293883, 0.26341861663415983, 0.26058233979099016, 0.25774717639863276, 0.2549074493558413, 0.2520574815613692, 0.24919159591397022, 0.24630411531239776, 0.24338936265540545, 0.24044166084174673, 0.23745533277017525, 0.2344247013394444, 0.2313440894483081, 0.22820781999551937, 0.22501021587983216, 0.22174559999999996],
        [0.3387679237068705, 0.35059432561457654, 0.36109837074474416, 0.3703409738247089, 0.37838304958180613, 0.3852855127433714, 0.39110927803674017, 0.39591526018924744, 0.3997643739282291, 0.40271753398102067, 0.4048356550749571, 0.40617965193737443, 0.4068104392956075, 0.40678893187699217, 0.40617604440886357, 0.40503269161855726, 0.40341978823340874, 0.40139824898075327, 0.3990289885879267, 0.3963729217822639, 0.3934909632911007, 0.3904440278417723, 0.38729303016161437, 0.3840988849779621, 0.3809225070181511, 0.37782481100951676, 0.3748667116793943, 0.3721091237551196, 0.36961296196402776, 0.3674391410334542, 0.3656485756907346, 0.36428251308860193, 0.36330353008138155, 0.36265453594879576, 0.36227843997056725, 0.3621181514264193, 0.36211657959607435, 0.36221663375925517, 0.36236122319568465, 0.3624932571850851, 0.36255564500717996, 0.36249129594169144, 0.36224311926834263, 0.36175402426685616, 0.3609669202169546, 0.3598247163983611, 0.35828551841177525, 0.35636821714180555, 0.3541068997940376, 0.3515356535740564, 0.3486885656874482, 0.345599723339798, 0.3423032137366916, 0.3388331240837143, 0.3352235415864516, 0.331508553450489, 0.3277222468814123, 0.3238987090848067, 0.32007202726625794, 0.3162762886313512, 0.3125455803856723, 0.3089073900902249, 0.30536280672768495, 0.3019063196361467, 0.2985324181537048, 0.2952355916184535, 0.292010329368487, 0.28885112074189956, 0.2857524550767858, 0.2827088217112399, 0.2797147099833561, 0.2767646092312289, 0.27385300879295243, 0.2709743980066211, 0.2681232662103294, 0.2652941027421713, 0.2624813969402414, 0.25967963814263406, 0.2568833156874433, 0.25408691891276386, 0.2512849371566897, 0.24847185975731542, 0.2456421760527352, 0.24279037538104345, 0.23991094708033436, 0.23699838048870236, 0.23404716494424183, 0.2310517897850469, 0.22800674434921214, 0.22490651797483163, 0.22174559999999993],
        [0.3372166139508772, 0.34905998011212275, 0.3595815095226968, 0.3688420719962146, 0.37690253734629087, 0.38382377538654044, 0.38966665593057853, 0.39449204879201977, 0.3983608237844792, 0.40133385072157185, 0.4034719994169127, 0.40483613968411636, 0.40548714133679803, 0.40548587418857246, 0.40489320805305473, 0.40377001274385965, 0.4021771580746021, 0.4001755138588972, 0.39782594991035974, 0.39518933604260476, 0.39232654206924716, 0.3892984378039016, 0.3861658930601833, 0.38298977765170716, 0.37983096139208805, 0.376750314094941, 0.37380870557388063, 0.37106700564252215, 0.36858608411448046, 0.3664268108033703, 0.3646500555228069, 0.36329702266140174, 0.3623302549077546, 0.3616926295254615, 0.3613270237781189, 0.3611763149293231, 0.36118338024267055, 0.36129109698175743, 0.36144234241018, 0.36157999379153466, 0.3616469283894178, 0.3615860234674258, 0.36134015628915483, 0.36085220411820124, 0.36006504421816127, 0.35892155385263147, 0.35737982806925217, 0.35545883305184023, 0.35319275276825657, 0.3506157711863623, 0.34776207227401823, 0.34466583999908573, 0.3413612583294253, 0.3378825112328982, 0.33426378267736534, 0.33053925663068773, 0.3267431170607264, 0.3229095479353423, 0.31907273322239643, 0.31526685688974954, 0.3115261029052631, 0.30787808515324755, 0.3043241371838128, 0.3008590224635188, 0.297477504458925, 0.2941743466365915, 0.2909443124630776, 0.28778216540494334, 0.28468266892874833, 0.28164058650105245, 0.2786506815884154, 0.27570771765739666, 0.27280645817455634, 0.26994166660645375, 0.26710810641964894, 0.2643005410807016, 0.26151373405617145, 0.2587424488126181, 0.25598144881660145, 0.25322549753468104, 0.2504693584334167, 0.24770779497936826, 0.24493557063909532, 0.2421474488791578, 0.23933819316611524, 0.2365025669665273, 0.23363533374695394, 0.2307312569739548, 0.22778510011408953, 0.224791626633918, 0.2217455999999999],
        [0.33563831746719897, 0.34749069546824946, 0.3580227615582945, 0.3672952860186954, 0.37536903913081243, 0.3823047911760073, 0.3881633124356407, 0.39300537319107337, 0.39689174372366665, 0.39988319431478137, 0.40204049524577856, 0.40342441679801916, 0.40409572925286397, 0.4041152028916742, 0.40354360799581074, 0.40244171484663444, 0.40087029372550637, 0.3988901149137876, 0.396561948692839, 0.39394656534402156, 0.3911047351486963, 0.3880972283882241, 0.38498481534396595, 0.3818282662972829, 0.37868835152953595, 0.375625841322086, 0.3727015059562938, 0.3699761157135208, 0.36751044087512763, 0.36536525172247525, 0.36360131853692484, 0.3622597768006664, 0.3613032227992072, 0.36067461801888334, 0.36031692394603126, 0.36017310206698716, 0.3601861138680875, 0.36029892083566845, 0.36045448445606615, 0.3605957662156173, 0.3606657276006579, 0.36060733009752427, 0.3603635351925528, 0.35987730437207993, 0.3590915991224416, 0.3579493809299743, 0.3564088046716767, 0.3544887987871967, 0.3522234851068444, 0.34964698546093026, 0.3467934216797644, 0.34369691559365717, 0.34039158903291866, 0.33691156382785925, 0.3332909618087892, 0.3295639048060186, 0.32576451464985784, 0.32192691317061706, 0.31808522219860674, 0.3142735635641368, 0.3105260590975178, 0.30687033317381934, 0.3033080203471504, 0.2998342577163794, 0.2964441823803744, 0.293132931438004, 0.2898956419881366, 0.2867274511296405, 0.28362349596138403, 0.28057891358223574, 0.2775888410910639, 0.2746484155867371, 0.2717527741681234, 0.2688970539340913, 0.2660763919835093, 0.26328592541524576, 0.26052079132816885, 0.2577761268211472, 0.2550470689930491, 0.25232875494274287, 0.24961632176909704, 0.24690490657097983, 0.2441896464472597, 0.24146567849680511, 0.23872813981848434, 0.23597216751116581, 0.23319289867371787, 0.23038547040500898, 0.2275450198039074, 0.22466668396928158, 0.22174559999999993],
        [0.33403230751670954, 0.34588618974363183, 0.3564222305138792, 0.365701049676612, 0.3737832670809904, 0.38072950257617494, 0.3866003760113259, 0.39145650723560355, 0.3953585160981684, 0.3983670224481807, 0.4005426461348006, 0.4019460070071889, 0.4026377249145056, 0.40267841970591106, 0.40212871123056587, 0.40104921933762994, 0.3995005638762639, 0.3975433646956282, 0.39523824164488297, 0.3926458145731886, 0.3898267033297055, 0.3868415277635939, 0.3837509077240143, 0.3806154630601269, 0.3774958136210922, 0.37445257925607034, 0.3715463798142219, 0.3688378351447068, 0.36638756509668596, 0.3642561895193193, 0.3625043282617675, 0.36117302329662815, 0.36022500509025107, 0.359603426232423, 0.35925143931293096, 0.35911219692156204, 0.35912885164810326, 0.35924455608234157, 0.359402462814064, 0.3595457244330576, 0.35961749352910954, 0.3595609226920066, 0.35931916451153606, 0.3588353715774846, 0.3580526964796395, 0.3569142918077878, 0.35537843682328485, 0.3534639174737617, 0.35120464637841725, 0.3486345361564504, 0.34578749942706094, 0.34269744880944764, 0.33939829692280965, 0.3359239563863464, 0.33230833981925706, 0.3285853598407405, 0.3247889290699963, 0.3209529601262234, 0.31711136562862097, 0.3132980581963883, 0.30954695044872466, 0.30588556990991894, 0.30231590372462014, 0.29883355394256744, 0.2954341226134994, 0.29211321178715494, 0.28886642351327324, 0.2856893598415929, 0.28257762282185284, 0.2795268145037921, 0.2765325369371495, 0.2735903921716638, 0.2706959822570742, 0.26784490924311927, 0.2650327751795381, 0.26225518211606974, 0.2595077321024526, 0.25678602718842586, 0.2540856694237285, 0.2514022608580993, 0.24873140354127707, 0.2460686995230008, 0.24340975085300942, 0.24075015958104176, 0.2380855277568368, 0.23541145743013334, 0.23272355065067027, 0.23001740946818652, 0.2272886359324209, 0.22453283209311242, 0.2217456],
        [0.33239785736028277, 0.34424618099894505, 0.35478002005179277, 0.3640597967544257, 0.37214593334244345, 0.37909885205144606, 0.38497897511703333, 0.389846724774805, 0.39376252326036076, 0.3967867928093007, 0.3989799556572245, 0.40040243403973197, 0.4011146501924229, 0.401177026350897, 0.4006499847507543, 0.3995939476275944, 0.39806933721701715, 0.39613657575462247, 0.3938560854760102, 0.39128828861677994, 0.3884936074125317, 0.3855324640988651, 0.38246528091138016, 0.37935248008567657, 0.3762544838573541, 0.37323171446201275, 0.370344594135252, 0.36765354511267206, 0.36521898962987226, 0.36310134992245285, 0.36136104822601345, 0.36003900993951937, 0.35909817311539804, 0.35848197896944206, 0.35813386871744457, 0.35799728357519806, 0.35801566475849567, 0.35813245348313005, 0.35829109096489403, 0.35843501841958053, 0.35850767706298226, 0.35845250811089224, 0.3582129527791031, 0.35773245228340783, 0.356954447839599, 0.35582238066346983, 0.3542947131283129, 0.3523899922374221, 0.3501417861515909, 0.3475836630316129, 0.34474919103828205, 0.341671938332392, 0.33838547307473643, 0.3349233634261086, 0.3313191775473029, 0.3276064835991124, 0.32381884974233116, 0.319989844137753, 0.31615303494617103, 0.3123419903283794, 0.30859027844517184, 0.3049252311195243, 0.3013492348231444, 0.2978584396899219, 0.2944489958537465, 0.2911170534485083, 0.28785876260809706, 0.2846702734664026, 0.2815477361573149, 0.2784873008147239, 0.2754851175725193, 0.27253733656459106, 0.26964010792482923, 0.2667895817871233, 0.26398190828536355, 0.2612132375534396, 0.2584797197252413, 0.25577750493465873, 0.2531027433155816, 0.2504515850018999, 0.24782018012750334, 0.245204678826282, 0.2426012312321256, 0.24000598747892418, 0.2374150977005674, 0.23482471203094532, 0.23223098060394778, 0.2296300535534646, 0.22701808101338558, 0.22439121311760077, 0.2217456],
        [0.3307342402587927, 0.3425703872948645, 0.3530962338343775, 0.3623719610365977, 0.370457750060791, 0.37741378206622406, 0.38330023821216264, 0.38817729965787295, 0.3921051475626211, 0.39514396308567346, 0.39735392738629594, 0.3987952216237548, 0.3995280269573161, 0.39961252454624613, 0.3991088955498106, 0.3980773211272763, 0.39657798243790876, 0.3946710606409745, 0.39241673689573975, 0.3898751923614702, 0.3871066081974324, 0.38417116556289216, 0.3811290456171159, 0.3780404295193696, 0.37496549842891963, 0.3719644335050319, 0.3690974159069724, 0.3664246267940077, 0.3640062473254037, 0.3619024586604265, 0.3601734419583423, 0.35885998451957246, 0.35792529820916, 0.3573132010333027, 0.35696751099819873, 0.35683204611004604, 0.3568506243750429, 0.3569670637993873, 0.3571251823892772, 0.35726879815091084, 0.3573417290904859, 0.35728779321420084, 0.3570508085282536, 0.3565745930388422, 0.3558029647521646, 0.3546797416744191, 0.3531636221909971, 0.3512728262040649, 0.34904045399498207, 0.346499605845108, 0.3436833820358027, 0.3406248828484257, 0.3373572085643365, 0.33391345946489503, 0.3303267358314608, 0.3266301379453935, 0.32285676608805264, 0.31903972054079793, 0.3152121015849891, 0.31140700950198574, 0.30765754457314765, 0.30399075256061425, 0.3004094611496456, 0.2969104435062817, 0.2934904727965624, 0.2901463221865278, 0.2868747648422176, 0.2836725739296718, 0.2805365226149307, 0.27746338406403387, 0.2744499314430213, 0.271492937917933, 0.2685891766548089, 0.26573542081968904, 0.2629284435786134, 0.26016501809762177, 0.2574419175427541, 0.2547559150800504, 0.2521037838755506, 0.2494822970952947, 0.2468882279053225, 0.24431834947167422, 0.24176943496038958, 0.23923825753750866, 0.23672159036907128, 0.23421620662111747, 0.23171887945968722, 0.22922638205082038, 0.2267354875605569, 0.22424296915493672, 0.22174559999999996],
        [0.32904072947311336, 0.34085852669206557, 0.35137097552397556, 0.36063797630758915, 0.36871942938165253, 0.3756752350849118, 0.38156529375611314, 0.38644950573400266, 0.3903877713573262, 0.3934399909648303, 0.39566606489526074, 0.397125893487364, 0.3978793770798856, 0.3979864160115722, 0.3975069106211696, 0.39650076124742406, 0.39502786822908154, 0.3931481319048881, 0.3909214526135903, 0.38840773069393364, 0.3856668664846647, 0.3827587603245293, 0.3797433125522737, 0.3766804235066438, 0.3736299935263862, 0.3706519229502465, 0.36780611211697095, 0.3651524613653058, 0.36275087103399695, 0.36066124146179057, 0.35894347298743284, 0.35763819482702, 0.3567089517060491, 0.3561000172273667, 0.3557556649938203, 0.35562016860825685, 0.35563780167352343, 0.355752837792467, 0.3559095505679346, 0.3560522136027733, 0.35612510049983015, 0.35607248486195214, 0.35583864029198664, 0.3553678403927803, 0.35460435876718027, 0.35349246901803383, 0.3519911526155737, 0.350118222499577, 0.34790619947720675, 0.3453876043556257, 0.3425949579419972, 0.33956078104348375, 0.33631759446724874, 0.33289791902045485, 0.3293342755102652, 0.3256591847438426, 0.3219051675283502, 0.3181047446709508, 0.3142904369788074, 0.31049476525908287, 0.3067502503189405, 0.3030835699911672, 0.2994980302110465, 0.29599109393948614, 0.2925602241373938, 0.2892028837656775, 0.28591653578524456, 0.2826986431570028, 0.2795466688418602, 0.27645807580072435, 0.27343032699450287, 0.27046088538410357, 0.2675472139304341, 0.2646867755944022, 0.2618770333369157, 0.25911545011888243, 0.25639948890120967, 0.25372661264480556, 0.2510942843105776, 0.24849996685943362, 0.24594112325228132, 0.24341521645002842, 0.24091970941358265, 0.23845206510385178, 0.23600974648174344, 0.23359021650816544, 0.23119093814402542, 0.22880937435023113, 0.22644298808769028, 0.22408924231731067, 0.22174559999999996],
        [0.32731659826411835, 0.3391103172512234, 0.3496043487829288, 0.3588582763518612, 0.36693168345064686, 0.3738841535719123, 0.37977527020828417, 0.3846646168523889, 0.3886117769968528, 0.3916763341343026, 0.3939178717573647, 0.3953959733586654, 0.39617022243083144, 0.39630020246648917, 0.3958454969582651, 0.39486568939878575, 0.39342036328067737, 0.3915691020965668, 0.3893714893390804, 0.38688710850084457, 0.38417554307448576, 0.3812963765526306, 0.37830919242790545, 0.3752735741929367, 0.3722491053403512, 0.3692953693627751, 0.3664719497528351, 0.36383843000315735, 0.36145439360636866, 0.3593794240550955, 0.3576731048419642, 0.356375888652094, 0.35545170494057665, 0.35484535235499587, 0.3545016295429358, 0.3543653351519807, 0.3543812678297148, 0.354494226223722, 0.3546490089815866, 0.3547904147508927, 0.3548632421792243, 0.3548122899141658, 0.35458235660330123, 0.3541182408942146, 0.35336474143449015, 0.3522666568717121, 0.35078329300627864, 0.34893198424984534, 0.3467445721668812, 0.3442528983218562, 0.3414888042792399, 0.3384841316035014, 0.3352707218591106, 0.33188041661053685, 0.3283450574222497, 0.32469648585871863, 0.32096654348441334, 0.3171870718638031, 0.3133899125613576, 0.3096069071415462, 0.3058698971688388, 0.30220511916916143, 0.2986163895142692, 0.29510191953737375, 0.29165992057168716, 0.2882886039504209, 0.2849861810067872, 0.2817508630739974, 0.2785808614852638, 0.27547438757379783, 0.2724296526728115, 0.2694448681155165, 0.26651824523512496, 0.26364799536484823, 0.2608323298378985, 0.2580694599874875, 0.2553575971468269, 0.25269495264912867, 0.25007973782760456, 0.2475101640154664, 0.24498444254592605, 0.24250078475219528, 0.2400574019674859, 0.23765250552500983, 0.23528430675797873, 0.23295101699960447, 0.23065084758309895, 0.22838200984167395, 0.22614271510854114, 0.2239311747169126, 0.22174559999999996],
        [0.32556111989268194, 0.3373254770330133, 0.34779645727357966, 0.35703329495387504, 0.36509522441339326, 0.3720414799916288, 0.3779312960280753, 0.382823906862227, 0.38677854683357776, 0.3898544502816219, 0.3921108515458533, 0.393606984965766, 0.3944020848808539, 0.3945553856306112, 0.3941261215545319, 0.39317352699211006, 0.3917568362828396, 0.3899352837662146, 0.3877681037817292, 0.3853145306688773, 0.38263379876715303, 0.3797851424160503, 0.37682779595506344, 0.373820993723686, 0.37082397006141254, 0.3678959593077368, 0.36509619580215275, 0.3624839138841546, 0.3601183478932362, 0.3580587321688918, 0.3563643010506153, 0.35507531378502727, 0.3541561292472551, 0.35355213121955215, 0.35320870348417205, 0.3530712298233685, 0.3530850940193954, 0.3531956798545061, 0.3533483711109544, 0.35348855157099396, 0.35356160501687844, 0.3535129152308614, 0.3532878659951968, 0.3528318410921379, 0.3520902243039385, 0.3510083994128525, 0.3495460319673485, 0.3477199145807566, 0.3455611216326221, 0.34310072750248977, 0.3403698065699053, 0.33739943321441385, 0.3342206818155604, 0.3308646267528903, 0.3273623424059488, 0.32374490315428095, 0.3200433833774322, 0.3162888574549475, 0.3125123997663722, 0.3087450846912514, 0.30501798660913054, 0.30135683585257556, 0.29776598656623643, 0.294244448847784, 0.29079123279488894, 0.28740534850522254, 0.28408580607645517, 0.2808316156062578, 0.27764178719230154, 0.274515330932257, 0.27145125692379496, 0.2684485752645864, 0.26550629605230214, 0.262623429384613, 0.25979898535918977, 0.25703197407370354, 0.2543214056258248, 0.25166629011322467, 0.24906563763357376, 0.2465184582845431, 0.24402376216380348, 0.2415805593690257, 0.2391878599978807, 0.23684467414803925, 0.23455001191717229, 0.23230288340295052, 0.23010229870304483, 0.2279472679151261, 0.22583680113686508, 0.22376990846593275, 0.22174559999999993],
        [0.3237735676196781, 0.3355037240981107, 0.3459474046582702, 0.35516346589809195, 0.3632107644155114, 0.37014815680846425, 0.37603449967488606, 0.3809286496127122, 0.38488946321987827, 0.38797579709432, 0.39024650783397274, 0.39176045203677207, 0.3925764863006533, 0.39275346722355237, 0.3923502514034045, 0.39142569543814537, 0.39003865592571035, 0.3882479894640352, 0.38611255265105543, 0.3836912020847065, 0.3810427943629238, 0.3782261860836431, 0.3753002338447999, 0.37232379424432954, 0.3693557238801677, 0.36645487935024995, 0.3636801172525118, 0.3610902941848887, 0.35874426674531634, 0.35670089153173, 0.3550190251420655, 0.3537387180160522, 0.3528247959605963, 0.3522232786243974, 0.3518801856561556, 0.351741536704571, 0.3517533514183433, 0.3518616494461727, 0.352012450436759, 0.3521517740388021, 0.352225639901002, 0.3521800676720587, 0.3519610770006725, 0.3515146875355428, 0.3507869189253697, 0.34972379081885324, 0.34828535810301936, 0.3464878166181981, 0.3443613974430451, 0.3419363316562165, 0.3392428503363682, 0.33631118456215625, 0.3331715654122363, 0.3298542239652644, 0.3263893912998966, 0.3228072984947884, 0.3191381766285962, 0.3154122567799759, 0.31165977002758305, 0.3079109474500738, 0.3041960201261044, 0.30054015579938814, 0.29694826887387066, 0.2934202104185556, 0.2899558315024462, 0.2865549831945459, 0.28321751656385813, 0.27994328267938634, 0.2767321326101339, 0.27358391742510435, 0.2704984881933009, 0.26747569598372706, 0.2645153918653865, 0.2616174269072821, 0.25878165217841764, 0.25600791874779666, 0.25329607768442225, 0.25064598005729805, 0.24805747693542735, 0.2455304193878136, 0.24306465848346023, 0.24066004529137067, 0.23831643088054838, 0.23603366631999667, 0.23381160267871912, 0.23165009102571898, 0.2295489824299997, 0.22750812796056477, 0.22552737868641756, 0.22360658567656141, 0.2217456],
        [0.3219532147059805, 0.3336447765071909, 0.34405729459934226, 0.3532492229689728, 0.36127901560261994, 0.3682051264868215, 0.3740860096081155, 0.37898011895303924, 0.38294590850813076, 0.38604183225992794, 0.38832634419496836, 0.3898578982997896, 0.3906949485609297, 0.3908959489649263, 0.390519353498317, 0.3896236161476399, 0.3882671908994324, 0.38650853174023236, 0.3844060926565777, 0.382018327635006, 0.3794036906620551, 0.37662063572426274, 0.3737276168081666, 0.3707830879003044, 0.3678455029872142, 0.36497331605543337, 0.36222498109149975, 0.35965895208195137, 0.35733368301332563, 0.35530762787216047, 0.3536392406449936, 0.35236834913540094, 0.35146027641511196, 0.35086171937289345, 0.35051937489751317, 0.3503799398777384, 0.3503901112023365, 0.35049658576007486, 0.35064606043972074, 0.35078523213004154, 0.3508607977198046, 0.35081945409777726, 0.35060789815272725, 0.3501728267734215, 0.34946093684862745, 0.3484189252671126, 0.3470072600175273, 0.3452414934880564, 0.34315094916676686, 0.34076495054172645, 0.3381128211010029, 0.33522388433266354, 0.3321274637247761, 0.3288528827654079, 0.3254294649426267, 0.3218865337445, 0.3182534126590953, 0.31455942517448027, 0.3108338947787224, 0.3071061449598891, 0.30340549920604826, 0.29975651476757736, 0.29616468394409434, 0.29263073279752755, 0.289155387389805, 0.28573937378285497, 0.28238341803860545, 0.27908824621898476, 0.2758545843859209, 0.2726831586013422, 0.2695746949271768, 0.2665299194253526, 0.263549558157798, 0.2606343371864411, 0.25778498257321003, 0.25500222038003295, 0.25228677666883803, 0.24963937750155335, 0.24706074894010713, 0.24455161704642756, 0.2421127078824427, 0.2397447475100808, 0.2374484619912699, 0.23522457738793834, 0.23307381976201405, 0.2309969151754254, 0.22899458969010034, 0.22706756936796713, 0.22521658027095384, 0.2234423484609888, 0.2217456],
        [0.3200993344124631, 0.3317483523209287, 0.3421262307591381, 0.3512909999509789, 0.35930069012033816, 0.3662133314911039, 0.3720869542871632, 0.37697958873240356, 0.3809492650507124, 0.38405401346597734, 0.38635186420208584, 0.38790084748292536, 0.38875899353238325, 0.38898433257434695, 0.38863489483270397, 0.3877687105313419, 0.3864438098941479, 0.38471822314500964, 0.3826499805078148, 0.38029711220645046, 0.3777176484648042, 0.37496961950676344, 0.3721110555562158, 0.3691999868370486, 0.36629444357314944, 0.36345245598840553, 0.3607320543067046, 0.35819126875193397, 0.35588812954798116, 0.35388066691873354, 0.35222691108807863, 0.35096645493330597, 0.3500651419453138, 0.34947037826840216, 0.34912957004687134, 0.34899012342502156, 0.34899944454715315, 0.34910493955756605, 0.3492540146005607, 0.3493940758204372, 0.34947252936149586, 0.34943678136803685, 0.3492342379843604, 0.34881230535476687, 0.348118389623556, 0.3470998969350286, 0.3457177263151087, 0.34398674831621845, 0.3419353263724035, 0.33959182391771, 0.33698460438618383, 0.33414203121187114, 0.3310924678288179, 0.32786427767106996, 0.3244858241726736, 0.3209854707676745, 0.31739158089011904, 0.31373251797405277, 0.31003664545352205, 0.30633232676257255, 0.3026479253352506, 0.29900734851512173, 0.2954166792838299, 0.2918775445325389, 0.2883915711524121, 0.28496038603461354, 0.2815856160703067, 0.27826888815065515, 0.2750118291668229, 0.27181606600997327, 0.26868322557127006, 0.26561493474187686, 0.2626128204129575, 0.2596785094756756, 0.2568136288211947, 0.2540198053406786, 0.2512986659252909, 0.24865183746619532, 0.24608094685455542, 0.24358762098153494, 0.2411734867382975, 0.2388401710160069, 0.23658930070582668, 0.23442250269892054, 0.23234140388645216, 0.2303476311595852, 0.22844281140948333, 0.2266285715273102, 0.2249065384042295, 0.2232783389314048, 0.22174559999999993],
        [0.3182112000000001, 0.32981416960000004, 0.3401543168000001, 0.3492892306285716, 0.3572765001142857, 0.3641737142857143, 0.3700384621714286, 0.3749283328000001, 0.3789009152, 0.3820137984, 0.3843245714285714, 0.38589082331428576, 0.38677014308571434, 0.38702011977142853, 0.3866983424, 0.38586240000000005, 0.38456988159999994, 0.38287837622857135, 0.38084547291428555, 0.3785287606857141, 0.37598582857142854, 0.37327426559999993, 0.37045166079999986, 0.3675756031999998, 0.3647036818285713, 0.3618934857142856, 0.3592026038857142, 0.3566886253714285, 0.35440913919999983, 0.3524217343999999, 0.3507839999999999, 0.3495352831999999, 0.34864196388571417, 0.3480521801142856, 0.3477140699428569, 0.3475757714285713, 0.3475854226285714, 0.3476911615999999, 0.3478411263999999, 0.3479834550857142, 0.34806628571428555, 0.34803775634285705, 0.3478460050285714, 0.3474391698285715, 0.34676538879999985, 0.34577279999999994, 0.34442274559999997, 0.34272938422857147, 0.3407200786285714, 0.3384221915428571, 0.33586308571428575, 0.3330701238857143, 0.33007066879999997, 0.32689208320000007, 0.3235617298285715, 0.32010697142857136, 0.31655517074285705, 0.3129336905142858, 0.30926989348571426, 0.3055911423999999, 0.3019248, 0.2982940928, 0.2947057024, 0.2911621741714286, 0.2876660534857143, 0.2842198857142857, 0.28082621622857146, 0.27748759039999993, 0.27420655359999996, 0.2709856512, 0.2678274285714286, 0.26473443108571426, 0.2617092041142857, 0.2587542930285714, 0.2558722431999999, 0.2530656, 0.2503369088, 0.24768871497142858, 0.24512356388571424, 0.24264400091428567, 0.2402525714285714, 0.23795182079999994, 0.23574429439999994, 0.23363253759999994, 0.23161909577142856, 0.22970651428571426, 0.22789733851428567, 0.22619411382857144, 0.22459938559999995, 0.22311569919999993, 0.2217456],
        [0.31628893198666985, 0.3278426745597805, 0.33814228230796367, 0.3472448883183228, 0.35520762567796094, 0.36208762747398193, 0.367942026793489, 0.37282795672358543, 0.3768025503513745, 0.37992294076395994, 0.38224626104844495, 0.3838296442919329, 0.38473022358152714, 0.3850051320043313, 0.38471150264744847, 0.38390646859798205, 0.3826471629430356, 0.3809907187697124, 0.3789942691651158, 0.37671494721634924, 0.3742098860105162, 0.37153621863471986, 0.36875107817606384, 0.3659115977216512, 0.36307491035858586, 0.3602981491739706, 0.35763844725490923, 0.3551529376885049, 0.35289875356186107, 0.3509330279620811, 0.34931289397626847, 0.34807744331954776, 0.34719360221913, 0.34661025553024666, 0.34627628810813005, 0.3461405848080119, 0.3461520304851247, 0.34625950999469984, 0.3464119081919697, 0.34655810993216596, 0.34664700007052107, 0.3466274634622665, 0.34644838496263475, 0.3460586494268575, 0.3454071417101666, 0.3444427466677945, 0.3431272570951535, 0.34147409754838015, 0.3395096005237911, 0.3372600985177033, 0.3347519240264337, 0.3320114095462993, 0.32906488757361696, 0.32593869060470343, 0.322659151135876, 0.3192526016634513, 0.3157453746837462, 0.3121638026930779, 0.30853421818776317, 0.30488295366411877, 0.301236341618462, 0.29761690473361885, 0.29403192643845366, 0.2904848803483401, 0.28697924007865183, 0.28351847924476226, 0.2801060714620452, 0.27674549034587403, 0.2734402095116229, 0.27019370257466496, 0.26700944315037395, 0.2638909048541235, 0.26084156130128744, 0.25786488610723896, 0.2549643528873521, 0.25214343525700034, 0.24940560683155724, 0.2467543412263965, 0.24419311205689173, 0.24172539293841655, 0.23935465748634457, 0.23708437931604945, 0.23491803204290482, 0.2328590892822843, 0.23091102464956154, 0.2290773117601101, 0.22736142422930355, 0.2257668356725158, 0.22429701970512003, 0.22295544994249025, 0.2217455999999999],
        [0.31433603991937054, 0.3258372260344489, 0.33609336056384015, 0.34516110446524956, 0.3530971186963815, 0.3599580642149412, 0.36580060197863346, 0.370681392945163, 0.374657098072235, 0.37778437831755424, 0.38011989463882573, 0.38172030799375406, 0.38264227934004424, 0.3829424696354013, 0.38267753983753, 0.3819041509041354, 0.38067896379292177, 0.37905863946159496, 0.3770998388678593, 0.37485922296941954, 0.3723934527239809, 0.3697591890892482, 0.36701309302292623, 0.36421182548271985, 0.3614120474263342, 0.35867041981147396, 0.35604360359584397, 0.3535882597371493, 0.3513610491930947, 0.34941863292138503, 0.3478176718797253, 0.3465969910513485, 0.34572407152160045, 0.34514855840135455, 0.344820096801485, 0.34468833183286535, 0.34470290860636976, 0.3448134722328716, 0.344969667823245, 0.3451211404883636, 0.3452175353391012, 0.3452084974863318, 0.3450436720409293, 0.34467270411376705, 0.34404523881571913, 0.3431109212576595, 0.34183200249838946, 0.3402211573884231, 0.3383036667262014, 0.3361048113101658, 0.333649871938758, 0.33096412941041903, 0.3280728645235908, 0.3250013580767143, 0.3217748908682314, 0.3184187436965831, 0.3149581973602111, 0.3114185326575567, 0.3078250303870613, 0.30420297134716634, 0.3005776363363134, 0.29697082684109993, 0.2933904271007479, 0.28984084204263555, 0.286326476594141, 0.28285173568264244, 0.27942102423551796, 0.276038747180146, 0.27270930944390426, 0.26943711595417136, 0.2662265716383252, 0.263082081423744, 0.2600080502378058, 0.25700888300788904, 0.2540889846613717, 0.251252760125632, 0.24850461432804807, 0.24584895219599803, 0.24329017865686006, 0.24083269863801243, 0.23848091706683316, 0.23623923887070053, 0.23411206897699258, 0.23210381231308766, 0.23021887380636374, 0.2284616583841991, 0.22683657097397178, 0.2253480165030601, 0.22400039989884213, 0.222798126088696, 0.2217456],
        [0.31235688060220473, 0.32380191101288436, 0.33401141077213437, 0.3430415500464795, 0.35094849900244374, 0.3577884278065521, 0.36361750662532855, 0.3684919056252978, 0.37246779497298427, 0.3756013448349125, 0.3779487253776067, 0.3795661067675916, 0.38050965917139146, 0.38083555275553094, 0.38059995768653426, 0.37985904413092597, 0.3786689822552306, 0.37708594222597247, 0.37516609420967634, 0.3729656083728662, 0.3705406548820669, 0.36794740390380265, 0.36524202560459823, 0.36248069015097784, 0.35971956770946584, 0.35701482844658705, 0.3544226425288655, 0.3519991801228259, 0.3498006113949927, 0.34788310651189036, 0.3463028356400432, 0.34509834374863285, 0.3442376750174694, 0.34367124842901914, 0.34334948296574913, 0.3432227976101267, 0.34324161134461817, 0.34335634315169067, 0.3435174120138111, 0.34367523691344626, 0.34378023683306297, 0.34378283075512817, 0.3436334376621088, 0.34328247653647165, 0.3426803663606836, 0.3417775261172116, 0.34053667412624417, 0.3389697260588563, 0.33710089692384493, 0.33495440173000673, 0.3325544554861387, 0.3299252732010375, 0.3270910698835, 0.32407606054232296, 0.3209044601863033, 0.31760048382423756, 0.31418834646492283, 0.3106922631171557, 0.307136448789733, 0.30354511849145166, 0.29994248723110833, 0.2963496230009927, 0.2927750057273657, 0.2892239683199808, 0.28570184368859175, 0.28221396474295235, 0.2787656643928159, 0.2753622755479363, 0.2720091311180672, 0.2687115640129623, 0.2654749071423752, 0.26230449341605955, 0.25920565574376897, 0.2561837270352571, 0.2532440402002777, 0.2503919281485845, 0.24763272378993073, 0.24497176003407062, 0.2424143697907574, 0.23996588596974494, 0.2376316414807868, 0.2354169692336367, 0.23332720213804825, 0.23136767310377515, 0.22954371504057114, 0.22786066085818962, 0.2263238434663845, 0.22493859577490927, 0.22371025069351763, 0.2226441411319633, 0.22174559999999996],
        [0.31035581083927494, 0.321740816483966, 0.33190029213735106, 0.34088989603914055, 0.34876528642904486, 0.35558212154677504, 0.3613960596320414, 0.3662627589245545, 0.37023787766402516, 0.373377074090164, 0.37573600644268146, 0.3773703329612884, 0.3783357118856949, 0.3786878014556123, 0.37848225991075074, 0.3777747454908208, 0.3766209164355332, 0.3750764309845986, 0.3731969473777277, 0.3710381238546309, 0.3686556186550188, 0.36610509001860203, 0.3634421961850913, 0.3607225953941973, 0.3580019458856306, 0.3553359058991016, 0.35278013367432104, 0.3503902874509995, 0.3482220254688476, 0.34633100596757604, 0.3447728871868952, 0.3435859187646324, 0.342738715931081, 0.34218248531465045, 0.3418684335437505, 0.34174776724679123, 0.341771693052182, 0.34189141758833286, 0.34205814748365354, 0.34222308936655343, 0.3423374498654426, 0.34235243560873074, 0.3422192532248277, 0.34188910934214306, 0.34131321058908637, 0.34044276359406794, 0.3392409642952536, 0.33771896586983624, 0.33589991080476483, 0.33380694158698854, 0.33146320070345686, 0.3288918306411187, 0.3261159738869233, 0.32315877292781986, 0.3200433702507576, 0.31679290834268553, 0.3134305296905529, 0.3099793767813091, 0.306462592101903, 0.3029033181392839, 0.2993246973804012, 0.29574705709184745, 0.29217946365879066, 0.2886281682460424, 0.2850994220184144, 0.28159947614071795, 0.27813458177776484, 0.2747109900943667, 0.2713349522553349, 0.26801271942548116, 0.26475054276961724, 0.2615546734525544, 0.25843136263910443, 0.2553868614940787, 0.252427421182289, 0.24955929286854697, 0.24678872771766402, 0.24412197689445178, 0.2415652915637219, 0.23912492289028586, 0.2368071220389553, 0.2346181401745418, 0.23256422846185695, 0.2306516380657124, 0.22888662015091965, 0.22727542588229027, 0.22582430642463588, 0.22453951294276805, 0.2234272966014984, 0.2224939085656385, 0.2217455999999999],
        [0.3083371874346841, 0.3196580294365735, 0.32976386386399514, 0.3387098134203606, 0.34655100080908163, 0.35334254873357057, 0.3591395798972387, 0.3639972170034983, 0.3679705827557611, 0.37111479985743906, 0.3734849910119438, 0.37513627892268747, 0.37612378629308163, 0.3765026358265383, 0.37632795022646937, 0.37565485219628675, 0.3745384644394019, 0.37303390965922717, 0.37119631055917424, 0.36908078984265486, 0.3667424702130811, 0.3642364743738646, 0.3616179250284174, 0.3589419448801512, 0.356263656632478, 0.3536381829888096, 0.35112064665255777, 0.3487661703271346, 0.34662987671595163, 0.34476688852242093, 0.34323232844995444, 0.3420641334525785, 0.3412314974867798, 0.3406864287596589, 0.3403809354783169, 0.34026702584985474, 0.3402967080813735, 0.3404219903799741, 0.3405948809527577, 0.340767388006825, 0.3408915197492772, 0.34091928438721525, 0.3408026901277401, 0.3404937451779528, 0.33994445774495413, 0.33910683603584535, 0.33794456532195466, 0.33646803913151946, 0.3346993280570042, 0.33266050269087405, 0.3303736336255933, 0.32786079145362684, 0.32514404676743947, 0.3222454701594957, 0.3191871322222603, 0.31599110354819776, 0.3126794547297732, 0.30927425635945105, 0.305797579029696, 0.3022714933329728, 0.29871806986174615, 0.2951568929922139, 0.29159760223550624, 0.2880473508864868, 0.2845132922400188, 0.28100257959096586, 0.2775223662341911, 0.2740798054645581, 0.27068205057693046, 0.2673362548661713, 0.2640495716271442, 0.2608291541547127, 0.25768215574374, 0.25461572968908947, 0.25163702928562487, 0.24875320782820934, 0.24597141861170638, 0.24329881493097932, 0.2407425500808918, 0.23830977735630698, 0.23600765005208849, 0.23384332146309958, 0.23182394488420388, 0.2299566736102647, 0.22824866093614546, 0.22670706015670952, 0.22533902456682034, 0.22415170746134144, 0.22315226213513603, 0.22234784188306778, 0.2217455999999999],
        [0.3063053671925348, 0.3175576368595861, 0.3276059851565713, 0.3365049731672674, 0.3443091619754511, 0.3510731126648989, 0.3568513863193876, 0.36169854402269414, 0.365669146858595, 0.36881775591086696, 0.371198932263287, 0.3728672369996316, 0.37387723120367733, 0.37428347595920125, 0.3741405323499799, 0.3735029614597901, 0.37242532437240833, 0.3709621821716117, 0.3691680959411766, 0.3670976267648799, 0.36480533572649837, 0.36234578390980876, 0.3597735323985876, 0.3571431422766118, 0.35450917462765796, 0.3519261905355029, 0.3494487510839234, 0.34713141735669584, 0.34502875043759734, 0.3431953114104044, 0.3416856613588939, 0.34053740516570274, 0.3397203229089101, 0.3391872384654546, 0.33889097571227583, 0.3387843585263126, 0.33882021078450447, 0.33895135636379026, 0.33913061914110926, 0.3393108229934006, 0.3394447917976034, 0.33948534943065706, 0.3393853197695004, 0.3390975266910728, 0.3385747940723131, 0.337769945790161, 0.3366471695228836, 0.33521610815406233, 0.33349776836860623, 0.3315131568514252, 0.32928328028742865, 0.3268291453615262, 0.32417175875862697, 0.3213321271636409, 0.31833125726147704, 0.3151901557370453, 0.31192982927525487, 0.3085712845610154, 0.30513552827923646, 0.3016435671148272, 0.29811640775269765, 0.29457289458064206, 0.2910232227979961, 0.2874754253069803, 0.28393753500981544, 0.28041758480872186, 0.2769236076059206, 0.273463636303632, 0.27004570380407694, 0.2666778430094759, 0.26336808682204954, 0.2601244681440186, 0.25695501987760355, 0.2538677749250252, 0.250870766188504, 0.24797202657026096, 0.24517958897251627, 0.24250148629749085, 0.23994575144740526, 0.23752041732448015, 0.2352335168309362, 0.23309308286899397, 0.23110714834087417, 0.2292837461487975, 0.22763090919498447, 0.22615667038165585, 0.2248690626110321, 0.22377611878533404, 0.22288587180678224, 0.2222063545775973, 0.22174559999999993],
        [0.3042647069169297, 0.31544372574188273, 0.32543051521958444, 0.3342790462569889, 0.34204328976104953, 0.34877721663872013, 0.3545347977969546, 0.35937000414270653, 0.36333680658292955, 0.3664891760245776, 0.36888108337460424, 0.37056649953996335, 0.37159939542760834, 0.3720337419444933, 0.3719235099975717, 0.37132267049379747, 0.3702851943401241, 0.36886505244350554, 0.36711621571089526, 0.3650926550492472, 0.36284834136551514, 0.36043724556665263, 0.35791333855961344, 0.35533059125135114, 0.3527429745488199, 0.350204459358973, 0.34776901658876425, 0.3454906171451476, 0.34342323193507657, 0.34162083186550485, 0.3401373878433864, 0.3390101512572361, 0.33820949542181566, 0.3376890741334476, 0.33740254118845486, 0.3373035503831603, 0.3373457555138866, 0.3374828103769566, 0.3376683687686934, 0.33785608448541943, 0.33799961132345774, 0.3380526030791311, 0.33796871354876235, 0.3377015965286743, 0.3372049058151895, 0.33643229520463136, 0.3353484692145766, 0.3339623352476208, 0.33229385142761353, 0.3303629758784046, 0.3281896667238436, 0.3257938820877804, 0.32319558009406446, 0.3204147188665456, 0.31747125652907376, 0.3143851512054984, 0.31117636101966917, 0.3078648440954362, 0.30447055855664873, 0.3010134625271565, 0.29751351413080973, 0.2939888257356815, 0.2904501266867432, 0.286906300573189, 0.2833662309842138, 0.27983880150901236, 0.2763328957367793, 0.2728573972567094, 0.26942118965799733, 0.26603315652983794, 0.262702181461426, 0.2594371480419559, 0.25624693986062275, 0.253140440506621, 0.25012653356914555, 0.24721410263739105, 0.24441203130055217, 0.24172920314782378, 0.23917450176840035, 0.23675681075147692, 0.234485013686248, 0.23236799416190837, 0.2304146357676528, 0.22863382209267605, 0.2270344367261727, 0.22562536325733748, 0.22441548527536526, 0.22341368636945066, 0.22262885012878839, 0.2220698601425732, 0.2217455999999999],
        [0.3022195634119714, 0.31332038307234267, 0.32324131325753946, 0.3320357036666528, 0.3397569039987742, 0.3464582639529951, 0.3521931332284068, 0.3570148615241007, 0.3609767985391681, 0.36413229397270047, 0.36653469752378925, 0.3682373588915256, 0.36929362777500113, 0.369756853873307, 0.36968038688553473, 0.3691175765107756, 0.368121772448121, 0.3667463243966623, 0.3650445820554911, 0.3630698951236984, 0.3608756133003758, 0.3585150862846146, 0.3560416637755062, 0.35350869547214203, 0.3509695310736135, 0.3484775202790117, 0.3460860127874283, 0.3438483582979545, 0.34181790650968186, 0.3400480071217015, 0.33859200983310495, 0.3374867890804101, 0.336703318249841, 0.3361960954650481, 0.33591961884968186, 0.33582838652739316, 0.33587689662183223, 0.33601964725664946, 0.3362111365554958, 0.33640586264202144, 0.33655832363987703, 0.3366230176727132, 0.3365544428641804, 0.3363070973379292, 0.33583547921761003, 0.33509408662687346, 0.3340481567135703, 0.3327058827223518, 0.3310861969220693, 0.3292080315815744, 0.3270903189697188, 0.3247519913553537, 0.3222119810073305, 0.3194892201945009, 0.3166026411857164, 0.3135711762498282, 0.31041375765568796, 0.3071493176721473, 0.30379678856805753, 0.30037510261227, 0.2969031920736365, 0.2933984503358827, 0.28987211524223117, 0.28633388575077945, 0.2827934608196245, 0.2792605394068633, 0.27574482047059334, 0.2722560029689114, 0.268803785859915, 0.2653978681017011, 0.2620479486523667, 0.258763726470009, 0.2555549005127254, 0.2524311697386128, 0.24940223310576837, 0.24647778957228936, 0.2436675380962727, 0.2409811776358157, 0.2384284071490155, 0.23601892559396914, 0.23376243192877388, 0.23166862511152675, 0.229747204100325, 0.22800786785326577, 0.2264603153284461, 0.22511424548396325, 0.22397935727791424, 0.2230653496683962, 0.22238192161350637, 0.22193877207134188, 0.2217455999999999],
        [0.3001742934817627, 0.31119169583984563, 0.321042238474941, 0.3297786163733871, 0.337453524521522, 0.3441196579056839, 0.349829711512211, 0.35463638032744144, 0.35859235933771355, 0.36175034352936547, 0.36416302788873534, 0.3658831074021615, 0.3669632770559818, 0.36745623183653475, 0.3674146667301585, 0.3668912767231912, 0.36593875680197085, 0.364609801952836, 0.3629571071621246, 0.36103336741617476, 0.35889127770132506, 0.35658353300391327, 0.3541628283102778, 0.35168185860675677, 0.34919331887968846, 0.34674990411541096, 0.34440430930026256, 0.34220922942058135, 0.34021735946270537, 0.33848139441297315, 0.3370540292577228, 0.33597173598845614, 0.33520609461733036, 0.33471246216166634, 0.33444619563878475, 0.3343626520660067, 0.334417188460653, 0.3345651618400443, 0.3347619292215018, 0.33496284762234607, 0.335123274059898, 0.3351985655514786, 0.33514407911440874, 0.33491517176600927, 0.3344672005236007, 0.3337555224045045, 0.33274592433640093, 0.33144591288841146, 0.3298734245400166, 0.32804639577069744, 0.32598276305993507, 0.3237004628872102, 0.321217431732004, 0.31855160607379707, 0.31572092239207067, 0.3127433171663054, 0.30963672687598254, 0.30641908800058293, 0.3031083370195875, 0.299722410412477, 0.2962792446587327, 0.292795532259795, 0.2892829898049436, 0.28575208990541784, 0.2822133051724573, 0.27867710821730113, 0.2751539716511887, 0.2716543680853595, 0.26818877013105286, 0.26476765039950817, 0.2614014815019648, 0.2581007360496621, 0.2548758866538393, 0.251737405925736, 0.24869576647659153, 0.24576144091764518, 0.24294490186013637, 0.2402566219153044, 0.23770707369438862, 0.23530672980862868, 0.23306606286926354, 0.23099554548753284, 0.22910565027467594, 0.22740684984193213, 0.2259096168005408, 0.22462442376174138, 0.22356174333677312, 0.22273204813687553, 0.22214581077328785, 0.22181350385724954, 0.22174559999999993],
        [0.298133253930406, 0.30906175103327044, 0.318837150076294, 0.3275114553543194, 0.33513667116218937, 0.3417648017947466, 0.3474478515468339, 0.3522378247132936, 0.35618672558896874, 0.35934655846870195, 0.3617693276473359, 0.3635070374197133, 0.3646116920806766, 0.36513529592506894, 0.3651298532477326, 0.3646473683435106, 0.3637398455072453, 0.3624592890337796, 0.3608577032179563, 0.3589870923546179, 0.3568994607386071, 0.3546468126647667, 0.3522811524279393, 0.3498544843229676, 0.3474188126446944, 0.34502614168796236, 0.342728475747614, 0.34057781911849216, 0.3386261760954396, 0.3369255509732989, 0.3355279480469127, 0.3344694093346054, 0.3337221277486278, 0.3332423339247122, 0.3329862584985909, 0.3329101321059963, 0.3329701853826609, 0.3331226489643169, 0.3333237534866968, 0.3335297295855327, 0.33369680789655737, 0.33378121905550273, 0.3337391936981015, 0.33352696246008595, 0.33310075597718813, 0.3324168048851409, 0.33144146439960503, 0.3301815880559561, 0.3286541539694982, 0.32687614025553574, 0.32486452502937296, 0.32263628640631403, 0.3202084025016631, 0.3175978514307244, 0.3148216113088022, 0.3118966602512007, 0.30883997637322436, 0.3056685377901769, 0.302399322617363, 0.2990493089700866, 0.29563547496365206, 0.2921738353859683, 0.28867655171536355, 0.28515482210277054, 0.2816198446991224, 0.2780828176553517, 0.2745549391223915, 0.27104740725117454, 0.2675714201926341, 0.2641381760977027, 0.26075887311731333, 0.25744470940239883, 0.2542068831038922, 0.2510565923727263, 0.2480050353598339, 0.24506341021614803, 0.24224291509260149, 0.23955474814012725, 0.2370101075096581, 0.23462019135212694, 0.23239619781846668, 0.23034932505961023, 0.2284907712264905, 0.2268317344700404, 0.22538341294119268, 0.22415700479088033, 0.2231637081700362, 0.22241472122959327, 0.22192124212048422, 0.22169446899364215, 0.22174559999999985],
        [0.2961008015620044, 0.3069346356414967, 0.31662990726610335, 0.32523789158657795, 0.33280986375367355, 0.33939709891814407, 0.3450508722307425, 0.3498224588422223, 0.35376313390333697, 0.35692417256483994, 0.3593568499774845, 0.3611124412920242, 0.36224222165921216, 0.362797466229802, 0.36282945015454704, 0.36238944858420075, 0.36152873666951624, 0.3602985895612472, 0.3587502824101471, 0.35693509036696913, 0.3549042885824668, 0.3527091522073934, 0.3504009563925024, 0.3480309762885471, 0.3456504870462811, 0.3433107638164576, 0.3410630817498302, 0.338958715997152, 0.33704894170917665, 0.3353850340366575, 0.3340182681303478, 0.3329842264720894, 0.33225572086807764, 0.33178987045559605, 0.33154379437192827, 0.3314746117543576, 0.33153944174016825, 0.33169540346664317, 0.3318996160710665, 0.3321091986907213, 0.33228127046289174, 0.332372950524861, 0.3323413580139129, 0.332143612067331, 0.33173683182239877, 0.33107813641640005, 0.33013446921971873, 0.32891207053514215, 0.3274270048985574, 0.32569533684585195, 0.32373313091291345, 0.3215564516356292, 0.31918136354988685, 0.31662393119157367, 0.31390021909657734, 0.3110262918007853, 0.30801821384008465, 0.3048920497503634, 0.3016638640675088, 0.2983497213274082, 0.2949656860659492, 0.2915271235929529, 0.2880466023139747, 0.284535991408504, 0.28100716005602977, 0.2774719774360414, 0.27394231272802766, 0.27043003511147806, 0.2669470137658818, 0.26350511787072783, 0.26011621660550543, 0.2567921791497037, 0.2535448746828119, 0.25038617238431915, 0.24732794143371456, 0.24438205101048752, 0.24156037029412686, 0.23887476846412195, 0.23633711469996194, 0.23395927818113602, 0.23175312808713322, 0.22973053359744286, 0.22790336389155405, 0.22628348814895605, 0.2248827755491379, 0.22371309527158872, 0.22278631649579786, 0.22211430840125432, 0.2217089401674474, 0.22158208097386614, 0.22174559999999982],
        [0.29408129318066034, 0.30481443665340346, 0.31442436924887385, 0.3229615960472903, 0.3304766221288714, 0.3370199525738364, 0.3426420924624038, 0.34739354687479246, 0.35132482089122136, 0.3544864195919091, 0.3569288480570748, 0.358702611366937, 0.3598582146017147, 0.36044616284162645, 0.36051696116689136, 0.36012111465772817, 0.3593091283943554, 0.3581315074569925, 0.3566387569258578, 0.3548813818811703, 0.3529098874031486, 0.3507747785720118, 0.34852656046797864, 0.3462157381712678, 0.34389281676209826, 0.34160830132068887, 0.33941269692725823, 0.3373565086620255, 0.335490241605209, 0.333864400837028, 0.3325294914377012, 0.3315206047541395, 0.3308111772000243, 0.3303592314557282, 0.3301227902016243, 0.3300598761180862, 0.33012851188548664, 0.33028672018419897, 0.3304925236945961, 0.3307039450970514, 0.3308790070719379, 0.33097573229962884, 0.33095214346049723, 0.33076626323491615, 0.3303761143032589, 0.32973971934589863, 0.32882463111327886, 0.32763652263612614, 0.326190597015237, 0.3245020573514084, 0.3225861067454371, 0.32045794829811997, 0.3181327851102538, 0.3156258202826355, 0.3129522569160617, 0.3101272981113294, 0.30716614696923544, 0.30408400659057655, 0.3008960800761495, 0.29761757052675114, 0.29426368104317846, 0.2908491607592985, 0.2873869429412606, 0.2838895068882846, 0.2803693318995899, 0.27683889727439637, 0.2733106823119236, 0.2697971663113912, 0.2663108285720192, 0.2628641483930269, 0.25946960507363426, 0.25613967791306075, 0.25288684621052626, 0.2497235892652503, 0.24666238637645263, 0.24371571684335294, 0.2408960599651709, 0.2382158950411262, 0.23568770137043848, 0.23332395825232752, 0.23113714498601293, 0.22913974087071448, 0.2273442252056517, 0.22576307729004447, 0.22440877642311235, 0.22329380190407508, 0.22243063303215227, 0.22183174910656367, 0.22150962942652896, 0.2214767532912678, 0.2217455999999999],
        [0.2920790855904764, 0.3027052410578701, 0.3122243952291102, 0.32068623971358423, 0.32814046612067954, 0.3346367660597839, 0.3402248311402844, 0.3449543529715688, 0.3488750231630245, 0.352036533324039, 0.35448857506399983, 0.35628083999229443, 0.35746301971831007, 0.35808480585143454, 0.35819589000105506, 0.35784596377655936, 0.35708471878733467, 0.3559618466427686, 0.3545270389522487, 0.35282998732516224, 0.3509203833708969, 0.34884791869884013, 0.3466622849183792, 0.3444131736389018, 0.34215027646979546, 0.3399232850204475, 0.33778189090024535, 0.33577578571857664, 0.33395466108482885, 0.3323682086083894, 0.33106611989864554, 0.33008296153398714, 0.3293927999688117, 0.32895457662651845, 0.3287272329305071, 0.3286697103041772, 0.3287409501709283, 0.32889989395415975, 0.3291054830772713, 0.32931665896366247, 0.3294923630367326, 0.32959153671988145, 0.32957312143650846, 0.3293960586100131, 0.32901928966379484, 0.3284017560212535, 0.32751164239682146, 0.3263541066690643, 0.32494355000758013, 0.3232943735819674, 0.3214209785618246, 0.31933776611675024, 0.3170591374163427, 0.31459949363020007, 0.31197323592792114, 0.30919476547910424, 0.3062784834533477, 0.30323879102025003, 0.3000900893494095, 0.2968467796104245, 0.2935232629728937, 0.29013371076355493, 0.2866913749377045, 0.28320927760777836, 0.27970044088621243, 0.2761778868854427, 0.2726546377179049, 0.2691437154960351, 0.26565814233226925, 0.26221094033904313, 0.2588151316287928, 0.25548373831395405, 0.25222978250696293, 0.24906628632025518, 0.24600627186626686, 0.24306276125743392, 0.2402487766061921, 0.23757734002497743, 0.23506147362622584, 0.23271419952237327, 0.23054853982585555, 0.22857751664910864, 0.22681415210456848, 0.22527146830467104, 0.22396248736185212, 0.22290023138854764, 0.22209772249719364, 0.22156798280022597, 0.22132403441008044, 0.22137889943919312, 0.22174559999999993],
        [0.2900985355955554, 0.3006111358437758, 0.31003384441131726, 0.31841549356258764, 0.3258049155619948, 0.33225094267394667, 0.3378024071628512, 0.34250814129311624, 0.34641697732914967, 0.3495777475353593, 0.35203928417615316, 0.35385041951593915, 0.3550599858191249, 0.3557168153501185, 0.35586974037332797, 0.3555675931531611, 0.3548592059540254, 0.3537934110403293, 0.35241904067648055, 0.3507849271268868, 0.3489399026559563, 0.3469327995280965, 0.3448124500077158, 0.34262768635922164, 0.3404273408470222, 0.33826024573552527, 0.3361752332891386, 0.3342211357722704, 0.33244678544932826, 0.3309010145847202, 0.3296326554428541, 0.3286757141648634, 0.328004892398784, 0.3275800656693769, 0.3273611095014039, 0.32730789941962607, 0.3273803109488048, 0.3275382196137014, 0.3277415009390774, 0.32795003044969384, 0.3281236836703124, 0.3282223361256941, 0.32820586334060076, 0.3280341408397933, 0.3276670441480331, 0.32706444879008156, 0.32619519538688296, 0.32506398494411287, 0.32368448356362955, 0.3220703573472913, 0.3202352723969568, 0.31819289481448404, 0.31595689070173166, 0.31354092616055795, 0.3109586672928214, 0.30822378020038027, 0.3053499309850929, 0.3023507857488178, 0.2992400105934133, 0.29603127162073756, 0.2927382349326494, 0.28937453748427205, 0.2859536996437897, 0.28248921263265186, 0.27899456767230757, 0.27548325598420653, 0.2719687687897978, 0.2684645973105309, 0.26498423276785504, 0.2615411663832196, 0.2581488893780741, 0.25482089297386756, 0.25157066839204956, 0.2484117068540693, 0.2453574995813762, 0.24242153779541967, 0.2396173127176489, 0.23695831556951327, 0.2344580375724621, 0.23212996994794488, 0.22998760391741074, 0.2280444307023092, 0.2263139415240895, 0.22480962760420103, 0.22354498016409308, 0.22253349042521497, 0.2217886496090162, 0.22132394893694596, 0.22115287963045352, 0.2212889329109884, 0.22174559999999988],
        [0.288144, 0.298536208, 0.30785657599999994, 0.3161530285714287, 0.32347349028571415, 0.3298658857142857, 0.3353781394285714, 0.34005817599999993, 0.34395391999999986, 0.3471132959999999, 0.3495842285714285, 0.35141464228571423, 0.3526524617142856, 0.35334561142857135, 0.353542016, 0.3532896, 0.3526362879999999, 0.35163000457142846, 0.3503186742857142, 0.34875022171428566, 0.34697257142857135, 0.34503364799999986, 0.34298137599999984, 0.3408636799999998, 0.33872848457142857, 0.3366237142857143, 0.33459729371428565, 0.33269714742857137, 0.33097119999999997, 0.329467376, 0.3282336, 0.32730327999999986, 0.3266517577142857, 0.3262398582857142, 0.3260284068571428, 0.32597822857142855, 0.32605014857142856, 0.32620499199999997, 0.326403584, 0.32660674971428577, 0.32677531428571427, 0.3268701028571428, 0.3268519405714286, 0.32668165257142856, 0.326320064, 0.325728, 0.3248749824, 0.32376531977142864, 0.3224120173714286, 0.32082808045714284, 0.3190265142857142, 0.31702032411428566, 0.3148225152, 0.31244609279999996, 0.3099040621714285, 0.30720942857142847, 0.3043751972571428, 0.3014143734857142, 0.29833996251428563, 0.2951649695999999, 0.29190239999999995, 0.2885654047999999, 0.2851677183999999, 0.28172322102857134, 0.2782457929142857, 0.2747493142857142, 0.27124766537142847, 0.26775472639999987, 0.2642843775999999, 0.2608504991999999, 0.2574669714285714, 0.25414767451428566, 0.2509064886857143, 0.2477572941714285, 0.2447139711999999, 0.24179040000000002, 0.23900046079999995, 0.2363580338285714, 0.23387699931428568, 0.2315712374857143, 0.22945462857142854, 0.22754105279999995, 0.22584439039999993, 0.22437852159999996, 0.22315732662857138, 0.2221946857142857, 0.22150447908571425, 0.22110058697142854, 0.22099688959999994, 0.2212072671999999, 0.2217455999999999],
        [0.2862215228610148, 0.2964863972834158, 0.30569843049979023, 0.3139045906173607, 0.3211518457433503, 0.32748716398498234, 0.33295751344947955, 0.3376098622440651, 0.34149117847596205, 0.3446484302523935, 0.34712858568058236, 0.3489786128677519, 0.35024547992112476, 0.35097615494792433, 0.35121760605537355, 0.3510168013506956, 0.3504207089411131, 0.3494762969338496, 0.3482305334361278, 0.34673038655517086, 0.3450228243982018, 0.3431548150724437, 0.3411733266851196, 0.33912532734345247, 0.33705778515466545, 0.3350176682259816, 0.3330519446646238, 0.33120758257781524, 0.329531550072779, 0.32807081525673787, 0.3268723462369152, 0.32596891468257283, 0.32533650651112955, 0.32493691120204277, 0.3247319182347701, 0.3246833170887692, 0.3247528972434977, 0.32490244817841313, 0.3250937593729732, 0.32528862030663525, 0.3254488204588571, 0.32553614930909613, 0.32551239633681034, 0.325339351021457, 0.32497880284249364, 0.32439254127937817, 0.3235507948183061, 0.322457547972426, 0.3211252242616242, 0.3195662472057873, 0.3177930403248022, 0.3158180271385549, 0.3136536311669324, 0.31131227592982086, 0.30880638494710705, 0.30614838173867753, 0.30335068982441876, 0.30042573272421746, 0.2973859339579599, 0.29424371704553276, 0.2910115055068227, 0.2877020164647989, 0.28432914145476296, 0.28090706561509843, 0.2774499740841898, 0.27397205200042074, 0.2704874845021757, 0.26701045672783835, 0.2635551538157931, 0.2601357609044238, 0.25676646313211454, 0.2534614456372495, 0.25023489355821277, 0.247100992033388, 0.24407392620115967, 0.24116788119991178, 0.2383970421680283, 0.2357755942438933, 0.2333177225658909, 0.2310376122724051, 0.22894944850181997, 0.22706741639251962, 0.22540570108288804, 0.22397848771130935, 0.22279996141616762, 0.22188430733584685, 0.2212457106087311, 0.22089835637320446, 0.220856429767651, 0.2211341159304548, 0.22174559999999982],
        [0.28434389724821346, 0.29447505452287437, 0.3035731736158292, 0.3116842251781429, 0.31885417986088, 0.3251290083151053, 0.3305546811918839, 0.3351771691422804, 0.3390424428173599, 0.3421964728681869, 0.34468522994582634, 0.3465546847013433, 0.3478508077858022, 0.34861956985026815, 0.3489069415458058, 0.3487588935234802, 0.3482213964343559, 0.3473404209294979, 0.34616193765997094, 0.34473191727684, 0.3430963304311697, 0.34130114777402504, 0.3393923399564707, 0.3374158776295716, 0.3354177314443927, 0.33344387205199844, 0.331540270103454, 0.32975289624982407, 0.3281277211421735, 0.326710715431567, 0.3255478497690696, 0.3246712270155388, 0.3240574788710037, 0.32366936924528616, 0.323469662048208, 0.32342112118959104, 0.3234865105792572, 0.3236285941270283, 0.32381013574272627, 0.3239938993361728, 0.3241426488171899, 0.32421914809559926, 0.32418616108122295, 0.3240064516838827, 0.32364278381340017, 0.32305792137959777, 0.3222228202863261, 0.3211412044135546, 0.3198249896352814, 0.318286091825505, 0.3165364268582238, 0.31458791060743607, 0.31245245894714024, 0.31014198775133484, 0.30766841289401803, 0.30504365024918834, 0.302279615690844, 0.2993882250929837, 0.2963813943296055, 0.29327103927470777, 0.2900690758022892, 0.2867878357347733, 0.28344131468828554, 0.2800439242273766, 0.27661007591659725, 0.2731541813204981, 0.26969065200363, 0.2662338995305437, 0.2627983354657898, 0.25939837137391913, 0.2560484188194824, 0.2527628893670304, 0.24955619458111372, 0.24644274602628324, 0.24343695526708956, 0.24055323386808355, 0.23780599339381583, 0.23520964540883718, 0.23277860147769816, 0.23052727316494975, 0.2284700720351426, 0.22662140965282737, 0.2249956975825549, 0.22360734738887586, 0.22247077063634096, 0.22160037888950104, 0.22101058371290655, 0.22071579667110863, 0.2207304293286576, 0.22106889325010448, 0.2217455999999999],
        [0.282525603484311, 0.29251738331521976, 0.3014965523533851, 0.30950805263165937, 0.3165968261828949, 0.3228078150399444, 0.3281859612356602, 0.3327762068028945, 0.33662349377450024, 0.3397727641833294, 0.3422689600622348, 0.3441570234440688, 0.34548189636168364, 0.346288520847932, 0.3466218389356662, 0.3465267926577387, 0.346048324047002, 0.3452313751363085, 0.3441208879585108, 0.34276180454646105, 0.341199066933012, 0.33947761715101593, 0.33764239723332545, 0.3357383492127927, 0.33381041512227044, 0.331903536994611, 0.33006265686266695, 0.32833271675929043, 0.3267586587173342, 0.32538542476965054, 0.324257956949092, 0.32340766409179894, 0.3228118222470648, 0.32243417426747045, 0.322238463005597, 0.3221884313140259, 0.32224782204533814, 0.32238037805211484, 0.32254984218693744, 0.32271995730238656, 0.32285446625104397, 0.32291711188549055, 0.3228716370583075, 0.3226817846220761, 0.3223112974293772, 0.3217239183327923, 0.3208913455141816, 0.31981709847252177, 0.3185126520360687, 0.3169894810330782, 0.3152590602918063, 0.31333286464050875, 0.3112223689074415, 0.3089390479208602, 0.30649437650902084, 0.3038998295001793, 0.3011668817225915, 0.2983070080045131, 0.2953316831742002, 0.2922523820599084, 0.28908057948989396, 0.2858282657415372, 0.2825094928887189, 0.27913882845444404, 0.2757308399617183, 0.27230009493354673, 0.2688611608929348, 0.2654286053628879, 0.2620169958664113, 0.2586408999265103, 0.25531488506619027, 0.25205351880845644, 0.24887136867631438, 0.24578300219276916, 0.2428029868808262, 0.23994589026349095, 0.23722627986376857, 0.23465872320466444, 0.232257787809184, 0.23003804120033247, 0.22801405090111512, 0.22620038443453744, 0.2246116093236046, 0.2232622930913222, 0.2221670032606953, 0.22134030735472932, 0.22079677289642965, 0.2205509674088015, 0.22061745841485025, 0.22101081343758125, 0.2217455999999999],
        [0.28078112189202276, 0.29062858725729673, 0.2994843137177259, 0.3073921933557949, 0.314396118253988, 0.3205399804947896, 0.3258676721606843, 0.3304230853341565, 0.3342501120976905, 0.3373926445337711, 0.3398945747248824, 0.341799794753509, 0.34315219670213515, 0.34399567265324554, 0.34437411468932433, 0.34433141489285635, 0.3439114653463256, 0.34315815813221673, 0.3421153853330142, 0.3408270390312025, 0.3393370113092659, 0.3376891942496888, 0.33592747993495586, 0.33409576044755146, 0.33223792786996004, 0.3303978742846659, 0.32861949177415356, 0.3269466724209075, 0.3254233083074122, 0.3240932915161519, 0.32300051412961117, 0.32217567300425476, 0.32159668409246955, 0.3212282681206215, 0.32103514581507797, 0.32098203790220575, 0.3210336651083716, 0.32115474815994216, 0.32131000778328433, 0.32146416470476485, 0.32158193965075077, 0.32162805334760847, 0.32156722652170516, 0.3213641798994076, 0.32098363420708215, 0.3203903101710962, 0.31955665721199433, 0.31848603952703525, 0.31718955000765503, 0.31567828154529015, 0.3139633270313774, 0.312055779357353, 0.3099667314146536, 0.30770727609471543, 0.30528850628897525, 0.3027215148888693, 0.3000173947858342, 0.29718723887130644, 0.2942421400367225, 0.29119319117351855, 0.2880514851731316, 0.28482870961670537, 0.28153893084421405, 0.27819680988533946, 0.27481700776976337, 0.27141418552716756, 0.26800300418723366, 0.2645981247796436, 0.261214208334079, 0.25786591588022173, 0.2545679084477536, 0.2513348470663561, 0.24818139276571138, 0.24512220657550085, 0.2421719495254065, 0.23934528264510996, 0.23665686696429294, 0.23412136351263743, 0.23175343331982493, 0.22956773741553738, 0.22757893682945637, 0.22580169259126387, 0.22425066573064145, 0.2229405172772711, 0.22188590826083432, 0.2211014997110131, 0.220601952657489, 0.22040192812994386, 0.22051608715805943, 0.2209590907715175, 0.22174559999999985],
        [0.2791249327940645, 0.28882386994594994, 0.2975522047141201, 0.305352767728434, 0.3122683896187512, 0.3183419010149309, 0.32361613254683264, 0.32813391484431526, 0.3319380785372385, 0.33507145425546164, 0.33757687262884395, 0.3394971642872447, 0.34087515986052314, 0.3417536899785387, 0.3421755852711506, 0.3421836763682182, 0.34182079389960096, 0.34112976849515797, 0.3401534307847488, 0.33893461139823255, 0.3375161409654686, 0.3359408501163162, 0.33425156948063484, 0.3324911296882838, 0.3307023613691223, 0.32892809515300975, 0.32721116166980546, 0.3255943915493685, 0.32412061542155857, 0.32283266391623483, 0.32177336766325654, 0.32097270084580815, 0.3204092118603746, 0.32004859265676594, 0.319856535184792, 0.3197987313942631, 0.31984087323498894, 0.3199486526567797, 0.32008776160944546, 0.32022389204279605, 0.3203227359066415, 0.320349985150792, 0.32027133172505745, 0.3200524675792479, 0.3196590846631732, 0.31905687492664353, 0.3182190420898868, 0.3171488369548029, 0.3158570220937094, 0.31435436007892403, 0.3126516134827646, 0.3107595448775488, 0.3086889168355946, 0.30645049192921925, 0.30405503273074097, 0.30151330181247704, 0.29883606174674554, 0.2960340751058641, 0.29311810446215036, 0.29009891238792207, 0.2869872614554971, 0.2837945704918923, 0.2805348833429224, 0.2772229001091014, 0.2738733208909431, 0.2705008457889612, 0.2671201749036699, 0.263746008335583, 0.26039304618521447, 0.2570759885530783, 0.25380953553968805, 0.250608387245558, 0.24748724377120188, 0.24446080521713368, 0.24154377168386723, 0.23875084327191654, 0.23609672008179544, 0.23359610221401786, 0.23126368976909772, 0.22911418284754892, 0.22716228154988535, 0.225422685976621, 0.22391009622826974, 0.22263921240534548, 0.2216247346083621, 0.22088136293783356, 0.22042379749427374, 0.22026673837819655, 0.22042488569011587, 0.22091293953054572, 0.22174559999999988],
        [0.2775715165131514, 0.28711843497802414, 0.29571597234783575, 0.30340589612746166, 0.31022997382177736, 0.3162299729356586, 0.321447660973981, 0.32592480544162006, 0.32970317384345144, 0.33282453368435094, 0.335330652469194, 0.3372632977028563, 0.3386642368902134, 0.33957523753614094, 0.34003806714551443, 0.3400944932232097, 0.33978628327410215, 0.3391552048030675, 0.33824302531498157, 0.33709151231471957, 0.33574243330715736, 0.3342375557971705, 0.3326186472896347, 0.33092747528942534, 0.3292058073014183, 0.32749541083048905, 0.32583805338151334, 0.3242755024593664, 0.32284952556892443, 0.32160189021506264, 0.32057436390265676, 0.31979619470936005, 0.319246553003937, 0.31889208972792954, 0.31869945582287984, 0.3186353022303297, 0.3186662798918216, 0.3187590397488972, 0.31888023274309873, 0.3189965098159684, 0.3190745219090479, 0.3190809199638796, 0.31898235492200544, 0.3187454777249675, 0.3183369393143078, 0.3177233906315684, 0.3168787868579806, 0.3158063001335324, 0.3145164068379006, 0.31301958335076263, 0.3113263060517955, 0.3094470513206763, 0.3073922955370822, 0.30517251508069027, 0.30279818633117755, 0.30027978566822133, 0.2976277894714986, 0.2948526741206864, 0.2919649159954621, 0.2889749914755024, 0.2858933769404848, 0.28273125149871275, 0.2795026051729953, 0.2762221307147685, 0.2729045208754676, 0.26956446840652865, 0.26621666605938715, 0.2628758065854786, 0.25955658273623905, 0.25627368726310407, 0.2530418129175092, 0.24987565245089027, 0.2467898986146828, 0.2437992441603226, 0.24091838183924533, 0.2381620044028867, 0.23554480460268226, 0.2330814751900678, 0.23078670891647893, 0.22867519853335141, 0.22676163679212086, 0.225060716444223, 0.22358713024109353, 0.2223555709341681, 0.2213807312748823, 0.22067730401467206, 0.22025998190497276, 0.2201434576972202, 0.22034242414285013, 0.2208715739932981, 0.22174559999999996],
        [0.2761353533719985, 0.2855274859503639, 0.2939913636241411, 0.3015676989307621, 0.30829720440765834, 0.3142205925922622, 0.31937857602200526, 0.32381186723431943, 0.32756117876663643, 0.3306672231563884, 0.3331707129410071, 0.3351123606579244, 0.33653287884457184, 0.3374729800383817, 0.33797337677678563, 0.3380747815972155, 0.3378179070371031, 0.33724346563388047, 0.3363921699249794, 0.33530473244783165, 0.3340218657398692, 0.33258428233852366, 0.33103269478122727, 0.32940781560541155, 0.3277503573485086, 0.32610103254795025, 0.3245005537411681, 0.32298963346559423, 0.32160898425866047, 0.3203993186577987, 0.3194013492004406, 0.31864360168781186, 0.3181058549763131, 0.31775570118613833, 0.3175607324374818, 0.3174885408505376, 0.3175067185455002, 0.31758285764256367, 0.31768455026192205, 0.3177793885237698, 0.31783496454830085, 0.31781887045570956, 0.31769869836619014, 0.3174420403999368, 0.3170164886771435, 0.31638963531800474, 0.31553617822639757, 0.31445923844093115, 0.31316904278389757, 0.3116758180775888, 0.30998979114429737, 0.30812118880631506, 0.3060802378859342, 0.30387716520544666, 0.30152219758714466, 0.29902556185332047, 0.2963974848262662, 0.2936481933282738, 0.29078791418163547, 0.2878268742086433, 0.28477530023158953, 0.28164415576878093, 0.27844735112258384, 0.275199533291379, 0.2719153492735476, 0.2686094460674704, 0.26529647067152845, 0.2619910700841026, 0.258707891303574, 0.2554615813283237, 0.25226678715673245, 0.24913815578718115, 0.24609033421805096, 0.24313796944772273, 0.24029570847457737, 0.23757819829699608, 0.23500008591335964, 0.23257601832204897, 0.2303206425214451, 0.22824860550992904, 0.22637455428588166, 0.22471313584768404, 0.223278997193717, 0.22208678532236165, 0.22115114723199886, 0.2204867299210095, 0.2201081803877748, 0.22003014563067547, 0.22026727264809257, 0.22083420843840706, 0.2217455999999999],
        [0.2748309236933217, 0.28406622645981383, 0.29239412554830435, 0.29985429651621986, 0.3064864149209869, 0.31233015632003186, 0.3174251962707816, 0.32181121033066246, 0.32552787405710104, 0.32861486300752407, 0.33111185273935806, 0.3330585188100294, 0.33449453677696483, 0.33545958219759087, 0.3359933306293341, 0.336135457629621, 0.3359256387558781, 0.33540354956553214, 0.3346088656160098, 0.33358126246473724, 0.3323604156691413, 0.33098600078664847, 0.32949769337468543, 0.3279351689906785, 0.3263381031920545, 0.3247461715362398, 0.3231990495806611, 0.3217364128827449, 0.3203979369999179, 0.3192232974896064, 0.3182521699092372, 0.3175123688740652, 0.31698426523065987, 0.31663636888341856, 0.3164371897367391, 0.31635523769501916, 0.3163590226626566, 0.3164170545440488, 0.31649784324359365, 0.31656989866568885, 0.31660173071473197, 0.31656184929512077, 0.31641876431125304, 0.31614098566752624, 0.3156970232683382, 0.3150553870180866, 0.31419150290525966, 0.31310846125470704, 0.3118162684753689, 0.31032493097618574, 0.3086444551660978, 0.30678484745404516, 0.3047561142489682, 0.30256826195980707, 0.30023129699550216, 0.2977552257649936, 0.2951500546772217, 0.29242579014112696, 0.28959243856564904, 0.2866600063597286, 0.28363849993230594, 0.2805386864337117, 0.277374375979839, 0.2741601394279717, 0.27091054763539313, 0.2676401714593871, 0.26436358175723745, 0.26109534938622736, 0.25785004520364097, 0.25464224006676167, 0.2514865048328732, 0.24839741035925922, 0.24538952750320334, 0.2424774271219892, 0.23967568007290047, 0.2369988572132209, 0.23446152940023393, 0.23207826749122343, 0.22986364234347295, 0.22783222481426613, 0.22599858576088672, 0.22437729604061823, 0.2229829265107444, 0.22183004802854894, 0.22093323145131544, 0.2203070476363275, 0.2199660674408688, 0.21992486172222311, 0.22019800133767392, 0.22080005714450493, 0.2217455999999999],
        [0.27367270779983616, 0.2827498601032186, 0.29094000512559387, 0.29828180926171993, 0.30481393890635516, 0.31057506045425776, 0.31560384030018596, 0.31993894483889823, 0.32361904046515266, 0.3266827935737076, 0.32916887055932154, 0.3311159378167523, 0.3325626617407584, 0.33354770872609807, 0.3341097451675296, 0.3342874374598113, 0.33411945199770127, 0.3336444551759581, 0.33290111338933964, 0.3319280930326047, 0.330764060500511, 0.329447682187817, 0.3280176244892811, 0.3265125537996616, 0.3249711365137166, 0.32343203902620443, 0.3219339277318834, 0.32051546902551165, 0.3192153293018476, 0.3180721749556495, 0.31712467238167547, 0.3163999433610215, 0.315878931220134, 0.3155310346717963, 0.3153256524287924, 0.31523218320390634, 0.3152200257099216, 0.31525857865962204, 0.3153172407657916, 0.3153654107412138, 0.3153724872986727, 0.31530786915095177, 0.3151409550108353, 0.31484114359110665, 0.3143778336045498, 0.3137204237639483, 0.3128450476046888, 0.3117547779525678, 0.31045942245598396, 0.30896878876333633, 0.3072926845230244, 0.3054409173834466, 0.30342329499300225, 0.30124962500009017, 0.2989297150531095, 0.29647337280045927, 0.2938904058905384, 0.29119062197174583, 0.28838382869248075, 0.285479833701142, 0.2824884446461287, 0.27942024662511955, 0.27628893453291237, 0.273108980713585, 0.269894857511215, 0.26666103726987994, 0.26342199233365754, 0.26019219504662533, 0.25698611775286123, 0.2538182327964426, 0.2507030125214473, 0.2476549292719528, 0.24468845539203687, 0.24181806322577715, 0.23905822511725125, 0.23642341341053685, 0.23392810044971163, 0.23158675857885308, 0.22941386014203902, 0.22742387748334705, 0.2256312829468548, 0.22405054887663986, 0.22269614761678, 0.22158255151135284, 0.22072423290443602, 0.22013566414010713, 0.2198313175624438, 0.21982566551552388, 0.22013318034342477, 0.22076833439022428, 0.2217456],
        [0.2726751860142571, 0.28159359047742294, 0.2896447493612776, 0.2968663575451466, 0.3032961099083553, 0.3089717013302295, 0.31393082669009437, 0.3182111808672754, 0.3218504587410984, 0.32488635519088876, 0.32735656509597183, 0.3292987833356731, 0.33075070478931823, 0.33175002433623263, 0.3323344368557419, 0.3325416372271712, 0.33240932032984655, 0.331975181043093, 0.33127691424623623, 0.3303522148186017, 0.32923877763951515, 0.32797429758830166, 0.326596469544287, 0.3251429883867965, 0.3236515489951559, 0.3221598462486904, 0.3207055750267257, 0.31932643020858725, 0.3180601066736004, 0.316944299301091, 0.31601670297038426, 0.31530377224158207, 0.3147870003978919, 0.3144366404032976, 0.3142229452217826, 0.31411616781733104, 0.31408656115392647, 0.3141043781955527, 0.31413987190619364, 0.3141632952498328, 0.314144901190454, 0.3140549426920411, 0.3138636727185779, 0.31354134423404817, 0.3130582102024354, 0.31238452358772373, 0.31149709903480693, 0.31039899791222086, 0.30909984326941103, 0.3076092581558236, 0.3059368656209043, 0.3040922887140992, 0.3020851504848539, 0.29992507398261425, 0.2976216822568264, 0.295184598356936, 0.29262344533238904, 0.2899478462326313, 0.28716742410710877, 0.2842918020052671, 0.28133060297655244, 0.27829423947461895, 0.275196281569955, 0.2720510887372574, 0.26887302045122335, 0.26567643618654924, 0.26247569541793214, 0.25928515762006865, 0.256119182267656, 0.2529921288353908, 0.24991835679796992, 0.2469122256300902, 0.24398809480644854, 0.24116032380174163, 0.23844327209066649, 0.23585129914791997, 0.23339876444819876, 0.2311000274661998, 0.22896944767661984, 0.2270213845541559, 0.22527019757350464, 0.22373024620936308, 0.22241588993642786, 0.221341488229396, 0.22052140056296435, 0.21996998641182955, 0.21970160525068858, 0.2197306165542383, 0.22007137979717553, 0.22073825445419712, 0.2217455999999999],
        [0.27185283865930016, 0.28061262117927144, 0.28852410526062405, 0.29562406174438477, 0.30194926147158013, 0.3075364752832373, 0.3124224740203827, 0.3166440285240434, 0.32023790963524584, 0.3232408881950172, 0.32568973504438387, 0.3276212210243729, 0.3290721169760109, 0.3300791937403245, 0.33067922215834084, 0.3309089730710865, 0.3308052173195881, 0.3304047257448726, 0.3297442691879668, 0.32886061848989745, 0.32779054449169126, 0.3265708180343749, 0.32523820995897523, 0.3238294911065191, 0.3223814323180333, 0.3209308044345445, 0.31951437829707946, 0.31816892474666497, 0.31693121462432783, 0.31583801877109474, 0.3149261080279926, 0.31422130260864833, 0.3137056202170908, 0.3133501279299485, 0.31312589282385045, 0.31300398197542545, 0.3129554624613026, 0.31295140135811034, 0.312962865742478, 0.31296092269103404, 0.3129166392804076, 0.31280108258722733, 0.31258531968812253, 0.3122404176597214, 0.31173744357865324, 0.31104746452154697, 0.310147943905736, 0.30904193051137413, 0.3077388694593195, 0.30624820587043056, 0.3045793848655655, 0.30274185156558286, 0.30074505109134103, 0.298598428563698, 0.29631142910351266, 0.2938934978316427, 0.29135407986894696, 0.28870262033628374, 0.28594856435451127, 0.2831013570444878, 0.2801704435270719, 0.2771660681138245, 0.2741016718791181, 0.27099149508802783, 0.2678497780056286, 0.2646907608969959, 0.2615286840272046, 0.25837778766132985, 0.255252312064447, 0.25216649750163084, 0.2491345842379568, 0.24617081253849984, 0.2432894226683352, 0.24050465489253794, 0.23783074947618318, 0.23528194668434618, 0.23287248678210187, 0.23061661003452555, 0.22852855670669225, 0.22662256706367723, 0.2249128813705554, 0.22341373989240207, 0.2221393828942923, 0.2211040506413014, 0.22032198339850428, 0.21980742143097612, 0.2195746050037921, 0.21963777438202742, 0.22001116983075697, 0.2207090316150561, 0.22174559999999993],
        [0.27122014605768063, 0.2798221558056087, 0.2875938198289013, 0.29457104223731884, 0.30078972714062185, 0.3062857786485712, 0.31109510087092734, 0.31525359791745083, 0.3187971738979025, 0.3217617329220429, 0.3241831790996325, 0.3260974165404321, 0.32754034935420206, 0.32854788165070353, 0.3291559175396965, 0.32940036113094195, 0.32931711653420026, 0.32894208785923224, 0.32831117921579855, 0.32746029471365967, 0.3264253384625763, 0.325242214572309, 0.32394682715261847, 0.32257508031326526, 0.32116287816400985, 0.3197461248146132, 0.3183607243748356, 0.3170425809544379, 0.3158275986631805, 0.3147516816108241, 0.31385073390712953, 0.313149981555122, 0.31263193813088724, 0.31226843910377544, 0.3120313199431369, 0.311892416118322, 0.31182356309868114, 0.31179659635356466, 0.31178335135232293, 0.3117556635643061, 0.3116853684588649, 0.3115443015053494, 0.31130429817311, 0.31093719393149716, 0.31041482424986105, 0.3097090245975521, 0.3087978689275981, 0.30768438512773544, 0.30637783956937814, 0.30488749862394016, 0.3032226286628355, 0.3013924960574779, 0.2994063671792815, 0.2972735083996601, 0.2950031860900277, 0.2926046666217981, 0.29008721636638546, 0.2874601016952036, 0.2847325889796664, 0.2819139445911877, 0.2790134349011818, 0.2760411356743509, 0.273010360248553, 0.26993523135493447, 0.26682987172464157, 0.26370840408882085, 0.2605849511786186, 0.25747363572518134, 0.2543885804596555, 0.2513439081131874, 0.2483537414169235, 0.24543220310201025, 0.242593415899594, 0.23985150254082113, 0.23722058575683813, 0.2347147882787914, 0.2323482328378273, 0.23013504216509226, 0.22808933899173273, 0.22622524604889507, 0.22455688606772575, 0.2230983817793711, 0.22186385591497762, 0.2208674312056917, 0.22012323038265974, 0.21964537617702815, 0.21944799131994333, 0.21954519854255167, 0.21995112057599955, 0.22067988015143356, 0.22174559999999996],
        [0.2707915885321138, 0.2792373979532795, 0.28686964007137755, 0.29372341940183344, 0.2998338404600728, 0.3052360077615211, 0.30996502582160396, 0.31405599915574695, 0.3175440322793754, 0.3204642297079153, 0.32285169595679214, 0.3247415355414312, 0.3261688529772582, 0.32716875277969876, 0.3277763394641783, 0.32802671754612256, 0.32795499154095675, 0.32759626596410696, 0.32698564533099844, 0.32615823415705675, 0.3251491369577076, 0.32399345824837633, 0.3227263025444887, 0.32138277436147017, 0.31999797821474646, 0.3186070186197429, 0.3172450000918851, 0.3159470271465988, 0.3147482042993094, 0.31368363606544253, 0.3127884269604237, 0.3120872561739041, 0.3115631015924379, 0.3111885157768041, 0.31093605128778234, 0.31077826068615216, 0.3106876965326932, 0.3106369113881846, 0.31059845781340617, 0.3105448883691371, 0.3104487556161571, 0.3102826121152455, 0.31001901042718183, 0.30963050311274565, 0.3090896427327162, 0.3083689818478733, 0.30744716081051476, 0.3063271711390122, 0.30501809214325565, 0.30352900313313536, 0.30186898341854135, 0.3000471123093639, 0.298072469115493, 0.29595413314681873, 0.29370118371323134, 0.29132270012462086, 0.2888277616908774, 0.28622544772189124, 0.28352483752755225, 0.2807350104177507, 0.27786504570237663, 0.2749248452878126, 0.2719276014664109, 0.2688873291270159, 0.26581804315847224, 0.26273375844962454, 0.2596484898893174, 0.25657625236639525, 0.2535310607697029, 0.2505269299880848, 0.24757787491038546, 0.24469791042544956, 0.2419010514221217, 0.23920131278924625, 0.236612709415668, 0.23414925619023147, 0.23182496800178123, 0.22965385973916183, 0.22764994629121782, 0.2258272425467939, 0.2241997633947345, 0.2227815237238843, 0.2215865384230878, 0.2206288223811897, 0.21992239048703446, 0.21948125762946671, 0.21931943869733095, 0.21945094857947187, 0.21988980216473386, 0.22065001434196174, 0.22174559999999996],
        [0.2705816464053151, 0.27887355121912827, 0.2863673129933211, 0.2930973136158132, 0.2990979349745251, 0.30440355895737675, 0.3090485674522885, 0.3130673423471801, 0.31649426552997206, 0.31936371888858445, 0.3217100843109372, 0.32356774368495067, 0.3249710788985449, 0.32595447183964, 0.32655230439615607, 0.32679895845601337, 0.326728815907132, 0.32637625863743197, 0.32577566853483353, 0.32496142748725687, 0.323967917382622, 0.3228295201088492, 0.3215806175538583, 0.32025559160556977, 0.31888882415190367, 0.31751469708078, 0.31616759228011904, 0.31488189163784075, 0.3136919770418655, 0.3126322303801133, 0.3117370335405042, 0.31103057355789626, 0.3104962580548993, 0.3101072998010606, 0.30983691156592774, 0.3096583061190485, 0.30954469622997, 0.30946929466823986, 0.3094053142034057, 0.30932596760501513, 0.30920446764261533, 0.3090140270857541, 0.308727858703979, 0.3083191752668373, 0.3077611895438766, 0.30702711430464463, 0.306096106264608, 0.30497109792291205, 0.30366096572462087, 0.302174586114799, 0.3005208355385109, 0.29870859044082076, 0.2967467272667932, 0.29464412246149246, 0.29240965246998313, 0.29005219373732943, 0.28758062270859597, 0.285003815828847, 0.2823306495431469, 0.27957000029656004, 0.27673074453415114, 0.27382260008582404, 0.2708586503208427, 0.26785281999331056, 0.264819033857331, 0.2617712166670078, 0.2587232931764443, 0.255689188139744, 0.2526828263110106, 0.2497181324443474, 0.24680903129385812, 0.2439694476136461, 0.24121330615781508, 0.2385545316804684, 0.23600704893570962, 0.23358478267764235, 0.23130165766036992, 0.22917159863799608, 0.22720853036462416, 0.2254263775943579, 0.22383906508130055, 0.22246051757955582, 0.2213046598432271, 0.22038541662641814, 0.21971671268323226, 0.219312472767773, 0.21918662163414399, 0.21935308403644865, 0.2198257847287905, 0.22061864846527307, 0.22174559999999993],
        [0.27060480000000003, 0.2787458192, 0.28610258560000007, 0.29270884525714286, 0.2985983442285714, 0.3038048285714286, 0.3083620443428571, 0.3123037376000001, 0.31566365439999994, 0.31847554079999996, 0.32077314285714287, 0.3225902066285715, 0.3239604781714286, 0.3249177035428572, 0.32549562880000005, 0.325728, 0.32564856319999996, 0.3252910644571429, 0.32468924982857145, 0.32387686537142857, 0.3228876571428571, 0.3217553711999999, 0.3205137536, 0.3191965504, 0.31783750765714286, 0.3164703714285715, 0.3151288877714286, 0.3138468027428572, 0.31265786240000004, 0.31159581280000004, 0.31069440000000004, 0.3099773808, 0.3094285549714287, 0.30902173302857144, 0.3087307254857143, 0.30852934285714295, 0.30839139565714296, 0.30829069440000006, 0.30820104960000005, 0.3080962717714286, 0.3079501714285715, 0.3077365590857143, 0.30742924525714294, 0.3070020404571429, 0.30642875520000007, 0.30568320000000004, 0.304744992, 0.303616974857143, 0.302307798857143, 0.3008261142857144, 0.2991805714285716, 0.29737982057142864, 0.2954325120000001, 0.29334729600000015, 0.291132822857143, 0.2887977428571429, 0.2863507062857144, 0.28380036342857157, 0.2811553645714287, 0.2784243600000001, 0.2756160000000002, 0.2727398032000002, 0.26980876160000017, 0.26683673554285725, 0.26383758537142865, 0.26082517142857153, 0.25781335405714295, 0.2548159936, 0.2518469504000001, 0.24892008480000008, 0.2460492571428572, 0.24324832777142863, 0.24053115702857147, 0.2379116052571429, 0.23540353279999995, 0.23302080000000006, 0.23077726719999994, 0.22868679474285714, 0.22676324297142855, 0.2250204722285714, 0.22347234285714282, 0.22213271519999994, 0.22101544959999989, 0.22013440639999995, 0.2195034459428571, 0.21913642857142854, 0.21904721462857138, 0.21924966445714286, 0.21975763839999995, 0.22058499679999996, 0.22174560000000001],
        [0.27087090296927047, 0.27886452028775033, 0.28608612028554653, 0.29256890660469126, 0.29834608288721626, 0.3034508527751536, 0.3079164199105352, 0.31177598793539296, 0.3150627604917589, 0.31780994122166506, 0.3200507337671435, 0.32181834177022584, 0.3231459688729441, 0.32406681871733045, 0.3246140949454168, 0.32482100119923507, 0.3247207411208171, 0.32434651835219513, 0.3237315365354008, 0.32290899931246625, 0.3219121103254235, 0.3207740732163043, 0.31952809162714085, 0.3182073691999648, 0.3168451095768085, 0.3154745163997036, 0.3141287933106821, 0.31284114395177626, 0.31164477196501755, 0.3105728809924384, 0.3096586746760704, 0.3089255464599477, 0.308357648996113, 0.30792932473861034, 0.30761491614148445, 0.30738876565878, 0.3072252157445411, 0.3070986088528126, 0.3069832874376387, 0.3068535939530642, 0.3066838708531332, 0.3064484605918905, 0.3061217056233807, 0.30567794840164814, 0.30509153138073714, 0.30433679701469235, 0.30339376313969046, 0.302265149120437, 0.30095934970376864, 0.2994847596365235, 0.2978497736655388, 0.2960627865376519, 0.2941321929997002, 0.29206638779852123, 0.28987376568095236, 0.287562721393831, 0.2851416496839946, 0.2826189452982805, 0.28000300298352626, 0.2773022174865692, 0.2745249835542468, 0.27168060142275, 0.26878199328568414, 0.26584298682600827, 0.2628774097266812, 0.25989908967066166, 0.25692185434090903, 0.2539595314203816, 0.25102594859203875, 0.2481349335388393, 0.2453003139437421, 0.24253591748970604, 0.23985557185969014, 0.23727310473665322, 0.23480234380355416, 0.23245711674335207, 0.23025125123900564, 0.22819857497347384, 0.22631291562971562, 0.22460810089068992, 0.22309795843935562, 0.22179631595867158, 0.2207170011315968, 0.21987384164109014, 0.21928066517011058, 0.2189512994016169, 0.21889957201856813, 0.21913931070392315, 0.21968434314064078, 0.22054849701168008, 0.22174559999999993],
        [0.27137130228777573, 0.27922043205428054, 0.28630824099954877, 0.2926674775412649, 0.2983308900971134, 0.30333122708477867, 0.30770123692194534, 0.31147366802629767, 0.3146812688155203, 0.31735678770729786, 0.3195329731193145, 0.32124257346925505, 0.32251833717480366, 0.32339301265364506, 0.3238993483234637, 0.32407009260194386, 0.3239379939067702, 0.3235358006556272, 0.3228962612661994, 0.32205212415617107, 0.32103613774322687, 0.31988105044505133, 0.31861961067932876, 0.3172845668637436, 0.3159086674159807, 0.3145246607537243, 0.31316529529465875, 0.3118633194564687, 0.31065148165683865, 0.309562530313453, 0.3086292138439963, 0.3078746249647974, 0.30728323358676285, 0.3068298539194435, 0.30648930017239057, 0.30623638655515456, 0.306045927277287, 0.30589273654833843, 0.30575162857785987, 0.3055974175754022, 0.30540491775051654, 0.30514894331275366, 0.3048043084716647, 0.3043458274368005, 0.3037483144177118, 0.30298658362395, 0.30204099845819243, 0.3009141190956248, 0.2996140549045589, 0.298148915253307, 0.2965268095101813, 0.2947558470434937, 0.29284413722155667, 0.29079978941268203, 0.2886309129851821, 0.2863456173073689, 0.28395201174755474, 0.2814582056740516, 0.27887230845517164, 0.27620242945922685, 0.2734566780545298, 0.27064411618966344, 0.2677776161342974, 0.2648710027383722, 0.26193810085182845, 0.2589927353246066, 0.25604873100664743, 0.2531199127478915, 0.2502201053982793, 0.2473631338077517, 0.24456282282624922, 0.24183299730371233, 0.23918748209008173, 0.23664010203529803, 0.23420468198930178, 0.23189504680203374, 0.2297250213234344, 0.2277084304034443, 0.2258590988920042, 0.22419085163905464, 0.22271751349453622, 0.22145290930838957, 0.2204108639305553, 0.21960520221097407, 0.2190497489995864, 0.21875832914633303, 0.21874476750115432, 0.2190228889139911, 0.21960651823478386, 0.2205094803134733, 0.22174560000000001],
        [0.2720927182605514, 0.2797994468665032, 0.2867541870804585, 0.29298930985065474, 0.29853718612532876, 0.30343018685271794, 0.30770068298105946, 0.31138104545859024, 0.3145036452335478, 0.3171008532541692, 0.3192050404686916, 0.32084857782535203, 0.32206383627238777, 0.3228831867580361, 0.32333900023053413, 0.32346364763811897, 0.32328949992902767, 0.3228489280514977, 0.3221743029537661, 0.3212979955840699, 0.3202523768906466, 0.3190698178217329, 0.31778268932556647, 0.3164233623503841, 0.3150242078444233, 0.313617596755921, 0.3122359000331143, 0.3109114886242408, 0.30967673347753705, 0.30856400554124075, 0.3076056757635887, 0.3068245922084375, 0.30620551140211916, 0.30572366698658493, 0.3053542926037861, 0.30507262189567436, 0.30485388850420075, 0.3046733260713164, 0.3045061682389729, 0.3043276486491215, 0.3041130009437134, 0.3038374587647, 0.3034762557540326, 0.3030046255536625, 0.3023978018055408, 0.30163101815161913, 0.3006849351428963, 0.29956192096656165, 0.29826977071885175, 0.29681627949600387, 0.29520924239425494, 0.29345645450984154, 0.2915657109390008, 0.28954480677796945, 0.28740153712298455, 0.28514369707028303, 0.2827790817161015, 0.28031548615667723, 0.277760705488247, 0.27512253480704746, 0.27240876920931567, 0.2696282125971248, 0.26679370409589215, 0.2639190916368713, 0.26101822315131584, 0.2581049465704795, 0.25519310982561577, 0.2522965608479781, 0.2494291475688204, 0.2466047179193961, 0.24383711983095863, 0.2411402012347618, 0.23852781006205911, 0.2360137942441041, 0.23361200171215038, 0.23133628039745172, 0.22920047823126147, 0.22721844314483328, 0.22540402306942078, 0.22377106593627757, 0.22233341967665718, 0.22110493222181327, 0.2200994515029993, 0.21933082545146906, 0.21881290199847606, 0.21855952907527376, 0.21858455461311593, 0.21890182654325596, 0.2195251927969476, 0.2204685013054444, 0.22174560000000001],
        [0.2730218711926335, 0.28058745709133076, 0.28740919786672764, 0.29351915531665146, 0.2989493912389283, 0.3037319674313855, 0.3078989456918495, 0.311482387818147, 0.31451435560810515, 0.31702691085955054, 0.3190521153703099, 0.32062203093821, 0.3217687193610775, 0.32252424243673933, 0.32292066196302227, 0.3229900397377532, 0.32276443755875844, 0.3222759172238652, 0.3215565405309002, 0.32063836927768996, 0.3195534652620615, 0.31833389028184156, 0.31701170613485674, 0.3156189746189339, 0.3141877575319, 0.31275011667158154, 0.31133811383580534, 0.3099838108223983, 0.30871926942918704, 0.3075765514539984, 0.30658771869465923, 0.305775424084757, 0.3051246851009229, 0.3046111103555485, 0.30421030846102576, 0.3038978880297465, 0.3036494576741026, 0.30344062600648575, 0.3032470016392879, 0.3030441931849008, 0.3028078092557162, 0.3025134584641261, 0.3021367494225225, 0.30165329074329683, 0.30103869103884096, 0.3002685589215469, 0.2993238103811929, 0.2982065909171025, 0.29692435340598616, 0.295484550724554, 0.29389463574951613, 0.29216206135758294, 0.2902942804254644, 0.28829874582987086, 0.2861829104475126, 0.28395422715509955, 0.28162014882934217, 0.27918812834695045, 0.27666561858463473, 0.27406007241910507, 0.27137894272707186, 0.2686307557415184, 0.2658283311205206, 0.2629855618784278, 0.2601163410295892, 0.257234561588354, 0.25435411656907125, 0.25148889898609045, 0.24865280185376057, 0.24585971818643088, 0.24312354099845068, 0.24045816330416903, 0.23787747811793528, 0.23539537845409844, 0.2330257573270079, 0.23078250775101286, 0.22867952274046238, 0.22673069530970583, 0.22494991847309223, 0.22335108524497105, 0.22194808863969123, 0.22075482167160207, 0.21978517735505287, 0.2190530487043928, 0.21857232873397098, 0.21835691045813668, 0.21842068689123903, 0.21877755104762747, 0.21944139594165082, 0.22042611458765865, 0.2217456],
        [0.2741454813890577, 0.28157035509567574, 0.2882585126968084, 0.2942417657230459, 0.29955192570497824, 0.3042208041731954, 0.30828021265828753, 0.3117619626908445, 0.3146978658014563, 0.31711973352071327, 0.31905937737920514, 0.32054860890752196, 0.3216192396362538, 0.3223030810959906, 0.3226319448173226, 0.32263764233083964, 0.32235198516713165, 0.3218067848567888, 0.32103385293040126, 0.3200650009185588, 0.3189320403518515, 0.31766678276086935, 0.31630103967620254, 0.314866622628441, 0.31339534314817474, 0.3119190127659937, 0.3104694430124881, 0.30907844541824786, 0.30777783151386284, 0.3065994128299232, 0.30557500089701894, 0.304727096487645, 0.30404095734191533, 0.30349253044184843, 0.3030577627694632, 0.30271260130677846, 0.302432993035813, 0.30219488493858543, 0.30197422399711443, 0.30174695719341893, 0.3014890315095177, 0.30117639392742923, 0.30078499142917264, 0.3002907709967664, 0.2996696796122291, 0.29889766425758024, 0.297955861360473, 0.2968461651311031, 0.2955756592253008, 0.29415142729889676, 0.2925805530077216, 0.29087012000760565, 0.2890272119543795, 0.2870589125038737, 0.2849723053119187, 0.282774474034345, 0.2804725023269832, 0.2780734738456639, 0.27558447224621746, 0.2730125811844744, 0.2703648843162654, 0.2676496107192287, 0.2648795711582355, 0.2620687218199643, 0.259231018891094, 0.25638041855830357, 0.2535308770082716, 0.2506963504276769, 0.2478907950031986, 0.2451281669215152, 0.24242242236930572, 0.23978751753324878, 0.23723740860002338, 0.23478605175630826, 0.23244740318878224, 0.23023541908412412, 0.22816405562901276, 0.22624726901012698, 0.22449901541414558, 0.22293325102774733, 0.22156393203761107, 0.2204050146304157, 0.21947045499284, 0.21877420931156277, 0.21833023377326286, 0.21815248456461897, 0.21825491787231002, 0.2186514898830149, 0.21935615678341222, 0.22038287476018095, 0.22174559999999996],
        [0.2754502691548601, 0.2827340332464506, 0.2892873709091524, 0.2951418928536292, 0.3003292097905445, 0.3048809324305621, 0.30882867148434573, 0.3122040376625589, 0.31503864167586526, 0.31736409423492873, 0.31921200605041283, 0.32061398783298123, 0.3216016502932976, 0.3222066041420255, 0.3224604600898288, 0.3223948288473711, 0.3220413211253159, 0.32143154763432724, 0.3205971190850685, 0.3195696461882034, 0.3183807396543957, 0.3170620101943089, 0.31564506851860685, 0.3141615253379531, 0.31264299136301144, 0.3111210773044455, 0.3096273938729188, 0.3081935517790952, 0.3068511617336383, 0.3056318344472117, 0.30456718063047933, 0.3036795853109902, 0.3029545307838373, 0.30236827366099883, 0.30189707055445275, 0.3015171780761779, 0.30120485283815235, 0.3009363514523544, 0.30068793053076254, 0.3004358466853549, 0.30015635652810985, 0.2998257166710057, 0.299420183726021, 0.298916014305134, 0.29828946502032266, 0.2975167924835656, 0.2965793252681274, 0.2954786797924182, 0.2942215444361344, 0.2928146075789719, 0.2912645576006274, 0.2895780828807973, 0.28776187179917767, 0.28582261273546505, 0.2837669940693556, 0.28160170418054586, 0.2793334314487321, 0.2769688642536106, 0.27451469097487763, 0.27197759999222976, 0.2693642796853632, 0.2666826426266405, 0.26394549815908913, 0.26116687981840314, 0.25836082114027603, 0.25554135566040165, 0.2527225169144739, 0.24991833843818645, 0.2471428537672332, 0.2444100964373077, 0.24173409998410395, 0.2391288979433156, 0.23660852385063647, 0.23418701124176042, 0.23187839365238105, 0.22969670461819247, 0.22765597767488802, 0.22577024635816179, 0.2240535442037074, 0.22251990474721872, 0.22118336152438955, 0.2200579480709136, 0.21915769792248466, 0.2184966446147966, 0.21808882168354307, 0.21794826266441797, 0.21808900109311496, 0.2185250705053279, 0.2192705044367505, 0.2203393364230766, 0.22174560000000001],
        [0.27692295479507606, 0.2840643839105678, 0.29048101184221164, 0.2962042884921918, 0.30126566376269287, 0.30569658755589935, 0.3095285097739956, 0.31279288031916613, 0.3155211490935954, 0.3177447659994679, 0.3194951809389682, 0.32080384381428056, 0.32170220452758935, 0.3222217129810794, 0.3223938190769348, 0.3222499727173403, 0.32182162380448004, 0.32114022224053884, 0.320237217927701, 0.3191440607681508, 0.3178922006640731, 0.31651308751765195, 0.31503817123107203, 0.31349890170651773, 0.31192672884617373, 0.31035310255222426, 0.3088094727268536, 0.3073272892722467, 0.30593800209058764, 0.3046730610840609, 0.30356391615485123, 0.3026328664486814, 0.30186560808542995, 0.3012386864285133, 0.3007286468413483, 0.3003120346873519, 0.2999653953299407, 0.29966527413253174, 0.29938821645854163, 0.2991107676713871, 0.298809473134485, 0.2984608782112523, 0.2980415282651057, 0.2975279686594619, 0.29689674475773764, 0.2961244019233499, 0.2951924392915468, 0.2941021710849033, 0.29285986529782515, 0.2914717899247185, 0.28994421295998996, 0.2882834023980452, 0.2864956262332905, 0.284587152460132, 0.2825642490729759, 0.2804331840662282, 0.27820022543429523, 0.275871641171583, 0.2734536992724977, 0.2709526677314454, 0.2683748145428323, 0.2657277165601376, 0.263024186073134, 0.26027834423066637, 0.2575043121815806, 0.2547162110747218, 0.2519281620589357, 0.24915428628306743, 0.24640870489596275, 0.24370553904646694, 0.24105890988342557, 0.23848293855568395, 0.23599174621208757, 0.23359945400148185, 0.2313201830727123, 0.2291680545746244, 0.2271571896560635, 0.22530170946587508, 0.2236157351529045, 0.22211338786599744, 0.22080878875399912, 0.2197160589657551, 0.21884931965011079, 0.21822269195591168, 0.21785029703200318, 0.21774625602723074, 0.2179246900904398, 0.21839972037047584, 0.2191854680161842, 0.22029605417641043, 0.2217456],
        [0.2785502586147418, 0.28554729945494, 0.29182467483443797, 0.29741370442252485, 0.30234570788848963, 0.3066520049016214, 0.31036391513120953, 0.3135127582465429, 0.31612985391691095, 0.31824652181160246, 0.31989408159990684, 0.3211038529511132, 0.32190715553451055, 0.3223353090193881, 0.3224196330750349, 0.32219144737074024, 0.321682071575793, 0.3209228253594827, 0.3199450283910981, 0.3187800003399286, 0.31745906087526315, 0.316013529666391, 0.3144747263826013, 0.31287397069318307, 0.3112425822674256, 0.3096118807746179, 0.30801318588404913, 0.30647781726500845, 0.3050370945867849, 0.30372233751866784, 0.3025648657299462, 0.3015869157946076, 0.30077439190543426, 0.3001041151599062, 0.299552906655504, 0.29909758748970805, 0.29871497875999875, 0.29838190156385647, 0.2980751769987616, 0.29777162616219455, 0.29744807015163577, 0.2970813300645657, 0.29664822699846466, 0.2961255820508131, 0.29549021631909134, 0.2947189509007799, 0.293793440618122, 0.29271467519241334, 0.291488478069712, 0.29012067269607655, 0.28861708251756557, 0.28698353098023716, 0.28522584153014985, 0.2833498376133621, 0.28136134267593216, 0.27926618016391863, 0.27707017352337976, 0.2747791462003741, 0.27239892164095997, 0.2699353232911957, 0.26739417459713977, 0.26478269761610523, 0.2621137088504223, 0.2594014234136767, 0.25666005641945344, 0.25390382298133746, 0.25114693821291423, 0.24840361722776874, 0.24568807513948626, 0.24301452706165194, 0.240397188107851, 0.23785027339166845, 0.23538799802668964, 0.2330245771264997, 0.2307742258046837, 0.2286511591748271, 0.22666959235051473, 0.22484374044533192, 0.2231878185728639, 0.22171604184669572, 0.22044262538041265, 0.21938178428759986, 0.21854773368184244, 0.2179546886767257, 0.21761686438583472, 0.21754847592275467, 0.21776373840107077, 0.2182768669343682, 0.21910207663623205, 0.22025358262024758, 0.22174559999999996],
        [0.280318900918893, 0.2871686722464798, 0.2933035992242836, 0.2987548924284191, 0.3035537624350007, 0.3077314198201425, 0.3113190751599594, 0.3143479390305655, 0.31684922200807547, 0.31885413466860363, 0.3203938875882644, 0.32149969134317247, 0.32220275650944175, 0.3225342936631873, 0.32252551338052315, 0.3222076262375637, 0.32161184281042365, 0.32076937367521746, 0.3197114294080593, 0.3184692205850638, 0.3170739577823454, 0.3155568515760184, 0.3139491125421973, 0.31228195125699665, 0.31058657829653075, 0.3088942042369142, 0.3072360396542614, 0.3056432951246865, 0.3041471812243043, 0.3027789085292292, 0.3015696876155754, 0.3005417092426576, 0.2996810849025913, 0.29896490627069155, 0.2983702650222738, 0.2978742528326537, 0.2974539613771465, 0.29708648233106755, 0.29674890736973225, 0.2964183281684561, 0.29607183640255436, 0.29568652374734267, 0.29523948187813615, 0.2947078024702504, 0.29406857719900054, 0.2932988977397024, 0.29238056643524374, 0.2913142282988038, 0.2901052390111337, 0.2887589542529855, 0.28728072970511065, 0.2856759210482609, 0.2839498839631875, 0.2821079741306424, 0.2801555472313772, 0.2780979589461434, 0.2759405649556927, 0.2736887209407768, 0.2713477825821469, 0.268923105560555, 0.26642004555675275, 0.2638454508909271, 0.2612121404410069, 0.2585344257243564, 0.2558266182583401, 0.25310302956032227, 0.25037797114766713, 0.24766575453773895, 0.24498069124790225, 0.24233709279552126, 0.23974927069796043, 0.23723153647258374, 0.23479820163675585, 0.23246357770784093, 0.23024197620320327, 0.22814770864020728, 0.22619508653621723, 0.22439842140859742, 0.22277202477471217, 0.22133020815192592, 0.2200872830576028, 0.21905756100910725, 0.21825535352380365, 0.21769497211905622, 0.21739072831222922, 0.21735693362068711, 0.2176078995617941, 0.21815793765291458, 0.21902135941141285, 0.2202124763546532, 0.22174560000000004],
        [0.2822156020125653, 0.2889143946520992, 0.29490302435020016, 0.3002126042936654, 0.30487424766929183, 0.30891906766387667, 0.31237817746421703, 0.31528269025711, 0.31766371922935266, 0.31955237756774235, 0.32097977845907616, 0.3219770350901509, 0.32257526064776393, 0.3228055683187123, 0.32269907128979325, 0.3222868827478036, 0.32160011587954074, 0.3206698838718017, 0.31952729991138357, 0.31820347718508346, 0.3167295288796987, 0.315136568182026, 0.3134557082788628, 0.3117180623570061, 0.3099547436032531, 0.30819686520440087, 0.3064755403472465, 0.304821882218587, 0.3032670040052198, 0.30184201889394163, 0.30057804007155, 0.2994972226867201, 0.298585889735642, 0.2978214061763832, 0.29718113696701187, 0.29664244706559634, 0.29618270143020425, 0.29577926501890384, 0.2954095027897633, 0.2950507797008503, 0.29468046071023296, 0.2942759107759796, 0.29381449485615796, 0.2932735779088362, 0.29263052489208224, 0.2918627007639641, 0.29095205393030266, 0.2898988665879295, 0.28870800438142874, 0.28738433295538446, 0.28593271795438147, 0.28435802502300345, 0.28266511980583503, 0.2808588679474602, 0.2789441350924634, 0.27692578688542885, 0.27480868897094074, 0.2725977069935833, 0.27029770659794106, 0.2679135534285978, 0.2654501131301383, 0.262913841480988, 0.26031755479493973, 0.25767565951962773, 0.25500256210268624, 0.25231266899174937, 0.24962038663445146, 0.2469401214784267, 0.24428627997130942, 0.24167326856073373, 0.23911549369433402, 0.2366273618197444, 0.23422327938459905, 0.23191765283653237, 0.22972488862317847, 0.22765939319217177, 0.2257355729911463, 0.22396783446773633, 0.22237058406957616, 0.22095822824430011, 0.2197451734395422, 0.21874582610293683, 0.21797459268211816, 0.21744587962472053, 0.21717409337837812, 0.21717364039072506, 0.21745892710939577, 0.21804435998202434, 0.21894434545624503, 0.22017328997969224, 0.22174559999999996],
        [0.2842270822007948, 0.2907703590387112, 0.29660818955063967, 0.30177159180205454, 0.3062915838584292, 0.3101991837852379, 0.3135254096479545, 0.3163012795120528, 0.3185578114430068, 0.3203260235062904, 0.32163693376737756, 0.3225215602917421, 0.3230109211448581, 0.3231360343921992, 0.32292791809923943, 0.3224175903314528, 0.32163606915431314, 0.32061437263329434, 0.31938351883387034, 0.31797452582151514, 0.3164184116617025, 0.31474619441990637, 0.3129888921616007, 0.3111775229522595, 0.3093431048573565, 0.3075166559423657, 0.30572919427276096, 0.3040117379140163, 0.3023953049316056, 0.30091091339100257, 0.29958958135768143, 0.2984534320206842, 0.29748900906332737, 0.2966739612924953, 0.2959859375150723, 0.2954025865379432, 0.2949015571679926, 0.29446049821210485, 0.29405705847716446, 0.2936688867700561, 0.29327363189766426, 0.2928489426668735, 0.2923724678845684, 0.29182185635763347, 0.291174756892953, 0.290408818297412, 0.28950614029068966, 0.2884666262436461, 0.2872946304399357, 0.28599450716321356, 0.2845706106971344, 0.2830272953253531, 0.2813689153315243, 0.27959982499930297, 0.2777243786123438, 0.27574693045430143, 0.273671834808831, 0.27150344595958714, 0.26924611819022476, 0.26690420578439844, 0.26448206302576327, 0.26198573448267237, 0.2594280258622736, 0.2568234331564131, 0.2541864523569374, 0.2515315794556926, 0.24887331044452493, 0.24622614131528076, 0.2436045680598064, 0.24102308666994812, 0.2384961931375522, 0.23603838345446487, 0.23366415361253248, 0.23138799960360124, 0.22922441741951752, 0.22718790305212755, 0.22529295249327755, 0.22355406173481387, 0.22198572676858286, 0.2206024435864307, 0.21941870818020368, 0.2184490165417481, 0.2177078646629103, 0.2172097485355365, 0.216969164151473, 0.21700060750256606, 0.217318574580662, 0.2179375613776071, 0.21887206388524758, 0.22013657809542975, 0.22174559999999993],
        [0.2863400617886172, 0.2927224577732281, 0.29840433416405426, 0.3034166067373775, 0.3077901912694791, 0.31155600353664076, 0.314744959315144, 0.3173879743812703, 0.31951596451130143, 0.3211598454815189, 0.3223505330682044, 0.3231189430476393, 0.323495991196105, 0.3235125932898834, 0.32319966510525594, 0.3225881224185043, 0.3217088810059098, 0.32059285664375425, 0.3192709651083191, 0.31777412217588585, 0.3161332436227363, 0.3143792452251518, 0.312543042759414, 0.31065555200180445, 0.30874768872860475, 0.3068503687160966, 0.3049945077405613, 0.3032110215782805, 0.30153082600553577, 0.29998483679860866, 0.29860396973378095, 0.29741031313843874, 0.2963906455443888, 0.2955229180345419, 0.2947850816918093, 0.29415508759910225, 0.2936108868393318, 0.2931304304954093, 0.29269166965024573, 0.29227255538675245, 0.29185103878784047, 0.2914050709364211, 0.2909126029154056, 0.29035158580770487, 0.28969997069623016, 0.28893570866389284, 0.2880410627037956, 0.2870155434498087, 0.28586297344599354, 0.284587175236412, 0.283191971365126, 0.2816811843761972, 0.2800586368136871, 0.27832815122165766, 0.2764935501441706, 0.27455865612528757, 0.2725272917090705, 0.27040327943958087, 0.2681904418608806, 0.2658926015170313, 0.26351358095209493, 0.26105899499236473, 0.2585416275930609, 0.25597605499163506, 0.2533768534255393, 0.2507585991322253, 0.2481358683491449, 0.24552323731374984, 0.24293528226349206, 0.24038657943582326, 0.23789170506819535, 0.23546523539806005, 0.23312174666286917, 0.23087581510007452, 0.228742016947128, 0.2267349284414814, 0.2248691258205865, 0.22315918532189508, 0.22161968318285893, 0.22026519564092997, 0.21911029893355993, 0.2181695692982006, 0.21745758297230391, 0.21698891619332158, 0.21677814519870547, 0.21683984622590732, 0.21718859551237898, 0.2178389692955723, 0.21880554381293899, 0.22010289530193097, 0.2217456],
        [0.28854126108106837, 0.2947565832225625, 0.3002766975288957, 0.3051324008834251, 0.309354490169507, 0.3129737622704989, 0.31602101406975713, 0.3185270424506387, 0.32052264429650046, 0.32203861649069915, 0.3231057559165918, 0.32375485945753496, 0.32401672399688564, 0.32392214641800054, 0.32350192360423663, 0.3227868524389507, 0.32180772980549943, 0.32059535258723987, 0.31918051766752886, 0.31759402192972297, 0.3158666622571792, 0.3140292355332543, 0.3121125386413053, 0.31014736846468877, 0.3081645218867618, 0.306194795790881, 0.30426898706040323, 0.3024178925786855, 0.30067230922908433, 0.2990630338949568, 0.2976208634596597, 0.2963678419338725, 0.295291001837567, 0.294368622818037, 0.2935789845225767, 0.2929003665984803, 0.2923110486930421, 0.2917893104535561, 0.2913134315273167, 0.29086169156161784, 0.290412370203754, 0.2899437471010191, 0.28943410190070734, 0.2888617142501131, 0.2882048637965302, 0.2874418301872532, 0.28655505835701095, 0.28554365439027235, 0.2844108896589407, 0.2831600355349195, 0.28179436339011255, 0.28031714459642315, 0.27873165052575505, 0.2770411525500117, 0.2752489220410967, 0.27335823037091356, 0.27137234891136586, 0.2692945490343571, 0.2671281021117909, 0.2648762795155707, 0.2625423526176002, 0.2601314881064493, 0.25765643393735377, 0.2551318333822158, 0.2525723297129374, 0.24999256620142102, 0.2474071861195686, 0.2448308327392825, 0.24227814933246483, 0.23976377917101774, 0.23730236552684347, 0.23490855167184416, 0.23259698087792208, 0.23038229641697916, 0.22827914156091783, 0.22630215958164024, 0.22446599375104842, 0.22278528734104472, 0.2212746836235312, 0.2199488258704101, 0.21882235735358357, 0.21790992134495377, 0.21722616111642296, 0.2167857199398933, 0.21660324108726695, 0.21669336783044602, 0.21707074344133276, 0.21775001119182943, 0.218745814353838, 0.22007279619926076, 0.2217456],
        [0.290817400383184, 0.2968586277536266, 0.3022105189836158, 0.3069037260239879, 0.3109689008255793, 0.31443669533922664, 0.31733776151576604, 0.31970275130603426, 0.32156231666086743, 0.3229471095311023, 0.3238877818675753, 0.32441498562112253, 0.3245593727425806, 0.3243515951827862, 0.32382230489257546, 0.32300215382278485, 0.3219217939242509, 0.3206118771478101, 0.3191030554442988, 0.31742598076455336, 0.31561130505941043, 0.31368968027970623, 0.31169175837627733, 0.30964819129996013, 0.3075896310015912, 0.3055467294320068, 0.3035501385420434, 0.3016305102825375, 0.29981849660432547, 0.2981447494582438, 0.29663992079512885, 0.29532599430087436, 0.29419028060160296, 0.2932114220584944, 0.2923680610327285, 0.2916388398854849, 0.2910024009779436, 0.2904373866712843, 0.289922439326687, 0.2894362013053312, 0.2889573149683969, 0.2884644226770638, 0.2879361667925118, 0.28735118967592066, 0.28668813368847007, 0.28592564119133995, 0.28504636443772663, 0.2840489952488922, 0.28293623533811557, 0.28171078641867514, 0.28037535020384996, 0.2789326284069187, 0.27738532274115985, 0.27573613491985216, 0.2739877666562746, 0.27214291966370563, 0.27020429565542403, 0.2681745963447087, 0.2660565234448381, 0.26385277866909096, 0.26156606373074615, 0.25920107892131067, 0.25677051884520485, 0.2542890766850775, 0.2517714456235773, 0.2492323188433531, 0.24668638952705352, 0.2441483508573274, 0.2416328960168234, 0.23915471818819034, 0.23672851055407695, 0.23436896629713191, 0.2320907786000041, 0.22990864064534206, 0.2278372456157947, 0.22589128669401076, 0.22408545706263885, 0.22243444990432779, 0.22095295840172638, 0.2196556757374833, 0.21855729509424723, 0.21767250965466703, 0.2170160126013914, 0.2166024971170691, 0.21644665638434885, 0.21656318358587937, 0.21696677190430944, 0.2176721145222878, 0.21869390462246316, 0.22004683538748426, 0.22174559999999996],
        [0.29315520000000006, 0.29901448373333334, 0.3041910378666667, 0.3087153339428572, 0.312617843504762, 0.3159290380952381, 0.31867938925714284, 0.3208993685333334, 0.32261944746666665, 0.32387009759999996, 0.32468179047619045, 0.3250849976380952, 0.3251101906285714, 0.32478784099047614, 0.3241484202666666, 0.32322239999999997, 0.32204025173333317, 0.32063244700952365, 0.3190294573714285, 0.3172617543619047, 0.31535980952380943, 0.3133540943999999, 0.31127508053333325, 0.30915323946666656, 0.3070190427428571, 0.30490296190476185, 0.302835468495238, 0.3008470340571428, 0.29896813013333334, 0.29722922826666665, 0.29566079999999995, 0.2942847461333332, 0.2930886844952381, 0.2920516621714286, 0.291152726247619, 0.29037092380952384, 0.2896853019428572, 0.28907490773333333, 0.2885187882666667, 0.2879959906285715, 0.28748556190476193, 0.28696654918095243, 0.28641799954285724, 0.28581896007619056, 0.28514847786666664, 0.2843856000000001, 0.28351321813333336, 0.2825296022095239, 0.2814368667428572, 0.280237126247619, 0.2789324952380952, 0.27752508822857147, 0.2760170197333334, 0.2744104042666667, 0.27270735634285725, 0.2709099904761904, 0.2690204211809523, 0.26704076297142854, 0.2649731303619048, 0.26281963786666657, 0.2605824, 0.2582656325333333, 0.2558819562666666, 0.2534460932571428, 0.25097276556190473, 0.24847669523809526, 0.24597260434285712, 0.24347521493333324, 0.24099924906666664, 0.23855942879999995, 0.23617047619047615, 0.23384711329523808, 0.23160406217142857, 0.22945604487619048, 0.22741778346666663, 0.22550400000000004, 0.2237294165333333, 0.22210875512380956, 0.22065673782857148, 0.21938808670476195, 0.21831752380952382, 0.21745977120000004, 0.2168295509333333, 0.2164415850666667, 0.21631059565714295, 0.21645130476190483, 0.2168784344380953, 0.2176067067428572, 0.21865084373333335, 0.22002556746666665, 0.22174560000000001],
        [0.2955418668619031, 0.30121092985413567, 0.30620472367622564, 0.31055349743975996, 0.3142875002563248, 0.31743698123750724, 0.32003218949489376, 0.3221033741400713, 0.32368078428462604, 0.32479466904014537, 0.32547527751821553, 0.3257528588304232, 0.3256576620883551, 0.32521993640359814, 0.3244699308877386, 0.32343789465236356, 0.3221540768090595, 0.3206487264694131, 0.3189520927450112, 0.31709442474744026, 0.31510597158828707, 0.31301698237913855, 0.31085770623158093, 0.3086583922572011, 0.3064492895675859, 0.30426064727432184, 0.3021227144889956, 0.3000657403231939, 0.2981199738885035, 0.296315664296511, 0.29468306065880306, 0.2932439537162925, 0.29198630072719667, 0.2908896005790585, 0.2899333521594213, 0.28909705435582855, 0.28836020605582335, 0.2877023061469488, 0.2871028535167484, 0.2865413470527653, 0.2859972856425428, 0.2854501681736239, 0.28487949353355235, 0.28426476060987094, 0.2835854682901231, 0.2828211154618521, 0.281954869720018, 0.280984573489248, 0.2799117379015866, 0.27873787408907763, 0.2774644931837655, 0.27609310631769457, 0.27462522462290856, 0.2730623592314521, 0.2714060212753691, 0.26965772188670384, 0.2678189721975005, 0.26589128333980333, 0.26387616644565637, 0.2617751326471039, 0.2595896930761901, 0.2573235615524873, 0.2549892626456804, 0.25260152361298266, 0.2501750717116071, 0.24772463419876656, 0.2452649383316744, 0.24281071136754365, 0.24037668056358738, 0.2379775731770188, 0.23562811646505083, 0.23334303768489664, 0.23113706409376938, 0.22902492294888208, 0.22702134150744777, 0.2251410470266797, 0.22339876676379083, 0.22180922797599428, 0.22038715792050317, 0.21914728385453064, 0.21810433303528973, 0.2172730327199935, 0.21666811016585505, 0.21630429263008755, 0.21619630736990408, 0.2163588816425176, 0.21680674270514133, 0.21755461781498842, 0.21861723422927168, 0.22000931920520456, 0.22174559999999993],
        [0.2979665544006838, 0.3034382901106503, 0.30824296654937305, 0.312410573378169, 0.31597110025835484, 0.3189545368512473, 0.3213908728181636, 0.32331009782042, 0.32474220151933375, 0.32571717357622154, 0.32626500365240024, 0.32641568140918653, 0.3261991965078972, 0.32564553860984924, 0.32478469737635934, 0.3236466624687443, 0.3222614235483211, 0.3206589702764065, 0.3188692923143171, 0.31692237932337003, 0.31484822096488196, 0.3126768069001695, 0.3104381267905499, 0.3081621702973397, 0.3058789270818558, 0.303618386805415, 0.301410539129334, 0.2992853737149298, 0.297272880223519, 0.2954030483164186, 0.2937058676549455, 0.2922029948994151, 0.2908827547061385, 0.2897251387304256, 0.288710138627586, 0.28781774605292954, 0.2870279526617663, 0.28632075010940594, 0.28567613005115805, 0.2850740841423328, 0.28449460403823984, 0.283917681394189, 0.28332330786549004, 0.28269147510745285, 0.28200217477538714, 0.28123539852460283, 0.2803746218291511, 0.27941725543804913, 0.2783641939190548, 0.277216331839927, 0.2759745637684237, 0.27463978427230357, 0.27321288791932485, 0.27169476927724595, 0.2700863229138252, 0.2683884433968211, 0.266602025293992, 0.26472796317309616, 0.262767151601892, 0.2607204851481379, 0.25858885837959233, 0.25637546864308663, 0.25409272440174474, 0.2517553368977634, 0.24937801737333953, 0.24697547707067016, 0.2445624272319519, 0.24215357909938184, 0.2397636439151569, 0.2374073329214738, 0.23509935736052961, 0.23285442847452104, 0.23068725750564512, 0.22861255569609862, 0.22664503428807847, 0.2247994045237816, 0.22309037764540485, 0.2215326648951451, 0.2201409775151993, 0.2189300267477642, 0.21791452383503682, 0.21710918001921398, 0.21652870654249265, 0.21618781464706954, 0.21610121557514178, 0.21628362056890604, 0.2167497408705593, 0.21751428772229853, 0.21859197236632036, 0.21999750604482193, 0.2217456],
        [0.3004189026734833, 0.30568777482303405, 0.310298386782914, 0.31428043963749336, 0.3176636344711425, 0.32047767236823144, 0.3227522544131309, 0.32451708169021065, 0.3258018552838415, 0.32663627627839337, 0.3270500457582368, 0.32707286480774195, 0.32673443451127904, 0.3260644559532186, 0.3250926302179305, 0.3238486583897855, 0.32236224155315363, 0.32066308079240524, 0.31878087719191067, 0.31674533183604003, 0.31458614580916366, 0.31233302019565207, 0.3100156560798753, 0.30766375454620376, 0.3053070166790078, 0.3029751435626574, 0.30069783628152325, 0.2985047959199754, 0.2964257235623842, 0.29449032029311994, 0.2927282871965529, 0.29116112792351756, 0.28977755639070657, 0.2885580890812757, 0.28748324247838186, 0.2865335330651812, 0.2856894773248305, 0.28493159174048605, 0.2842403927953044, 0.2835963969724418, 0.28298012075505485, 0.2823720806263001, 0.2817527930693339, 0.28110277456731275, 0.2804025416033929, 0.2796326106607313, 0.27877679018090007, 0.2778320564391371, 0.2767986776690957, 0.27567692210442984, 0.2744670579787933, 0.2731693535258396, 0.27178407697922236, 0.2703114965725954, 0.26875188053961235, 0.2671054971139269, 0.26537261452919286, 0.26355350101906383, 0.26164842481719347, 0.2596576541572354, 0.25758145727284354, 0.2554225039830306, 0.2531930704482464, 0.25090783441429965, 0.2485814736269994, 0.24622866583215444, 0.24386408877557367, 0.24150242020306603, 0.23915833786044033, 0.23684651949350552, 0.23458164284807037, 0.23237838566994395, 0.230251425704935, 0.22821544069885252, 0.22628510839750532, 0.22447510654670227, 0.22280011289225224, 0.22127480517996423, 0.2199138611556471, 0.21873195856510955, 0.21774377515416066, 0.21696398866860925, 0.2164072768542642, 0.21608831745693446, 0.21602178822242893, 0.21622236689655638, 0.21670473122512574, 0.2174835589539459, 0.2185735278288257, 0.21998931559557405, 0.22174560000000001],
        [0.302888551737443, 0.30795059431144445, 0.3123636046736542, 0.3161569740971424, 0.31936009385497843, 0.32200235522023263, 0.32411314946597464, 0.32572186786527435, 0.3268579016912014, 0.327550642216826, 0.3278294807152179, 0.32772380845944676, 0.3272630167225827, 0.3264764967776953, 0.3253936398978547, 0.3240438373561305, 0.3224564804255927, 0.3206609603793112, 0.31868666849035576, 0.3165629960317962, 0.3143193342767025, 0.3119850744981443, 0.3095896079691917, 0.3071623259629145, 0.30473261975238247, 0.30232988061066546, 0.29998349981083344, 0.29772286862595604, 0.29557737832910347, 0.2935764201933453, 0.29174938549175145, 0.2901176110294175, 0.2886702157395438, 0.28738826408735557, 0.2862528205380785, 0.28524494955693835, 0.2843457156091608, 0.2835361831599715, 0.2827974166745961, 0.28211048061826033, 0.28145643945618976, 0.2808163576536103, 0.2801712996757476, 0.27950232998782715, 0.2787905130550746, 0.27801691334271583, 0.2771656904954315, 0.276233384875722, 0.27521963202554284, 0.2741240674868498, 0.2729463268015982, 0.2716860455117436, 0.27034285915924156, 0.26891640328604755, 0.26740631343411736, 0.2658122251454061, 0.2641337739618696, 0.26237059542546326, 0.2605223250781427, 0.25858859846186333, 0.2565690511185809, 0.25446581775021876, 0.25229102969857264, 0.2500593174654064, 0.24778531155248362, 0.2454836424615682, 0.2431689406944238, 0.24085583675281413, 0.23855896113850303, 0.23629294435325415, 0.23407241689883138, 0.23191200927699832, 0.22982635198951873, 0.22783007553815637, 0.225937810424675, 0.22416418715083838, 0.22252383621841015, 0.2210313881291542, 0.21970147338483415, 0.21854872248721385, 0.2175877659380569, 0.21683323423912715, 0.2162997578921883, 0.2160019673990042, 0.21595449326133845, 0.21617196598095478, 0.2166690160596171, 0.21746027399908907, 0.2185603703011343, 0.21998393546751666, 0.22174559999999993],
        [0.30536514164970435, 0.3102179588960385, 0.3144312405183994, 0.318034054636525, 0.3210554693701538, 0.3235245528390241, 0.32547037316287397, 0.32692199846144177, 0.32790849685446594, 0.32845893646168445, 0.3286023854028359, 0.32836791179765823, 0.32778458376588976, 0.326881469427269, 0.32568763690153385, 0.3242321543084229, 0.32254408976767424, 0.32065251139902623, 0.31858648732221706, 0.31637508565698486, 0.3140473745230683, 0.31163242204020525, 0.30915929632813427, 0.30665706550659344, 0.304154797695321, 0.30168156101405547, 0.2992664235825347, 0.29693845352049736, 0.29472671894768143, 0.2926602879838253, 0.2907682287486672, 0.28907170245793234, 0.28756024271129393, 0.28621547620441157, 0.2850190296329454, 0.28395252969255547, 0.2829976030789017, 0.28213587648764393, 0.2813489766144421, 0.28061853015495647, 0.27992616380484664, 0.27925350425977274, 0.27858217821539477, 0.27789381236737276, 0.2771700334113664, 0.2763924680430357, 0.2755456384929124, 0.2746256491310142, 0.2736314998622301, 0.27256219059144976, 0.2714167212235623, 0.27019409166345704, 0.2688933018160232, 0.2675133515861501, 0.2660532408787272, 0.26451196959864354, 0.2628885376507887, 0.26118194494005176, 0.2593911913713221, 0.2575152768494889, 0.25555320127944164, 0.25350656012255063, 0.25138733106611083, 0.24921008735389852, 0.2469894022296895, 0.24473984893726022, 0.2424760007203865, 0.2402124308228446, 0.23796371248841064, 0.23574441896086065, 0.23356912348397074, 0.23145239930151706, 0.22940881965727572, 0.22745295779502278, 0.22559938695853435, 0.2238626803915867, 0.2222574113379557, 0.22079815304141756, 0.21949947874574832, 0.21837596169472423, 0.21744217513212127, 0.21671269230171555, 0.21620208644728334, 0.2159249308126005, 0.21589579864144337, 0.21612926317758788, 0.21663989766481023, 0.21744227534688654, 0.2185509694675928, 0.21998055327070526, 0.22174559999999996],
        [0.3078383124674087, 0.3124810788969735, 0.3164939146139548, 0.3199055591350507, 0.3227447519769592, 0.32504023265637877, 0.3268207406900078, 0.3281150155945445, 0.32895179688668713, 0.32935982408313397, 0.32936783670058317, 0.32900457425573315, 0.32829877626528225, 0.32727918224592856, 0.32597453171437035, 0.32441356418730605, 0.32262501918143377, 0.32063763621345187, 0.31848015480005865, 0.3161813144579524, 0.3137698547038314, 0.31127451505439363, 0.3087240350263379, 0.30614715413636195, 0.30357261190116436, 0.3010291478374434, 0.2985455014618972, 0.29615041229122413, 0.29387261984212243, 0.2917408636312903, 0.2897838831754263, 0.2880226604498789, 0.2864471472645996, 0.28503953788819003, 0.2837820265892519, 0.2826568076363874, 0.28164607529819785, 0.2807320238432852, 0.2798968475402515, 0.27912274065769827, 0.2783918974642271, 0.27768651222844026, 0.27698877921893933, 0.27628089270432604, 0.27554504695320214, 0.2747634362341696, 0.2739209498935098, 0.27301325758822365, 0.2720387240529912, 0.2709957140224929, 0.2698825922314093, 0.2686977234144208, 0.26743947230620757, 0.26610620364145005, 0.2646962821548289, 0.2632080725810241, 0.2616399396547165, 0.2599902481105861, 0.2582573626833135, 0.25643964810757885, 0.25453546911806285, 0.25254588127792577, 0.2504827034642483, 0.24836044538259092, 0.24619361673851428, 0.24399672723757912, 0.241784286585346, 0.2395708044873755, 0.23737079064922842, 0.23519875477646518, 0.23306920657464658, 0.23099665574933312, 0.22899561200608545, 0.22708058505046425, 0.22526608458803016, 0.2235666203243438, 0.22199670196496574, 0.22057083921545662, 0.2193035417813771, 0.2182093193682878, 0.21730268168174935, 0.21659813842732234, 0.21611019931056752, 0.2158533740370454, 0.21584217231231664, 0.21609110384194194, 0.21661467833148182, 0.2174274054864969, 0.2185437950125479, 0.21997835661519535, 0.22174560000000001],
        [0.31029770424769715, 0.31473116463440665, 0.318544247257126, 0.321765365472128, 0.324422932635685, 0.32654536210406976, 0.328161067233555, 0.3292984613804132, 0.3299859579009169, 0.3302519701513391, 0.33012491148795226, 0.32963319526702883, 0.3288052348448416, 0.32766944357766314, 0.3262542348217662, 0.3245880219334233, 0.3226992182689069, 0.32061623718448995, 0.318367492036445, 0.3159813961810445, 0.31348636297456145, 0.310910805773268, 0.30828313793343715, 0.3056317728113413, 0.30298512376325326, 0.3003716041454456, 0.29781962731419087, 0.29535760662576177, 0.293013955436431, 0.29081708710247095, 0.28879541498015454, 0.2869697432460744, 0.2853304393581041, 0.28386026159443717, 0.28254196823326727, 0.2813583175527884, 0.2802920678311939, 0.27932597734667736, 0.2784428043774327, 0.27762530720165335, 0.276856244097533, 0.2761183733432656, 0.27539445321704453, 0.27466724199706344, 0.2739194979615161, 0.2731339793885961, 0.2722959404173905, 0.27140061863056025, 0.27044574747165945, 0.26942906038424225, 0.268348290811863, 0.2672011721980757, 0.265985437986435, 0.26469882162049463, 0.2633390565438091, 0.2619038761999325, 0.260391014032419, 0.25879820348482313, 0.25712317800069867, 0.25536367102360014, 0.25351741599708155, 0.2515849313942436, 0.2495778758063719, 0.2475106928542983, 0.2453978261588549, 0.24325371934087348, 0.24109281602118623, 0.23892955982062491, 0.2367783943600216, 0.23465376326020823, 0.23257011014201678, 0.2305418786262792, 0.2285835123338273, 0.2267094548854932, 0.22493414990210883, 0.2232720410045062, 0.22173757181351722, 0.2203451859499738, 0.2191093270347079, 0.21804443868855158, 0.21716496453233666, 0.21648534818689524, 0.2160200332730592, 0.2157834634116605, 0.21579008222353113, 0.216054333329503, 0.2165906603504081, 0.21741350690707842, 0.21853731662034587, 0.21997653311104237, 0.2217456],
        [0.31273295704771126, 0.316959426428495, 0.3205748587447188, 0.3236073515271666, 0.32608500230662235, 0.3280359086138702, 0.32948816797969444, 0.33046987793487886, 0.33100913601020787, 0.3311340397364653, 0.3308726866444355, 0.3302531742649023, 0.32930360012864973, 0.32805206176646207, 0.3265266567091235, 0.324755482487418, 0.32276663663212946, 0.3205882166740421, 0.3182483201439401, 0.3157750445726075, 0.3131964874908286, 0.3105407464293869, 0.30783591891906703, 0.3051101024906529, 0.30239139467492865, 0.29970789300267836, 0.29708769500468596, 0.29455889821173564, 0.2921496001546115, 0.28988789836409773, 0.28780189037097814, 0.28591220908733606, 0.28420962895045054, 0.28267745977889963, 0.2812990113912611, 0.2800575936061133, 0.2789365162420344, 0.27791908911760216, 0.2769886220513947, 0.27612842486199013, 0.27532180736796646, 0.27455207938790177, 0.2738025507403742, 0.27305653124396173, 0.27229733071724227, 0.27150825897879416, 0.2706749257847215, 0.26979214064123436, 0.2688570129920689, 0.267866652280961, 0.2668181679516472, 0.26570866944786353, 0.26453526621334617, 0.26329506769183125, 0.26198518332705506, 0.2606027225627536, 0.2591447948426632, 0.25760850961051995, 0.25599097631006007, 0.2542893043850197, 0.25250060327913504, 0.25062486064940376, 0.248673577005869, 0.2466611310718357, 0.2446019015706085, 0.24251026722549218, 0.24040060675979136, 0.23828729889681102, 0.2361847223598558, 0.23410725587223039, 0.23206927815723963, 0.23008516793818812, 0.2281693039383808, 0.2263360648811223, 0.22459982948971735, 0.22297497648747083, 0.22147588459768727, 0.22011693254367165, 0.21891249904872856, 0.21787696283616273, 0.21702470262927903, 0.21637009715138214, 0.21592752512577676, 0.2157113652757678, 0.21573599632465984, 0.2160157969957577, 0.2165651460123661, 0.2173984220977897, 0.21853000397533343, 0.21997427036830192, 0.2217456],
        [0.31513371092459236, 0.319157074599396, 0.3225783693735385, 0.32542539517957536, 0.3277259519500617, 0.3295078396175532, 0.3307988581146052, 0.331626807373773, 0.33201948732761194, 0.33200469790867765, 0.3316102390495254, 0.33086391068271054, 0.32979351274078855, 0.3284268451563149, 0.3267917078618447, 0.32491590078993376, 0.32282722387313695, 0.32055347704401016, 0.31812246023510865, 0.3155619733789877, 0.3128998164082028, 0.31016378925530924, 0.3073816918528627, 0.3045813241334182, 0.3017904860295315, 0.2990369774737578, 0.2963485983986524, 0.2937531487367709, 0.29127842842066853, 0.2889522373829009, 0.2868023755560232, 0.28484931621448134, 0.2830842260002822, 0.28149094489732357, 0.2800533128895027, 0.2787551699607169, 0.27758035609486414, 0.27651271127584137, 0.2755360754875464, 0.27463428871387646, 0.2737911909387291, 0.27299062214600184, 0.2722164223195921, 0.2714524314433973, 0.2706824895013149, 0.2698904364772424, 0.26906222171566974, 0.26819223200345604, 0.26727696348805297, 0.2663129123169123, 0.2652965746374858, 0.264224446597225, 0.26309302434358145, 0.2618988040240071, 0.26063828178595344, 0.25930795377687216, 0.25790431614421494, 0.2564238650354335, 0.25486309659797957, 0.25321850697930454, 0.25148659232686044, 0.24966681922130565, 0.24777053597612692, 0.24581206133801795, 0.24380571405367238, 0.24176581286978371, 0.2397066765330458, 0.23764262379015208, 0.2355879733877963, 0.2335570440726721, 0.23156415459147323, 0.22962362369089304, 0.22774977011762546, 0.22595691261836398, 0.22425936993980233, 0.22267146082863412, 0.221207504031553, 0.21988181829525258, 0.21870872236642644, 0.21770253499176845, 0.216877574917972, 0.21624816089173082, 0.21582861165973866, 0.21563324596868907, 0.2156763825652757, 0.21597234019619216, 0.21653543760813215, 0.21737999354778934, 0.21852032676185718, 0.21997075599702953, 0.22174560000000004],
        [0.3174896059354816, 0.32131531946726644, 0.3245473994403907, 0.32721337430876346, 0.32934077252629396, 0.33095712254689164, 0.33208995282446585, 0.33276679181292595, 0.33301516796618114, 0.3328626097381408, 0.3323366455827142, 0.3314648039538107, 0.33027461330533975, 0.32879360209121017, 0.3270492987653318, 0.3250692317816136, 0.3228809295939653, 0.3205119206562957, 0.31798973342251446, 0.31534189634653087, 0.3125959378822542, 0.3097793864835936, 0.3069197706044587, 0.30404461869875854, 0.30118145922040257, 0.2983578206233001, 0.29560123136136035, 0.29293921988849275, 0.2903993146586065, 0.288009044125611, 0.2857959367434155, 0.28378032286832694, 0.2819537404662421, 0.2803005294054554, 0.2788050295542611, 0.27745158078095367, 0.27622452295382754, 0.275108195941177, 0.2740869396112965, 0.27314509383248026, 0.2722669984730228, 0.27143699340121846, 0.27063941848536155, 0.26985861359374663, 0.26907891859466776, 0.2682846733564197, 0.2674621439304018, 0.2666053011004351, 0.26571004183344554, 0.26477226309635926, 0.26378786185610237, 0.2627527350796011, 0.2616627797337814, 0.2605138927855694, 0.25930197120189125, 0.25802291194967303, 0.2566726119958408, 0.25524696830732074, 0.253741877851039, 0.25215323759392155, 0.2504769445028946, 0.2487119572878487, 0.24686948163053268, 0.24496378495565982, 0.24300913468794347, 0.24101979825209685, 0.23901004307283324, 0.23699413657486595, 0.23498634618290842, 0.2330009393216738, 0.23105218341587544, 0.2291543458902266, 0.22732169416944067, 0.22556849567823084, 0.22390901784131037, 0.22235752808339276, 0.22092829382919119, 0.21963558250341889, 0.21849366153078925, 0.2175167983360156, 0.2167192603438111, 0.21611531497888917, 0.21571922966596302, 0.21554527182974612, 0.2156077088949516, 0.2159208082862928, 0.21649883742848294, 0.2173560637462355, 0.21850675466426359, 0.2199651776072807, 0.22174559999999996],
        [0.31979028213752064, 0.32342537135226396, 0.3264745692420809, 0.32896516679413995, 0.33092445499560974, 0.33237972483365885, 0.3333582672954559, 0.3338873733681695, 0.3339943340389679, 0.3337064402950202, 0.33305098312349474, 0.3320552535115601, 0.33074654244638485, 0.3291521409151377, 0.32729933990498705, 0.3252154304031017, 0.3229277033966499, 0.3204634498728006, 0.3178499608187222, 0.3151145272215835, 0.3122844400685527, 0.3093869903467988, 0.30644946904349, 0.30349916714579517, 0.3005633756408828, 0.29766938551592154, 0.2948444877580799, 0.29211597335452644, 0.28951113329242983, 0.28705725855895864, 0.28478164014128143, 0.2827044872896905, 0.28081768230697346, 0.2791060257590416, 0.27755431821180604, 0.27614736023117825, 0.2748699523830695, 0.27370689523339103, 0.2726429893480539, 0.27166303529296965, 0.27075183363404953, 0.2698941849372048, 0.26907488976834665, 0.2682787486933865, 0.26749056227823537, 0.2666951310888049, 0.2658790081490851, 0.2650357563153819, 0.2641606909020803, 0.26324912722356497, 0.262296380594221, 0.26129776632843316, 0.26024859974058645, 0.2591441961450655, 0.2579798708562554, 0.256750939188541, 0.2554527164563072, 0.25408051797393877, 0.2526296590558207, 0.2510954550163377, 0.24947322116987497, 0.24776142502693263, 0.2459711428824737, 0.2441166032275764, 0.2422120345533191, 0.2402716653507802, 0.23830972411103812, 0.23634043932517115, 0.23437803948425773, 0.232436753079376, 0.23053080860160463, 0.22867443454202177, 0.22688185939170594, 0.2251673116417353, 0.2235450197831884, 0.22202921230714354, 0.220634117704679, 0.21937396446687327, 0.21826298108480463, 0.2173153960495515, 0.21654543785219213, 0.215967334983805, 0.21559531593546843, 0.2154436091982609, 0.21552644326326048, 0.21585804662154584, 0.21645264776419518, 0.21732447518228692, 0.21848775736689935, 0.21995672280911097, 0.22174559999999996],
        [0.32202537958785066, 0.32547844057454567, 0.3283524990754149, 0.3306746505151143, 0.33247199031830005, 0.33377161390962795, 0.3346006167137541, 0.33498609415533415, 0.3349551416590245, 0.3345348546494809, 0.33375232855135933, 0.33263465878931575, 0.3312089407880061, 0.32950226997208654, 0.32754174176621276, 0.3253544515950409, 0.32296749488322685, 0.32040796705542657, 0.31770296353629623, 0.31487957975049147, 0.3119649111226686, 0.3089860530774833, 0.30597010103959166, 0.3029441504336497, 0.2999352966843133, 0.29697063521623857, 0.2940772614540813, 0.2912822708224974, 0.28861275874614306, 0.2860958206496742, 0.28375855195774674, 0.28162106771938905, 0.27967556148111955, 0.2779072464138285, 0.2763013356884069, 0.27484304247574537, 0.27351757994673465, 0.2723101612722651, 0.27120599962322756, 0.2701903081705127, 0.26924830008501116, 0.26836518853761365, 0.2675261866992109, 0.2667165077406934, 0.26592136483295176, 0.26512597114687686, 0.2643171300918863, 0.26348800603150657, 0.2626333535677909, 0.2617479273027926, 0.2608264818385654, 0.2598637717771624, 0.25885455172063704, 0.25779357627104277, 0.256675600030433, 0.25549537760086105, 0.25424766358438045, 0.2529272125830445, 0.2515287791989066, 0.25004711803402013, 0.2484769836904386, 0.246816372616457, 0.2450762486453371, 0.24327081745658244, 0.24141428472969645, 0.23952085614418273, 0.23760473737954463, 0.23568013411528568, 0.23376125203090942, 0.23186229680591933, 0.2299974741198189, 0.22818098965211156, 0.22642704908230082, 0.2247498580898901, 0.22316362235438297, 0.22168254755528302, 0.22032083937209354, 0.21909270348431809, 0.21801234557146007, 0.2170939713130232, 0.2163517863885107, 0.2157999964774262, 0.21545280725927315, 0.21532442441355512, 0.21542905361977555, 0.2157809005574378, 0.2163941709060455, 0.2172830703451021, 0.21846180455411102, 0.21994457921257585, 0.2217456],
        [0.324184538343613, 0.3274657374542684, 0.3301738092371979, 0.3323357033510955, 0.33397836945465537, 0.3351287572065718, 0.3358138162655391, 0.3360604962902513, 0.3358957469394027, 0.33534651787168773, 0.3344397587458002, 0.3332024192204347, 0.331661448954285, 0.3298437976060457, 0.32777641483441083, 0.32548625029807476, 0.32300025365573143, 0.3203453745660753, 0.3175485626878004, 0.3146367676796012, 0.3116369392001716, 0.30857602690820585, 0.3054809804623984, 0.3023787495214433, 0.2992962837440348, 0.2962605327888671, 0.29329844631463436, 0.2904369739800308, 0.28770306544375074, 0.28512367036448827, 0.2827257384009377, 0.2805293223982398, 0.27852688794732317, 0.27670400382556254, 0.275046238810333, 0.27353916167900955, 0.27216834120896727, 0.2709193461775812, 0.26977774536222615, 0.2687291075402773, 0.2677590014891095, 0.2668529959860981, 0.2659966598086178, 0.26517556173404366, 0.26437527053975074, 0.26358135500311414, 0.26278082547897236, 0.26196645863201906, 0.261132472704411, 0.26027308593830534, 0.2593825165758592, 0.25845498285922963, 0.25748470303057364, 0.2564658953320483, 0.2553927780058107, 0.25425956929401783, 0.25306048743882686, 0.25178975068239473, 0.2504415772668787, 0.24901018543443554, 0.2474897934272226, 0.24587795023432107, 0.24418552783251005, 0.24242672894549272, 0.24061575629697254, 0.23876681261065277, 0.23689410061023672, 0.2350118230194277, 0.23313418256192905, 0.23127538196144415, 0.2294496239416762, 0.2276711112263286, 0.2259540465391046, 0.22431263260370765, 0.22276107214384083, 0.22131356788320783, 0.2199843225455116, 0.21878753885445562, 0.21773741953374323, 0.21684816730707768, 0.21613398489816238, 0.21560907503070054, 0.21528764042839552, 0.21518388381495077, 0.2153120079140694, 0.21568621544945482, 0.21632070914481036, 0.21722969172383935, 0.21842736591024509, 0.21992793442773081, 0.22174560000000004],
        [0.326257398461949, 0.32937847231158973, 0.3319311200242355, 0.3339422031814923, 0.3354385833649663, 0.3364471221562635, 0.33699468113699, 0.3371081218887517, 0.33681430599315487, 0.33614009503180553, 0.3351123505863099, 0.33375793423827377, 0.33210370756930324, 0.3301765321610045, 0.3280032695949837, 0.3256107814528466, 0.3230259293161994, 0.32027557476664825, 0.3173865793857993, 0.31438580475525835, 0.3113001124566317, 0.30815636407152514, 0.3049814211815449, 0.30180214536829725, 0.29864539821338804, 0.29553804129842337, 0.2925069362050093, 0.28957894451475175, 0.28678092780925707, 0.28413974767013106, 0.28168226567898, 0.27942850956705995, 0.27737117166422764, 0.27549611044998995, 0.2737891844038535, 0.2722362520053254, 0.2708231717339123, 0.269535802069121, 0.2683600014904584, 0.26728162847743125, 0.2662865415095464, 0.2653605990663107, 0.26448965962723103, 0.26365958167181397, 0.26285622367956657, 0.26206544412999555, 0.2612744100305102, 0.26047552250012934, 0.25966249118577417, 0.258829025734366, 0.25796883579282626, 0.25707563100807607, 0.2561431210270367, 0.25516501549662934, 0.2541350240637754, 0.2530468563753962, 0.25189422207841283, 0.2506708308197467, 0.249370392246319, 0.24798661600505092, 0.24651321174286397, 0.24494730805842446, 0.24329970935737966, 0.24158463899712218, 0.23981632033504446, 0.23800897672853905, 0.23617683153499852, 0.23433410811181524, 0.23249502981638184, 0.23067382000609074, 0.22888470203833458, 0.2271418992705058, 0.2254596350599969, 0.22385213276420032, 0.22233361574050872, 0.22091830734631454, 0.21962043093901026, 0.2184542098759885, 0.21743386751464153, 0.2165736272123622, 0.21588771232654275, 0.21539034621457578, 0.21509575223385388, 0.2150181537417695, 0.21517177409571514, 0.21557083665308327, 0.2162295647712665, 0.21716218180765723, 0.21838291111964808, 0.21990597606463144, 0.2217456],
        [0.3282336000000001, 0.33120785546666676, 0.3336170517333334, 0.3354880278857144, 0.33684762300952387, 0.33772267619047625, 0.33814002651428576, 0.33812651306666675, 0.33770897493333335, 0.33691425119999996, 0.33576918095238106, 0.3343006032761905, 0.33253535725714295, 0.33050028198095244, 0.32822221653333333, 0.32572800000000013, 0.3230444714666667, 0.32019847001904767, 0.31721683474285717, 0.3141264047238096, 0.3109540190476191, 0.30772651679999996, 0.30447073706666666, 0.30121351893333337, 0.29798170148571423, 0.29480212380952386, 0.2917016249904763, 0.2887070441142858, 0.28584522026666676, 0.2831429925333334, 0.2806272000000001, 0.2783178874666668, 0.2762079225904763, 0.27428337874285724, 0.2725303292952382, 0.2709348476190477, 0.26948300708571443, 0.26816088106666675, 0.2669545429333334, 0.26585006605714295, 0.2648335238095239, 0.2638909895619048, 0.26300853668571444, 0.2621722385523811, 0.2613681685333334, 0.2605824000000001, 0.2598021994666667, 0.2590196060190478, 0.25822785188571445, 0.2574201692952382, 0.2565897904761905, 0.255729947657143, 0.2548338730666668, 0.25389479893333344, 0.2529059574857144, 0.25186058095238106, 0.25075190156190486, 0.24957315154285725, 0.24831756312380968, 0.2469783685333334, 0.2455488000000001, 0.24402559626666676, 0.24241952213333343, 0.2407448489142858, 0.23901584792380962, 0.23724679047619057, 0.23545194788571436, 0.23364559146666666, 0.23184199253333335, 0.23005542240000001, 0.22830015238095244, 0.22659045379047624, 0.22494059794285717, 0.223364856152381, 0.22187749973333332, 0.22049280000000002, 0.2192250282666667, 0.2180884558476191, 0.21709735405714287, 0.2162659942095238, 0.21560864761904758, 0.2151395856, 0.21487307946666662, 0.21482340053333335, 0.21500482011428573, 0.21543160952380955, 0.2161180400761905, 0.2170783830857143, 0.2183269098666667, 0.21987789173333333, 0.22174560000000004],
        [0.3301062055831171, 0.332947979432655, 0.3352266195913578, 0.33696901360472636, 0.3382020490182613, 0.33895261337746296, 0.3392475942278324, 0.3391138791148699, 0.33857835558407645, 0.3376679111809528, 0.3364094334509994, 0.334829809939717, 0.3329559281926061, 0.33081467575516765, 0.32843294017290203, 0.3258376089913101, 0.3230555697558923, 0.32011371001214955, 0.3170389173055824, 0.3138580791816915, 0.31059808318597765, 0.3072858168639413, 0.30394816776108324, 0.30061202342290416, 0.2973042713949047, 0.29405179922258545, 0.29088149445144723, 0.2878202446269905, 0.2848949372947161, 0.2821324600001248, 0.2795597002887168, 0.2771967655826147, 0.27503664281042717, 0.2730655387773839, 0.27126966028871535, 0.2696352141496516, 0.2681484071654227, 0.2667954461412587, 0.2655625378823897, 0.2644358891940459, 0.26340170688145764, 0.26244619774985467, 0.26155556860446727, 0.2607160262505256, 0.25991377749325956, 0.2591350291378996, 0.2583670850932454, 0.25760163768237676, 0.2568314763319424, 0.2560493904685923, 0.2552481695189756, 0.25442060290974133, 0.25355948006753926, 0.2526575904190185, 0.2517077233908283, 0.2507026684096179, 0.2496352149020369, 0.2484981522947346, 0.24728427001436018, 0.24598635748756292, 0.2445972041409924, 0.2431131925280114, 0.24154507770883793, 0.23990720787040354, 0.23821393119963974, 0.23647959588347825, 0.23471855010885034, 0.23294514206268788, 0.23117371993192234, 0.22941863190348522, 0.22769422616430823, 0.22601485090132284, 0.22439485430146067, 0.22284858455165324, 0.22139038983883222, 0.2200346183499291, 0.21879561827187538, 0.2176877377916028, 0.21672532509604278, 0.215922728372127, 0.21529429580678694, 0.21485437558695422, 0.2146173158995605, 0.2145974649315373, 0.21480917086981607, 0.2152667819013285, 0.21598464621300612, 0.21697711199178052, 0.21825852742458324, 0.2198432406983458, 0.22174559999999996],
        [0.33188196810948933, 0.33460446549470385, 0.33676441854541844, 0.3383888295257167, 0.33950470069968147, 0.34013903433139603, 0.34031883268494356, 0.34007109802440727, 0.3394228326138702, 0.3384010387174157, 0.337032718599127, 0.335344874523087, 0.33336450875337886, 0.331118623554086, 0.3286342211892915, 0.3259383039230785, 0.3230578740195301, 0.3200199337427297, 0.3168514853567603, 0.31357953112570497, 0.3102310733136472, 0.30683311418466985, 0.3034126560028562, 0.2999967010322895, 0.2966122515370529, 0.2932863097812295, 0.2900458780289024, 0.28691795854415497, 0.28392955359107025, 0.28110766543373156, 0.2784792963362218, 0.276064658379409, 0.2738568029112992, 0.27184199109668317, 0.2700064841003515, 0.26833654308709537, 0.2668184292217051, 0.2654384036689717, 0.26418272759368583, 0.26303766216063823, 0.26198946853461963, 0.2610244078804209, 0.26012874136283265, 0.25928873014664583, 0.25849063539665096, 0.257720718277639, 0.25696626055859567, 0.25621862642528853, 0.2554702006676792, 0.2547133680757306, 0.25394051343940466, 0.2531440215486638, 0.2523162771934701, 0.2514496651637862, 0.25053657024957426, 0.24956937724079636, 0.24854047092741513, 0.24744223609939262, 0.24626705754669131, 0.24500732005927323, 0.24365540842710104, 0.24220738447567874, 0.2406740181726792, 0.23906975652131707, 0.2374090465248071, 0.23570633518636377, 0.23397606950920202, 0.2322326964965364, 0.23049066315158181, 0.22876441647755283, 0.22706840347766413, 0.22541707115513043, 0.2238248665131665, 0.22230623655498696, 0.22087562828380647, 0.21954748870284002, 0.218336264815302, 0.2172564036244072, 0.21632235213337037, 0.21554855734540615, 0.21494946626372932, 0.21453952589155453, 0.2143331832320965, 0.21434488528856993, 0.21458907906418956, 0.21508021156217003, 0.21583272978572607, 0.21686108073807242, 0.2181797114224237, 0.21980306884199466, 0.22174560000000001],
        [0.3335710630455155, 0.3361858171309606, 0.33823743847268545, 0.33975310309742923, 0.3407599870319303, 0.34128526630292766, 0.3413561169371602, 0.3409997149613668, 0.3402432364022859, 0.33911385728665683, 0.33763875364121815, 0.3358451014927086, 0.3337600768678671, 0.3314108557934324, 0.3288246142961433, 0.32602852840273866, 0.32304977413995734, 0.31991552753453806, 0.31665296461321985, 0.3132892614027413, 0.3098515939298413, 0.30636713822125844, 0.30286307030373205, 0.2993665662040005, 0.2959048019488027, 0.2925049535648776, 0.2891941970789639, 0.28599970851780043, 0.282948663908126, 0.28006823927667956, 0.2773856106501997, 0.27492113156629167, 0.2726678656060264, 0.27061205386134085, 0.26873993742417224, 0.26703775738645774, 0.2654917548401343, 0.26408817087713937, 0.2628132465894098, 0.26165322306888283, 0.2605943414074957, 0.2596228426971855, 0.2587249680298893, 0.2578869584975442, 0.25709505519208753, 0.2563354992054563, 0.2555954950967037, 0.25486610129334786, 0.2541393396900227, 0.2534072321813623, 0.2526618006620007, 0.2518950670265719, 0.2510990531697101, 0.2502657809860491, 0.2493872723702233, 0.2484555492168664, 0.24746263342061267, 0.24640054687609625, 0.245261311477951, 0.24403694912081078, 0.24271948169931012, 0.24130468723395274, 0.23980336824872242, 0.23823008339347293, 0.23659939131805796, 0.23492585067233132, 0.23322402010614662, 0.23150845826935765, 0.22979372381181817, 0.2280943753833819, 0.22642497163390243, 0.22480007121323362, 0.22323423277122925, 0.22174201495774284, 0.22033797642262826, 0.2190366758157393, 0.21785267178692952, 0.2168005229860527, 0.21589478806296256, 0.21515002566751282, 0.21458079444955735, 0.2142016530589497, 0.2140271601455436, 0.2140718743591929, 0.2143503543497513, 0.2148771587670724, 0.21566684626101, 0.21673397548141787, 0.2180931050781497, 0.21975879370105914, 0.22174560000000001],
        [0.3351836658575943, 0.3377005378195729, 0.3396526692503292, 0.34106746176860786, 0.3419723169931534, 0.3423946365427103, 0.3423618220360233, 0.3419012750918368, 0.3410403973288958, 0.3398065903659447, 0.3382272558217283, 0.33632979531499074, 0.33414161046447705, 0.3316901028889317, 0.32900267420709906, 0.32610672603772417, 0.32302965999955124, 0.3197988777113252, 0.3164417807917905, 0.3129857708596917, 0.3094582495337734, 0.3058866184327803, 0.3022982791754571, 0.29872063338054816, 0.2951810826667982, 0.29170702865295184, 0.2883258729577536, 0.28506501719994826, 0.2819518629982802, 0.2790138119714943, 0.2762782657383348, 0.2737657508525052, 0.2714692936075427, 0.26937504523194317, 0.2674691569542029, 0.26573778000281734, 0.2641670656062827, 0.262743164993095, 0.2614522293917499, 0.2602804100307436, 0.2592138581385718, 0.25823872494373046, 0.2573411616747157, 0.2565073195600234, 0.25572334982814926, 0.2549754037075895, 0.2542505579415552, 0.2535395913321196, 0.25283420819607066, 0.25212611285019704, 0.25140700961128665, 0.25066860279612824, 0.24990259672150988, 0.24910069570421983, 0.24825460406104666, 0.24735602610877838, 0.2463966661642036, 0.24536822854411047, 0.24426241756528735, 0.24307093754452244, 0.24178549279860428, 0.24040161592711748, 0.238930152660833, 0.23738577701331784, 0.23578316299813945, 0.23413698462886492, 0.2324619159190617, 0.23077263088229694, 0.2290838035321379, 0.2274101078821517, 0.22576621794590587, 0.22416680773696743, 0.22262655126890368, 0.22116012255528195, 0.21978219560966944, 0.21850744444563341, 0.21735054307674104, 0.21632616551655967, 0.21544898577865654, 0.21473367787659886, 0.21419491582395392, 0.213847373634289, 0.21370572532117124, 0.2137846448981681, 0.21409880637884654, 0.214662883776774, 0.21549155110551774, 0.21659948237864501, 0.21800135160972284, 0.2197118328123188, 0.2217456],
        [0.3367299520121248, 0.3391571310386887, 0.3410171007555203, 0.34233753298799696, 0.34314609956149633, 0.34347047230139593, 0.3433383230330734, 0.34277732358190616, 0.34181514577327193, 0.3404794614325482, 0.33879794238511235, 0.33679826045634226, 0.3345080874716152, 0.3319550952563089, 0.3291669556358007, 0.32617134043546836, 0.3229959214806893, 0.31966837059684117, 0.31621635960930145, 0.3126675603434478, 0.30904964462465756, 0.3053902842783084, 0.30171715112977804, 0.2980579170044438, 0.29444025372768334, 0.29089183312487416, 0.2874403270213938, 0.28411340724261996, 0.28093874561392995, 0.2779440139607014, 0.275156884108312, 0.2725980819472918, 0.2702605496287822, 0.26813028336907674, 0.26619327938446913, 0.26443553389125335, 0.26284304310572315, 0.2614018032441723, 0.2600978105228946, 0.25891706115818375, 0.25784555136633375, 0.25686927736363824, 0.25597423536639097, 0.2551464215908858, 0.2543718322534165, 0.25363646357027686, 0.25292721832713644, 0.25223462558716847, 0.2515501209829215, 0.2508651401469443, 0.250171118711786, 0.24945949230999503, 0.24872169657412044, 0.247949167136711, 0.24713333963031542, 0.2462656496874826, 0.24533753294076135, 0.2443404250227004, 0.2432657615658487, 0.24210497820275487, 0.2408495105659679, 0.23949468567945736, 0.23805139613287635, 0.23653442590729865, 0.2349585589837983, 0.23333857934344907, 0.2316892709673249, 0.23002541783649966, 0.22836180393204739, 0.22671321323504193, 0.22509442972655697, 0.2235202373876667, 0.22200542019944486, 0.22056476214296533, 0.2192130471993021, 0.21796505934952903, 0.21683558257471994, 0.2158394008559488, 0.21499129817428955, 0.214306058510816, 0.21379846584660206, 0.2134833041627216, 0.21337535744024871, 0.21348940966025706, 0.21384024480382066, 0.21444264685201342, 0.21531139978590913, 0.21646128758658173, 0.2179070942351051, 0.21966360371255325, 0.2217456],
        [0.33822009697550576, 0.3405641002664555, 0.34233772286542885, 0.34356894420434064, 0.34428574371510495, 0.34451610082963724, 0.34428799497985174, 0.3436294055976631, 0.34256831211498623, 0.3411326939637355, 0.33935053057582587, 0.33724980138317184, 0.33485848581768796, 0.3322045633112891, 0.32931601329588983, 0.3262208152034049, 0.3229469484657487, 0.3195223925148364, 0.3159751267825822, 0.3123331307009009, 0.3086243837017073, 0.304876865216916, 0.3011185546784415, 0.2973774315181987, 0.2936814751681022, 0.29005866506006667, 0.2865369806260066, 0.2831444012978368, 0.279908906507472, 0.27685847568682675, 0.27402108826781574, 0.27141769055989406, 0.26904109638267887, 0.26687708643332725, 0.26491144140899653, 0.2631299420068444, 0.261518368924028, 0.26006250285770477, 0.258748124505032, 0.2575610145631671, 0.2564869537292675, 0.25551172270049055, 0.25462110217399364, 0.25380087284693403, 0.25303681541646916, 0.2523147105797564, 0.2516212454874335, 0.2509467331040593, 0.250282392847673, 0.24961944413631387, 0.24894910638802142, 0.2482625990208345, 0.24755114145279267, 0.24680595310193498, 0.2460182533863008, 0.2451792617239292, 0.2442801975328596, 0.2433122802311312, 0.24226672923678327, 0.24113476396785488, 0.23990760384238555, 0.23858041161525653, 0.23716412338871798, 0.23567361860186203, 0.23412377669378126, 0.23252947710356758, 0.23090559927031357, 0.2292670226331113, 0.2276286266310532, 0.22600529070323153, 0.22441189428873845, 0.22286331682666627, 0.22137443775610738, 0.21996013651615395, 0.21863529254589825, 0.21741478528443264, 0.21631349417084927, 0.21534629864424057, 0.21452807814369865, 0.2138737121083159, 0.21339807997718457, 0.2131160611893969, 0.21304253518404526, 0.21319238140022187, 0.21358047927701893, 0.21422170825352888, 0.21513094776884384, 0.2163230772620563, 0.21781297617225812, 0.219615523938542, 0.22174560000000004],
        [0.3396642762141357, 0.34192994898102047, 0.34362152545722513, 0.34476732286638234, 0.345395658432125, 0.3455348493780861, 0.3452132129278988, 0.3444590663051959, 0.34330072673361034, 0.34176651143677517, 0.33988473763832333, 0.3376837225618878, 0.3351917834311013, 0.3324372374695971, 0.329448401901008, 0.3262535939489669, 0.3228811308371069, 0.31935932978906073, 0.3157165080284617, 0.31198098277894243, 0.3081810712641363, 0.3043450907076757, 0.30050135833319397, 0.2966781913643239, 0.29290390702469854, 0.289206822537951, 0.28561525512771396, 0.28215752201762034, 0.2788619404313033, 0.2757568275923957, 0.2728705007245306, 0.2702241423995542, 0.26781039658216665, 0.26561477258528104, 0.2636227797218107, 0.2618199273046693, 0.26019172464676976, 0.2587236810610256, 0.2574013058603503, 0.2562101083576568, 0.2551355978658589, 0.25416328369786956, 0.25327867516660235, 0.25246728158497045, 0.25171461226588715, 0.2510061765222661, 0.2503284086564319, 0.24967144292835652, 0.2490263385874232, 0.24838415488301518, 0.24773595106451599, 0.2470727863813089, 0.2463857200827772, 0.2456658114183043, 0.2449041196372736, 0.24409170398906835, 0.2432196237230719, 0.24227893808866766, 0.24126070633523894, 0.240155987712169, 0.23895584146884144, 0.23765530885879893, 0.23626535915222302, 0.23480094362345474, 0.23327701354683492, 0.23170852019670474, 0.23011041484740516, 0.22849764877327713, 0.22688517324866173, 0.22528793954789983, 0.22372089894533265, 0.22219900271530102, 0.22073720213214607, 0.21935044847020857, 0.2180536930038298, 0.21686188700735062, 0.21578998175511213, 0.21485292852145516, 0.2140656785807209, 0.2134431832072502, 0.21300039367538412, 0.21275226125946378, 0.21271373723383002, 0.21289977287282402, 0.2133253194507866, 0.2140053282420588, 0.21495475052098173, 0.21618853756189627, 0.21772164063914348, 0.2195690110270644, 0.2217456],
        [0.3410726651944136, 0.34326318066053185, 0.34487549840807974, 0.34593829642286655, 0.34648025269070193, 0.3465300451973951, 0.3461163519287557, 0.34526785087059303, 0.34401322000871665, 0.34238113732893577, 0.34040028081706014, 0.33809932845889895, 0.3355069582402616, 0.33265184814695786, 0.32956267616479673, 0.32626812027958807, 0.3227968584771409, 0.31917756874326486, 0.31543892906376947, 0.31160961742446397, 0.30771831181115794, 0.30379369020966074, 0.29986443060578183, 0.29595921098533057, 0.2921067093341167, 0.28833560363794936, 0.28467457188263795, 0.2811522920539919, 0.27779744213782087, 0.27463870011993413, 0.2717047439861412, 0.2690170031755146, 0.2665679129401795, 0.2643426599855242, 0.26232643101693714, 0.2605044127398067, 0.25886179185952113, 0.25738375508146866, 0.25605548911103776, 0.2548621806536167, 0.2537890164145937, 0.2528211830993574, 0.251943867413296, 0.25114225606179774, 0.2504015357502509, 0.24970689318404407, 0.24904447706811814, 0.24840428410562526, 0.24777727299927013, 0.24715440245175777, 0.2465266311657929, 0.24588491784408037, 0.24522022118932504, 0.24452349990423172, 0.2437857126915052, 0.2429978182538503, 0.24215077529397194, 0.24123554251457494, 0.24024307861836408, 0.23916434230804406, 0.23799029228632004, 0.23671589253436895, 0.23535212814725714, 0.2339139894985234, 0.2324164669617063, 0.23087455091034473, 0.22930323171797715, 0.22771749975814248, 0.22613234540437932, 0.22456275903022635, 0.22302373100922226, 0.2215302517149058, 0.22009731152081563, 0.21873990080049036, 0.21747300992746885, 0.21631162927528974, 0.21527074921749167, 0.2143653601276133, 0.2136104523791934, 0.21302101634577073, 0.21261204240088388, 0.21239852091807152, 0.21239544227087245, 0.21261779683282533, 0.21308057497746888, 0.2137987670783417, 0.21478736350898248, 0.2160613546429301, 0.2176357308537231, 0.21952548251490012, 0.22174560000000004],
        [0.3424554393827383, 0.3445722987831368, 0.34610663159516275, 0.34708749232253727, 0.34754393546898144, 0.34750501553821633, 0.3469997870339631, 0.34605730445994287, 0.34470662231987675, 0.3429767951174858, 0.34089687735649116, 0.33849592354061414, 0.3358029881735754, 0.33284712575909636, 0.3296573908008982, 0.3262628378027017, 0.3226925212682282, 0.3189754957011988, 0.31514081560533463, 0.3112175354843567, 0.3072347098419863, 0.3032213931819443, 0.2992066400079519, 0.29521950482373016, 0.29128904213300033, 0.28744430643948354, 0.28371435224690067, 0.280128234058973, 0.2767150063794217, 0.27350372371196763, 0.2705234405603321, 0.26779583859701744, 0.26531310816965153, 0.26306006679464317, 0.2610215319884016, 0.25918232126733565, 0.25752725214785455, 0.25604114214636714, 0.2547088087792827, 0.25351506956301, 0.25244474201395817, 0.2514826436485363, 0.25061359198315336, 0.24982240453421842, 0.2490938988181404, 0.2484128923513285, 0.24776521995647802, 0.24714078568143008, 0.24653051088031197, 0.2459253169072512, 0.24531612511637518, 0.2446938568618113, 0.24404943349768699, 0.2433737763781296, 0.2426578068572666, 0.24189244628922543, 0.24106861602813343, 0.2401772374281181, 0.23920923184330678, 0.23815552062782688, 0.23700702513580596, 0.23575867776625067, 0.2344214550976856, 0.2330103447535148, 0.2315403343571421, 0.23002641153197162, 0.22848356390140723, 0.22692677908885278, 0.22537104471771252, 0.22383134841139024, 0.22232267779328987, 0.2208600204868154, 0.21945836411537095, 0.21813269630236023, 0.21689800467118742, 0.21576927684525635, 0.214761500447971, 0.2138896631027354, 0.21316875243295344, 0.21261375606202917, 0.21223966161336646, 0.2120614567103693, 0.2120941289764417, 0.21235266603498765, 0.2128520555094111, 0.21360728502311588, 0.21463334219950603, 0.21594521466198563, 0.21755789003395848, 0.21948635593882862, 0.22174560000000004],
        [0.34382277424550844, 0.34586580682698304, 0.3473219148956447, 0.34822053801413844, 0.34859111574510926, 0.34846308765120204, 0.3478658932950619, 0.3468289722393338, 0.3453817640466627, 0.3435537082796937, 0.3413742445010717, 0.33887281227344174, 0.3360788511594486, 0.33302180072173754, 0.32973110052295346, 0.3262361901257413, 0.3225665090927459, 0.31875149698661276, 0.3148205933699865, 0.31080323780551206, 0.3067288698558346, 0.30262692908359895, 0.29852685505145027, 0.29445808732203343, 0.29045006545799357, 0.2865322290219754, 0.28273401757662425, 0.27908487068458493, 0.2756142279085023, 0.2723515288110217, 0.2693262129547878, 0.2665602143733052, 0.2640454449835165, 0.26176631117322385, 0.2597072193302293, 0.2578525758423348, 0.25618678709734266, 0.25469425948305463, 0.25335939938727325, 0.25216661319780015, 0.2511003073024377, 0.25014488808898794, 0.24928476194525298, 0.2485043352590348, 0.24778801441813544, 0.24712020581035724, 0.24648640655549744, 0.24587647670133567, 0.24528136702764655, 0.2446920283142049, 0.24409941134078572, 0.24349446688716372, 0.24286814573311372, 0.24221139865841043, 0.24151517644282888, 0.2407704298661437, 0.23996810970812982, 0.23909916674856202, 0.23815455176721514, 0.23712521554386393, 0.23600210885828335, 0.23478017967872816, 0.23347036472737379, 0.23208759791487554, 0.23064681315188904, 0.22916294434906956, 0.22765092541707257, 0.22612569026655346, 0.22460217280816772, 0.22309530695257074, 0.221620026610418, 0.2201912656923648, 0.21882395810906674, 0.21753303777117905, 0.21633343858935733, 0.21524009447425693, 0.2142679393365333, 0.21343190708684187, 0.21274693163583794, 0.21222794689417715, 0.21188988677251472, 0.21174768518150622, 0.21181627603180705, 0.21211059323407264, 0.21264557069895837, 0.2134361423371197, 0.214497242059212, 0.21584380377589077, 0.21749076139781143, 0.2194530488356293, 0.2217456],
        [0.3451848452491229, 0.3471522082702181, 0.34852833818669576, 0.3493430609464142, 0.34962620249723103, 0.3494075887870046, 0.348717045763593, 0.3475843993748543, 0.34603947556864656, 0.344112100292828, 0.34183209949525656, 0.3392292991237906, 0.3363335251262877, 0.3331746034506064, 0.32978236004460454, 0.3261866208561403, 0.3224172118330718, 0.31850395892325706, 0.3144766880745543, 0.31036522523482146, 0.3061993963519168, 0.30200902737369817, 0.2978239442480238, 0.2936739729227518, 0.28958893934574026, 0.28559866946484724, 0.2817329892279309, 0.27802172458284913, 0.27449470147746013, 0.27118174585962196, 0.268112683677193, 0.26530969621362016, 0.26276438609470876, 0.26046071128185266, 0.25838262973644593, 0.256514099419883, 0.2548390782935579, 0.25334152431886475, 0.2520053954571977, 0.25081464966995093, 0.2497532449185185, 0.24880513916429475, 0.24795429036867372, 0.24718465649304963, 0.2464801954988164, 0.24582486534736847, 0.24520380609916256, 0.2446068862109069, 0.24402515623837198, 0.24344966673732865, 0.24287146826354775, 0.24228161137280002, 0.24167114662085615, 0.2410311245634869, 0.24035259575646314, 0.23962661075555552, 0.2388442201165348, 0.2379964743951719, 0.23707442414723737, 0.23606911992850207, 0.2349716122947368, 0.23377691339608572, 0.23249588176018712, 0.2311433375090526, 0.22973410076469392, 0.22828299164912275, 0.22680483028435083, 0.22531443679238974, 0.2238266312952514, 0.22235623391494727, 0.22091806477348924, 0.21952694399288877, 0.2181976916951578, 0.21694512800230797, 0.21578407303635078, 0.21472934691929824, 0.21379576977316173, 0.21299816171995317, 0.21235134288168417, 0.21187013338036648, 0.21156935333801163, 0.2114638228766315, 0.21156836211823773, 0.21189779118484206, 0.2124669301984561, 0.21329059928109162, 0.21438361855476024, 0.2157608081414737, 0.2174369881632436, 0.2194269787420818, 0.22174559999999996],
        [0.34655182785998057, 0.3484400065909899, 0.3497328913454867, 0.3504606885681085, 0.3506536047034926, 0.3503418461962763, 0.3495556194910974, 0.3483251310325929, 0.34668058726540046, 0.34465219463415736, 0.3422701595835012, 0.3395646885580694, 0.336565988002499, 0.33330426436142785, 0.32980972407949316, 0.3261125736013324, 0.32224301937158284, 0.31823126783488215, 0.3141075254358675, 0.3099019986191766, 0.30564489382944665, 0.3013664175113149, 0.29709677610941915, 0.2928661760683965, 0.28870482383288465, 0.2846429258475209, 0.28071068855694253, 0.27693831840578714, 0.27335602183869195, 0.26999400530029455, 0.2668824752352323, 0.26404384982720486, 0.2614693942161621, 0.25914258528111567, 0.2570468999010773, 0.2551658149550592, 0.2534828073220731, 0.25198135388113085, 0.2506449315112444, 0.24945701709142562, 0.24840108750068643, 0.24746061961803872, 0.2466190903224944, 0.24585997649306532, 0.24516675500876328, 0.24452290274860036, 0.2439131878214595, 0.24332754325570852, 0.2427571933095863, 0.24219336224133195, 0.24162727430918438, 0.24105015377138247, 0.24045322488616527, 0.23982771191177168, 0.23916483910644074, 0.23845583072841117, 0.23769191103592224, 0.23686430428721286, 0.2359642347405218, 0.23498292665408807, 0.23391160428615088, 0.23274539404260763, 0.23149503091999107, 0.23017515206249262, 0.22880039461430357, 0.22738539571961547, 0.22594479252261956, 0.2244932221675073, 0.2230453217984701, 0.22161572855969927, 0.22021907959538622, 0.21887001204972242, 0.21758316306689915, 0.21637316979110782, 0.2152546693665399, 0.2142422989373867, 0.2133506956478396, 0.21259449664209, 0.2119883390643293, 0.2115468600587489, 0.21128469676954015, 0.21121648634089446, 0.21135686591700326, 0.21172047264205787, 0.21232194366024973, 0.21317591611577014, 0.21429702715281054, 0.2156999139155624, 0.217399213548217, 0.21940956319496568, 0.22174560000000001],
        [0.3479338975444802, 0.3497377052674458, 0.3509425642491875, 0.35157904832796544, 0.35167773134203933, 0.3512691871296693, 0.3503839895291156, 0.3490527123786377, 0.34730592951649597, 0.3451742147809502, 0.34268814201026043, 0.3398782850426867, 0.33677521771648866, 0.33340951386992684, 0.32981174734126084, 0.32601249196875076, 0.3220423215906563, 0.31793181004523796, 0.3137115311707553, 0.30941205880546846, 0.3050639667876374, 0.30069782895552205, 0.2963442191473826, 0.2920337112014787, 0.2877968789560706, 0.28366429624941814, 0.27966653691978133, 0.27583417480542016, 0.2721977837445946, 0.2687879375755645, 0.26563521013659014, 0.2627622409233016, 0.26015993206081056, 0.25781125133159893, 0.2556991665181488, 0.253806645402942, 0.2521166557684606, 0.25061216539718645, 0.24927614207160154, 0.24809155357418788, 0.24704136768742735, 0.24610855219380195, 0.24527607487579373, 0.2445269035158845, 0.24384400589655614, 0.2432103498002909, 0.242610320956374, 0.24203397688130526, 0.24147279303838765, 0.24091824489092428, 0.24036180790221848, 0.23979495753557323, 0.23920916925429167, 0.238595918521677, 0.2379466808010324, 0.23725293155566077, 0.23650614624886554, 0.23569780034394966, 0.23481936930421632, 0.23386232859296863, 0.23281815367350975, 0.2316821367425778, 0.23046483693065092, 0.2291806301016422, 0.2278438921194647, 0.2264689988480317, 0.22507032615125616, 0.2236622498930512, 0.2222591459373301, 0.2208753901480058, 0.21952535838899148, 0.2182234265242003, 0.2169839704175453, 0.21582136593293963, 0.2147499889342964, 0.21378421528552877, 0.21293842085054976, 0.2122269814932726, 0.21166427307761027, 0.21126467146747607, 0.2110425525267829, 0.21101229211944403, 0.21118826610937252, 0.21158485036048155, 0.21221642073668417, 0.21309735310189354, 0.2142420233200227, 0.21566480725498477, 0.21738008077069296, 0.21940221973106036, 0.22174560000000001],
        [0.34934122976902043, 0.35105380777773326, 0.35216434677496844, 0.3527037676747289, 0.35270299139101713, 0.3521929388378361, 0.3512045309291885, 0.34976868857907734, 0.3479163327015051, 0.3456783842104749, 0.3430857640199894, 0.34016939304405114, 0.3369601921966632, 0.3334890823918283, 0.3297869845435492, 0.32588481956582876, 0.32181350837266964, 0.3176039718780747, 0.3132871309960468, 0.3088939066405887, 0.304455219725703, 0.30000199116539267, 0.2955651418736607, 0.29117559276450944, 0.28686426475194193, 0.282662078749961, 0.27859995567256923, 0.27470881643376965, 0.2710195819475649, 0.26756317312795785, 0.26437051088895114, 0.2614644352111524, 0.258835462341588, 0.2564660275938888, 0.2543385662816859, 0.2524355137186103, 0.250739305218293, 0.249232376094365, 0.24789716166045733, 0.246716097230201, 0.24567161811722704, 0.2447461596351664, 0.24392215709765028, 0.24318204581830952, 0.24250826111077498, 0.24188323828867805, 0.24129097473789218, 0.2407217161332618, 0.24016727022187379, 0.23961944475081517, 0.23907004746717314, 0.23851088611803453, 0.23793376845048636, 0.2373305022116156, 0.2366928951485094, 0.23601275500825458, 0.2352818895379383, 0.23449210648464752, 0.23363521359546918, 0.23270301861749026, 0.23168732929779795, 0.2305836566202805, 0.22940232451603207, 0.2281573601529481, 0.2268627906989241, 0.22553264332185563, 0.22418094518963805, 0.22282172347016696, 0.22146900533133793, 0.2201368179410463, 0.2188391884671876, 0.2175901440776574, 0.21640371194035113, 0.21529391922316432, 0.21427479309399242, 0.21336036072073106, 0.2125646492712755, 0.2119016859135215, 0.21138549781536436, 0.21103011214469963, 0.21084955606942285, 0.21085785675742952, 0.21106904137661506, 0.21149713709487505, 0.21215617108010493, 0.21306017050020024, 0.2142231625230564, 0.215659174316569, 0.2173822330486334, 0.21940636588714524, 0.22174560000000001],
        [0.3507840000000002, 0.3523968176000002, 0.3534052288000002, 0.35384047405714303, 0.3537337938285716, 0.3531164285714287, 0.35201961874285725, 0.35047460480000014, 0.34851262720000004, 0.34616492639999996, 0.34346274285714296, 0.3404373170285716, 0.3371198893714287, 0.33354170034285724, 0.32973399040000007, 0.3257280000000001, 0.3215549696000001, 0.31724613965714293, 0.31283275062857147, 0.3083460429714286, 0.30381725714285723, 0.2992776336, 0.2947584127999999, 0.2902908352, 0.28590614125714287, 0.28163557142857143, 0.2775103661714286, 0.27356176594285714, 0.2698210112, 0.26631934240000005, 0.263088, 0.26014999839999997, 0.2574954477714286, 0.2551062322285715, 0.2529642358857143, 0.25105134285714287, 0.2493494372571429, 0.2478404032, 0.24650612480000006, 0.2453284861714286, 0.2442893714285715, 0.24337066468571433, 0.2425542500571429, 0.24182201165714298, 0.24115583360000006, 0.2405376000000001, 0.23995091840000002, 0.23938629005714296, 0.23883593965714292, 0.23829209188571435, 0.23774697142857143, 0.2371928029714286, 0.2366218112, 0.23602622080000005, 0.23539825645714288, 0.23473014285714286, 0.2340141046857143, 0.23324236662857145, 0.2324071533714286, 0.23150068959999995, 0.23051519999999998, 0.2294464688, 0.2283045184, 0.22710293074285712, 0.22585528777142855, 0.22457517142857145, 0.22327616365714284, 0.22197184639999992, 0.22067580159999997, 0.21940161119999999, 0.2181628571428571, 0.21697312137142857, 0.21584598582857142, 0.21479503245714285, 0.21383384319999998, 0.21297600000000005, 0.21223508480000003, 0.21162467954285724, 0.21115836617142864, 0.2108497266285715, 0.2107123428571429, 0.2107597968, 0.2110056704, 0.21146354560000005, 0.21214700434285721, 0.21306962857142867, 0.21424500022857149, 0.21568670125714293, 0.2174083136, 0.2194234192, 0.22174560000000001],
        [0.35226934280562894, 0.3537726446269187, 0.35467001843929125, 0.3549929908576779, 0.3547730884970097, 0.354041837972218, 0.35283076589823426, 0.3511713988899896, 0.3490952635624153, 0.34663388653044286, 0.34381879440900337, 0.34068151381302825, 0.3372535713574487, 0.33356649365719604, 0.32965180732720134, 0.32554103898239617, 0.3212657152377118, 0.3168573627080794, 0.31234750800843053, 0.30776767775369607, 0.30314939855880746, 0.29852419703869615, 0.2939235998082931, 0.28937913348253, 0.284922324676338, 0.28058470000464825, 0.2763977860823921, 0.27239310952450096, 0.26860219694590587, 0.26505657496153834, 0.2617877701863297, 0.25881894134252237, 0.25613977558160494, 0.2537315921623772, 0.2515757103436388, 0.24965344938418949, 0.2479461285428292, 0.24643506707835752, 0.24510158424957437, 0.2439269993152794, 0.24289263153427246, 0.24197980016535334, 0.24116982446732177, 0.24044402369897752, 0.23978371711912033, 0.23917022398655002, 0.23858676484270444, 0.23802416535957388, 0.2374751524917867, 0.23693245319397108, 0.23638879442075555, 0.2358369031267685, 0.23526950626663817, 0.23467933079499287, 0.2340591036664611, 0.23340155183567107, 0.23269940225725122, 0.23194538188582983, 0.23113221767603537, 0.23025263658249598, 0.2292993655598403, 0.22826851617333352, 0.22716973843078989, 0.22601606695066023, 0.2248205363513958, 0.22359618125144765, 0.22235603626926692, 0.22111313602330465, 0.21988051513201198, 0.21867120821384003, 0.2174982498872398, 0.21637467477066252, 0.21531351748255922, 0.21432781264138095, 0.21343059486557878, 0.21263489877360403, 0.21195375898390756, 0.2114002101149405, 0.2109872867851541, 0.2107280236129993, 0.21063545521692728, 0.2107226162153891, 0.2110025412268359, 0.21148826486971878, 0.21219282176248871, 0.21312924652359688, 0.21431057377149448, 0.21574983812463253, 0.21746007420146193, 0.2194543166204341, 0.2217456],
        [0.35379222916135966, 0.3551768244092613, 0.3559547967592056, 0.35615792519370804, 0.35581798869528414, 0.3549667662464495, 0.35363603682971984, 0.3518575794276107, 0.34966317302263733, 0.34708459659731583, 0.34415362913416137, 0.3409020496156897, 0.3373616370244164, 0.3335641703428569, 0.3295414285535269, 0.325325190638942, 0.3209472355816177, 0.3164393423640696, 0.3118332899688134, 0.3071608573783645, 0.3024538235752385, 0.29774396754195104, 0.29306306826101775, 0.288442904714954, 0.28391525588627564, 0.27951190075749804, 0.27526461831113674, 0.2712051875297075, 0.2673653873957259, 0.2637769968917073, 0.2604717950001674, 0.2574730554651417, 0.2547700310767456, 0.25234346938661373, 0.25017411794638156, 0.2482427243076841, 0.24653003602215642, 0.24501680064143366, 0.24368376571715097, 0.2425116788009434, 0.2414812874444461, 0.24057333919929413, 0.23976858161712267, 0.2390477622495667, 0.23839162864826133, 0.23778092836484188, 0.2371985016300959, 0.23663555939142208, 0.23608540527537142, 0.23554134290849515, 0.2349966759173445, 0.2344447079284706, 0.2338787425684247, 0.23329208346375785, 0.23267803424102138, 0.23202989852676625, 0.23134097994754382, 0.23060458212990523, 0.22981400870040164, 0.2289625632855841, 0.22804354951200403, 0.22705345270113192, 0.22600148495411645, 0.22490004006702577, 0.22376151183592788, 0.2225982940568909, 0.22142278052598305, 0.2202473650392724, 0.21908444139282698, 0.217946403382715, 0.21684564480500457, 0.21579455945576365, 0.2148055411310606, 0.21389098362696324, 0.21306328073953987, 0.21233482626485864, 0.21171801399898746, 0.21122523773799462, 0.21086889127794808, 0.21066136841491612, 0.21061506294496668, 0.21074236866416798, 0.21105567936858813, 0.21156738885429524, 0.21228989091735734, 0.21323557935384257, 0.21441684795981922, 0.2158460905313551, 0.21753570086451843, 0.21949807275537736, 0.22174560000000001],
        [0.35534458914445544, 0.3566022989123243, 0.35725346306394473, 0.3573300801163337, 0.35686414858650867, 0.35588766699148683, 0.3544326338482858, 0.35253104767392257, 0.3502149069854147, 0.3475162102997792, 0.34446695613403383, 0.3410991430051955, 0.33744476943028157, 0.33353583392630953, 0.32940433501029653, 0.3250822711992599, 0.32060164101021704, 0.3159944429601852, 0.3112926755661816, 0.30652833734522356, 0.3017334268143287, 0.29693994249051386, 0.2921798828907968, 0.2874852465321945, 0.28288803193172446, 0.27842023760640383, 0.2741138620732499, 0.27000090384928027, 0.2661133614515119, 0.26248323339696233, 0.2591425182026488, 0.25611457733771575, 0.2533882240798169, 0.2509436346587326, 0.24876098530424381, 0.24682045224613117, 0.2451022117141753, 0.24358643993815696, 0.24225331314785695, 0.24108300757305565, 0.24005569944353403, 0.23915156498907272, 0.2383507804394524, 0.23763352202445384, 0.2369799659738575, 0.23637028851744432, 0.23578695999228552, 0.235221627164615, 0.23466823090795694, 0.2341207120958357, 0.23357301160177593, 0.23301907029930188, 0.2324528290619379, 0.23186822876320837, 0.23125921027663776, 0.2306197144757504, 0.2299436822340707, 0.22922505442512303, 0.22845777192243186, 0.22763577559952136, 0.22675300632991618, 0.2258063601115587, 0.22480455344006417, 0.22375925793546603, 0.22268214521779744, 0.22158488690709197, 0.22047915462338274, 0.21937661998670333, 0.21828895461708697, 0.21722783013456706, 0.21620491815917692, 0.2152318903109499, 0.21432041820991954, 0.2134821734761189, 0.21272882772958154, 0.21207205259034073, 0.21152351967842992, 0.21109490061388234, 0.21079786701673137, 0.2106440905070105, 0.21064524270475285, 0.210812995229992, 0.21115901970276116, 0.21169498774309384, 0.21243257097102325, 0.21338344100658282, 0.21455926946980583, 0.21597172798072575, 0.21763248815937578, 0.2195532216257895, 0.22174560000000001],
        [0.35691835283217993, 0.35804201010140474, 0.3585599166577104, 0.3585042586766552, 0.357907222333797, 0.3568009938046938, 0.35521775926490406, 0.35318970488998547, 0.3507490168554962, 0.3479278813369945, 0.3447584845100383, 0.34127301255018583, 0.33750365163299484, 0.33348258793402363, 0.3292420076288301, 0.3248140968929728, 0.3202310419020093, 0.31552502883149774, 0.31072824385699643, 0.30587287315406336, 0.3009911028982564, 0.29611511926513395, 0.29127710843025373, 0.2865092565691742, 0.28184374985745325, 0.27731277447064884, 0.2729485165843192, 0.26878316237402233, 0.2648488980153163, 0.26117790968375937, 0.2578023835549093, 0.25474574353010226, 0.2519963644137859, 0.24953385873618564, 0.247337839027527, 0.24538791781803557, 0.24366370763793674, 0.24214482101745605, 0.24081087048681904, 0.2396414685762513, 0.23861622781597822, 0.23771476073622536, 0.23691667986721823, 0.23620159773918245, 0.2355491268823433, 0.23493887982692646, 0.2343529711593847, 0.2337835236910804, 0.23322516228960308, 0.2326725118225423, 0.23212019715748788, 0.23156284316202932, 0.23099507470375621, 0.23041151665025822, 0.22980679386912486, 0.2291755312279458, 0.2285123535943107, 0.22781188583580916, 0.22706875282003078, 0.22627757941456514, 0.22543299048700202, 0.22453232013277782, 0.2235837393587177, 0.2225981283994936, 0.22158636748977756, 0.22055933686424162, 0.21952791675755765, 0.21850298740439777, 0.21749542903943409, 0.21651612189733846, 0.21557594621278303, 0.21468578222043963, 0.21385651015498044, 0.21309901025107741, 0.21242416274340253, 0.2118428478666279, 0.2113659458554254, 0.2110043369444672, 0.21076890136842516, 0.21067051936197143, 0.2107200711597779, 0.2109284369965167, 0.2113064971068597, 0.21186513172547908, 0.21261522108704675, 0.21356764542623474, 0.21473328497771502, 0.21612301997615974, 0.21774773065624076, 0.21961829725263016, 0.22174559999999996],
        [0.3585054503017968, 0.3594888999417995, 0.3598680568447053, 0.35967526392577337, 0.35894286410026327, 0.3577032002834346, 0.35598861539054677, 0.35383145233685914, 0.35126405403763117, 0.34831876340812257, 0.3450279233635925, 0.34142387681930064, 0.3375389666905063, 0.33340553589246913, 0.3290559273404483, 0.3245224839497036, 0.3198375486354942, 0.31503346431307977, 0.31014257389771965, 0.3051972203046735, 0.30022974644920053, 0.2952724952465604, 0.29035780961201235, 0.28551803246081614, 0.28078550670823116, 0.2761925752695166, 0.2717715810599322, 0.2675548669947374, 0.26357477598919166, 0.2598636509585542, 0.2564538348180848, 0.2533687906121593, 0.2505964619016199, 0.2481159123764247, 0.24590620572653257, 0.24394640564190204, 0.2422155758124916, 0.24069277992825966, 0.23935708167916483, 0.23818754475516565, 0.23716323284622062, 0.23626320964228845, 0.2354665388333274, 0.23475228410929622, 0.2340995091601533, 0.23348727767585714, 0.2328973663615047, 0.23232240398274623, 0.23175773232037, 0.23119869315516453, 0.2306406282679185, 0.2300788794394202, 0.22950878845045825, 0.228925697081821, 0.2283249471142971, 0.22770188032867475, 0.22705183850574276, 0.22637016342628943, 0.2256521968711033, 0.22489328062097289, 0.22408875645668663, 0.22323641449295312, 0.22234383818016157, 0.22142105930262115, 0.22047810964464118, 0.21952502099053087, 0.2185718251245995, 0.21762855383115623, 0.21670523889451063, 0.21581191209897163, 0.21495860522884866, 0.21415535006845088, 0.21341217840208757, 0.21273912201406803, 0.21214621268870149, 0.21164348221029725, 0.21124096236316448, 0.21094868493161245, 0.21077668169995054, 0.21073498445248792, 0.2108336249735338, 0.2110826350473975, 0.2114920464583883, 0.21207189099081541, 0.21283220042898815, 0.21378300655721566, 0.2149343411598073, 0.21629623602107234, 0.21787872292531987, 0.21969183365685938, 0.2217456],
        [0.3600978116305692, 0.3609359103988053, 0.3611717829291307, 0.3608378989147884, 0.3599667280490214, 0.3585907400250729, 0.3567424045361858, 0.3544541912756033, 0.3517585699365683, 0.34868801021232404, 0.3452749817961137, 0.34155195438118013, 0.3375513976607663, 0.33330578132811545, 0.3288475750764707, 0.32420924859907485, 0.31942327158917116, 0.3145221137400027, 0.30953824474481256, 0.3045041342968438, 0.29945225208933934, 0.29441506781554244, 0.28942505116869593, 0.2845146718420431, 0.27971639952882693, 0.2750627039222904, 0.27058605471567665, 0.26631892160222875, 0.2622937742751899, 0.25854308242780283, 0.25509931575331096, 0.25198595515374467, 0.24919052636628533, 0.24669156633690145, 0.2444676120115619, 0.2424972003362353, 0.24075886825689055, 0.23923115271949622, 0.23789259067002103, 0.23672171905443376, 0.23569707481870317, 0.23479719490879794, 0.23400061627068688, 0.2332858758503386, 0.23263151059372178, 0.23201605744680537, 0.23142097682875687, 0.23083942305154007, 0.23026747390031746, 0.22970120716025175, 0.2291367006165056, 0.22857003205424153, 0.2279972792586223, 0.22741452001481038, 0.22681783210796858, 0.22620329332325936, 0.22556698144584542, 0.22490497426088954, 0.22421334955355404, 0.2234881851090017, 0.2227255587123952, 0.22192372492024842, 0.22108964537448025, 0.220232458488361, 0.21936130267516107, 0.21848531634815063, 0.21761363792059987, 0.21675540580577907, 0.21591975841695865, 0.2151158341674088, 0.21435277147039972, 0.21363970873920168, 0.21298578438708504, 0.21240013682732, 0.2118919044731769, 0.21147022573792593, 0.21114423903483734, 0.2109230827771815, 0.2108158953782285, 0.21083181525124883, 0.21097998080951252, 0.21126953046628996, 0.21170960263485147, 0.21230933572846725, 0.21307786816040764, 0.21402433834394277, 0.215157884692343, 0.2164876456188786, 0.21802275953681974, 0.2197723648594368, 0.22174560000000001],
        [0.36168736689576086, 0.3623759834377191, 0.36246499421518896, 0.36198696669480085, 0.3609744683431851, 0.3594600666269725, 0.3574763290127931, 0.35505582296727756, 0.3522311159570564, 0.3490347754487601, 0.3454993689090191, 0.3416574638044639, 0.33754162760172485, 0.33318442776743246, 0.32861843176821715, 0.3238762070707095, 0.31899032114153986, 0.3139933414473387, 0.3089178354547367, 0.30379637063036413, 0.2986615144408515, 0.29354583435282916, 0.2884818978329277, 0.28350227234777764, 0.2786395253640093, 0.27392622434825337, 0.26939493676713994, 0.2650782300872998, 0.26100867177536335, 0.25721882929796086, 0.25374127012172315, 0.2505994737247161, 0.2477805676307493, 0.24526259137506767, 0.24302358449291625, 0.2410415865195402, 0.23929463699018458, 0.23776077544009439, 0.23641804140451483, 0.2352444744186909, 0.23421811401786766, 0.23331699973729023, 0.2325191711122038, 0.23180266767785315, 0.2311455289694835, 0.23052579452234004, 0.22992463379125244, 0.22933573590938972, 0.22875591992950547, 0.22818200490435334, 0.22761080988668708, 0.22703915392926038, 0.22646385608482686, 0.22588173540614012, 0.22528961094595396, 0.22468430175702192, 0.22406262689209777, 0.2234214054039351, 0.22275745634528762, 0.22206759876890894, 0.22134865172755291, 0.22059933314282743, 0.21982595641175834, 0.21903673380022587, 0.21823987757411029, 0.21744359999929166, 0.21665611334165039, 0.2158856298670665, 0.21514036184142044, 0.21442852153059225, 0.21375832120046218, 0.21313797311691043, 0.21257568954581726, 0.21207968275306285, 0.21165816500452744, 0.2113193485660913, 0.21107144570363454, 0.21092266868303744, 0.21088122977018006, 0.21095534123094292, 0.211153215331206, 0.21148306433684957, 0.21195310051375388, 0.21257153612779917, 0.2133465834448655, 0.21428645473083327, 0.2153993622515826, 0.21669351827299374, 0.2181771350609468, 0.2198584248813222, 0.22174560000000001],
        [0.363266046174635, 0.36380206102383755, 0.3637415900070817, 0.363117270316911, 0.3619617391458682, 0.36030763368649693, 0.35818759113134047, 0.3556342486729418, 0.35268024350384436, 0.3493582128165916, 0.34570079380372637, 0.3417406236577922, 0.33751033957133225, 0.3330425787368898, 0.328369978347008, 0.3235251755942303, 0.31854080767109966, 0.3134495117701597, 0.3082839250839535, 0.30307668480502425, 0.29786042812591534, 0.29266779223916994, 0.28753141433733137, 0.2824839316129428, 0.27755798125854747, 0.2727862004666887, 0.26820122642990984, 0.263835696340754, 0.2597222473917643, 0.25589351677548433, 0.2523821416844573, 0.24921158289493162, 0.24636859551797877, 0.24383075824837508, 0.24157564978089702, 0.2395808488103213, 0.23782393403142446, 0.2362824841389829, 0.23493407782777326, 0.2337562937925722, 0.23272671072815604, 0.23182290732930141, 0.23102246229078505, 0.23030295430738332, 0.22964196207387272, 0.22901706428503002, 0.22840916847910256, 0.22781249756822286, 0.22722460330799382, 0.2266430374540188, 0.22606535176190104, 0.22548909798724381, 0.22491182788565028, 0.22433109321272374, 0.22374444572406746, 0.22314943717528446, 0.22254361932197828, 0.22192454391975203, 0.22128976272420878, 0.22063682749095193, 0.2199632899755848, 0.21926832088885403, 0.21855756676208032, 0.2178382930817281, 0.21711776533426153, 0.216403249006145, 0.2157020095838427, 0.21502131255381887, 0.21436842340253798, 0.2137506076164642, 0.21317513068206176, 0.212649258085795, 0.21218025531412826, 0.21177538785352568, 0.21144192119045166, 0.21118712081137048, 0.2110182522027463, 0.2109425808510436, 0.21096737224272644, 0.21109989186425923, 0.21134740520210624, 0.21171717774273172, 0.2122164749726, 0.2128525623781754, 0.21363270544592206, 0.21456416966230438, 0.21565422051378655, 0.21691012348683292, 0.21833914406790775, 0.21994854774347533, 0.2217456],
        [0.3648257795444554, 0.36520708512245753, 0.3649954696090112, 0.3642236128322194, 0.36292419462018466, 0.3611298948010107, 0.3588733932028001, 0.35618736965365594, 0.35310450398168136, 0.34965747601497926, 0.3458789655816528, 0.341801652509805, 0.3374582166275387, 0.33288133776295714, 0.3281036957441632, 0.3231579703992599, 0.3180768415563503, 0.3128929890435375, 0.3076390926889245, 0.3023478323206142, 0.29705188776670965, 0.2917839388553139, 0.2865766654145301, 0.281462747272461, 0.2764748642572101, 0.27164569619688, 0.26700792291957376, 0.26259422425339446, 0.25843728002644534, 0.25456977006682896, 0.2510243742026488, 0.24782451923424906, 0.2449566198509406, 0.24239783771427545, 0.24012533448580567, 0.23811627182708348, 0.236347811399661, 0.2347971148650903, 0.2334413438849235, 0.2322576601207127, 0.23122322523401015, 0.23031520088636787, 0.22951074873933805, 0.2287870304544728, 0.22812120769332406, 0.22749044211744426, 0.2268754121224188, 0.22627086303996732, 0.22567505693584253, 0.22508625587579756, 0.22450272192558537, 0.22392271715095896, 0.22334450361767116, 0.22276634339147502, 0.22218649853812344, 0.22160323112336938, 0.2210148032129659, 0.22041947687266591, 0.2198155141682223, 0.219201177165388, 0.2185747279299162, 0.21793576988649202, 0.21728927189553088, 0.2166415441763803, 0.2159988969483879, 0.2153676404309014, 0.21475408484326847, 0.21416454040483662, 0.21360531733495364, 0.21308272585296703, 0.21260307617822455, 0.21217267853007377, 0.21179784312786237, 0.21148488019093797, 0.21124009993864823, 0.2110698125903408, 0.21098032836536326, 0.21097795748306328, 0.21106901016278856, 0.21125979662388666, 0.21155662708570525, 0.21196581176759202, 0.2124936608888945, 0.21314648466896055, 0.21393059332713754, 0.21485229708277326, 0.21591790615521536, 0.21713373076381148, 0.2185060811279091, 0.2200412674668561, 0.22174560000000001],
        [0.36635849708248525, 0.36658399769887606, 0.36622053232517926, 0.36530079729182646, 0.3638574889292486, 0.36192330356787716, 0.3595309375381438, 0.3567130871704796, 0.35350244879531584, 0.3499317187430843, 0.34603359334421585, 0.34184076892914234, 0.3373859418282946, 0.3327018083721043, 0.3278210648910027, 0.3227764077154212, 0.3176005331757911, 0.3123261376025439, 0.30698591732611086, 0.3016125686769233, 0.29623878798541264, 0.29089727158201023, 0.28562071579714743, 0.2804418169612556, 0.2753932714047661, 0.27050777545811017, 0.2658180254517193, 0.2613567177160249, 0.2571565485814581, 0.2532502143784505, 0.24967041143743332, 0.24644051931252614, 0.2435466504526017, 0.2409656005302205, 0.23867416521794346, 0.23664914018833144, 0.23486732111394504, 0.23330550366734512, 0.2319404835210924, 0.23074905634774778, 0.22970801781987188, 0.2287941636100256, 0.2279842893907697, 0.22725519083466494, 0.22658366361427196, 0.22594650340215175, 0.22532419595131226, 0.22471198733655068, 0.22410881371311148, 0.22351361123623908, 0.22292531606117807, 0.22234286434317282, 0.22176519223746774, 0.22119123589930745, 0.22061993148393633, 0.22005021514659878, 0.21948102304253936, 0.21891129132700254, 0.21833995615523272, 0.21776595368247437, 0.217188220063972, 0.21660676186390523, 0.2160258672821944, 0.21545089492769487, 0.2148872034092622, 0.21434015133575182, 0.2138150973160193, 0.21331739995891988, 0.21285241787330939, 0.21242550966804297, 0.2120420339519763, 0.21170734933396468, 0.21142681442286376, 0.21120578782752888, 0.2110496281568156, 0.21096369401957932, 0.21095334402467553, 0.2110239367809598, 0.2111808308972874, 0.21142938498251398, 0.21177495764549492, 0.21222290749508577, 0.21277859314014191, 0.21344737318951892, 0.2142346062520722, 0.2151456509366572, 0.21618586585212943, 0.21736060960734432, 0.2186752408111574, 0.22013511807242414, 0.2217456],
        [0.36785612886598823, 0.36792574071838974, 0.36741067745978784, 0.3663436267468326, 0.36475727623617343, 0.3626843135844605, 0.36015742644834364, 0.3572093024844726, 0.3538726293494972, 0.35018009470006733, 0.34616438619283296, 0.341858191484444, 0.33729419823154994, 0.3325050940908009, 0.3275235667188465, 0.32238230377233706, 0.31711399290792186, 0.311751321782251, 0.30632697805197445, 0.3008736493737418, 0.29542402340420315, 0.2900107878000083, 0.28466663021780675, 0.27942423831424884, 0.27431629974598426, 0.2693755021696627, 0.26463453324193414, 0.2601260806194484, 0.2558828319588554, 0.2519374749168048, 0.24832269714994665, 0.2450618196996209, 0.24214069714592898, 0.23953581745366215, 0.2372236685876119, 0.23518073851256988, 0.23338351519332748, 0.23180848659467607, 0.23043214068140727, 0.2292309654183125, 0.22818144877018323, 0.22726007870181092, 0.2264433431779872, 0.2257077301635034, 0.2250297276231509, 0.22438582352172137, 0.22375635119589418, 0.22313702546990086, 0.22252740653986058, 0.22192705460189283, 0.22133552985211705, 0.22075239248665252, 0.22017720270161864, 0.21960952069313483, 0.21904890665732046, 0.2184949207902949, 0.21794712328817753, 0.21740507434708778, 0.21686833416314494, 0.21633646293246836, 0.21580902085117765, 0.21528637854925756, 0.21477214839215553, 0.21427075317918454, 0.21378661570965737, 0.21332415878288719, 0.21288780519818687, 0.21248197775486927, 0.2121110992522475, 0.21177959248963435, 0.2114918802663429, 0.2112523853816861, 0.21106553063497674, 0.21093573882552785, 0.21086743275265246, 0.21086503521566347, 0.21093296901387382, 0.21107565694659638, 0.2112975218131442, 0.21160298641283026, 0.21199647354496742, 0.21248240600886859, 0.21306520660384687, 0.21374929812921514, 0.21453910338428633, 0.21543904516837337, 0.21645354628078922, 0.2175870295208469, 0.21884391768785927, 0.22022863358113928, 0.2217456],
        [0.3693106049722277, 0.3692252561462955, 0.36855980431703894, 0.36734690424833827, 0.3656192107040735, 0.36340937844812443, 0.36075006224437156, 0.35767391685669475, 0.3542135970489739, 0.3504017575850896, 0.3462710532289218, 0.3418541387443502, 0.3371836688952552, 0.3322922984455168, 0.327212682159015, 0.32197747479963007, 0.3166193311312418, 0.31117090591773067, 0.30566485392297654, 0.30013382991085946, 0.2946104886452596, 0.28912748489005696, 0.2837174734091317, 0.27841310896636395, 0.27324704632563357, 0.26825194025082094, 0.26346044550580594, 0.25890521685446866, 0.2546189090606893, 0.25063417688834777, 0.2469836751013244, 0.24369065696539113, 0.2407407697538894, 0.238110259242052, 0.2357753712051123, 0.2337123514183036, 0.23189744565685905, 0.2303068996960118, 0.22891695931099507, 0.2277038702770421, 0.22664387836938601, 0.2257132293632601, 0.2248881690338976, 0.2241449431565316, 0.2234597975063954, 0.22280897785872214, 0.22217270908627604, 0.22154713245194557, 0.22093236831614987, 0.22032853703930824, 0.21973575898184033, 0.21915415450416517, 0.21858384396670227, 0.21802494772987085, 0.21747758615409032, 0.21694187959977992, 0.21641794842735912, 0.2159059129972472, 0.21540589366986354, 0.21491801080562728, 0.2144423847649581, 0.2139797016707127, 0.21353291069549876, 0.21310552677436156, 0.21270106484234633, 0.21232303983449835, 0.21197496668586283, 0.21166036033148491, 0.21138273570641009, 0.21114560774568356, 0.2109524913843504, 0.2108069015574559, 0.21071235320004547, 0.21067236124716424, 0.21069044063385745, 0.21077010629517046, 0.21091487316614832, 0.2111282561818364, 0.21141377027727998, 0.21177493038752435, 0.21221525144761452, 0.21273824839259597, 0.2133474361575139, 0.2140463296774136, 0.2148384438873402, 0.21572729372233906, 0.21671639411745533, 0.21780926000773432, 0.21900940632822122, 0.22032034801396136, 0.2217456],
        [0.3707138554784672, 0.3704754859478902, 0.36966181220113453, 0.36830543284744405, 0.36643894649606223, 0.36409495175623285, 0.3613060472371994, 0.3581048315482057, 0.35452390329849526, 0.3505958610973119, 0.3463533035538993, 0.3418288292775009, 0.3370550368773603, 0.33206452496272143, 0.3268898921428278, 0.3215637370269231, 0.3161186582242508, 0.3105872543440549, 0.3050021239955787, 0.29939586578806593, 0.2938010783307604, 0.28825036023290573, 0.2827763101037455, 0.2774115265525233, 0.272188608188483, 0.26714015362086807, 0.2622987614589221, 0.25769703031188895, 0.2533675587890121, 0.2493429454995352, 0.2456557890527021, 0.24232926767969476, 0.23934887809944974, 0.23669069665284184, 0.23433079968074608, 0.23224526352403735, 0.23041016452359067, 0.22880157902028084, 0.22739558335498283, 0.22616825386857164, 0.2250956669019221, 0.22415389879590922, 0.223319025891408, 0.2225671245292932, 0.22187427105043983, 0.22121654179572287, 0.220574100852569, 0.21994346329461245, 0.2193252319420391, 0.21872000961503482, 0.21812839913378573, 0.21755100331847782, 0.2169884249892969, 0.21644126696642899, 0.2159101320700601, 0.21539562312037602, 0.2148983429375629, 0.21441889434180672, 0.21395788015329326, 0.21351590319220848, 0.21309356627873854, 0.21269181295643447, 0.21231294966230868, 0.21195962355673867, 0.21163448180010194, 0.21134017155277618, 0.21107933997513875, 0.2108546342275673, 0.2106687014704394, 0.21052418886413268, 0.2104237435690245, 0.21037001274549247, 0.21036564355391424, 0.21041328315466723, 0.21051557870812904, 0.2106751773746773, 0.21089472631468947, 0.21117687268854307, 0.21152426365661572, 0.21193954637928497, 0.21242536801692832, 0.21298437572992338, 0.21361921667864767, 0.21433253802347868, 0.21512698692479412, 0.21600521054297137, 0.21696985603838803, 0.21802357057142172, 0.21916900130244987, 0.22040879539185013, 0.22174560000000001],
        [0.37205781046197006, 0.3716693720884704, 0.3707106004162763, 0.36921401559525024, 0.3672121377752537, 0.3647374871061494, 0.36182258373779924, 0.3584999478200653, 0.3548020995028099, 0.35076155893589506, 0.346410846269183, 0.34178248165253583, 0.33690898523581564, 0.33182287716888476, 0.32655667760160506, 0.32114290668383877, 0.31561408456544804, 0.31000273139629514, 0.3043413673262422, 0.29866251250515113, 0.2929986870828843, 0.28738241120930363, 0.2818462050342715, 0.2764225887076499, 0.27114408237930115, 0.26604320619908717, 0.2611524803168703, 0.2565044248825124, 0.2521315600458759, 0.2480664059568228, 0.24434148276521533, 0.24097988841238938, 0.23796703200557698, 0.23527890044348343, 0.23289148062481443, 0.23078075944827578, 0.22892272381257298, 0.22729336061641175, 0.22586865675849757, 0.22462459913753627, 0.22353717465223338, 0.22258237020129454, 0.22173617268342544, 0.2209745689973316, 0.22027354604171867, 0.2196090907152925, 0.21896135772488423, 0.2183271730098292, 0.21770753031758813, 0.21710342339562186, 0.21651584599139137, 0.21594579185235743, 0.21539425472598106, 0.21486222835972302, 0.21435070650104424, 0.21386068289740542, 0.2133931512962677, 0.21294910544509188, 0.21252953909133868, 0.21213544598246908, 0.2117678198659441, 0.21142779413458665, 0.21111706076266976, 0.2108374513698282, 0.21059079757569713, 0.21037893099991142, 0.21020368326210623, 0.21006688598191658, 0.2099703707789775, 0.20991596927292397, 0.20990551308339106, 0.20994083383001377, 0.21002376313242713, 0.21015613261026614, 0.21033977388316588, 0.2105765185707614, 0.21086819829268758, 0.21121664466857965, 0.2116236893180725, 0.21209116386080118, 0.2126208999164007, 0.21321472910450612, 0.21387448304475248, 0.21460199335677488, 0.21539909166020815, 0.21626760957468752, 0.2172093787198478, 0.21822623071532424, 0.21931999718075165, 0.22049250973576523, 0.2217456],
        [0.3733344, 0.3727998565333333, 0.3717000682666667, 0.37006745554285736, 0.36793443870476206, 0.36533343809523827, 0.36229687405714295, 0.35885716693333347, 0.35504673706666673, 0.35089800480000016, 0.3464433904761906, 0.3417153144380954, 0.33674619702857167, 0.3315684585904763, 0.32621451946666685, 0.3207168000000002, 0.31510772053333336, 0.3094197014095239, 0.3036851629714286, 0.2979365255619048, 0.29220620952380955, 0.2865266352, 0.2809302229333334, 0.2754493930666666, 0.2701165659428572, 0.2649641619047619, 0.2600246012952381, 0.25533030445714283, 0.25091369173333333, 0.24680718346666664, 0.24304320000000004, 0.23964475573333327, 0.2365972412952381, 0.23387664137142858, 0.231458940647619, 0.22932012380952374, 0.2274361755428571, 0.22578308053333335, 0.22433682346666659, 0.2230733890285714, 0.2219687619047618, 0.2209989267809523, 0.22013986834285715, 0.21936757127619044, 0.21865802026666664, 0.21798719999999996, 0.2173353109333333, 0.2166994166095238, 0.21608079634285712, 0.21548072944761898, 0.2149004952380952, 0.21434137302857137, 0.21380464213333333, 0.2132915818666667, 0.21280347154285717, 0.21234159047619044, 0.21190721798095238, 0.2115016333714286, 0.21112611596190475, 0.21078194506666664, 0.2104704, 0.21019272693333338, 0.20995003946666663, 0.2097434180571429, 0.20957394316190478, 0.20944269523809528, 0.20935075474285714, 0.20929920213333333, 0.20928911786666665, 0.20932158239999998, 0.2093976761904762, 0.2095184796952381, 0.20968507337142855, 0.2098985376761905, 0.21015995306666665, 0.21047040000000003, 0.21083095893333337, 0.21124271032380956, 0.21170673462857142, 0.2122241123047619, 0.21279592380952386, 0.21342324959999998, 0.21410717013333333, 0.21484876586666668, 0.21564911725714292, 0.21650930476190478, 0.21743040883809528, 0.2184135099428572, 0.21945968853333334, 0.2205700250666667, 0.2217456],
        [0.3745368711943676, 0.3738610506600061, 0.37262513848349704, 0.37086143528181986, 0.3686022416719539, 0.3658798582708788, 0.36272658569557387, 0.35917472456301874, 0.3552565754901928, 0.35100443909407575, 0.3464506159916465, 0.34162740679988524, 0.3365671121357708, 0.3313020326162831, 0.3258644688584013, 0.32028672147910514, 0.314601091095374, 0.30883987832418724, 0.3030353837825244, 0.297219908087365, 0.29142575185568836, 0.28568521570447414, 0.2800306002507017, 0.27449420611135045, 0.2691083339034002, 0.26390528424383014, 0.2589173577496196, 0.25417685503774845, 0.2497160767251958, 0.24556732342894128, 0.24176289576596435, 0.23832572321041637, 0.23524125066513657, 0.2324855518901357, 0.23003470064542494, 0.2278647706910153, 0.2259518357869178, 0.2242719696931433, 0.22280124616970298, 0.22151573897660773, 0.2203915218738687, 0.21940466862149668, 0.2185312529795029, 0.2177473487078983, 0.21702902956669373, 0.21635236931590046, 0.21569767108382815, 0.21506215547198265, 0.21444727245016812, 0.2138544719881892, 0.2132852040558503, 0.21274091862295594, 0.2122230656593106, 0.21173309513471858, 0.21127245701898456, 0.2108426012819129, 0.21044497789330802, 0.21008103682297447, 0.2097522280407167, 0.2094600015163391, 0.20920580721964635, 0.20899092063101957, 0.20881591927314816, 0.20868120617929822, 0.2085871843827359, 0.2085342569167275, 0.20852282681453882, 0.2085532971094364, 0.2086260708346862, 0.20874155102355438, 0.20890014070930715, 0.20910224292521065, 0.20934826070453094, 0.20963859708053434, 0.2099736550864869, 0.21035383775565492, 0.21077954812130428, 0.21125118921670133, 0.21176916407511218, 0.212333875729803, 0.21294572721403998, 0.21360512156108916, 0.21431246180421676, 0.21506815097668905, 0.21587259211177204, 0.2167261882427319, 0.21762934240283482, 0.2185824576253469, 0.21958593694353437, 0.2206401833906633, 0.22174559999999996],
        [0.37566373924507296, 0.37485174349493827, 0.37348482750591805, 0.3715951555655094, 0.369214891961209, 0.3663762009805138, 0.36311124691092067, 0.3594521940399263, 0.35543120665502775, 0.35108044904372177, 0.3464320854935054, 0.341518280291875, 0.33637119772632795, 0.3310230020843609, 0.3255058576534706, 0.31985192872115414, 0.314093379574908, 0.3082623745022294, 0.3023910777906151, 0.29651165372756183, 0.29065626660056654, 0.284857080697126, 0.2791462603047372, 0.2735559697108969, 0.26811837320310195, 0.26286563506884925, 0.2578299195956356, 0.2530433910709578, 0.2485382137823129, 0.24434655201719743, 0.2405005700631086, 0.23702311240365856, 0.23389974430692245, 0.23110671123709065, 0.22862025865835378, 0.22641663203490214, 0.22447207683092654, 0.2227628385106172, 0.22126516253816486, 0.21995529437775985, 0.21880947949359272, 0.21780396334985405, 0.21691499141073436, 0.21611880914042414, 0.2153916620031138, 0.21470979546299393, 0.2140536662854851, 0.21342057644092782, 0.2128120392008926, 0.21222956783695013, 0.21167467562067094, 0.21114887582362557, 0.21065368171738452, 0.2101906065735184, 0.20976116366359793, 0.20936686625919348, 0.20900922763187577, 0.20868976105321538, 0.20840997979478265, 0.20817139712814833, 0.20797552632488306, 0.2078235947067171, 0.20771568579602048, 0.20765159716532292, 0.20763112638715434, 0.20765407103404437, 0.2077202286785229, 0.20782939689311963, 0.20798137325036448, 0.20817595532278715, 0.20841294068291744, 0.20869212690328517, 0.20901331155642003, 0.209376292214852, 0.20978086645111066, 0.21022683183772592, 0.2107139859472276, 0.21124212635214534, 0.21181105062500902, 0.2124205563383485, 0.2130704410646934, 0.21376050237657362, 0.21449053784651906, 0.21526034504705935, 0.2160697215507242, 0.21691846493004355, 0.21780637275754722, 0.21873324260576493, 0.21969887204722638, 0.22070305865446146, 0.22174560000000001],
        [0.3767148363766634, 0.3757718934768095, 0.3742791752000701, 0.3722686966877516, 0.36977247308115985, 0.3668225195216017, 0.36345085115038306, 0.35968948310880994, 0.35557043053818893, 0.3511257085798263, 0.34638733237502806, 0.3413873170651006, 0.3361576777913499, 0.33073042969508254, 0.3251375879176045, 0.31941116760022215, 0.31358318388424167, 0.30768565191096925, 0.30175058682171135, 0.29581000375777394, 0.2898959178604634, 0.2840403442710858, 0.27827529813094765, 0.272632794581355, 0.26714484876361405, 0.2618434758190313, 0.2567606908889126, 0.2519285091145645, 0.24737894563729307, 0.24314401559840465, 0.23925573413920537, 0.23573686187111184, 0.23257314128598258, 0.22974106034578587, 0.2272171070124906, 0.2249777692480654, 0.22299953501447878, 0.22125889227369955, 0.21973232898769623, 0.21839633311843762, 0.2172273926278921, 0.2162019954780286, 0.2152966296308157, 0.21448778304822202, 0.21375194369221603, 0.21306559952476667, 0.21240940402322095, 0.21178067272644027, 0.21118088668866436, 0.21061152696413302, 0.21007407460708624, 0.2095700106717637, 0.20910081621240528, 0.20866797228325085, 0.20827295993854014, 0.20791726023251295, 0.20760235421940926, 0.20732972295346877, 0.2071008474889314, 0.20691720888003684, 0.20678028818102515, 0.20669119618967904, 0.2066495626779541, 0.2066546471613488, 0.20670570915536168, 0.2068020081754915, 0.2069428037372366, 0.20712735535609564, 0.20735492254756724, 0.20762476482714984, 0.2079361417103422, 0.20828831271264261, 0.20868053734954983, 0.2091120751365624, 0.20958218558917888, 0.21009012822289785, 0.2106351625532178, 0.21121654809563725, 0.21183354436565494, 0.21248541087876924, 0.213171407150479, 0.21389079269628242, 0.2146428270316783, 0.21542676967216517, 0.21624188013324167, 0.21708741793040617, 0.2179626425791573, 0.2188668135949938, 0.21979919049341395, 0.22075903278991654, 0.2217456],
        [0.3776899948136861, 0.3766214590442998, 0.3750082214320932, 0.3728821389423718, 0.37027506854043934, 0.367218867191601, 0.3637453918611609, 0.35988649951442375, 0.35567404711669426, 0.3511398916332771, 0.34631589002947644, 0.3412338992705973, 0.3359257763219438, 0.3304233781488209, 0.32475856171653317, 0.3189631839903849, 0.3130691019356808, 0.30710817251772565, 0.3011122527018236, 0.2951131994532796, 0.2891428697373981, 0.2832331205194837, 0.27741580876484107, 0.2717227914387745, 0.26618592550658876, 0.2608370679335885, 0.255708075685078, 0.25083080572636224, 0.2462371150227455, 0.24195886053953253, 0.23802789924202772, 0.23446691017082852, 0.23126186066770357, 0.22838954014971388, 0.22582673803392098, 0.22355024373738597, 0.22153684667717022, 0.21976333627033498, 0.2182065019339415, 0.21684313308505118, 0.21565001914072507, 0.21460394951802467, 0.2136817136340112, 0.21286010090574578, 0.21211590075028994, 0.2114259025847048, 0.21077099178195277, 0.21014843753860088, 0.20955960500711707, 0.2090058593399692, 0.20848856568962565, 0.20800908920855435, 0.20756879504922324, 0.20716904836410036, 0.20681121430565386, 0.2064966580263517, 0.20622674467866195, 0.20600283941505257, 0.2058263073879918, 0.20569851374994735, 0.20562082365338766, 0.20559417210915856, 0.20561777356161953, 0.2056904123135075, 0.20581087266755999, 0.2059779389265142, 0.20619039539310743, 0.20644702637007684, 0.20674661616016005, 0.2070879490660941, 0.2074698093906163, 0.20789098143646392, 0.20835024950637435, 0.2088463979030848, 0.20937821092933262, 0.2099444728878551, 0.21054396808138928, 0.2111754808126728, 0.21183779538444278, 0.21252969609943645, 0.21324996726039117, 0.21399739317004424, 0.21477075813113305, 0.2155688464463947, 0.21639044241856661, 0.2172343303503859, 0.21809929454459, 0.21898411930391623, 0.21988758893110175, 0.2208084877288839, 0.2217456],
        [0.37858904678068855, 0.3774003986360889, 0.3756720060681284, 0.37343556262319605, 0.37072276184768016, 0.36756529728796994, 0.3639948624904543, 0.36004315100152173, 0.3557418563675613, 0.35112267213496173, 0.346217291850112, 0.3410574090594008, 0.3356747173092169, 0.33010091014594917, 0.3243676811159866, 0.3185067237657177, 0.31254973164153155, 0.306528398289817, 0.3004744172569627, 0.29441948208935753, 0.28839528633339034, 0.28243352353544987, 0.2765658872419252, 0.27082407099920475, 0.2652397683536778, 0.2598446728517329, 0.2546704780397588, 0.24974887746414456, 0.24511156467127884, 0.24079023320755052, 0.23681657661934846, 0.23321319586086062, 0.22996632151747218, 0.2270530915823673, 0.2244506440487301, 0.22213611690974505, 0.22008664815859638, 0.2182793757884682, 0.2166914377925449, 0.21529997216401073, 0.21408211689604978, 0.2130150099818465, 0.21207578941458516, 0.21124159318744984, 0.21048955929362492, 0.2097968257262946, 0.20914453704659758, 0.20852986408749058, 0.20795398424988434, 0.20741807493469, 0.2069233135428186, 0.20647087747518114, 0.20606194413268858, 0.20569769091625192, 0.20537929522678214, 0.20510793446519035, 0.20488478603238744, 0.20471102732928456, 0.20458783575679257, 0.2045163887158225, 0.20449786360728547, 0.2045329694944089, 0.20462054208968716, 0.20475894876793088, 0.2049465569039509, 0.2051817338725579, 0.20546284704856266, 0.20578826380677595, 0.20615635152200862, 0.20656547756907134, 0.20701400932277497, 0.20750031415793005, 0.20802275944934764, 0.20857971257183833, 0.2091695409002129, 0.20979061180928216, 0.21044129267385686, 0.21111995086874769, 0.2118249537687655, 0.212554668748721, 0.21330746318342506, 0.2140817044476883, 0.21487575991632152, 0.21568799696413563, 0.21651678296594126, 0.2173604852965492, 0.21821747133077016, 0.21908610844341497, 0.21996476400929435, 0.22085180540321908, 0.2217456],
        [0.37941182450221783, 0.378108670690857, 0.3762705689743155, 0.3739290480240495, 0.37111563651151475, 0.36786186310816726, 0.364199256485463, 0.36015934531485766, 0.35577365826780744, 0.3510737240157683, 0.34609107123019606, 0.34085722858254663, 0.3354037247442761, 0.3297620883868401, 0.3239638481816948, 0.3180405328002962, 0.31202367091409994, 0.3059447911945622, 0.29983542231313887, 0.2937270929412858, 0.28765133175045904, 0.28163966741211444, 0.27572362859770794, 0.2699347439786955, 0.26430454222653305, 0.25886455201267666, 0.2536463020085819, 0.2486813208857051, 0.2440011373155019, 0.23963727996942838, 0.2356212775189405, 0.2319756574992603, 0.22868694290067512, 0.2257326555772384, 0.2230903173830034, 0.22073745017202367, 0.2186515757983527, 0.21681021611604387, 0.21519089297915062, 0.21377112824172625, 0.21252844375782445, 0.2114403613814985, 0.21048440296680188, 0.20963809036778805, 0.20887894543851027, 0.20818449003302225, 0.20753614730207243, 0.20693094558319025, 0.20636981451060007, 0.2058536837185266, 0.20538348284119437, 0.20496014151282774, 0.20458458936765153, 0.20425775603988988, 0.20398057116376775, 0.20375396437350932, 0.2035788653033393, 0.2034562035874822, 0.20338690886016253, 0.20337191075560476, 0.20341213890803356, 0.20350803537468315, 0.20365809190482764, 0.20386031267075072, 0.20411270184473626, 0.20441326359906797, 0.2047600021060298, 0.20515092153790535, 0.20558402606697848, 0.20605731986553322, 0.20656880710585304, 0.20711649196022194, 0.20769837860092363, 0.20831247120024196, 0.20895677393046072, 0.2096292909638637, 0.21032802647273474, 0.21105098462935756, 0.211796169606016, 0.21256158557499397, 0.21334523670857505, 0.2141451271790432, 0.21495926115868214, 0.2157856428197758, 0.21662227633460787, 0.21746716587546214, 0.21831831561462245, 0.21917372972437263, 0.22003141237699633, 0.22088936774477755, 0.2217456],
        [0.3801581602028214, 0.3787462336472837, 0.376803950016795, 0.3743626754387581, 0.37145377604057594, 0.36810861794965116, 0.36435856729338684, 0.3602349901991857, 0.35576925279445054, 0.35099272120658437, 0.3459367615629902, 0.34063273999107063, 0.33511202261822837, 0.3294059755718666, 0.323545964979388, 0.31756335696819554, 0.31148951766569183, 0.30535581319928, 0.29919360969636283, 0.29303427328434306, 0.28690917009062367, 0.28084966624260754, 0.27488712786769737, 0.2690529210932961, 0.2633784120468066, 0.2578949668556318, 0.25263395164717445, 0.24762673254883738, 0.24290467568802349, 0.2384991471921356, 0.23444151318857662, 0.23075423364407965, 0.2274241438826992, 0.2244291730678197, 0.22174725036282608, 0.2193563049311029, 0.21723426593603481, 0.2153590625410065, 0.21370862390940268, 0.212260879204608, 0.21099375759000716, 0.20988518822898475, 0.20891310028492566, 0.20805542292121437, 0.2072900853012355, 0.2065950165883739, 0.20595193003329412, 0.20535767523578072, 0.2048128858828979, 0.20431819566171025, 0.2038742382592821, 0.20348164736267804, 0.20314105665896226, 0.2028530998351992, 0.20261841057845342, 0.20243762257578923, 0.20231136951427103, 0.20224028508096328, 0.20222500296293044, 0.20226615684723676, 0.2023643804209469, 0.20251981677923447, 0.20273064664971135, 0.20299456016809883, 0.2033092474701179, 0.20367239869148998, 0.20408170396793604, 0.20453485343517744, 0.20502953722893544, 0.20556344548493108, 0.20613426833888565, 0.2067396959265203, 0.20737741838355633, 0.20804512584571483, 0.20874050844871714, 0.2094612563282843, 0.2102050596201376, 0.2109696084599982, 0.2117525929835873, 0.2125517033266262, 0.21336462962483602, 0.21418906201393798, 0.2150226906296532, 0.21586320560770303, 0.21670829708380873, 0.2175556551936912, 0.21840297007307186, 0.21924793185767183, 0.2200882306832124, 0.22092155668541472, 0.22174559999999996],
        [0.38082788610704654, 0.3793130459440492, 0.3772721890617073, 0.37473652516114764, 0.3717372639434964, 0.3683056151098803, 0.36447278836142594, 0.36026999339925975, 0.35572843992450826, 0.3508793376382982, 0.345753896241756, 0.3403833254360082, 0.33479883492218127, 0.3290316344014019, 0.32311293357479626, 0.3170739421434913, 0.3109458698086135, 0.3047599262712893, 0.29854732123264516, 0.2923392643938078, 0.2861669654559037, 0.28006163412005936, 0.27405448008740135, 0.26817671305905616, 0.2624595427361505, 0.25693417881981073, 0.25163183101116343, 0.24658370901133514, 0.2418210225214525, 0.2373749812426418, 0.23327679487602987, 0.22954886285337087, 0.22617834352893101, 0.223143584987604, 0.2204229353142836, 0.21799474259386373, 0.21583735491123826, 0.2139291203513009, 0.21224838699894558, 0.21077350293906602, 0.20948281625655624, 0.20835467503630978, 0.20736742736322084, 0.20649942132218294, 0.20572900499808994, 0.20503452647583592, 0.2043979927251799, 0.20381604625534305, 0.2032889884604117, 0.2028171207344723, 0.20240074447161152, 0.2020401610659156, 0.20173567191147113, 0.20148757840236448, 0.20129618193268223, 0.20116178389651065, 0.20108468568793633, 0.20106518870104567, 0.2011035943299252, 0.20120020396866128, 0.20135531901134052, 0.2015687607373161, 0.20183842996700901, 0.20216174740610693, 0.20253613376029775, 0.20295900973526917, 0.20342779603670905, 0.20393991337030504, 0.20449278244174499, 0.2050838239567167, 0.2057104586209079, 0.20637010714000634, 0.2070601902196999, 0.20777812856567618, 0.20852134288362312, 0.20928725387922847, 0.21007328225817995, 0.21087684872616533, 0.21169537398887234, 0.21252627875198893, 0.21336698372120275, 0.21421490960220152, 0.21506747710067314, 0.2159221069223054, 0.21677621977278597, 0.21762723635780265, 0.21847257738304318, 0.2193096635541955, 0.22013591557694714, 0.2209487541569861, 0.2217456],
        [0.3814208344394406, 0.37980906601983316, 0.3776753259751927, 0.3750506774850432, 0.37196618372890866, 0.36845290788631296, 0.36454191313678, 0.36026426265983386, 0.3556510196349982, 0.3507332472417972, 0.34554200865975493, 0.34010836706839503, 0.3344633856472415, 0.3286381275758184, 0.3226636560336496, 0.3165710342002591, 0.3103913252551706, 0.3041555923779086, 0.2978948987479965, 0.2916403075449584, 0.2854228819483184, 0.27927368513760015, 0.2732237802923277, 0.2673042305920252, 0.26154609921621647, 0.2559804493444254, 0.2506383441561758, 0.2455508468309919, 0.24074902054839747, 0.2362639284879165, 0.23212663382907295, 0.22835948368518602, 0.22494996090475738, 0.22187683227008356, 0.21911886456346125, 0.21665482456718743, 0.2144634790635586, 0.21252359483487165, 0.21081393866342338, 0.20931327733151048, 0.2080003776214297, 0.20685400631547776, 0.20585293019595163, 0.20497591604514784, 0.20420173064536315, 0.2035091407788944, 0.20288044286264664, 0.20231205185195805, 0.20180391233677505, 0.20135596890704405, 0.2009681661527117, 0.2006404486637243, 0.20037276103002838, 0.20016504784157033, 0.20001725368829676, 0.19992932316015402, 0.19990120084708854, 0.19993283133904693, 0.20002415922597555, 0.20017512909782076, 0.20038568554452935, 0.20065531427818106, 0.20098166549939084, 0.20136193053090692, 0.2017933006954776, 0.20227296731585118, 0.20279812171477607, 0.20336595521500045, 0.20397365913927287, 0.2046184248103415, 0.20529744355095475, 0.20600790668386085, 0.20674700553180816, 0.20751193141754498, 0.2082998756638198, 0.2091080295933808, 0.2099335845289762, 0.2107737317933545, 0.21162566270926406, 0.21248656859945306, 0.21335364078666977, 0.21422407059366275, 0.21509504934318022, 0.2159637683579705, 0.21682741896078192, 0.21768319247436266, 0.21852828022146129, 0.219359873524826, 0.2201751637072051, 0.22097134209134703, 0.2217456],
        [0.3819368374245508, 0.3802342523133156, 0.3780134006233916, 0.375305212704271, 0.3721406189054457, 0.36855054957640765, 0.364565935066649, 0.3602177057256618, 0.35553679190293785, 0.3505541239479693, 0.34530063221024826, 0.3398072470392666, 0.3341048987845163, 0.3282245177954895, 0.322197034421678, 0.31605337901257424, 0.3098244819176697, 0.3035412734864567, 0.2972346840684273, 0.29093564401307326, 0.2846750836698868, 0.2784839333883599, 0.2723931235179845, 0.2664335844082527, 0.26063624640865646, 0.2550320398686879, 0.24965189513783873, 0.24452674256560133, 0.23968751250146753, 0.2351651352949293, 0.2309905412954788, 0.2271860346975774, 0.22373941507556508, 0.22062985584875092, 0.21783653043644435, 0.21533861225795475, 0.21311527473259134, 0.21114569127966346, 0.20940903531848035, 0.20788448026835138, 0.20655119954858583, 0.20538836657849305, 0.20437515477738236, 0.203490737564563, 0.2027142883593443, 0.20202498058103566, 0.20140538793061138, 0.20085168523570673, 0.2003634476056217, 0.19994025014965677, 0.19958166797711205, 0.19928727619728778, 0.19905664991948416, 0.1988893642530015, 0.19878499430714003, 0.19874311519119986, 0.1987633020144814, 0.19884512988628475, 0.19898817391591023, 0.19919200921265795, 0.19945621088582835, 0.1997799244310827, 0.20016057688952751, 0.20059516568863042, 0.20108068825585912, 0.2016141420186812, 0.20219252440456445, 0.20281283284097631, 0.20347206475538468, 0.20416721757525705, 0.20489528872806123, 0.2056532756412647, 0.20643817574233525, 0.20724698645874046, 0.20807670521794805, 0.2089243294474257, 0.209786856574641, 0.2106612840270616, 0.21154460923215526, 0.21243382961738952, 0.2133259426102321, 0.2142179456381506, 0.21510683612861276, 0.2159896115090863, 0.21686326920703874, 0.2177248066499377, 0.218571221265251, 0.21939951048044629, 0.22020667172299102, 0.22098970242035304, 0.2217456],
        [0.3823757272869244, 0.38058856326317625, 0.3782864528724442, 0.3755002111126563, 0.3722606529817398, 0.3685985934776228, 0.36454484759823286, 0.3601302303414977, 0.3553855567053449, 0.3503416416877023, 0.3450293002864977, 0.3394793474996586, 0.3337225983251127, 0.32778986776078795, 0.3217119708046118, 0.31551972245451204, 0.30924393770841624, 0.3029154315642524, 0.296565019019948, 0.2902235150734308, 0.2839217347226286, 0.2776904929654689, 0.27156060479987937, 0.2655628852237882, 0.25972814923512255, 0.2540872118318104, 0.24867088801177925, 0.24350999277295704, 0.23863534111327128, 0.23407774803064982, 0.2298680285230202, 0.22602845444859687, 0.22254712510674068, 0.21940359665709866, 0.2165774252593183, 0.214048167073047, 0.2117953782579321, 0.20979861497362082, 0.20803743337976063, 0.2064913896359989, 0.20514003990198285, 0.2039629403373599, 0.2029396471017774, 0.20204971635488264, 0.20127270425632293, 0.2005881669657458, 0.19997893541399112, 0.19944093961666984, 0.19897338436058545, 0.19857547443254162, 0.19824641461934184, 0.19798540970778966, 0.1977916644846887, 0.1976643837368426, 0.19760277225105477, 0.19760603481412878, 0.19767337621286832, 0.1978040012340769, 0.19799711466455813, 0.19825192129111535, 0.1985676259005525, 0.19894303822527398, 0.19937538778008942, 0.1998615090254093, 0.20039823642164423, 0.20098240442920481, 0.20161084750850153, 0.20228040011994503, 0.20298789672394602, 0.20373017178091488, 0.20450405975126235, 0.20530639509539883, 0.2061340122737351, 0.20698374574668163, 0.207852429974649, 0.20873689941804793, 0.20963398853728873, 0.2105405317927822, 0.2114533636449389, 0.21236931855416935, 0.21328523098088412, 0.2141979353854939, 0.21510426622840914, 0.21600105797004054, 0.21688514507079865, 0.21775336199109394, 0.21860254319133712, 0.21942952313193878, 0.2202311362733094, 0.22100421707585954, 0.22174559999999996],
        [0.3827373362511089, 0.38087195730809514, 0.37849452258849114, 0.3756357530040248, 0.37232636946642406, 0.3685970928874169, 0.3644786441787314, 0.3600017442520954, 0.355197114019237, 0.3500954743918841, 0.34472754628176455, 0.3391240506006067, 0.3333157082601379, 0.32733324017208676, 0.3212073672481807, 0.3149688104001481, 0.30864829053971654, 0.3022765285786144, 0.2958842454285694, 0.28950216200130946, 0.2831609992085628, 0.2768914779620572, 0.27072431917352063, 0.26469024375468103, 0.2588199726172665, 0.253144226673005, 0.24769372683362434, 0.24249919401085251, 0.2375913491164176, 0.23300091306204754, 0.2287586067594703, 0.2248866814962968, 0.22137351006367095, 0.21819899562861922, 0.21534304135816834, 0.2127855504193451, 0.21050642597917635, 0.20848557120468855, 0.20670288926290864, 0.2051382833208631, 0.20377165654557883, 0.20258291210408255, 0.20155195316340094, 0.20065868289056066, 0.19988300445258844, 0.19920482101651107, 0.19860719279770284, 0.19808580820492844, 0.19763951269530003, 0.1972671517259299, 0.19696757075393048, 0.19673961523641387, 0.19658213063049243, 0.1964939623932783, 0.19647395598188386, 0.1965209568534213, 0.19663381046500295, 0.19681136227374113, 0.19705245773674793, 0.19735594231113568, 0.19772066145401673, 0.19814510269000826, 0.19862632181374715, 0.19916101668737535, 0.19974588517303477, 0.20037762513286736, 0.20105293442901487, 0.2017685109236193, 0.20252105247882257, 0.20330725695676657, 0.20412382221959322, 0.20496744612944426, 0.20583482654846186, 0.2067226613387876, 0.20762764836256373, 0.20854648548193191, 0.20947587055903405, 0.21041250145601215, 0.21135307603500808, 0.21229429215816364, 0.21323284768762088, 0.21416544048552155, 0.21508876841400776, 0.21599952933522126, 0.21689442111130394, 0.21777014160439775, 0.21862338867664458, 0.21945086019018634, 0.22024925400716486, 0.2210152679897221, 0.2217456],
        [0.3830214965416514, 0.3810843928867521, 0.3786376496376723, 0.3757119186722021, 0.37233785186813084, 0.3685461011032484, 0.3643673182553446, 0.3598321552022091, 0.35497126382163174, 0.3498152959914025, 0.3443949035893105, 0.33874073849314623, 0.3328834525806991, 0.3268536977297587, 0.320682125818115, 0.3143993887235578, 0.30803613832387655, 0.3016230264968614, 0.29519070512030193, 0.28876982607198787, 0.282391041229709, 0.2760850024712551, 0.26988236167441587, 0.26381377071698103, 0.25790988147674043, 0.25220134583148385, 0.24671881565900092, 0.24149294283708148, 0.23655437924351536, 0.23193377675609203, 0.22766178725260164, 0.22376065439872916, 0.2202189890117426, 0.21701699369680505, 0.21413487105907983, 0.2115528237037303, 0.20925105423591966, 0.20720976526081125, 0.20540915938356824, 0.20382943920935412, 0.20245080734333204, 0.20125346639066533, 0.2002176189565173, 0.1993234676460511, 0.19855121506443016, 0.19788106381681778, 0.19729626756666352, 0.19679228421056333, 0.19636762270339908, 0.196020792000053, 0.1957503010554073, 0.195554658824344, 0.19543237426174528, 0.19538195632249333, 0.19540191396147022, 0.19549075613355793, 0.19564699179363884, 0.19586912989659497, 0.19615567939730852, 0.19650514925066145, 0.19691604841153615, 0.1973865648545385, 0.1979136026331712, 0.19849374482066037, 0.19912357449023257, 0.19979967471511428, 0.20051862856853178, 0.20127701912371151, 0.20207142945388004, 0.20289844263226361, 0.2037546417320887, 0.20463660982658186, 0.20554092998896933, 0.20646418529247762, 0.20740295881033308, 0.20835383361576218, 0.2093133927819913, 0.21027821938224697, 0.21124489648975545, 0.21221000717774335, 0.21317013451943684, 0.21412186158806254, 0.21506177145684682, 0.21598644719901613, 0.21689247188779678, 0.21777642859641536, 0.21863490039809813, 0.21946447036607153, 0.220261721573562, 0.22102323709379604, 0.2217456],
        [0.3832280403830993, 0.38122582843782704, 0.37871587388612854, 0.37572878841101387, 0.37229518369549275, 0.36844567142257556, 0.3642108632752722, 0.35962137093659263, 0.35470780608954683, 0.349500780417145, 0.34403090560239713, 0.33832879332831306, 0.332425055277903, 0.3263503031341769, 0.32013514858014486, 0.31381020329881654, 0.3074060789732024, 0.30095338728631227, 0.2944827399211562, 0.2880247485607442, 0.28161002488808634, 0.2752691805861926, 0.26903282733807293, 0.2629315768267374, 0.2569960407351961, 0.25125683074645905, 0.24574455854353622, 0.24048983580943756, 0.23552327422717315, 0.23087548547975303, 0.22657708125018716, 0.22265031171394617, 0.21908398101634244, 0.2158585317951488, 0.2129544066881381, 0.2103520483330834, 0.20803189936775757, 0.20597440242993342, 0.20416000015738398, 0.20256913518788205, 0.20118225015920066, 0.19997978770911254, 0.19894219047539075, 0.19804990109580817, 0.19728336220813747, 0.19662301645015196, 0.19605226720579025, 0.19556636084365542, 0.19516350447851638, 0.19484190522514208, 0.1945997701983016, 0.1944353065127638, 0.1943467212832977, 0.19433222162467223, 0.19439001465165645, 0.1945183074790192, 0.1947153072215295, 0.19497922099395634, 0.19530825591106862, 0.19570061908763534, 0.19615451763842554, 0.19666787174811806, 0.19723745388103192, 0.19785974957139607, 0.19853124435343944, 0.19924842376139099, 0.20000777332947958, 0.20080577859193424, 0.20163892508298395, 0.20250369833685758, 0.2033965838877841, 0.2043140672699925, 0.20525263401771165, 0.20620876966517054, 0.2071789597465981, 0.20815968979622337, 0.20914744534827512, 0.21013871193698241, 0.2111299750965742, 0.21211772036127938, 0.21309843326532688, 0.21406859934294573, 0.2150247041283648, 0.21596323315581312, 0.21688067195951954, 0.217773506073713, 0.21863822103262257, 0.2194713023704771, 0.22026923562150558, 0.22102850631993687, 0.2217456],
        [0.38335680000000005, 0.3812962224, 0.3787292352, 0.37568644251428573, 0.3721984484571429, 0.36829585714285723, 0.3640092726857143, 0.35936929919999994, 0.35440654079999995, 0.3491516016, 0.34363508571428575, 0.3378875972571429, 0.33193974034285717, 0.3258221190857143, 0.3195653376, 0.3132, 0.3067567103999999, 0.3002660729142857, 0.2937586916571429, 0.2872651707428571, 0.2808161142857143, 0.2744421264, 0.2681738112, 0.26204177279999996, 0.25607661531428566, 0.2503089428571429, 0.24476935954285717, 0.2394884694857143, 0.2344968768, 0.22982518559999998, 0.225504, 0.22155559199999997, 0.2179689051428572, 0.2147245508571429, 0.21180314057142857, 0.2091852857142857, 0.20685159771428574, 0.20478268800000005, 0.20295916800000002, 0.20136164914285715, 0.1999707428571428, 0.19876706057142854, 0.19773121371428573, 0.19684381371428572, 0.19608547199999993, 0.1954368, 0.1948812992, 0.19441403131428575, 0.19403294811428567, 0.19373600137142855, 0.19352114285714284, 0.19338632434285713, 0.19332949760000004, 0.19334861439999998, 0.19344162651428579, 0.19360648571428574, 0.1938411437714286, 0.19414355245714288, 0.19451166354285718, 0.1949434288, 0.1954368, 0.19598947040000006, 0.19659809920000001, 0.19725908708571435, 0.1979688347428572, 0.19872374285714298, 0.19952021211428575, 0.20035464320000002, 0.2012234368, 0.20212299360000002, 0.20304971428571433, 0.20399999954285722, 0.20497025005714287, 0.2059568665142857, 0.20695624959999998, 0.20796480000000006, 0.20897891840000005, 0.20999500548571434, 0.2110094619428572, 0.2120186884571429, 0.21301908571428568, 0.21400705440000004, 0.2149789952, 0.2159313088, 0.21686039588571432, 0.2177626571428572, 0.21863449325714293, 0.21947230491428577, 0.22027249280000002, 0.2210314576, 0.22174560000000001],
        [0.3834076076169006, 0.3812955332119506, 0.37867777344542697, 0.37558496127584334, 0.3720477296617135, 0.36809671156155127, 0.36376253993387064, 0.359075847737185, 0.35406726793000853, 0.34876743347085476, 0.34320697731823774, 0.33741653243067093, 0.3314267317666683, 0.3252682082847437, 0.31897159494341076, 0.31256752470118343, 0.30608663051657525, 0.2995595453481003, 0.29301690215427223, 0.28648933389360487, 0.280007473524612, 0.27360195400580734, 0.26730340829570476, 0.261142469352818, 0.2551497701356609, 0.24935594360274724, 0.24379162271259078, 0.2384874404237053, 0.23347402969460462, 0.22878202348380253, 0.22444205474981277, 0.22047643381494264, 0.21687418045667345, 0.2136159918162798, 0.2106825650350364, 0.20805459725421818, 0.20571278561509956, 0.20363782725895538, 0.20181041932706037, 0.20021125896068928, 0.19882104330111675, 0.19762046948961753, 0.1965902346674663, 0.1957110359759379, 0.19496357055630686, 0.194328535549848, 0.19378947103420968, 0.19334128883253504, 0.1929817437043407, 0.1927085904091435, 0.1925195837064602, 0.19241247835580755, 0.19238502911670222, 0.19243499074866102, 0.19256011801120065, 0.19275816566383788, 0.1930268884660895, 0.19336404117747225, 0.1937673785575028, 0.1942346553656979, 0.1947636263615745, 0.19535180783943748, 0.19599576223274584, 0.19669181350974682, 0.1974362856386876, 0.1982255025878154, 0.1990557883253776, 0.1999234668196213, 0.20082486203879385, 0.20175629795114242, 0.2027140985249143, 0.20369458772835672, 0.20469408952971696, 0.20570892789724213, 0.2067354267991796, 0.20776991020377675, 0.20880870207928046, 0.20984812639393824, 0.21088450711599727, 0.21191416821370482, 0.21293343365530806, 0.21393862740905428, 0.21492607344319073, 0.2158920957259647, 0.2168330182256234, 0.21774516491041399, 0.21862485974858384, 0.2194684267083801, 0.22027218975805007, 0.2210324728658409, 0.22174560000000001],
        [0.3833802954583485, 0.38122371931235893, 0.37856152848854985, 0.37542442498951234, 0.37184311081783755, 0.36784828797611674, 0.36347065846694115, 0.35874092429290194, 0.35368978745659024, 0.3483479499605975, 0.3427461138075147, 0.33691498099993317, 0.3308852535404438, 0.32468763343163815, 0.3183528226761072, 0.3119115232764422, 0.3053944372352344, 0.298832266555075, 0.29225571323855515, 0.2856954792882661, 0.2791822667067989, 0.27274677749674486, 0.2664197136606952, 0.2602317772012412, 0.25421367012097384, 0.24839609442248448, 0.2428097521083642, 0.2374853451812042, 0.2324535756435958, 0.22774514549813016, 0.2233907567473984, 0.21941277571682635, 0.2158002260231781, 0.2125337956060521, 0.2095941724050471, 0.20696204435976176, 0.20461809940979464, 0.20254302549474432, 0.2007175105542095, 0.19912224252778862, 0.1977379093550806, 0.19654519897568376, 0.19552479932919697, 0.19465739835521867, 0.19392368399334753, 0.19330434418318224, 0.19278289019333636, 0.19235412660848428, 0.19201568134231517, 0.19176518230851833, 0.1916002574207831, 0.1915185345927988, 0.19151764173825467, 0.19159520677084002, 0.19174885760424415, 0.19197622215215632, 0.19227492832826584, 0.19264260404626218, 0.19307687721983438, 0.19357537576267184, 0.1941357275884639, 0.1947553310956837, 0.19543066662194, 0.1961579849896254, 0.19693353702113253, 0.19775357353885406, 0.19861434536518252, 0.19951210332251068, 0.20044309823323112, 0.2014035809197364, 0.20238980220441924, 0.20339801290967213, 0.20442446385788784, 0.20546540587145892, 0.20651708977277808, 0.2075757663842379, 0.20863768652823092, 0.20969910102714992, 0.21075626070338743, 0.21180541637933611, 0.21284281887738854, 0.21386471901993742, 0.2148673676293754, 0.21584701552809502, 0.21679991353848893, 0.2177223124829498, 0.21861046318387023, 0.21946061646364284, 0.22026902314466018, 0.2210319340493151, 0.22174560000000001],
        [0.383274695748891, 0.38108073913990487, 0.3783805401955088, 0.3752049139491181, 0.37158467543414736, 0.36755063968401164, 0.3631336217321257, 0.3583644366119044, 0.3532738993567628, 0.34789282500011576, 0.3422520285753781, 0.3363823251159647, 0.33031452965529057, 0.3240794572267704, 0.31770792286381927, 0.311230741599852, 0.30467872846828326, 0.29808269850252833, 0.291473466736002, 0.284881848202119, 0.27833865793429424, 0.2718747109659427, 0.2655208223304793, 0.25930780706131884, 0.2532664801918763, 0.24742765675556647, 0.2418221517858043, 0.23648078031600464, 0.2314343573795824, 0.22671369800995245, 0.22234961724052976, 0.2183645562637031, 0.2147474609077577, 0.2114789031599522, 0.2085394550075459, 0.20590968843779764, 0.20357017543796646, 0.2015014879953114, 0.19968419809709131, 0.19809887773056542, 0.19672609888299253, 0.19554643354163165, 0.1945404536937419, 0.19368873132658218, 0.19297183842741147, 0.19237034698348884, 0.19186766416229703, 0.1914585378522144, 0.19114055112184278, 0.19091128703978424, 0.19076832867464086, 0.19070925909501463, 0.1907316613695075, 0.19083311856672167, 0.191011213755259, 0.19126353000372148, 0.19158765038071127, 0.1919811579548303, 0.19244163579468065, 0.19296666696886425, 0.19355383454598327, 0.19420048719799177, 0.19490303601025288, 0.1956576576714818, 0.19646052887039378, 0.1973078262957041, 0.19819572663612803, 0.19912040658038066, 0.2000780428171774, 0.2010648120352335, 0.20207689092326395, 0.20311045616998427, 0.20416168446410965, 0.2052267524943552, 0.20630183694943632, 0.20738311451806818, 0.20846676188896598, 0.20954895575084506, 0.2106258727924206, 0.21169368970240784, 0.212748583169522, 0.2137867298824784, 0.21480430652999222, 0.21579748980077879, 0.21676245638355324, 0.21769538296703086, 0.2185924462399269, 0.2194498228909566, 0.22026368960883516, 0.2210302230822779, 0.22174560000000001],
        [0.3830906407130755, 0.3808665511332682, 0.3781348484324446, 0.3749265084484867, 0.371272507019276, 0.3672038199826946, 0.3627514231766243, 0.3579462924389467, 0.3528194036075439, 0.3474017325202975, 0.3417242550150895, 0.33581794692980177, 0.32971378410231583, 0.32344274237051374, 0.3170357975722771, 0.3105239255454881, 0.3039381021280281, 0.29730930315777937, 0.2906685044726234, 0.28404668191044213, 0.2774748113091175, 0.27098386850653106, 0.26460482934056495, 0.25836866964910066, 0.2523063652700203, 0.24644889204120557, 0.24082722580053822, 0.23547234238590017, 0.23041521763517317, 0.22568682738623908, 0.22131814747697975, 0.21733171401362525, 0.2137163041757991, 0.21045225541147275, 0.20751990516861815, 0.2048995908952069, 0.20257165003921074, 0.20051642004860132, 0.19871423837135044, 0.19714544245542961, 0.19579036974881073, 0.19462935769946543, 0.19364274375536542, 0.19281086536448247, 0.19211405997478803, 0.19153266503425415, 0.19104990042600878, 0.19066051577380633, 0.1903621431365573, 0.19015241457317258, 0.19002896214256285, 0.18998941790363885, 0.19003141391531123, 0.19015258223649073, 0.19035055492608813, 0.19062296404301404, 0.19096744164617926, 0.19138161979449458, 0.19186313054687051, 0.1924096059622179, 0.19301867809944756, 0.19368772317561492, 0.194413094040355, 0.19519088770144785, 0.19601720116667323, 0.19688813144381115, 0.19779977554064135, 0.19874823046494378, 0.19972959322449843, 0.20073996082708512, 0.20177543028048375, 0.20283209859247417, 0.2039060627708363, 0.20499341982335015, 0.20609026675779543, 0.20719270058195216, 0.20829681830360014, 0.2093987169305194, 0.2104944934704897, 0.211580244931291, 0.21265206832070316, 0.21370606064650607, 0.21473831891647968, 0.2157449401384039, 0.21672202132005858, 0.21766565946922356, 0.21857195159367873, 0.21943699470120415, 0.22025688579957953, 0.22102772189658487, 0.22174560000000001],
        [0.38282796257544915, 0.3805811137311289, 0.3778244930654972, 0.3745892887814433, 0.3709066890818558, 0.36680788216962407, 0.3623240562476366, 0.3574863995187825, 0.3523261001859509, 0.3468743464520305, 0.34116232651991035, 0.33522122859247944, 0.32908224087262644, 0.32277655156324064, 0.3163353488672108, 0.3097898209874258, 0.3031711561267747, 0.2965105424881464, 0.2898391682744299, 0.283188221688514, 0.27658889093328776, 0.27007236421164005, 0.26366982972645986, 0.2574124756806361, 0.2513314902770577, 0.24545806171861373, 0.2398233782081929, 0.23445862794868438, 0.22939499914297692, 0.22466367999395953, 0.22029585870452126, 0.21631418752464476, 0.21270717489268892, 0.20945479329410616, 0.2065370152143492, 0.20393381313887057, 0.2016251595531229, 0.19959102694255873, 0.1978113877926307, 0.19626621458879143, 0.19493547981649342, 0.19379915596118938, 0.19283721550833186, 0.1920296309433734, 0.19135637475176667, 0.19079741941896428, 0.1903357064693885, 0.18996605358334087, 0.1896862474800925, 0.18949407487891454, 0.1893873224990784, 0.18936377705985505, 0.1894212252805158, 0.18955745388033182, 0.18977024957857425, 0.19005739909451433, 0.19041668914742335, 0.1908459064565724, 0.19134283774123265, 0.1919052697206753, 0.1925309891141717, 0.19321748605780625, 0.19396106435491697, 0.19475773122565535, 0.19560349389017267, 0.19649435956862038, 0.1974263354811499, 0.19839542884791253, 0.19939764688905975, 0.20042899682474288, 0.20148548587511345, 0.2025631212603226, 0.20365791020052187, 0.2047658599158627, 0.20588297762649635, 0.20700527055257434, 0.2081287459142479, 0.20924941093166857, 0.21036327282498765, 0.21146633881435656, 0.21255461611992668, 0.2136241119618494, 0.21467083356027605, 0.2156907881353582, 0.21667998290724702, 0.2176344250960941, 0.2185501219220506, 0.21942308060526816, 0.22024930836589784, 0.2210248124240914, 0.2217456],
        [0.3824864935605593, 0.3802243853721668, 0.37744951396080717, 0.3741933352418138, 0.3704873051305198, 0.3663628795422585, 0.36185151439236274, 0.35698466559616615, 0.3517937890690016, 0.3463103407262026, 0.3405657764831022, 0.33459155225503356, 0.3284191239573299, 0.3220799475053244, 0.31560547881435036, 0.3090271737997409, 0.3023764883768292, 0.2956848784609485, 0.28898379996743206, 0.2823047088116129, 0.2756790609088245, 0.26913831217439976, 0.2627139185236721, 0.2564373358719746, 0.25034002013464063, 0.2444534272270032, 0.23880901306439553, 0.2334382335621509, 0.22837254463560247, 0.22364340220008347, 0.21928226217092708, 0.21531191535481384, 0.211720492123814, 0.20848745774134503, 0.20559227747082434, 0.20301441657566965, 0.2007333403192985, 0.19872851396512828, 0.1969794027765765, 0.19546547201706085, 0.1941661869499988, 0.19306101283880778, 0.19212941494690547, 0.19135085853770928, 0.19070480887463673, 0.1901707312211055, 0.18973118977735323, 0.18938114449089902, 0.18911865424608204, 0.1889417779272415, 0.18884857441871677, 0.188837102604847, 0.18890542136997157, 0.1890515895984296, 0.18927366617456037, 0.18956970998270312, 0.18993777990719712, 0.19037593483238163, 0.19088223364259588, 0.1914547352221791, 0.1920914984554707, 0.19279022287381892, 0.19354717059660917, 0.19435824439023597, 0.1952193470210939, 0.19612638125557738, 0.1970752498600811, 0.19806185560099948, 0.19908210124472708, 0.20013188955765843, 0.2012071233061881, 0.20230370525671054, 0.20341753817562036, 0.2045445248293121, 0.20568056798418016, 0.20682157040661928, 0.20796343486302377, 0.2091020641197883, 0.2102333609433074, 0.21135322809997556, 0.2124575683561873, 0.21354228447833717, 0.21460327923281966, 0.2156364553860295, 0.21663771570436097, 0.21760296295420872, 0.21852809990196725, 0.21940902931403117, 0.22024165395679485, 0.22102187659665296, 0.2217456],
        [0.38206606589295333, 0.3797963244950618, 0.37700995098451473, 0.37373872812342385, 0.3700144386739004, 0.3658688653980562, 0.36133379105800256, 0.35644099841585125, 0.3512222702337137, 0.3457093892737016, 0.3399341382979264, 0.33392830006849966, 0.32772365734753295, 0.3213519928971379, 0.31484508947942585, 0.3082347298565086, 0.3015526967904975, 0.29483077304350425, 0.2881007413776404, 0.2813943845550175, 0.274743485337747, 0.2681798264879405, 0.2617351907677097, 0.25544136093916586, 0.24933011976442085, 0.24343325000558605, 0.237782534424773, 0.23240975578409337, 0.22734669684565864, 0.22262514037158032, 0.2182768691239701, 0.21432483606218453, 0.210756674934561, 0.2075511896866816, 0.20468718426412896, 0.2021434626124853, 0.1998988286773331, 0.19793208640425453, 0.19622203973883215, 0.19474749262664812, 0.19348724901328496, 0.19242011284432495, 0.19152488806535053, 0.190780378621944, 0.1901653884596876, 0.18965872152416396, 0.18924245783481994, 0.18891178170656164, 0.18866515352815966, 0.18850103368838467, 0.1884178825760074, 0.18841416057979857, 0.18848832808852875, 0.18863884549096874, 0.1888641731758892, 0.1891627715320607, 0.18953310094825412, 0.18997362181324, 0.19048279451578906, 0.19105907944467193, 0.19170093698865948, 0.19240638065290608, 0.19317163640810212, 0.19399248334132158, 0.1948647005396387, 0.19578406709012758, 0.19674636207986235, 0.1977473645959171, 0.198782853725366, 0.19984860855528325, 0.20094040817274286, 0.20205403166481897, 0.2031852581185858, 0.2043298666211174, 0.2054836362594879, 0.20664234612077154, 0.20780177529204227, 0.2089577028603744, 0.21010590791284187, 0.21124216953651898, 0.21236226681847975, 0.2134619788457984, 0.21453708470554894, 0.21558336348480572, 0.2165965942706426, 0.21757255615013388, 0.21850702821035362, 0.21939578953837596, 0.22023461922127502, 0.221019296346125, 0.22174559999999993],
        [0.38156651179717854, 0.37929688953849394, 0.37650584400276055, 0.373225547720099, 0.3694881732206304, 0.36532589303447577, 0.36077087969175603, 0.355855305722592, 0.3506113436571047, 0.34507116602541527, 0.33926694535764457, 0.33323085418391346, 0.32699506503434295, 0.32059175043905397, 0.31405308292816747, 0.3074112350318044, 0.30069837928008586, 0.2939466882031326, 0.2871883343310657, 0.28045549019400606, 0.2737803283220746, 0.2671950212453923, 0.2607317414940803, 0.25442266159825927, 0.24829995408805036, 0.2423957914935745, 0.2367423463449525, 0.23137179117230547, 0.22631629850575427, 0.2216080408754199, 0.21727919081142336, 0.2133528882048091, 0.20981614239031665, 0.2066469300636088, 0.2038232279203484, 0.20132301265619862, 0.19912426096682231, 0.1972049495478823, 0.1955430550950417, 0.19411655430396332, 0.19290342387031023, 0.19188164048974524, 0.19102918085793147, 0.19032402167053164, 0.18974413962320885, 0.189267511411626, 0.18887561812670575, 0.18856395844040974, 0.18833153541995915, 0.1881773521325753, 0.18810041164547966, 0.18809971702589331, 0.18817427134103773, 0.18832307765813405, 0.18854513904440368, 0.18883945856706782, 0.18920503929334795, 0.18964088429046524, 0.190145996625641, 0.1907193793660965, 0.19136003557905315, 0.1920664064243211, 0.1928346854320664, 0.19366050422504405, 0.19453949442600907, 0.19546728765771643, 0.19643951554292108, 0.19745180970437803, 0.19849980176484233, 0.1995791233470689, 0.20068540607381274, 0.20181428156782882, 0.2029613814518722, 0.2041223373486978, 0.20529278088106065, 0.20646834367171574, 0.207644657343418, 0.20881735351892247, 0.20998206382098408, 0.21113441987235793, 0.21227005329579887, 0.213384595714062, 0.21447367874990225, 0.21553293402607468, 0.21655799316533417, 0.21754448779043578, 0.2184880495241345, 0.21938430998918534, 0.22022890080834312, 0.22101745360436303, 0.2217456],
        [0.3809876634977822, 0.37872603894114304, 0.3759372328816845, 0.3726538743256649, 0.3689085922793424, 0.3647340157489756, 0.36016277374082284, 0.3552274952611423, 0.3499608093161925, 0.3443953449122316, 0.33856373105551824, 0.3324985967523106, 0.3262325710088669, 0.3197982828314457, 0.31322836122630526, 0.3065554351997039, 0.2998121337579, 0.29303108590715204, 0.2862449206537183, 0.27948626700385704, 0.27278775396382665, 0.26618201053988555, 0.259701665738292, 0.2533793485653044, 0.24724768802718117, 0.24133931313018056, 0.23568685288056093, 0.23032293628458067, 0.2252801923484981, 0.2205912500785716, 0.21628873848105953, 0.21239601034073963, 0.20889931355646774, 0.20577561980561876, 0.203001900765568, 0.20055512811369053, 0.19841227352736157, 0.19655030868395615, 0.19494620526084944, 0.19357693493541656, 0.19241946938503268, 0.19145078028707288, 0.1906478393189124, 0.18998761815792634, 0.18944708848148967, 0.18900322196697775, 0.18863677813792756, 0.1883436679025241, 0.1881235900151142, 0.1879762432300448, 0.18790132630166276, 0.18789853798431505, 0.1879675770323485, 0.18810814220011007, 0.18831993224194657, 0.18860264591220496, 0.18895598196523208, 0.18937963915537498, 0.18987331623698045, 0.19043671196439524, 0.19106952509196654, 0.19177074721731688, 0.1925365413111724, 0.19336236318753502, 0.19424366866040665, 0.19517591354378921, 0.19615455365168458, 0.19717504479809467, 0.19823284279702147, 0.19932340346246688, 0.20044218260843272, 0.201584636048921, 0.20274621959793357, 0.20392238906947235, 0.2051086002775393, 0.2063003090361364, 0.20749297115926532, 0.2086820424609282, 0.20986297875512686, 0.21103123585586325, 0.21218226957713926, 0.2133115357329568, 0.21441449013731778, 0.21548658860422423, 0.2165232869476779, 0.21752004098168076, 0.21847230652023472, 0.21937553937734175, 0.22022519536700363, 0.22101673030322244, 0.22174560000000004],
        [0.38032935321931155, 0.37808373114168886, 0.3753041574874272, 0.37202378823394705, 0.36827577935866923, 0.36409328683901426, 0.35950946665240296, 0.3545574747762561, 0.3492704671879942, 0.34368159986503827, 0.33782402878480866, 0.33173090992472626, 0.3254353992622117, 0.31897065277468584, 0.31236982643956906, 0.30566607623428227, 0.29889255813624616, 0.29208242812288143, 0.2852688421716088, 0.2784849562598488, 0.2717639263650224, 0.26513890846455007, 0.2586430585358526, 0.2523095325563507, 0.24617148650346507, 0.24026207635461638, 0.23461445808722534, 0.22926178767871258, 0.22423722110649894, 0.219573914348005, 0.21530502338065155, 0.21145414102802818, 0.2080066074984008, 0.20493819984620418, 0.20222469512587302, 0.19984187039184217, 0.1977655026985465, 0.19597136910042062, 0.1944352466518995, 0.19313291240741787, 0.19204014342141046, 0.19113271674831214, 0.19038640944255772, 0.18977699855858193, 0.18928026115081953, 0.18887197427370542, 0.18853204535340234, 0.1882569033029857, 0.18804710740725855, 0.18790321695102422, 0.18782579121908613, 0.1878153894962474, 0.18787257106731145, 0.18799789521708146, 0.18819192123036074, 0.18845520839195248, 0.18878831598666018, 0.18919180329928692, 0.18966622961463608, 0.19021215421751086, 0.19083013639271462, 0.1915198500611467, 0.19227742768809067, 0.19309811637492633, 0.19397716322303332, 0.1949098153337914, 0.19589131980858024, 0.1969169237487796, 0.1979818742557692, 0.19908141843092866, 0.2002108033756378, 0.20136527619127628, 0.20254008397922382, 0.20373047384086015, 0.2049316928775649, 0.20613898819071794, 0.20734760688169881, 0.20855279605188734, 0.20974980280266314, 0.21093387423540605, 0.2121002574514957, 0.21324419955231172, 0.21436094763923397, 0.21544574881364215, 0.21649385017691597, 0.21750049883043504, 0.21846094187557916, 0.219370426413728, 0.22022419954626124, 0.2210175083745587, 0.22174560000000001],
        [0.3795914131863139, 0.37736992457881147, 0.374606657686129, 0.3713353697387713, 0.3675898179672432, 0.36340375960204996, 0.35881095187369644, 0.3538451520126874, 0.3485401172495279, 0.342929604814723, 0.3370473719387776, 0.33092717585219655, 0.3246027737854848, 0.31810792296914736, 0.3114763806336892, 0.3047419040096152, 0.2979382503274303, 0.2910991768176395, 0.2842584407107478, 0.27744979923726, 0.27070700962768124, 0.2640638291125162, 0.2575540149222701, 0.2512113242874477, 0.2450695144385541, 0.23916234260609412, 0.23352356602057275, 0.22818694191249492, 0.2231862275123656, 0.21855518005068972, 0.2143275567579723, 0.21052721882472694, 0.2071384432815028, 0.2041356111188575, 0.2014931033273488, 0.19918530089753458, 0.19718658481997262, 0.19547133608522055, 0.1940139356838362, 0.1927887646063774, 0.19177020384340185, 0.19093263438546731, 0.19025043722313167, 0.1896979933469526, 0.1892496837474878, 0.1888798894152952, 0.18856752725804718, 0.18830965785187537, 0.18810787769002585, 0.187963783265745, 0.18787897107227905, 0.1878550376028742, 0.18789357935077677, 0.18799619280923296, 0.18816447447148898, 0.18840002083079113, 0.18870442838038565, 0.18907929361351888, 0.18952621302343686, 0.1900467831033859, 0.19064260034661243, 0.19131416198506362, 0.1920575682054917, 0.19286781993334973, 0.19373991809409086, 0.1946688636131684, 0.19564965741603552, 0.1966773004281453, 0.19774679357495106, 0.1988531377819059, 0.1999913339744631, 0.20115638307807573, 0.20234328601819707, 0.20354704372028026, 0.20476265710977848, 0.20598512711214506, 0.20720945465283294, 0.2084306406572955, 0.20964368605098588, 0.21084359175935724, 0.21202535870786277, 0.2131839878219557, 0.21431448002708914, 0.21541183624871643, 0.2164710574122906, 0.21748714444326495, 0.21845509826709258, 0.2193699198092267, 0.22022660999512053, 0.2210201697502272, 0.2217456],
        [0.3787736756233367, 0.37658457769119064, 0.3738447733439301, 0.370588699133963, 0.3668507916136974, 0.3626654873355414, 0.35806722285190296, 0.35309043471519014, 0.347769559477811, 0.34213903369217374, 0.3362332939106863, 0.3300867766857568, 0.32373391856979306, 0.31720915611520334, 0.31054692587439564, 0.303781664399778, 0.2969478082437583, 0.290079793958745, 0.2832120580971459, 0.27637903721136897, 0.2696151678538224, 0.2629548865769141, 0.2564326299330523, 0.25008283447464497, 0.24393993675410017, 0.2380383733238259, 0.2324125807362302, 0.22709699554372123, 0.22212605429870694, 0.21753419355359538, 0.21335584986079464, 0.20961518228888806, 0.20629523997116034, 0.20336879455707124, 0.20080861769608077, 0.1985874810376489, 0.1966781562312355, 0.19505341492630046, 0.1936860287723038, 0.1925487694187053, 0.191614408514965, 0.19085571771054277, 0.1902454686548986, 0.1897564329974924, 0.18936138238778394, 0.18903308847523337, 0.18874933133677904, 0.1885079247592741, 0.18831169095704997, 0.18816345214443836, 0.18806603053577095, 0.1880222483453792, 0.18803492778759476, 0.18810689107674924, 0.18824096042717425, 0.18843995805320138, 0.1887067061691622, 0.1890440269893884, 0.1894547427282115, 0.18994167559996314, 0.19050764781897495, 0.19115413001832102, 0.19187718650604602, 0.19267153000893703, 0.1935318732537812, 0.19445292896736577, 0.19542940987647778, 0.19645602870790435, 0.19752749818843282, 0.1986385310448502, 0.1997838400039436, 0.2009581377925003, 0.20215613713730735, 0.20337255076515193, 0.20460209140282115, 0.2058394717771023, 0.20707940461478236, 0.20831660264264856, 0.20954577858748802, 0.21076164517608795, 0.21195891513523546, 0.2131323011917176, 0.2142765160723217, 0.21538627250383485, 0.21645628321304416, 0.21748126092673678, 0.2184559183716999, 0.21937496827472064, 0.2202331233625861, 0.22102509636208353, 0.22174560000000004],
        [0.37787597275492707, 0.3757276489175063, 0.3730185443269709, 0.36978385671334796, 0.3660587838066642, 0.36187852333694664, 0.3572782730342224, 0.35229323062851825, 0.34695859384986116, 0.3413095604282783, 0.33538132809379645, 0.32920909457644254, 0.32282805760624356, 0.3162734149132266, 0.30958036422741836, 0.3027841032788461, 0.29591982979753645, 0.28902274151351665, 0.28212803615681353, 0.2752709114574541, 0.2684865651454652, 0.26181019495087393, 0.2552769986037072, 0.24892217383399196, 0.2427809183717552, 0.23688842994702383, 0.23127990628982475, 0.22599054513018507, 0.22105554419813161, 0.21651010122369144, 0.21238941393689142, 0.20871796997856357, 0.2054774166327601, 0.2026386910943379, 0.20017273055815413, 0.19805047221906605, 0.19624285327193064, 0.19472081091160498, 0.1934552823329463, 0.19241720473081161, 0.19157751530005804, 0.1909071512355427, 0.19037704973212277, 0.18995814798465527, 0.1896213831879973, 0.18933769253700602, 0.18908356507451488, 0.18885769723526266, 0.18866433730196452, 0.18850773355733555, 0.18839213428409102, 0.18832178776494596, 0.18830094228261554, 0.1883338461198149, 0.18842474755925925, 0.1885778948836636, 0.18879753637574326, 0.18908792031821334, 0.18945329499378885, 0.18989790868518497, 0.190426009675117, 0.19104020119017184, 0.19173650623242403, 0.19250930274781994, 0.19335296868230606, 0.1942618819818287, 0.1952304205923343, 0.1962529624597692, 0.19732388553007996, 0.19843756774921284, 0.19958838706311435, 0.20077072141773072, 0.20197894875900854, 0.20320744703289406, 0.2044505941853338, 0.20570276816227415, 0.20695834690966136, 0.20821170837344205, 0.20945723049956247, 0.21068929123396907, 0.21190226852260818, 0.21309054031142635, 0.21424848454636986, 0.2153704791733852, 0.21645090213841872, 0.2174841313874168, 0.21846454486632588, 0.21938652052109234, 0.22024443629766255, 0.22103267014198297, 0.2217456],
        [0.37689813680563244, 0.3747990966964384, 0.37212801050139194, 0.3689209227707518, 0.36521387805477645, 0.36104292090372464, 0.35644409586785486, 0.3514534474974258, 0.346107020342696, 0.3404408589539244, 0.3344910078813693, 0.3282935116752896, 0.3218844148859435, 0.31529976206359, 0.30857559775848764, 0.3017479665208949, 0.2948529129010705, 0.28792648144927313, 0.2810047167157613, 0.2741236632507938, 0.2673193656046291, 0.2606278683275258, 0.25408521596974265, 0.2477274530815382, 0.24159062421317115, 0.23571077391490003, 0.23012394673698344, 0.22486618722968013, 0.2199735399432486, 0.21548204942794755, 0.2114277602340356, 0.20783552045180573, 0.2046853923316888, 0.20194624166414996, 0.19958693423965432, 0.19757633584866713, 0.19588331228165362, 0.19447672932907886, 0.1933254527814081, 0.19239834842910647, 0.19166428206263922, 0.19109211947247148, 0.1906507264490685, 0.1903089687828954, 0.1900357122644173, 0.18979982268409956, 0.18957633595617177, 0.18936496848992218, 0.18917160681840334, 0.18900213747466793, 0.18886244699176874, 0.18875842190275832, 0.18869594874068946, 0.18868091403861476, 0.18871920432958691, 0.18881670614665857, 0.1889793060228825, 0.1892128904913113, 0.18952334608499763, 0.1899165593369942, 0.19039841678035374, 0.19097282252986933, 0.1916357510272963, 0.19238119429613038, 0.19320314435986727, 0.1940955932420028, 0.1950525329660326, 0.19606795555545248, 0.19713585303375827, 0.19825021742444565, 0.19940504075101034, 0.20059431503694813, 0.20181203230575476, 0.20305218458092597, 0.2043087638859575, 0.2055757622443452, 0.20684717167958466, 0.20811698421517177, 0.20937919187460213, 0.21062778668137164, 0.21185676065897596, 0.21306010583091084, 0.21423181422067206, 0.21536587785175543, 0.2164562887476566, 0.21749703893187133, 0.2184821204278954, 0.21940552525922458, 0.22026124544935455, 0.22104327302178106, 0.2217456],
        [0.37584000000000006, 0.3737988794666667, 0.3711732117333334, 0.3679999776000001, 0.3643161578666667, 0.3601587333333334, 0.3555646848000001, 0.3505709930666667, 0.34521463893333326, 0.3395326032, 0.33356186666666676, 0.32733941013333345, 0.3209022144, 0.3142872602666667, 0.3075315285333334, 0.300672, 0.2937456554666666, 0.2867894757333333, 0.2798404416, 0.2729355338666666, 0.2661117333333333, 0.2594060207999999, 0.2528553770666666, 0.24649678293333327, 0.24036721919999998, 0.23450366666666664, 0.2289431061333333, 0.2237225184, 0.21887888426666663, 0.21444918453333328, 0.21047039999999997, 0.2069677722666666, 0.20391958613333333, 0.2012923872, 0.19905272106666663, 0.1971671333333333, 0.19560216960000001, 0.19432437546666667, 0.19330029653333336, 0.19249647840000003, 0.1918794666666667, 0.19141580693333335, 0.19107204480000003, 0.19081472586666676, 0.19061039573333333, 0.19042560000000006, 0.19023375146666666, 0.19003573173333344, 0.18983928960000007, 0.18965217386666666, 0.18948213333333339, 0.18933691680000003, 0.18922427306666673, 0.1891519509333334, 0.18912769920000008, 0.18915926666666671, 0.1892544021333334, 0.18942085440000006, 0.18966637226666677, 0.18999870453333334, 0.19042560000000006, 0.1909524410666667, 0.19157514453333338, 0.19228726080000003, 0.19308234026666668, 0.19395393333333338, 0.1948955904, 0.19590086186666666, 0.19696329813333335, 0.1980764496, 0.19923386666666668, 0.20042909973333334, 0.2016556992, 0.20290721546666668, 0.20417719893333333, 0.20545920000000004, 0.20674676906666667, 0.20803345653333336, 0.2093128128, 0.2105783882666667, 0.21182373333333335, 0.2130423984, 0.2142279338666666, 0.21537389013333336, 0.2164738176, 0.21752126666666668, 0.21850978773333335, 0.21943293120000004, 0.22028424746666667, 0.22105728693333332, 0.2217456]]
        
        return spline_sit[az][alt]
    
    def splineStand(self, az, alt):
        spline_stand = [[0.45675000000000016, 0.45849193333333343, 0.4599670666666667, 0.46117954285714297, 0.46213350476190485, 0.4628330952380953, 0.4632824571428572, 0.4634857333333333, 0.4634470666666666, 0.46317059999999993, 0.4626604761904761, 0.4619208380952381, 0.46095582857142847, 0.4597695904761905, 0.4583662666666667, 0.45674999999999993, 0.4549249333333332, 0.4528952095238094, 0.45066497142857137, 0.44823836190476185, 0.44561952380952374, 0.44281259999999995, 0.43982173333333324, 0.4366510666666666, 0.4333047428571428, 0.42978690476190473, 0.42610169523809527, 0.4222532571428571, 0.41824573333333337, 0.41408326666666667, 0.40977, 0.40531211999999994, 0.40072398857142866, 0.39602201142857146, 0.3912225942857143, 0.38634214285714286, 0.3813970628571429, 0.37640376000000003, 0.3713786400000001, 0.3663381085714286, 0.36129857142857147, 0.3562764342857143, 0.35128810285714296, 0.346349982857143, 0.3414784800000001, 0.33669000000000016, 0.3319958666666668, 0.3273870761904763, 0.32284954285714296, 0.3183691809523811, 0.3139319047619049, 0.30952362857142873, 0.3051302666666668, 0.3007377333333335, 0.2963319428571431, 0.2918988095238097, 0.2874242476190478, 0.2828941714285717, 0.2782944952380954, 0.27361113333333353, 0.26883000000000024, 0.26394060000000025, 0.2589468000000002, 0.25385605714285736, 0.24867582857142873, 0.2434135714285716, 0.23807674285714303, 0.23267280000000012, 0.2272092000000001, 0.2216934000000001, 0.21613285714285727, 0.21053502857142867, 0.2049073714285715, 0.19925734285714294, 0.19359240000000008, 0.18792000000000006, 0.18224760000000007, 0.17658265714285717, 0.17093262857142857, 0.16530497142857142, 0.15970714285714288, 0.15414659999999997, 0.14863079999999995, 0.1431672, 0.13776325714285714, 0.13242642857142856, 0.12716417142857142, 0.12198394285714287, 0.1168932, 0.1118994, 0.10701000000000002],
        [0.4560783176960358, 0.4578024133537986, 0.4592631529561212, 0.46046447265894797, 0.46141030861822346, 0.4621045969898925, 0.4625512739298996, 0.4627542755941892, 0.46271753813870614, 0.462444997719395, 0.4619405904922003, 0.46120825261306697, 0.4602519202379389, 0.45907552952276137, 0.45768301662347877, 0.45607831769603563, 0.4542653688963765, 0.4522481063804463, 0.45003046630418947, 0.44761638482355026, 0.4450097980944739, 0.4422146422729047, 0.4392348535147872, 0.43607436797606597, 0.4327371218126859, 0.4292270511805914, 0.42554809223572715, 0.42170418113403757, 0.41769925403146735, 0.4135372470839613, 0.4092220964474639, 0.4047598776980606, 0.4001652240924007, 0.39545490830727403, 0.3906457030194709, 0.3857543809057816, 0.3807977146429961, 0.3757924769079045, 0.3707554403772966, 0.36570337772796285, 0.3606530616366932, 0.35562126478027795, 0.35062475983550695, 0.3456803194791706, 0.34080471638805854, 0.3360147232389613, 0.33132194501363277, 0.32671731591368247, 0.32218660244568403, 0.3177155711162106, 0.3132899884318361, 0.30889562089913386, 0.3045182350246773, 0.30014359731504003, 0.29575747427679533, 0.29134563241651695, 0.28689383824077835, 0.28238785825615276, 0.277813458969214, 0.2731564068865354, 0.2684024685146905, 0.26354099835782685, 0.2585757029103879, 0.25351387666439135, 0.24836281411185473, 0.24312980974479576, 0.23782215805523185, 0.23244715353518072, 0.22701209067665998, 0.2215242639716872, 0.21599096791227998, 0.21041949699045587, 0.2048171456982326, 0.19919120852762748, 0.19354897997065845, 0.18789775451934293, 0.18224482666569852, 0.17659749090174287, 0.1709630417194935, 0.16534877361096806, 0.15976198106818415, 0.1542099585831593, 0.1487000006479113, 0.14323940175445754, 0.1378354563948157, 0.13249545906100332, 0.1272267042450381, 0.12203648643893752, 0.11693210013471926, 0.11192083982440089, 0.10701000000000001],
        [0.45541200414461575, 0.4571132194507449, 0.4585554631724062, 0.4597424139618574, 0.46067775047135556, 0.4613651513531587, 0.4618082952595242, 0.46201086084270954, 0.46197652675497236, 0.4617089716485705, 0.4612118741757608, 0.46048891298880157, 0.4595437667399497, 0.45838011408146306, 0.45700163366559926, 0.4554120041446157, 0.45361490417076983, 0.4516140123963194, 0.449413007473522, 0.4470155680546349, 0.4444253727919158, 0.4416461003376223, 0.4386814293440119, 0.4355350384633421, 0.43221060634787056, 0.42871181164985456, 0.4250423330215518, 0.4212058491152201, 0.4172060385831166, 0.413046580077499, 0.408731152250625, 0.4042656830759605, 0.39966509781180676, 0.39494657103767367, 0.3901272773330709, 0.3852243912775082, 0.3802550874504955, 0.37523654043154253, 0.3701859248001588, 0.3651204151358544, 0.3600571860181393, 0.35501341202652276, 0.350006267740515, 0.34505292773962554, 0.34017056660336425, 0.3353763589112411, 0.33068221862674385, 0.32607901724927413, 0.32155236566221157, 0.3170878747489359, 0.312671155392827, 0.3082878184772645, 0.3039234748856282, 0.2995637355012976, 0.29519421120765266, 0.2908005128880729, 0.28636825142593836, 0.2818830377046286, 0.2773304826075232, 0.27269619701800213, 0.2679657918194449, 0.26312847130266764, 0.25818781338823055, 0.2531509894041303, 0.24802517067836308, 0.2428175285389257, 0.2375352343138147, 0.2321854593310264, 0.22677537491855754, 0.22131215240440455, 0.215802963116564, 0.21025497838303234, 0.20467536953180604, 0.19907130789088182, 0.19344996478825607, 0.18781851155192528, 0.18218411950988594, 0.1765539599901348, 0.17093520432066817, 0.16533502382948265, 0.1597605898445747, 0.15421907369394094, 0.14871764670557786, 0.143263480207482, 0.1378637455276498, 0.1325256139940779, 0.12725625693476267, 0.12206284567770082, 0.11695255155088871, 0.11193254588232295, 0.10701000000000002],
        [0.4547490187205585, 0.4564228206705611, 0.457842879576833, 0.45901257124232286, 0.45993527146997926, 0.4606143560627513, 0.46105320082358775, 0.4612551815554371, 0.46122367406124837, 0.4609620541439705, 0.4604736976065519, 0.45976198025194176, 0.45883027788308833, 0.45768196630294095, 0.45632042131444794, 0.45474901872055845, 0.4529711343242208, 0.45099014392838427, 0.4488094233359975, 0.44643234835000933, 0.4438622947733682, 0.4411026384090232, 0.43815675505992313, 0.43502802052901646, 0.4317198106192526, 0.42823550113357983, 0.4245784678749468, 0.42075208664630265, 0.4167597332505959, 0.4126047834907757, 0.4082906131697904, 0.4038229697364625, 0.3992170872231074, 0.3944905713079145, 0.38966102766907224, 0.38474606198477007, 0.37976327993319703, 0.37473028719254176, 0.3696646894409936, 0.3645840923567413, 0.35950610161797436, 0.35444832290288136, 0.34942836188965154, 0.34446382425647387, 0.3395723156815371, 0.33477144184303065, 0.3300734491901641, 0.32546914725623044, 0.3209439863455431, 0.31648341676241587, 0.3120728888111625, 0.3076978527960965, 0.30334375902153154, 0.2989960577917813, 0.29464019941115943, 0.2902616341839794, 0.28584581241455526, 0.2813781844072003, 0.27684420046622826, 0.2722293108959527, 0.26751896600068753, 0.2627022218105824, 0.2577825572591332, 0.25276705700567137, 0.247662805709529, 0.24247688803003775, 0.2372163886265296, 0.23188839215833623, 0.22649998328478968, 0.22105824666522148, 0.21557026695896375, 0.21004312882534815, 0.20448391692370657, 0.19889971591337077, 0.19329761045367264, 0.18768468520394413, 0.18206802482351683, 0.17645471397172277, 0.17085183730789366, 0.16526647949136142, 0.15970572518145776, 0.1541766590375146, 0.1486863657188637, 0.14324192988483714, 0.13785043619476642, 0.1325189693079834, 0.1272546138838202, 0.1220644545816084, 0.11695557606067987, 0.11193506298036647, 0.10701000000000004],
        [0.45408732079868186, 0.4557296860596361, 0.4571242844307124, 0.45827414897679625, 0.4591823127627727, 0.45985180885352744, 0.4602856703139463, 0.46048693020891424, 0.46045862160331663, 0.4602037775620393, 0.4597254311499676, 0.4590266154319867, 0.4581103634729823, 0.4569797083378397, 0.4556376830914444, 0.4540873207986817, 0.4523316545244373, 0.4503737173335965, 0.4482165422910448, 0.4458631624616674, 0.44331661091034996, 0.44057992070197793, 0.4376561249014367, 0.4345482565736115, 0.4312593487833883, 0.4277924345956522, 0.4241505470752884, 0.4203367192871826, 0.4163539842962203, 0.4122053751672869, 0.4078939249652678, 0.4034251712823293, 0.398814669819763, 0.3940804808061402, 0.3892406644700335, 0.38431328104001466, 0.37931639074465623, 0.3742680538125297, 0.36918633047220734, 0.3640892809522613, 0.3589949654812635, 0.35392144428778605, 0.34888677760040115, 0.34390902564768083, 0.3390062486581968, 0.33419650686052155, 0.3294923983880577, 0.3248846729935305, 0.32035861833449564, 0.31589952206850935, 0.31149267185312723, 0.3071233553459054, 0.3027768602043997, 0.298438474086166, 0.2940934846487602, 0.2897271795497381, 0.28532484644665584, 0.2808717729970693, 0.27635324685853424, 0.2717545556886063, 0.26706098714484205, 0.2622614528576311, 0.2573593603487008, 0.25236174111261256, 0.24727562664392796, 0.24210804843720815, 0.23686603798701483, 0.23155662678790914, 0.22618684633445285, 0.2207637281212071, 0.21529430364273353, 0.20978560439359345, 0.20424466186834828, 0.19867850756155947, 0.19309417296778855, 0.18749868958159677, 0.18189908889754566, 0.17630240241019668, 0.1707156616141112, 0.16514589800385063, 0.1596001430739765, 0.1540854283190501, 0.148608785233633, 0.14317724531228657, 0.13779784004957216, 0.13247760094005134, 0.12722355947828548, 0.12204274715883597, 0.11694219547626426, 0.1119289359251318, 0.10701000000000002],
        [0.45342486975380447, 0.4550322846643588, 0.4563985599953555, 0.457526351641729, 0.45841831549841366, 0.4590771074603447, 0.4595053834224563, 0.459705799279683, 0.45968101092695984, 0.4594336742592214, 0.4589664451714019, 0.45828197955843636, 0.45738293331525914, 0.4562719623368049, 0.4549517225180086, 0.4534248697538045, 0.4516940599391272, 0.4497619489689115, 0.44763119273809204, 0.44530444714160333, 0.4427843680743802, 0.4400736114313569, 0.4371748331074686, 0.43409068899764924, 0.43082383499683413, 0.42737692699995744, 0.423752620901954, 0.4199535725977583, 0.4159824379823049, 0.4118418729505288, 0.4075345333973641, 0.40306572131632395, 0.3984513230952334, 0.39370987122049544, 0.38885989817851324, 0.38391993645569, 0.37890851853842944, 0.3738441769131338, 0.3687454440662068, 0.3636308524840516, 0.3585189346530713, 0.35342822305966914, 0.34837725019024846, 0.3433845485312121, 0.33846865056896336, 0.3336480887899055, 0.328935827904589, 0.3243225615201538, 0.3197934154678868, 0.31533351557907513, 0.3109279876850061, 0.30656195761696714, 0.30222055120624475, 0.2978888942841267, 0.2935521126818996, 0.28919533223085075, 0.28480367876226764, 0.2803622781074371, 0.27585625609764625, 0.2712707385641823, 0.2665908513383326, 0.26180536741987337, 0.25691764848253856, 0.25193470336855145, 0.24686354092013518, 0.24171116997951328, 0.2364845993889085, 0.23119083799054435, 0.22583689462664408, 0.22042977813943082, 0.21497649737112798, 0.20948406116395846, 0.20395947836014575, 0.198409757801913, 0.19284190833148349, 0.18726293879108036, 0.18167985802292688, 0.17609967486924633, 0.17052939817226184, 0.16497603677419673, 0.15944659951727413, 0.15394809524371733, 0.1484875327957496, 0.14307192101559407, 0.13770826874547412, 0.13240358482761277, 0.12716487810423346, 0.12199915741755929, 0.11691343160981348, 0.1119147095232193, 0.10701000000000001],
        [0.45275962496074446, 0.4543290855311184, 0.4556645885320734, 0.4567683837135732, 0.4576427208255809, 0.4582898496180599, 0.45871201984097404, 0.4589114812442866, 0.45889048357796086, 0.45865127659196064, 0.4581961100362492, 0.45752723366079007, 0.4566468972155464, 0.455557350450482, 0.4542608431155601, 0.4527596249607445, 0.4510559457359981, 0.449152055191285, 0.44705020307656823, 0.44475263914181123, 0.4422616131369777, 0.43957937481203097, 0.43670817391693456, 0.43365026020165176, 0.4304078834161461, 0.4269832933103813, 0.42337873963432043, 0.41959647213792706, 0.41563874057116484, 0.4115077946839972, 0.4072058842263871, 0.4027380534412092, 0.3981205245429793, 0.393372314239124, 0.3885124392370698, 0.3835599162442437, 0.3785337619680721, 0.37345299311598146, 0.3683366263953988, 0.36320367851375046, 0.35807316617846324, 0.3529641060969635, 0.34789551497667814, 0.3428864095250337, 0.3379558064494568, 0.3331227224573742, 0.3284004994239223, 0.32377977989507956, 0.31924553158453356, 0.31478272220597237, 0.31037631947308425, 0.3060112910995572, 0.30167260479907904, 0.2973452282853379, 0.29301412927202203, 0.28866427547281914, 0.2842806346014174, 0.2798481743715049, 0.2753518624967698, 0.27077666669089967, 0.2661075546675832, 0.2613331684733691, 0.25645684748625147, 0.25148560541708553, 0.24642645597672636, 0.24128641287602914, 0.2360724898258489, 0.23079170053704084, 0.22545105872046017, 0.22005757808696189, 0.2146182723474013, 0.20914015521263338, 0.2036302403935134, 0.19809554160089646, 0.19254307254563763, 0.18697984693859215, 0.18141287849061502, 0.1758491809125616, 0.1702957679152868, 0.1647596532096459, 0.15924785050649393, 0.15376737351668615, 0.14832523595107763, 0.14292845152052355, 0.13758403393587895, 0.13229899690799912, 0.1270803541477391, 0.12193511936595404, 0.11687030627349908, 0.11189292858122935, 0.10701000000000001],
        [0.45208954579432004, 0.45361855770630344, 0.45492125230217717, 0.4559994496687803, 0.45685496989295177, 0.4574896330615306, 0.45790525926135595, 0.45810366857926693, 0.45808668110210227, 0.4578561169167016, 0.45741379610990346, 0.4567615387685472, 0.45590116497947153, 0.45483449482951593, 0.45356334840551904, 0.4520895457943201, 0.4504149070827581, 0.44854125235767217, 0.44647040170590147, 0.44420417521428485, 0.44174439296966145, 0.43909287505887024, 0.43625144156875023, 0.4332219125861408, 0.43000610819788077, 0.426605848490809, 0.4230229535517649, 0.4192592434675872, 0.41531653832511506, 0.4111966582111877, 0.406901423212644, 0.40243560125974753, 0.39781575165646077, 0.39306138155016995, 0.3881919980882617, 0.383227108418123, 0.3781862196871404, 0.3730888390427004, 0.36795447363218986, 0.3628026306029954, 0.3576528171025036, 0.3525245402781011, 0.34743730727717476, 0.3424106252471112, 0.3374640013352967, 0.3326169426891187, 0.3278831746302219, 0.323253295177287, 0.3187121205232533, 0.3142444668610599, 0.3098351503836463, 0.3054689872839514, 0.30113079375491464, 0.29680538598947503, 0.2924775801805721, 0.2881321925211448, 0.2837540392041325, 0.2793279364224746, 0.27483870036910985, 0.2702711472369778, 0.2656100932190178, 0.2608440589941782, 0.2559763831854448, 0.2510141089018125, 0.24596427925227668, 0.24083393734583208, 0.23563012629147415, 0.2303598891981976, 0.22503026917499774, 0.21964830933086954, 0.21422105277480807, 0.20875554261580834, 0.20325882196286557, 0.19773793392497477, 0.1921999216111309, 0.1866518281303292, 0.18110069659156458, 0.1755535701038322, 0.1700174917761271, 0.16449950471744443, 0.1590066520367791, 0.1535459768431263, 0.1481245222454811, 0.1427493313528385, 0.13742744727419368, 0.13216591311854156, 0.12697177199487727, 0.12185206701219592, 0.11681384127949253, 0.1118641379057622, 0.10701000000000001],
        [0.45141259162934955, 0.45289917023630316, 0.4541674335669778, 0.45521875398380224, 0.4560545038492047, 0.45667605552561397, 0.4570847813754584, 0.4572820537611666, 0.4572692450451671, 0.45704772758988843, 0.45661887375775895, 0.4559840559112074, 0.4551446464126621, 0.45410201762455177, 0.4528575419093046, 0.45141259162934955, 0.44976853914711473, 0.4479267568250289, 0.4458886170255206, 0.4436554921110182, 0.4412287544439503, 0.4386097763867454, 0.43579993030183195, 0.43280058855163855, 0.429613123498594, 0.4262389075051262, 0.42267931293366406, 0.41893571214663616, 0.4150094775064707, 0.4109019813755965, 0.40661459611644213, 0.40215179837470205, 0.3975304819291381, 0.39277064484177726, 0.3878922851746473, 0.3829154009897758, 0.3778599903491901, 0.3727460513149178, 0.3675935819489867, 0.362422580313424, 0.3572530444702576, 0.3521049724815146, 0.3469983624092231, 0.3419532123154103, 0.3369895202621036, 0.33212728431133076, 0.32738061520765177, 0.32274007442575553, 0.3181903361228633, 0.31371607445619665, 0.309301963582977, 0.3049326776604255, 0.3005928908457636, 0.29626727729621277, 0.2919405111689944, 0.2875972666213297, 0.28322221781044, 0.27880003889354693, 0.27431540402787175, 0.2697529873706358, 0.2650974630790605, 0.2603372419583603, 0.25547568140572324, 0.2505198754663299, 0.2454769181853614, 0.2403539036079986, 0.23515792577942243, 0.22989607874481374, 0.22457545654935362, 0.219203153238223, 0.21378626285660263, 0.2083318794496736, 0.20284709706261675, 0.19733900974061303, 0.19181471152884336, 0.18628129647248876, 0.18074585861673004, 0.17521549200674819, 0.16969729068772413, 0.1641983487048387, 0.15872576010327294, 0.15328661892820775, 0.14788801922482409, 0.14253705503830283, 0.13724082041382493, 0.13200640939657138, 0.12684091603172293, 0.12175143436446069, 0.11674505843996548, 0.11182888230341824, 0.10700999999999998],
        [0.4507267218406513, 0.4521693921675063, 0.4534020145877864, 0.4544255011350906, 0.4552407638430181, 0.4558487147451675, 0.456250265875138, 0.4564463292665284, 0.45643781695293784, 0.45622564096796553, 0.45581071334521, 0.45519394611827046, 0.45437625132074594, 0.45335854098623507, 0.4521417271483374, 0.4507267218406514, 0.4491144370967761, 0.44730578495031076, 0.44530167743485416, 0.44310302658400547, 0.4407107444313633, 0.438125743010527, 0.43534893435509536, 0.43238123049866733, 0.42922354347484215, 0.4258767853172185, 0.42234186805939544, 0.41861970373497187, 0.4147112043775469, 0.4106172820207195, 0.4063388486980887, 0.4018800783888357, 0.39725819285447184, 0.3924936758020905, 0.3876070109387853, 0.3826186819716495, 0.37754917260777726, 0.3724189665542615, 0.367248547518196, 0.3620583992066744, 0.35686900532679006, 0.3517008495856365, 0.34657441569030756, 0.34151018734789657, 0.33652864826549683, 0.33165028215020226, 0.32688958284037656, 0.3222370846994644, 0.3176773322221811, 0.3131948699032417, 0.30877424223736144, 0.3043999937192552, 0.3000566688436386, 0.29572881210522617, 0.2914009679987335, 0.28705768101887535, 0.28268349566036716, 0.27826295641792387, 0.2737806077862608, 0.26922099426009277, 0.2645686603341353, 0.2598119203419757, 0.2549541679726922, 0.25000256675423554, 0.24496428021455613, 0.23984647188160477, 0.23465630528333203, 0.22940094394768845, 0.22408755140262476, 0.21872329117609157, 0.2133153267960396, 0.20787082179041924, 0.2023969396871813, 0.1969008440142763, 0.19138969829965505, 0.18587066607126804, 0.18035091085706595, 0.17483759618499925, 0.16933788558301877, 0.16385894257907505, 0.15840793070111864, 0.15299201347710037, 0.14761835443497068, 0.14229411710268025, 0.1370264650081798, 0.13182256167941983, 0.12668957064435102, 0.12163465543092404, 0.11666497956708942, 0.11178770658079787, 0.10701],
        [0.4500298958030435, 0.4514276925463018, 0.4526238776259138, 0.4536188955990974, 0.45441319102306954, 0.45500720845504816, 0.4554013924522507, 0.4555961875718945, 0.45559203837119744, 0.45538938940737694, 0.45498868523765057, 0.4543903704192357, 0.4535948895093501, 0.45260268706521123, 0.4514142076440365, 0.45002989580304364, 0.44845019609944986, 0.446675553090473, 0.4447064113333307, 0.44254321538524033, 0.4401864098034194, 0.43763643914508554, 0.4348937479674563, 0.4319587808277491, 0.4288319822831815, 0.42551379689097124, 0.4220046692083357, 0.4183050437924923, 0.4144153652006588, 0.4103360779900525, 0.4060676267178913, 0.4016138749049109, 0.39699236192592213, 0.3922240461192535, 0.38732988582323385, 0.3823308393761922, 0.3772478651164577, 0.3721019213823588, 0.36691396651222463, 0.3617049588443842, 0.356495856717166, 0.35130761846889935, 0.34616120243791304, 0.3410775669625359, 0.3360776703810966, 0.3311824710319244, 0.32640683921256003, 0.32174129305739285, 0.3171702626600236, 0.3126781781140538, 0.3082494695130843, 0.3038685669507165, 0.29951990052055133, 0.29518790031619013, 0.2908569964312339, 0.28651161895928373, 0.282136197993941, 0.2777151636288067, 0.27323294595748204, 0.268673975073568, 0.264022681070666, 0.25926729712108376, 0.2544112687119567, 0.2494618444091269, 0.24442627277843615, 0.23931180238572694, 0.23412568179684104, 0.22887515957762058, 0.2235674842939078, 0.21820990451154462, 0.2128096687963732, 0.20737402571423555, 0.2019102238309737, 0.1964255117124298, 0.19092713792444602, 0.18542235103286425, 0.1799183996035267, 0.17442253220227533, 0.16894199739495225, 0.16348404374739972, 0.1580559198254595, 0.15266487419497382, 0.1473181554217848, 0.14202301207173454, 0.136786692710665, 0.1316164459044183, 0.1265195202188365, 0.12150316421976172, 0.11657462647303597, 0.11174115554450136, 0.10701000000000001],
        [0.4493200728913444, 0.4506725404190788, 0.4518319049426715, 0.452798141852274, 0.45357122653803766, 0.4541511343901134, 0.45453784079865306, 0.45473132115380765, 0.45473155084572847, 0.45453850526456724, 0.45415215980047485, 0.4535724898436028, 0.4527994707841025, 0.451833078012125, 0.4506732869178219, 0.4493200728913445, 0.4477734113228438, 0.4460332776024715, 0.4440996471203788, 0.44197249526671717, 0.4396517974316375, 0.43713752900529157, 0.4344296653778304, 0.43152818193940556, 0.4284330540801684, 0.4251442571902699, 0.42166176665986166, 0.41798555787909497, 0.4141156062381211, 0.41005188712709134, 0.40579437593615714, 0.4013466215256908, 0.39672646663694927, 0.39195532748141015, 0.38705462027055154, 0.38204576121585127, 0.3769501665287873, 0.3717892524208371, 0.36658443510347916, 0.3613571307881908, 0.3561287556864503, 0.3509207260097353, 0.3457544579695239, 0.3406513677772938, 0.3356328716445227, 0.33072038578268886, 0.325929146008367, 0.3212496665585201, 0.31666628127520835, 0.31216332400049174, 0.3077251285764306, 0.3033360288450847, 0.2989803586485143, 0.29464245182877935, 0.29030664222794017, 0.2859572636880565, 0.28157865005118865, 0.2771551351593967, 0.2726710528547407, 0.2681107369792808, 0.2634585213750768, 0.2587025752717447, 0.2538464094491218, 0.24889737007460147, 0.24386280331557691, 0.23875005533944127, 0.23356647231358768, 0.22831940040540938, 0.22301618578229956, 0.21766417461165133, 0.21227071306085796, 0.2068431472973125, 0.20138882348840834, 0.19591508780153843, 0.19042928640409607, 0.18493876546347454, 0.17945087114706681, 0.17397294962226625, 0.16851234705646584, 0.16307640961705896, 0.15767248347143867, 0.15230791478699812, 0.14699004973113064, 0.14172623447122934, 0.1365238151746874, 0.13139013800889796, 0.1263325491412542, 0.12135839473914938, 0.11647502096997658, 0.11168977400112907, 0.10701000000000001],
        [0.44859521248037215, 0.4499024048322257, 0.45102497879937004, 0.45196244437107225, 0.45271431153659997, 0.4532800902852204, 0.45365929060620136, 0.45385142248881, 0.45385599592231374, 0.4536725208959803, 0.45330050739907685, 0.4527394654208712, 0.4519889049506304, 0.45104833597762195, 0.4499172684911134, 0.4485952124803722, 0.4470816779346657, 0.4453761748432615, 0.44347821319542696, 0.4413873029804293, 0.4391029541875364, 0.43662467680601535, 0.43395198082513387, 0.4310843762341591, 0.42802137302235865, 0.4247624811790002, 0.4213072106933506, 0.41765507155467785, 0.41380557375224913, 0.40975822727533184, 0.40551254211319354, 0.4010717518539378, 0.39645398448101343, 0.3916810915767048, 0.3867749247232967, 0.3817573355030742, 0.37665017549832175, 0.37147529629132403, 0.36625454946436614, 0.3610097865997323, 0.3557628592797077, 0.350535619086577, 0.3453499176026248, 0.34022760641013594, 0.33519053709139507, 0.330260561228687, 0.32545326491196114, 0.3207591722618256, 0.3161625419065525, 0.3116476324744148, 0.30719870259368504, 0.30280001089263575, 0.29843581599953956, 0.29409037654266895, 0.28974795115029667, 0.2853927984506953, 0.2810091770721373, 0.2765813456428953, 0.272093562791242, 0.2675300871454498, 0.2628751773337915, 0.2581169577700179, 0.25325901600979245, 0.2483088053942571, 0.24327377926455365, 0.23816139096182412, 0.23297909382721013, 0.22773434120185368, 0.2224345864268967, 0.2170872828434809, 0.2116998837927482, 0.20627984261584048, 0.2008346126538995, 0.19537164724806722, 0.18989839973948544, 0.18442232346929605, 0.17895087177864086, 0.17349149800866176, 0.16805165550050055, 0.16263879759529914, 0.1572603776341993, 0.15192384895834304, 0.1466366649088721, 0.1414062788269284, 0.13624014405365378, 0.13114571393019003, 0.12613044179767907, 0.12120178099726273, 0.11636718487008287, 0.11163410675728133, 0.10701],
        [0.4478532739449452, 0.44911575483213206, 0.4502019814573207, 0.451111007631944, 0.45184188716743495, 0.45239367387522655, 0.452765421566752, 0.4529561840534441, 0.452965015146736, 0.4527909686580607, 0.45243309839885104, 0.4518904581805404, 0.45116210181456134, 0.45024708311234724, 0.44914445588533075, 0.4478532739449454, 0.44637259110262356, 0.44470146116979864, 0.4428389379579037, 0.4407840752783714, 0.43853592694263527, 0.4360935467621278, 0.4334559885482823, 0.4306223061125317, 0.4275915532663091, 0.4243627838210474, 0.4209350515881797, 0.4173074103791388, 0.41347891400535774, 0.40944861627826995, 0.405215571009308, 0.40078269949241496, 0.39616839295157513, 0.39139491009328137, 0.3864845096240281, 0.38145945025030875, 0.37634199067861723, 0.37115438961544706, 0.3659189057672923, 0.36065779784064633, 0.35539332454200334, 0.35014774457785675, 0.34494331665470046, 0.33980229947902824, 0.3347469517573336, 0.32979953219611063, 0.3249759576075071, 0.32026677722628843, 0.31565619839287345, 0.3111284284476816, 0.30666767473113254, 0.3022581445836453, 0.2978840453456394, 0.2935295843575338, 0.28917896895974826, 0.28481640649270185, 0.28042610429681397, 0.2759922697125041, 0.27149911008019123, 0.2669308327402949, 0.2622716450332344, 0.2575096475919635, 0.2526485142195738, 0.24769581201169122, 0.24265910806394184, 0.23754596947195167, 0.23236396333134657, 0.22712065673775272, 0.2218236167867961, 0.21648041057410272, 0.21109860519529855, 0.20568576774600952, 0.2002494653218618, 0.19479726501848132, 0.189336733931494, 0.18387543915652607, 0.17842094778920325, 0.1729808269251517, 0.16756264365999746, 0.1621739650893665, 0.1568223583088848, 0.15151539041417844, 0.1462606285008733, 0.14106563966459557, 0.13593799100097106, 0.1308852496056259, 0.12591498257418607, 0.12103475700227756, 0.11625213998552632, 0.1115746986195585, 0.10701000000000001],
        [0.4470922166598817, 0.44831105946518646, 0.4493617951778344, 0.45024303611134076, 0.4509533945792206, 0.4514914828949891, 0.4518559133721613, 0.45204529832425255, 0.45205825006477784, 0.45189338090725245, 0.4515493031651915, 0.45102462915210995, 0.45031797118152317, 0.44942794156694593, 0.44835315262189385, 0.44709221665988186, 0.4456437459944249, 0.44400635293903845, 0.4421786498072375, 0.4401592489125372, 0.4379467625684528, 0.43553980308849916, 0.43293698278619164, 0.4301369139750453, 0.4271382089685755, 0.42393948008029725, 0.42053933962372525, 0.4169363999123754, 0.41312927325976234, 0.4091165719794014, 0.4048969083848076, 0.4004728980438852, 0.3958631695420944, 0.3910903547192841, 0.3861770854153038, 0.3811459934700025, 0.37601971072322943, 0.3708208690148336, 0.36557210018466435, 0.3602960360725707, 0.35501530851840185, 0.349752549362007, 0.3445303904432354, 0.3393714636019362, 0.33429840067795824, 0.3293338335111512, 0.324493985779169, 0.3197694485108878, 0.3151444045729882, 0.31060303683215124, 0.3061295281550579, 0.3017080614083891, 0.2973228194588258, 0.2929579851730489, 0.28859774141773925, 0.28422627105957793, 0.27982775696524603, 0.2753863820014242, 0.2708863290347935, 0.2663117809320348, 0.2616469205598293, 0.25687984771364136, 0.2520143299040709, 0.24705805157050156, 0.24201869715231678, 0.23690395108890025, 0.23172149781963522, 0.22647902178390558, 0.22118420742109463, 0.215844739170586, 0.21046830147176324, 0.2050625787640099, 0.19963525548670957, 0.19419401607924566, 0.18874654498100182, 0.18330052663136162, 0.17786364546970848, 0.17244358593542605, 0.1670480324678979, 0.16168466950650745, 0.15636118149063835, 0.15108525285967414, 0.1458645680529983, 0.14070681150999448, 0.1356196676700461, 0.1306108209725368, 0.12568795585685008, 0.12085875676236951, 0.11613090812847858, 0.11151209439456089, 0.10701],
        [0.44631, 0.4474867877777778, 0.4485033022222222, 0.44935773428571446, 0.450048274920635, 0.45057311507936515, 0.45093044571428587, 0.45111845777777787, 0.4511353422222223, 0.45097929000000003, 0.4506484920634921, 0.4501411393650795, 0.44945542285714285, 0.44858953349206365, 0.44754166222222225, 0.4463100000000001, 0.4448927377777779, 0.4432880665079366, 0.4414941771428571, 0.4395092606349207, 0.4373315079365081, 0.43495911000000004, 0.43239025777777773, 0.4296231422222222, 0.42665595428571434, 0.42348688492063497, 0.42011412507936513, 0.41653586571428575, 0.41275029777777783, 0.40875561222222223, 0.40455, 0.400135781111111, 0.3955317917460318, 0.39076099714285717, 0.3858463625396826, 0.38081085317460317, 0.3756774342857143, 0.3704690711111111, 0.3652087288888889, 0.35991937285714287, 0.3546239682539683, 0.3493454803174603, 0.34410687428571435, 0.3389311153968256, 0.333841168888889, 0.3288600000000002, 0.3240041111111112, 0.31926415317460327, 0.3146243142857144, 0.31006878253968256, 0.3055817460317462, 0.301147392857143, 0.2967499111111112, 0.29237348888888887, 0.28800231428571443, 0.28362057539682545, 0.27921246031746044, 0.27476215714285723, 0.2702538539682541, 0.26567173888888895, 0.26100000000000007, 0.25622676111111126, 0.251355888888889, 0.24639518571428579, 0.24135245396825403, 0.23623549603174615, 0.23105211428571434, 0.2258101111111111, 0.22051728888888888, 0.21518144999999997, 0.2098103968253969, 0.20441193174603178, 0.1989938571428572, 0.19356397539682543, 0.18813008888888885, 0.1827, 0.17728151111111115, 0.17188242460317465, 0.16651054285714284, 0.16117366825396826, 0.15587960317460314, 0.15063615, 0.1454511111111111, 0.1403322888888889, 0.13528748571428573, 0.13032450396825399, 0.12545114603174606, 0.12067521428571433, 0.11600451111111112, 0.11144683888888889, 0.10701000000000001],
        [0.44550458334011817, 0.44664140881629505, 0.4476253848517952, 0.44845430663151653, 0.44912596934035626, 0.44963816816321206, 0.44998869828498156, 0.45017535489056226, 0.4501959331648515, 0.4500482282927475, 0.44973003545914714, 0.4492391498489483, 0.4485733666470484, 0.4477304810383451, 0.4467082882077358, 0.4455045833401183, 0.4441171616203897, 0.4425438182334483, 0.44078234836419095, 0.4388305471975156, 0.43668620991831975, 0.43434713171150074, 0.43181110776195636, 0.42907593325458404, 0.4261394033742815, 0.42299931330594626, 0.41965345823447564, 0.41609963334476746, 0.41233563382171906, 0.4083592548502282, 0.4041682916151923, 0.3997647822968553, 0.3951677370568473, 0.39040040905214435, 0.38548605143972253, 0.3804479173765582, 0.37530926001962767, 0.37009333252590715, 0.36482338805237274, 0.3595226797560009, 0.35421446079376745, 0.3489219843226491, 0.34366850349962186, 0.3384772714816619, 0.33337154142574554, 0.32837456648884905, 0.32350309528749766, 0.318747858276414, 0.3140930813698691, 0.30952299048213455, 0.30502181152748187, 0.30057377042018246, 0.2961630930745077, 0.291774005404729, 0.28739073332511794, 0.2829975027499458, 0.2785785395934842, 0.2741180697700046, 0.269600319193778, 0.26500951377907633, 0.26032987944017083, 0.2555495907604328, 0.25067261699963284, 0.2457068760866414, 0.24066028595032876, 0.2355407645195654, 0.23035622972322187, 0.22511459949016846, 0.21982379174927566, 0.21449172442941394, 0.20912631545945365, 0.20373548276826514, 0.198327144284719, 0.19290921793768545, 0.18748962165603514, 0.1820762733686384, 0.17667709100436554, 0.1712999924920871, 0.1659528957606735, 0.16064371873899513, 0.15538037935592242, 0.15017079554032578, 0.1450228852210757, 0.13994456632704255, 0.13494375678709675, 0.1300283745301087, 0.12520633748494886, 0.12048556358048765, 0.11587397074559548, 0.11137947690914282, 0.10701],
        [0.4446739260550547, 0.4457733916271272, 0.44672692532786445, 0.447531957625199, 0.4481859189870625, 0.44868623988138717, 0.4490303507761052, 0.4492156821391485, 0.4492396644384491, 0.44909972814193916, 0.4487933037175509, 0.44831782163321626, 0.4476707123568673, 0.44684940635643594, 0.4458513340998544, 0.44467392605505485, 0.443314612689969, 0.4417708244725293, 0.4400399918706677, 0.43811954535231623, 0.43600691538540703, 0.43369953243787207, 0.4311948269776435, 0.4284902294726532, 0.4255831703908336, 0.42247108020011664, 0.4191513893684341, 0.4156215283637183, 0.41187892765390133, 0.4079210177069152, 0.403745228990692, 0.399353335203881, 0.3947644829680017, 0.39000216213528993, 0.3850898625579824, 0.38005107408831545, 0.37490928657852574, 0.36968798988084917, 0.36441067384752257, 0.3591008283307822, 0.3537819431828645, 0.3484775082560057, 0.34321101340244253, 0.3380059484744112, 0.33288580332414797, 0.3278740678038895, 0.32298769999249294, 0.3182175308752992, 0.3135478596642697, 0.308962985571366, 0.3044472078085501, 0.2999848255877834, 0.2955601381210275, 0.2911574446202441, 0.28676104429739474, 0.2823552363644411, 0.27792432003334483, 0.27345259451606757, 0.26892435902457085, 0.26432391277081624, 0.2596355549667657, 0.2548475396376662, 0.24996394006190778, 0.24499278433116597, 0.23994210053711643, 0.23481991677143463, 0.22963426112579624, 0.22439316169187687, 0.21910464656135195, 0.21377674382589718, 0.2084174815771882, 0.20303488790690047, 0.19763699090670958, 0.19223181866829117, 0.18682739928332076, 0.18143176084347395, 0.17605293144042633, 0.17069893916585352, 0.16537781211143102, 0.16009757836883448, 0.15486626602973946, 0.14969190318582146, 0.1445825179287562, 0.1395461383502192, 0.13459079254188605, 0.12972450859543228, 0.12495531460253351, 0.12029123865486532, 0.11574030884410327, 0.11131055326192295, 0.10701],
        [0.44381598751962775, 0.4448812052566631, 0.44580680591174116, 0.4465898917432136, 0.4472275650094319, 0.44771692796874785, 0.448055082879513, 0.4482391320000789, 0.4482661775887973, 0.4481333219040197, 0.4478376672040977, 0.4473763157473829, 0.4467463697922268, 0.44594493159698134, 0.44496910341999774, 0.44381598751962786, 0.4424826861542231, 0.44096630158213534, 0.439263936061716, 0.4373726918513166, 0.43528967120928885, 0.4330119763939845, 0.43053670966375496, 0.42786097327695166, 0.42498186949192684, 0.4218965005670316, 0.4186019687606175, 0.4150953763310365, 0.4113738255366397, 0.40743441863577917, 0.4032742578868063, 0.39889487343495084, 0.3943155069729548, 0.38955982808043804, 0.3846515063370206, 0.3796142113223226, 0.37447161261596407, 0.3692473797975649, 0.3639651824467451, 0.35864869014312484, 0.35332157246632406, 0.34800749899596267, 0.342730139311661, 0.3375131629930388, 0.332380239619716, 0.32735503877131306, 0.322454686910261, 0.31767013803023814, 0.31298580300773343, 0.30838609271923606, 0.3038554180412358, 0.2993781898502216, 0.29493881902268276, 0.2905217164351089, 0.28611129296398924, 0.2816919594858127, 0.2772481268770691, 0.27276420601424767, 0.26822460777383744, 0.263613743032328, 0.2589160226662085, 0.25411981071887113, 0.24922928390131874, 0.24425257209145734, 0.23919780516719244, 0.23407311300642997, 0.2288866254870756, 0.22364647248703512, 0.21836078388421434, 0.21303768955651906, 0.20768531938185492, 0.2023118032381277, 0.1969252710032433, 0.1915338525551073, 0.1861456777716256, 0.18076887653070398, 0.175411578710248, 0.17008191418816362, 0.16478801284235658, 0.1595380045507326, 0.15434001919119744, 0.1492021866416569, 0.1441326367800167, 0.13913949948418267, 0.13423090463206053, 0.129414982101556, 0.1246998617705749, 0.12009367351702299, 0.11560454721880603, 0.11124061275382977, 0.10701],
        [0.44292872710865555, 0.4439633187512915, 0.444863908864736, 0.4456273134620118, 0.44625034855614243, 0.44672983016015105, 0.44706257428706137, 0.4472453969498961, 0.4472751141616788, 0.44714854193543274, 0.44686249628418123, 0.44641379322094754, 0.44579924875875465, 0.4450156789106264, 0.44405989968958554, 0.4429287271086556, 0.4416189771808598, 0.44012746591922147, 0.438451009336764, 0.4365864234465104, 0.43453052426148403, 0.43228012779470826, 0.4298320500592064, 0.42718310706800156, 0.42433011483411726, 0.4212698893705765, 0.4179992466904027, 0.4145150028066192, 0.4108139737322492, 0.40689297548031594, 0.40274882406384277, 0.39838283059282753, 0.39381428656516715, 0.3890669785757327, 0.38416469321939545, 0.379131217091027, 0.37399033678549853, 0.3687658388976813, 0.3634815100224468, 0.3581611367546662, 0.352828505689211, 0.3475074034209525, 0.34222161654476196, 0.33699493165551064, 0.33185113534807, 0.3268140142173113, 0.32190081772496654, 0.3171026468002102, 0.31240406523907754, 0.3077896368376034, 0.30324392539182343, 0.2987514946977725, 0.2942969085514859, 0.28986473074899843, 0.2854395250863457, 0.28100585535956263, 0.2765482853646844, 0.2720513788977462, 0.26749969975478316, 0.2628778117318305, 0.2581702786249233, 0.25336560698010735, 0.24846807434347093, 0.24348590101111287, 0.23842730727913214, 0.23330051344362762, 0.22811373980069807, 0.22287520664644245, 0.21759313427695967, 0.21227574298834867, 0.2069312530767082, 0.20156788483813715, 0.1961938585687345, 0.19081739456459906, 0.18544671312182975, 0.18009003453652545, 0.174755579104785, 0.16945156712270731, 0.16418621888639126, 0.15896775469193575, 0.15380439483543965, 0.14870435961300177, 0.14367586932072113, 0.13872714425469654, 0.1338664047110269, 0.12910187098581105, 0.12444176337514791, 0.11989430217513636, 0.11546770768187525, 0.1111702001914635, 0.10700999999999998],
        [0.4420101041969564, 0.4430182011574018, 0.44389711644816005, 0.4446434272580456, 0.4452537107758722, 0.44572454419045454, 0.4460525046906065, 0.4462341694651424, 0.4462661157028764, 0.4461449205926229, 0.44586716132319604, 0.4454294150834098, 0.4448282590620784, 0.44406027044801644, 0.4431220264300377, 0.4420101041969565, 0.440721080937587, 0.4392515338407437, 0.4375980400952406, 0.43575717688989174, 0.43372552141351167, 0.4314996508549143, 0.42907614240291403, 0.42645157324632477, 0.4236225205739613, 0.4205855615746372, 0.417337273437167, 0.41387423335036483, 0.41019301850304485, 0.40629020608402144, 0.40216237328210863, 0.397810640280274, 0.39325429923809907, 0.388517185309318, 0.38362313364766554, 0.37859597940687634, 0.3734595577406853, 0.3682377038028264, 0.3629542527470346, 0.3576330397270445, 0.3522978998965906, 0.3469726684094075, 0.34168118041922996, 0.3364472710797925, 0.3312947755448295, 0.32624752896807574, 0.3213228541207733, 0.3165120242441947, 0.31179980019711945, 0.30717094283832735, 0.3026102130265983, 0.2981023716207123, 0.2936321794794488, 0.2891843974615878, 0.28474378642590914, 0.28029510723119255, 0.27582312073621784, 0.27131258779976486, 0.26674826928061335, 0.2621149260375431, 0.25739731892933415, 0.2525841313974348, 0.24767973721396933, 0.24269243273373042, 0.23763051431151094, 0.23250227830210382, 0.22731602106030185, 0.22208003894089787, 0.21680262829868474, 0.21149208548845538, 0.20615670686500248, 0.20080478878311897, 0.1954446275975977, 0.19008451966323148, 0.1847327613348132, 0.17939764896713573, 0.17408747891499182, 0.16881054753317437, 0.1635751511764762, 0.15838958619969026, 0.15326214895760926, 0.14820113580502609, 0.14321484309673357, 0.13831156718752471, 0.1334996044321921, 0.12878725118552878, 0.1241828038023275, 0.11969455863738115, 0.11533081204548254, 0.11109986038142454, 0.10701],
        [0.4410580781593486, 0.4420443215213825, 0.4429053109233247, 0.44363743760776647, 0.44423709281729934, 0.44470066779451506, 0.44502455378200495, 0.4452051420223604, 0.44523882375817286, 0.44512199023203436, 0.44485103268653586, 0.44442234236426914, 0.44383231050782546, 0.4430773283597965, 0.4421537871627738, 0.44105807815934867, 0.4397865925921126, 0.43833572170365737, 0.4367018567365743, 0.43488138893345474, 0.4328707095368905, 0.43066620978947273, 0.42826428093379326, 0.4256613142124434, 0.4228537008680148, 0.4198378321430989, 0.41661009928028697, 0.41316689352217084, 0.40950460611134176, 0.4056196282903914, 0.4015083513019112, 0.3971717361000529, 0.3926290224852106, 0.38790401996933793, 0.3830205380643892, 0.37800238628231847, 0.37287337413507987, 0.3676573111346273, 0.36237800679291504, 0.357059270621897, 0.35172491213352736, 0.34639874083976013, 0.3411045662525496, 0.3358661978838496, 0.3307074452456142, 0.32565211784979775, 0.3207175577818458, 0.31589523742117065, 0.3111701617206762, 0.3065273356332663, 0.301951764111845, 0.2974284521093162, 0.2929424045785837, 0.2884786264725516, 0.2840221227441238, 0.27955789834620404, 0.2750709582316964, 0.2705463073535048, 0.265968950664533, 0.261323893117685, 0.2565961396658648, 0.2517745869469133, 0.2468636983384189, 0.2418718289029074, 0.23680733370290416, 0.23167856780093493, 0.22649388625952516, 0.2212616441412004, 0.21599019650848625, 0.2106878984239083, 0.2053631049499922, 0.20002417114926324, 0.1946794520842472, 0.18933730281746958, 0.18400607841145597, 0.1786941339287319, 0.17340982443182293, 0.1681615049832547, 0.16295753064555263, 0.15780625648124239, 0.1527160375528495, 0.14769522892289955, 0.14275218565391812, 0.13789526280843076, 0.13313281544896302, 0.12847319863804044, 0.1239247674381886, 0.1194958769119331, 0.11519488212179943, 0.1110301381303132, 0.10700999999999998],
        [0.4400706083706503, 0.44104014888962273, 0.44188737455154065, 0.44260854898762647, 0.44319993582910205, 0.4436577987071902, 0.4439784012531129, 0.44415800709809244, 0.44419287987335115, 0.4440792832101114, 0.44381348073959537, 0.44339173609302535, 0.4428103129016234, 0.4420654747966123, 0.4411534854092137, 0.4400706083706504, 0.4388131073121443, 0.43737724586491794, 0.43575928766019356, 0.4339554963291932, 0.43196213550313944, 0.42977546881325435, 0.42739175989076034, 0.4248072723668796, 0.4220182698728344, 0.4190210160398472, 0.41581177449914, 0.4123868088819352, 0.408742382819455, 0.4048747599429218, 0.40078020388355784, 0.39645955165492713, 0.3919319337999623, 0.3872210542439369, 0.38235061691212496, 0.3773443257298008, 0.3722258846222385, 0.36701899751471173, 0.3617473683324947, 0.3564347010008616, 0.3511046994450863, 0.345781067590443, 0.3404875093622055, 0.3352477286856481, 0.3300854294860446, 0.32502431568866924, 0.32008169039234824, 0.31524925339011756, 0.31051230364856525, 0.3058561401342795, 0.3012660618138484, 0.29672736765386026, 0.2922253566209031, 0.2877453276815651, 0.2832725798024343, 0.2787924119500991, 0.2742901230911473, 0.26975101219216746, 0.26516037821974736, 0.26050352014047534, 0.25576573692093957, 0.25093617660460266, 0.24601938354242497, 0.2410237511622416, 0.23595767289188727, 0.2308295421591972, 0.22564775239200618, 0.22042069701814912, 0.21515676946546108, 0.20986436316177695, 0.2045518715349317, 0.1992276880127602, 0.1939002060230975, 0.18857781899377843, 0.183268920352638, 0.17798190352751125, 0.1727251619462329, 0.167507089036638, 0.16233607822656157, 0.15722052294383848, 0.1521688166163037, 0.1471893526717921, 0.14229052453813879, 0.13748072564317854, 0.13276834941474638, 0.12816178928067726, 0.12366943866880609, 0.11929969100696787, 0.11506093972299745, 0.11096157824472984, 0.10700999999999997],
        [0.43904565420567987, 0.44000415230851125, 0.440842189594119, 0.44155596587407686, 0.44214168095995826, 0.4425955346633371, 0.44291372679578683, 0.4430924571688811, 0.4431279255941937, 0.4430163318832983, 0.4427538758477683, 0.4423367572991777, 0.4417611760490998, 0.44102333190910853, 0.44011942469077736, 0.4390456542056799, 0.43779822026538984, 0.43637332268148094, 0.434767161265527, 0.4329759358291012, 0.4309958461837776, 0.4288230921411295, 0.42645387351273095, 0.4238843901101553, 0.4211108417449763, 0.4181294282287676, 0.41493634937310275, 0.4115278049895555, 0.4078999948896996, 0.4040491188851084, 0.39997137678735584, 0.3956675205476595, 0.3911565106758143, 0.3864618598212587, 0.3816070806334313, 0.3766156857617711, 0.37151118785571685, 0.366317099564707, 0.36105693353818047, 0.35575420242557604, 0.35043241887633236, 0.3451150955398882, 0.33982574506568236, 0.3345878801031535, 0.3294250133017402, 0.3243606573108814, 0.3194120136364449, 0.31457103921001467, 0.3098233798196039, 0.30515468125322576, 0.30055058929889344, 0.29599674974462015, 0.29147880837841883, 0.28698241098830285, 0.2824932033622852, 0.2779968312883791, 0.27347894055459765, 0.2689251769489542, 0.2643211862594617, 0.2596526142741333, 0.25490510678098227, 0.25006810334656265, 0.24514621865159242, 0.24014786115533043, 0.23508143931703557, 0.22995536159596683, 0.22477803645138303, 0.21955787234254304, 0.21430327772870592, 0.20902266106913045, 0.20372443082307554, 0.19841699544980007, 0.19310876340856298, 0.1878081431586231, 0.18252354315923944, 0.17726337186967078, 0.1720360377491761, 0.1668499492570143, 0.1617135148524442, 0.15663514299472486, 0.15162324214311496, 0.14668622075687357, 0.14183248729525952, 0.13707045021753178, 0.13240851798294914, 0.12785509905077058, 0.12341860188025497, 0.11910743493066121, 0.11493000666124817, 0.1108947255312748, 0.10700999999999997],
        [0.4379811750392556, 0.4389348008244372, 0.4397686383123711, 0.4404788927435699, 0.4410617693585463, 0.4415134733978132, 0.4418302101018833, 0.442008184711269, 0.4420436024664835, 0.4419326686080393, 0.4416715883764492, 0.441256567012226, 0.4406838097558822, 0.4399495218479308, 0.4390499085288843, 0.4379811750392556, 0.43673952661955723, 0.43532116851030234, 0.4337223059520033, 0.43193914418517276, 0.42996788845032385, 0.42780474398796897, 0.425445916038621, 0.42288760984279256, 0.42012603064099663, 0.41715738367374566, 0.4139778741815525, 0.41058370740493, 0.40697108858439063, 0.4031362229604474, 0.39907531577361277, 0.39478907638101296, 0.39029623060622715, 0.3856200083894475, 0.3807836396708666, 0.37581035439067695, 0.37072338248907083, 0.36554595390624073, 0.360301298582379, 0.35501264645767816, 0.3497032274723306, 0.34439627156652863, 0.33911500868046485, 0.3338826687543316, 0.3287224817283211, 0.32365767754262603, 0.31870528919829993, 0.3138575619398413, 0.30910054407260956, 0.30442028390196424, 0.29980282973326505, 0.29523422987187165, 0.2907005326231434, 0.28618778629244007, 0.2816820391851211, 0.27716933960654616, 0.2726357358620748, 0.26806727625706667, 0.26345000909688127, 0.2587699826868781, 0.254013245332417, 0.24916957014885333, 0.24424362949152642, 0.23924382052577176, 0.23417854041692454, 0.22905618633032024, 0.22388515543129411, 0.2186738448851814, 0.21343065185731772, 0.20816397351303811, 0.20288220701767812, 0.19759374953657297, 0.19230699823505806, 0.18703035027846865, 0.18177220283214013, 0.17654095306140793, 0.17134499813160717, 0.16619273520807334, 0.1610925614561418, 0.15605287404114776, 0.15108207012842664, 0.1461885468833138, 0.1413807014711445, 0.13666693105725422, 0.13205563280697813, 0.12755520388565164, 0.12317404145861009, 0.11892054269118883, 0.11480310474872316, 0.11083012479654844, 0.10700999999999998],
        [0.4368751302461956, 0.43783056348378935, 0.43866560296760765, 0.439376534072557, 0.439959642173544, 0.44041121264547556, 0.4407275308632582, 0.44090488220179846, 0.44093955203600294, 0.44082782574077867, 0.44056598869103203, 0.4401503262616696, 0.43957712382759817, 0.43884266676372424, 0.4379432404449545, 0.4368751302461957, 0.43563462154235433, 0.43421799970833713, 0.43262155011905074, 0.4308415581494019, 0.42887430917429703, 0.42671608856864285, 0.4243631817073462, 0.4218118739653135, 0.4190584507174515, 0.416099197338667, 0.4129303992038662, 0.40954834168795606, 0.4059493101658432, 0.40212959001243426, 0.39808546660263583, 0.39381765275775, 0.38934457108466086, 0.3846890716366475, 0.3798740044669894, 0.37492221962896594, 0.3698565671758565, 0.3646998971609403, 0.35947505963749693, 0.35420490465880566, 0.3489122822781457, 0.34362004254879647, 0.33835103552403745, 0.3331281112571479, 0.3279741198014071, 0.32291191121009466, 0.3179582787620778, 0.31310578863857674, 0.30834095024639924, 0.3036502729923536, 0.2990202662832479, 0.29443743952589024, 0.2898883021270888, 0.2853593634936515, 0.2808371330323865, 0.27630812015010175, 0.2717588342536056, 0.26717578474970605, 0.26254548104521114, 0.2578544325469289, 0.25308914866166765, 0.24823977998753424, 0.24331104188783204, 0.23831129091716302, 0.2332488836301294, 0.2281321765813335, 0.22296952632537734, 0.2177692894168631, 0.21253982241039304, 0.20728948186056917, 0.20202662432199384, 0.1967596063492691, 0.19149678449699714, 0.18624651531978006, 0.18101715537222024, 0.17581706120891968, 0.17065458938448053, 0.16553809645350503, 0.1604759389705953, 0.1554764734903536, 0.15054805656738193, 0.14569904475628265, 0.14093779461165776, 0.13627266268810956, 0.13171200554024018, 0.12726417972265172, 0.12293754178994643, 0.11874044829672648, 0.1146812557975939, 0.11076832084715105, 0.10701],
        [0.43572547920131816, 0.43668990933295665, 0.43753196582113957, 0.43824809433748985, 0.4388347405536296, 0.43928835014118156, 0.4396053687717682, 0.4397822421170118, 0.4398154158485352, 0.43970133563796066, 0.43943644715691077, 0.439017196077008, 0.43844002806987487, 0.4377013888071339, 0.4367977239604076, 0.43572547920131827, 0.4344811002014885, 0.433061032632541, 0.431461722166098, 0.4296796144737823, 0.42771115522721614, 0.42555279009802194, 0.4232009647578225, 0.4206521248782401, 0.41790271613089736, 0.4149491841874168, 0.41178797471942064, 0.40841553339853165, 0.40482830589637225, 0.401022737884565, 0.3969952750347323, 0.3927466832806335, 0.3882950096045757, 0.3836626212510026, 0.37887188546435796, 0.37394516948908574, 0.3689048405696296, 0.36377326595043336, 0.358572812875941, 0.353325848590596, 0.3480547403388425, 0.3427818553651241, 0.3375295609138848, 0.33232022422956814, 0.3271762125566181, 0.3221198931394786, 0.31716774401194237, 0.31231268636519993, 0.3075417521797903, 0.30284197343625274, 0.2982003821151269, 0.2936040101969519, 0.2890398896622672, 0.284495052491612, 0.2799565306655258, 0.2754113561645477, 0.2708465609692172, 0.26624917706007384, 0.26160623641765657, 0.25690477102250486, 0.2521318128551582, 0.24727793583866545, 0.24234788166611423, 0.23734993397310186, 0.23229237639522565, 0.22718349256808296, 0.22203156612727104, 0.21684488070838714, 0.2116317199470287, 0.20640036747879287, 0.20115910693927713, 0.19591622196407857, 0.19067999618879466, 0.18545871324902252, 0.18026065678035963, 0.17509411041840328, 0.16996735779875063, 0.16488868255699912, 0.15986636832874593, 0.15490869874958849, 0.150023957455124, 0.14522042808094981, 0.1405063942626632, 0.13589013963586155, 0.13137994783614207, 0.12698410249910205, 0.12271088726033885, 0.11856858575544975, 0.11456548162003202, 0.11070985848968301, 0.10700999999999998],
        [0.4345301812794417, 0.43551130741832783, 0.43636660913427827, 0.4370927780148203, 0.43768650564748124, 0.4381444836197885, 0.4384634035192696, 0.43863995693345187, 0.43867083544986263, 0.4385527306560295, 0.4382823341394797, 0.43785633748774094, 0.4372714322883403, 0.43652431012880527, 0.4356116625966633, 0.43453018127944176, 0.433276557764668, 0.4318474836398697, 0.4302396504925739, 0.42844974991030815, 0.4264744734806, 0.4243105127909767, 0.42195455942896576, 0.41940330498209444, 0.41665344103789026, 0.4137016591838808, 0.41054465100759296, 0.40717910809655466, 0.40360172203829303, 0.3998091844203356, 0.3957981868302097, 0.3915696015524263, 0.38714102365943226, 0.3825342289206571, 0.37777099310553097, 0.3728730919834839, 0.367862301323946, 0.36276039689634726, 0.35758915447011763, 0.3523703498146872, 0.3471257586994861, 0.341877156893944, 0.3366463201674915, 0.33145502428955825, 0.3263250450295741, 0.32127815815696964, 0.31633044663205834, 0.31147522217869056, 0.30670010371160006, 0.3019927101455208, 0.29734066039518686, 0.29273157337533234, 0.2881530680006909, 0.2835927631859967, 0.2790382778459837, 0.27447723089538584, 0.26989724124893705, 0.26528592782137145, 0.26063090952742285, 0.2559198052818253, 0.2511402339993128, 0.24628324067830665, 0.24135357465197824, 0.23635941133718597, 0.23130892615078869, 0.22621029450964494, 0.22107169183061345, 0.21590129353055273, 0.21070727502632158, 0.20549781173477863, 0.20028107907278242, 0.1950652524571916, 0.18985850730486503, 0.18466901903266103, 0.1795049630574385, 0.17437451479605595, 0.16928584966537205, 0.1642471430822455, 0.1592665704635349, 0.15435230722609894, 0.1495125287867962, 0.14475541056248534, 0.14008912797002507, 0.135521856426274, 0.13106177134809074, 0.12671704815233395, 0.12249586225586234, 0.11840638907553448, 0.11445680402820901, 0.11065528253074462, 0.10701],
        [0.43328719585538433, 0.4342932267862922, 0.4351684151683346, 0.435909789581, 0.43651437860377684, 0.4369792108161536, 0.4373013147976187, 0.43747771912766076, 0.4375054523857681, 0.43738154315142946, 0.43710302000413326, 0.4366669115233679, 0.43607024628862173, 0.43531005287938346, 0.4343833598751416, 0.4332871958553844, 0.4320185893996004, 0.43057456908727837, 0.42895216349790655, 0.4271484012109736, 0.4251603108059677, 0.4229849208623776, 0.42061925995969174, 0.4180603566773986, 0.41530523959498655, 0.4123509372919444, 0.40919447834776024, 0.40583289134192274, 0.40226320485392053, 0.3984824474632417, 0.39448764774937506, 0.3902798411758914, 0.38587609074269064, 0.381297466333755, 0.3765650378330667, 0.37169987512460817, 0.3667230480923617, 0.3616556266203095, 0.35651868059243386, 0.351333279892717, 0.34612049440514125, 0.3409013940136889, 0.3356970486023423, 0.33052852805508365, 0.3254169022558951, 0.32038324108875915, 0.3154431483065897, 0.3105903631380277, 0.3058131586806458, 0.30109980803201664, 0.2964385842897128, 0.2918177605513071, 0.2872256099143721, 0.28265040547648046, 0.27808042033520486, 0.27350392758811776, 0.26890920033279203, 0.2642845116668003, 0.25961813468771516, 0.2548983424931092, 0.2501134081805553, 0.24525489748251778, 0.24032754667102899, 0.23533938465301293, 0.23029844033539382, 0.2252127426250956, 0.22009032042904264, 0.21493920265415886, 0.20976741820736847, 0.2045829959955955, 0.19939396492576417, 0.19420835390479843, 0.18903419183962253, 0.18387950763716057, 0.1787523302043366, 0.17366068844807483, 0.1686126112752992, 0.16361612759293404, 0.15867926630790327, 0.1538100563271311, 0.1490165265575416, 0.14430670590605896, 0.1396886232796072, 0.13517030758511053, 0.130759787729493, 0.1264650926196787, 0.12229425116259177, 0.11825529226515635, 0.11435624483429647, 0.11060513777693633, 0.10701],
        [0.4319944823039643, 0.43303413648323846, 0.4339362661846196, 0.43469833351248083, 0.43531780057119457, 0.43579212946513407, 0.4361187822986721, 0.4362952211761812, 0.4363189082020345, 0.4361873054806048, 0.4358978751162652, 0.43544807921338813, 0.4348353798763467, 0.4340572392095137, 0.43311111931726193, 0.4319944823039643, 0.43070479027399367, 0.4292395053317229, 0.4275960895815248, 0.4257720051277722, 0.423764714074838, 0.4215716785270952, 0.41919036058891646, 0.41661822236467444, 0.41385272595874256, 0.4108913334754931, 0.4077315070192992, 0.4043707086945338, 0.40080640060556955, 0.39703604485677935, 0.39305710355253604, 0.38887083575379117, 0.384493688347811, 0.3799459051784402, 0.37524773008952367, 0.37041940692490605, 0.3654811795284325, 0.3604532917439474, 0.35535598741529606, 0.35020951038632286, 0.3450341045008729, 0.3398500136027909, 0.3346774815359217, 0.3295367521441101, 0.32444806927120073, 0.3194316767610388, 0.31450261071970065, 0.3096550763021907, 0.3048780709257448, 0.300160592007599, 0.2954916369649894, 0.29086020321515205, 0.2862552881753229, 0.28166588926273806, 0.2770810038946334, 0.2724896294882451, 0.2678807634608092, 0.26324340322956175, 0.25856654621173863, 0.2538391898245759, 0.24905033148530972, 0.24419210922735857, 0.23926922354887153, 0.2342895155641803, 0.22926082638761633, 0.22419099713351134, 0.21908786891619683, 0.21395928285000457, 0.20881308004926608, 0.20365710162831285, 0.19849918870147673, 0.19334718238308915, 0.1882089237874818, 0.18309225402898624, 0.17800501422193418, 0.1729550454806571, 0.16795018891948663, 0.1629982856527545, 0.15810717679479216, 0.15328470345993134, 0.1485387067625036, 0.14387702781684053, 0.1393075077372738, 0.134837987638135, 0.1304763086337557, 0.1262303118384675, 0.1221078383666021, 0.11811672933249104, 0.11426482585046586, 0.11055996903485835, 0.10700999999999998],
        [0.43065000000000003, 0.4317325055555555, 0.4326690444444445, 0.4334576142857144, 0.43409621269841275, 0.43458283730158737, 0.43491548571428573, 0.43509215555555564, 0.4351108444444444, 0.43496955, 0.43466626984126977, 0.4341990015873016, 0.43356574285714283, 0.43276449126984134, 0.43179324444444445, 0.43065000000000003, 0.42933275555555556, 0.4278395087301587, 0.42616825714285717, 0.42431699841269843, 0.4222837301587302, 0.42006645, 0.41766315555555544, 0.4150718444444443, 0.4122905142857142, 0.40931716269841273, 0.4061497873015873, 0.4027863857142857, 0.3992249555555555, 0.39546349444444445, 0.39149999999999996, 0.38733601888888874, 0.38298729396825404, 0.3784731171428572, 0.37381278031746024, 0.36902557539682534, 0.3641307942857143, 0.3591477288888889, 0.3540956711111112, 0.3489939128571429, 0.3438617460317461, 0.3387184625396825, 0.33358335428571434, 0.3284757131746033, 0.3234148311111112, 0.3184200000000001, 0.3135055955555556, 0.3086663287301589, 0.3038919942857144, 0.299172386984127, 0.29449730158730164, 0.28985653285714286, 0.2852398755555557, 0.28063712444444455, 0.2760380742857144, 0.2714325198412699, 0.266810255873016, 0.26216107714285725, 0.2574747784126985, 0.2527411544444445, 0.24795000000000011, 0.24309407888888898, 0.2381780311111112, 0.2332094657142858, 0.2281959917460318, 0.2231452182539683, 0.21806475428571429, 0.2129622088888889, 0.20784519111111113, 0.20272131, 0.19759817460317458, 0.19248339396825398, 0.18738457714285714, 0.18230933317460313, 0.17726527111111107, 0.17226, 0.16730112888888887, 0.1623962668253968, 0.15755302285714284, 0.15277900603174602, 0.14808182539682532, 0.14346908999999994, 0.13894840888888882, 0.1345273911111111, 0.13021364571428568, 0.12601478174603173, 0.1219384082539682, 0.11799213428571428, 0.11418356888888886, 0.1105203211111111, 0.10700999999999998],
        [0.4292522022768246, 0.43038699090464255, 0.4313655721515949, 0.4321865832607007, 0.4328486614749784, 0.43335044403744744, 0.43369056819112656, 0.43386767117903485, 0.4338803902441912, 0.43372736262961464, 0.433407225578324, 0.4329186163333385, 0.4322601721376768, 0.43143053023435796, 0.4304283278664008, 0.4292522022768246, 0.427900790708648, 0.4263727304048902, 0.4246666586085701, 0.42278121256270657, 0.42071502951031864, 0.4184667466944251, 0.4160350013580452, 0.4134184307441977, 0.41061567209590166, 0.40762536265617605, 0.40444613966803966, 0.4010766403745117, 0.3975155020186108, 0.39376136184335614, 0.3898128570917666, 0.3856718875339412, 0.38135340304829907, 0.37687561604033887, 0.37225673891555977, 0.3675149840794604, 0.3626685639375404, 0.3577356908952981, 0.3527345773582328, 0.3476834357318435, 0.34260047842162883, 0.33750391783308803, 0.33241196637172027, 0.3273428364430241, 0.3223147404524986, 0.31734589080564296, 0.31244990876246714, 0.30762205100102663, 0.30285298305388775, 0.29813337045361704, 0.29345387873278106, 0.2888051734239463, 0.2841779200596792, 0.27956278417254626, 0.27495043129511415, 0.2703315269599491, 0.2656967366996178, 0.2610367260466867, 0.2563421605337224, 0.2516037056932911, 0.24681202705795965, 0.24196056780307595, 0.23705388167511396, 0.2320993000633293, 0.22710415435697748, 0.22207577594531425, 0.21702149621759495, 0.21194864656307522, 0.20686455837101067, 0.20177656303065683, 0.19669199193126924, 0.19161817646210352, 0.1865624480124152, 0.18153213797145978, 0.17653457772849285, 0.17157709867277013, 0.16666703219354692, 0.161811709680079, 0.15701846252162177, 0.15229462210743094, 0.147647519826762, 0.14308448706887045, 0.13861285522301195, 0.13423995567844205, 0.12997311982441626, 0.12581967905019015, 0.12178696474501934, 0.11788230829815938, 0.11411304109886578, 0.11048649453639409, 0.10700999999999997],
        [0.427801518301832, 0.42899700085194004, 0.4300244312797572, 0.43088317933163284, 0.43157261475391606, 0.4320921072929563, 0.43244102669510265, 0.43261874270670464, 0.43262462507411137, 0.4324580435436722, 0.4321183678617363, 0.4316049677746531, 0.43091721302877173, 0.43005447337044167, 0.42901611854601196, 0.42780151830183205, 0.4264100423842509, 0.42484106053961823, 0.42309394251428317, 0.42116805805459473, 0.4190627769069025, 0.41677746881755573, 0.41431150353290347, 0.41166425079929525, 0.4088350803630803, 0.40582336197060775, 0.402628465368227, 0.39924976030228726, 0.39568661651913783, 0.39193840376512795, 0.38800449178660695, 0.38388719204168353, 0.3796005828355046, 0.375161684184976, 0.37058751610700386, 0.36589509861849456, 0.3611014517363541, 0.35622359547748855, 0.3512785498588042, 0.34628333489720714, 0.34125497060960347, 0.3362104770128993, 0.331166874124001, 0.32614118195981445, 0.32115042053724585, 0.31621160987320146, 0.31133753334534237, 0.30652402777435056, 0.3017626933416627, 0.2970451302287158, 0.292362938616947, 0.28770771868779277, 0.28307107062269027, 0.27844459460307636, 0.273819890810388, 0.2691885594260619, 0.2645422006315353, 0.25987241460824473, 0.2551708015376273, 0.2504289616011198, 0.24563849498015938, 0.24079357074551563, 0.23589863352529097, 0.23096069683692053, 0.2259867741978394, 0.22098387912548284, 0.21595902513728613, 0.21091922575068428, 0.2058714944831127, 0.20082284485200644, 0.19578029037480074, 0.19075084456893068, 0.18574152095183172, 0.1807593330409388, 0.17581129435368723, 0.1709044184075122, 0.16604571871984883, 0.16124220880813236, 0.15650090218979798, 0.15182881238228094, 0.14723295290301636, 0.14272033726943942, 0.13829797899898544, 0.13397289160908948, 0.12975208861718682, 0.12564258354071256, 0.12165138989710199, 0.11778552120379025, 0.11405199097821252, 0.11045781273780406, 0.10701],
        [0.4262988712009305, 0.42756213157389794, 0.4286441437450918, 0.42954508827625215, 0.4302651457291187, 0.4308044966654321, 0.43116332164693183, 0.43134180123535815, 0.43134011599245115, 0.4311584464799508, 0.4307969732595972, 0.4302558768931303, 0.42953533794229015, 0.4286355369688168, 0.42755665453445013, 0.4262988712009306, 0.42486236752999773, 0.42324732408339194, 0.42145392142285315, 0.4194823401101212, 0.41733276070693653, 0.4150053637750387, 0.4125003298761681, 0.40981783957206463, 0.40695807342446844, 0.4039212119951195, 0.40070743584575774, 0.3973169255381232, 0.39374986163395614, 0.39000642469499636, 0.38608679528298395, 0.38199374611484477, 0.3777404185282478, 0.3733425460160477, 0.3688158620710991, 0.36417610018625696, 0.3594389938543757, 0.35462027656831013, 0.34973568182091513, 0.3448009431050451, 0.339831793913555, 0.3348439677392996, 0.32985319807513336, 0.32487521841391115, 0.3199257622484876, 0.31502056307171755, 0.3101714965732362, 0.3053750072298018, 0.30062368171495263, 0.2959101067022274, 0.2912268688651648, 0.2865665548773034, 0.2819217514121822, 0.27728504514333896, 0.27264902274431313, 0.2680062708886428, 0.2633493762498669, 0.2586709255015241, 0.25396350531715267, 0.2492197023702913, 0.24443210333447893, 0.2395956408517113, 0.2347146314378143, 0.22979573757707117, 0.22484562175376502, 0.21987094645217917, 0.21487837415659675, 0.20987456735130094, 0.20486618852057512, 0.1998599001487023, 0.19486236471996582, 0.18988024471864884, 0.18492020262903455, 0.1799889009354062, 0.17509300212204693, 0.17023916867324007, 0.16543406307326874, 0.16068434780641613, 0.15599668535696556, 0.1513777382092001, 0.14683416884740308, 0.1423726397558576, 0.13799981341884693, 0.13372235232065435, 0.12954691894556294, 0.12548017577785603, 0.12152878530181666, 0.1176994100017282, 0.11399871236187377, 0.11043335486653663, 0.10700999999999998],
        [0.42474518410002904, 0.42608197924696695, 0.4272232314637597, 0.4281699958723, 0.4289233275944803, 0.4294842817521936, 0.4298539134673324, 0.4300332778617895, 0.43002343005745763, 0.42982542517622957, 0.42944031833999774, 0.42886916467065506, 0.42811301929009404, 0.4271729373202076, 0.42604997388288846, 0.4247451841000291, 0.4232596230935222, 0.42159434598526074, 0.4197504078971373, 0.4177288639510444, 0.41553076926887506, 0.41315717897252163, 0.41060914818387706, 0.40788773202483397, 0.4049939856172851, 0.4019289640831232, 0.39869372254424074, 0.3952893161225306, 0.39171679993988545, 0.387977229118198, 0.38407165877936095, 0.38000336345615404, 0.3757844953249064, 0.37142942597283374, 0.36695252698715203, 0.36236816995507737, 0.3576907264638259, 0.35293456810061313, 0.3481140664526555, 0.3432435931071688, 0.338337519651369, 0.33341021767247214, 0.32847605875769414, 0.32354941449425123, 0.3186446564693589, 0.31377615627023364, 0.30895482571520416, 0.30417773754705185, 0.29943850473967093, 0.2947307402669558, 0.2900480571028006, 0.2853840682210999, 0.28073238659574784, 0.2760866252006386, 0.2714403970096668, 0.26678731499672637, 0.2621209921357119, 0.2574350414005175, 0.2527230757650376, 0.24797870820316653, 0.24319555168879844, 0.23836933125716617, 0.23350422018885617, 0.22860650382579323, 0.2236824675099023, 0.21873839658310823, 0.21378057638733594, 0.20881529226451018, 0.20384882955655598, 0.19888747360539816, 0.1939375097529616, 0.1890052233411711, 0.18409689971195164, 0.17921882420722804, 0.17437728216892517, 0.169578558938968, 0.16482893985928124, 0.16013471027178988, 0.1555021555184188, 0.15093756094109284, 0.14644721188173687, 0.14203739368227578, 0.1377143916846344, 0.13348449123073777, 0.12935397766251056, 0.1253291363218777, 0.12141625255076414, 0.11762161169109474, 0.11395149908479428, 0.11041220007378773, 0.10700999999999998],
        [0.4231413801250363, 0.4245561400475976, 0.42576021635192185, 0.4267555878975178, 0.427544233543894, 0.4281281321505594, 0.42850926257702265, 0.42868960368279246, 0.4286711343273776, 0.4284558333702868, 0.42804567967102886, 0.4274426520891124, 0.42664872948404614, 0.4256658907153389, 0.4244961146424994, 0.4231413801250363, 0.4216036660224583, 0.4198849511942744, 0.41798721449999304, 0.41591243479912304, 0.4136625909511731, 0.41123966181565214, 0.4086456262520686, 0.4058824631199314, 0.4029521512787493, 0.39985666958803096, 0.39659799690728503, 0.3931781120960204, 0.38959899401374576, 0.3858626215199697, 0.38197097347420117, 0.37792785776834076, 0.3737443984238579, 0.36943354849461363, 0.36500826103446915, 0.36048148909728595, 0.35586618573692524, 0.351175304007248, 0.34642179696211567, 0.34161861765538953, 0.3367787191409308, 0.3319150544726008, 0.3270405767042607, 0.32216823888977164, 0.31731099408299496, 0.31248179533779197, 0.30769054804030155, 0.30293496690577243, 0.29820971898173143, 0.29350947131570515, 0.2888288909552204, 0.2841626449478034, 0.2795054003409811, 0.2748518241822798, 0.2701965835192263, 0.26553434539934706, 0.260859776870169, 0.25616754497921834, 0.25145231677402197, 0.2467087593021062, 0.24193153961099803, 0.2371171950973836, 0.23226974455458865, 0.2273950771250987, 0.22249908195139903, 0.21758764817597526, 0.21266666494131276, 0.20774202138989697, 0.20281960666421348, 0.19790530990674773, 0.19300502025998503, 0.18812462686641096, 0.183270018868511, 0.17844708540877052, 0.17366171562967508, 0.16891979867371001, 0.16422722368336087, 0.15958987980111305, 0.15501365616945215, 0.1505044419308634, 0.14606812622783247, 0.14171059820284473, 0.13743774699838562, 0.13325546175694072, 0.1291696316209953, 0.125186145733035, 0.12131089323554513, 0.11754976327101127, 0.11390864498191881, 0.1103934275107532, 0.10700999999999997],
        [0.4214883824018611, 0.4229842101522403, 0.42425362032573904, 0.425299550129647, 0.4261249367712535, 0.4267327174578482, 0.42712582939672084, 0.42730720979516085, 0.42727979586045783, 0.4270465247999016, 0.4266103338207817, 0.4259741601303875, 0.4251409409360088, 0.4241136134449351, 0.4228951148644559, 0.421488382401861, 0.41989635326443986, 0.41812196465948226, 0.4161681537942776, 0.4140378578761154, 0.41173401411228555, 0.40925955971007744, 0.4066174318767807, 0.40381056781968483, 0.4008419047460798, 0.39771437986325486, 0.39443093037849947, 0.39099449349910365, 0.3874080064323566, 0.38367440638554823, 0.379796630565968, 0.37577904275413404, 0.3716317130234798, 0.36736613802066687, 0.36299381439235706, 0.3585262387852123, 0.35397490784589425, 0.3493513182210647, 0.34466696655738566, 0.3399333495015188, 0.33516196370012585, 0.3303643057998688, 0.32555187244740946, 0.3207361602894095, 0.3159286659725306, 0.31114088614343494, 0.30638169081758343, 0.3016494434856351, 0.2969398810070478, 0.29224874024127995, 0.2875717580477898, 0.2829046712860355, 0.27824321681547504, 0.2735831314955668, 0.268920152185769, 0.26425001574553963, 0.259568459034337, 0.25487121891161935, 0.2501540322368448, 0.24541263586947146, 0.24064276666895773, 0.23584178550786697, 0.23101354931118412, 0.22616353901699937, 0.22129723556340303, 0.21642011988848528, 0.21153767293033632, 0.2066553756270463, 0.20177870891670574, 0.1969131537374046, 0.19206419102723324, 0.1872373017242818, 0.1824379667666405, 0.1776716670923997, 0.1729438836396495, 0.1682600973464802, 0.16362578915098194, 0.15904643999124504, 0.15452753080535966, 0.15007454253141614, 0.14569295610750457, 0.1413882524717153, 0.1371659125621384, 0.1330314173168643, 0.1289902476739831, 0.125047884571585, 0.12120980894776034, 0.11748150174059929, 0.11386844388819206, 0.11037611632862884, 0.10700999999999997],
        [0.4197871140564118, 0.4213657857373454, 0.4227019653013721, 0.4237995683464289, 0.42466251047045184, 0.42529470727137825, 0.42570007434714485, 0.42588252729568815, 0.4258459817149451, 0.42559435320285244, 0.42513155735734676, 0.42446150977636515, 0.4235881260578439, 0.42251532179972034, 0.4212470125999306, 0.41978711405641184, 0.4181395417671005, 0.4163082113299336, 0.414297038342848, 0.4121099384037801, 0.40975082711066685, 0.407223620061445, 0.40453223285405127, 0.4016805810864224, 0.3986725803564952, 0.3955121462622065, 0.39220319440149276, 0.388749640372291, 0.3851553997725379, 0.38142438820017005, 0.37756052125312445, 0.37356873211626307, 0.36945802432214964, 0.365238418990273, 0.3609199372401221, 0.3565126001911859, 0.35202642896295344, 0.3474714446749136, 0.34285766844655546, 0.33819512139736774, 0.33349382464683947, 0.3287637993144597, 0.3240150665197174, 0.31925764738210155, 0.31450156302110094, 0.3097568345562047, 0.3050312813161054, 0.3003239154663112, 0.29563154738153347, 0.290950987436484, 0.28627904600587484, 0.2816125334644172, 0.2769482601868231, 0.27228303654780417, 0.2676136729220719, 0.2629369796843384, 0.2582497672093149, 0.25354884587171345, 0.24883102604624555, 0.2440931181076229, 0.23933193243055742, 0.23454565562411941, 0.2297379792348145, 0.22491397104350724, 0.22007869883106201, 0.21523723037834327, 0.21039463346621554, 0.2055559758755431, 0.20072632538719065, 0.1959107497820224, 0.19111431684090305, 0.18634209434469673, 0.1815991500742681, 0.17689055181048155, 0.17222136733420157, 0.16759666442629256, 0.1630215108676189, 0.1585009744390452, 0.15404012292143585, 0.14964402409565528, 0.14531774574256787, 0.14106635564303813, 0.13689492157793054, 0.13280851132810956, 0.12881219267443955, 0.12491103339778502, 0.12111010127901038, 0.11741446409898015, 0.11382918963855866, 0.11035934567861046, 0.10700999999999997],
        [0.4180384982145973, 0.4197004629793635, 0.42110377319498205, 0.4222533283256045, 0.42315402783538286, 0.4238107711884684, 0.4242284578490132, 0.42441198728116847, 0.42436625894908625, 0.42409617231691804, 0.4236066268488155, 0.4229025220089305, 0.4219887572614145, 0.4208702320704192, 0.4195518459000962, 0.4180384982145973, 0.4163350884780741, 0.41444651615467826, 0.4123776807085616, 0.4101334816038755, 0.4077188183047719, 0.40513859027540233, 0.4023976969799185, 0.399501037882472, 0.39645351244721466, 0.393260020138298, 0.3899254604198738, 0.3864547327560936, 0.38285273661110913, 0.379124371449072, 0.3752745367341341, 0.37130873955745713, 0.36723491751824505, 0.36306161584271157, 0.3587973797570708, 0.35445075448753677, 0.35003028526032354, 0.3455445173016448, 0.3410019958377149, 0.33641126609474764, 0.33178087329895695, 0.32711936267655695, 0.32243527945376177, 0.31773716885678505, 0.31303357611184096, 0.30833304644514353, 0.3036423468049226, 0.2989611310274722, 0.29428727467110194, 0.2896186532941215, 0.28495314245484116, 0.2802886177115703, 0.27562295462261865, 0.27095402874629615, 0.2662797156409127, 0.26159789086477786, 0.25690642997620156, 0.2522032085334936, 0.2474861020949637, 0.24275298621892155, 0.23800173646367723, 0.23323135858164423, 0.2284453791016521, 0.2236484547466342, 0.2188452422395238, 0.21404039830325455, 0.20923857966075962, 0.20444444303497236, 0.1996626451488264, 0.19489784272525498, 0.1901546924871914, 0.18543785115756922, 0.18075197545932173, 0.17610172211538225, 0.1714917478486843, 0.16692670938216123, 0.16241126343874634, 0.15795006674137313, 0.15354777601297492, 0.14920904797648507, 0.14493853935483705, 0.14074090687096413, 0.13662080724779987, 0.13258289720827754, 0.12863183347533053, 0.12477227277189225, 0.12100887182089602, 0.11734628734527532, 0.11378917606796346, 0.1103421947118939, 0.10700999999999998],
        [0.4162434580023263, 0.4179878380547449, 0.4194575659227294, 0.4206585158449158, 0.42159656205993984, 0.4222775788064371, 0.42270744032304375, 0.4228920208483955, 0.42283719462112784, 0.422548835879877, 0.4220328188632786, 0.42129501780996853, 0.42034130695858235, 0.419177560547756, 0.4178096528161256, 0.4162434580023263, 0.4144848503449942, 0.41253970408276547, 0.4104138934542755, 0.40811329269816016, 0.4056437760530553, 0.40301121775759674, 0.40022149205042024, 0.39728047317016174, 0.39419403535545683, 0.39096805284494146, 0.3876083998772513, 0.38412095069102237, 0.3805115795248902, 0.37678616061749076, 0.3729505682074599, 0.36901087878044525, 0.36497397781014346, 0.36084695301726216, 0.3566368921225097, 0.35235088284659466, 0.34799601291022486, 0.34357937003410866, 0.3391080419389543, 0.33458911634546984, 0.3300296809743637, 0.325436823546344, 0.3208176317821189, 0.31617919340239675, 0.3115285961278855, 0.30687292767929364, 0.30221791455309044, 0.2975638383487898, 0.29290961944166694, 0.28825417820699684, 0.2835964350200547, 0.2789353102561157, 0.2742697242904549, 0.26959859749834736, 0.26492085025506834, 0.2602354029358927, 0.25554117591609576, 0.2508370895709527, 0.24612206427573846, 0.24139502040572816, 0.23665487833619714, 0.23190144751594477, 0.22713809368786894, 0.2223690716683921, 0.21759863627393627, 0.212831042320924, 0.2080705446257775, 0.20332139800491902, 0.19858785727477107, 0.19387417725175574, 0.1891846127522955, 0.18452341859281252, 0.17989484958972923, 0.17530316055946787, 0.17075260631845074, 0.16624744168310024, 0.16179192146983853, 0.15739030049508806, 0.15304683357527105, 0.14876577552680986, 0.14455138116612676, 0.14040790530964412, 0.13633960277378415, 0.13235072837496928, 0.12844553692962174, 0.12462828325416384, 0.12090322216501792, 0.11727460847860624, 0.11374669701135115, 0.11032374257967495, 0.10700999999999997],
        [0.4144029165455075, 0.41622750713994006, 0.4177618654007752, 0.41901281668210383, 0.4199871863380161, 0.42069179972260295, 0.42113348218995506, 0.42131905909416284, 0.4212553557893169, 0.4209491976295081, 0.420407409968827, 0.4196368181613641, 0.41864424756121, 0.4174365235224555, 0.4160204713991911, 0.4144029165455075, 0.412590684315495, 0.41059060006324466, 0.4084094891428471, 0.4060541769083925, 0.403531488713972, 0.4008482499136758, 0.3980112858615948, 0.39502742191181944, 0.39190348341844067, 0.38864629573554865, 0.3852626842172343, 0.3817594742175882, 0.37814349109070095, 0.374421560190663, 0.37060050687156537, 0.366686963487957, 0.36268679039622237, 0.3586056549532042, 0.35444922451574556, 0.35022316644068924, 0.3459331480848783, 0.34158483680515533, 0.33718389995836356, 0.33273600490134597, 0.3282468189909452, 0.3237220095840042, 0.3191672440373661, 0.3145881897078737, 0.30999051395236976, 0.3053798841276975, 0.3007610118296641, 0.29613478560993545, 0.29150113825914187, 0.2868600025679138, 0.28221131132688143, 0.27755499732667516, 0.2728909933579252, 0.2682192322112621, 0.2635396466773161, 0.25885216954671747, 0.2541567336100966, 0.2494532716580838, 0.24474171648130943, 0.24002200087040368, 0.23529405761599717, 0.2305584755625243, 0.22581846776963743, 0.22107790335079286, 0.21634065141944714, 0.2116105810890568, 0.20689156147307833, 0.20218746168496804, 0.19750215083818265, 0.19283949804617853, 0.18820337242241214, 0.18359764308034, 0.17902617913341864, 0.17449284969510445, 0.17000152387885392, 0.16555607079812368, 0.16116035956637004, 0.1568182592970495, 0.1525336391036187, 0.14831036809953396, 0.14415231539825182, 0.14006335011322874, 0.13604734135792124, 0.13210815824578584, 0.12824966989027897, 0.12447574540485709, 0.12079025390297672, 0.11719706449809436, 0.11370004630366642, 0.11030306843314949, 0.10700999999999995],
        [0.4125177969700495, 0.4144190664113994, 0.4160151935452804, 0.4173139166149099, 0.41832297386350537, 0.41905010353428457, 0.41950304387046505, 0.41968953311526447, 0.41961730951190024, 0.4192941113035902, 0.4187276767335516, 0.4179257440450025, 0.41689605148115993, 0.4156463372852419, 0.41418433970046586, 0.4125177969700494, 0.41065444733721, 0.4086020290451655, 0.4063682803371334, 0.40396093945633116, 0.40138774464597643, 0.3986564341492869, 0.39577474620948, 0.39275041906977337, 0.3895911909733848, 0.3863048001635317, 0.38289898488343144, 0.37938148337630206, 0.37576003388536083, 0.37204237465382545, 0.36823624392491355, 0.36434880738272124, 0.3603849404748594, 0.3563489460898174, 0.35224512711608447, 0.3480777864421502, 0.34385122695650394, 0.339569751547635, 0.3352376631040329, 0.33085926451418696, 0.32643885866658656, 0.32198074844972113, 0.3174892367520802, 0.3129686264621529, 0.30842322046842874, 0.3038573216593971, 0.29927466590369883, 0.2946767209905806, 0.2900643876894405, 0.2854385667696765, 0.280800159000687, 0.27615006515186985, 0.27148918599262306, 0.26681842229234487, 0.2621386748204334, 0.2574508443462866, 0.25275583163930265, 0.24805453746887973, 0.2433478626044158, 0.23863670781530885, 0.23392197387095728, 0.22920499585688617, 0.2244888461231295, 0.21977703133584842, 0.21507305816120426, 0.21038043326535805, 0.2057026633144711, 0.2010432549747044, 0.19640571491221928, 0.19179354979317687, 0.1872102662837384, 0.18265937105006494, 0.1781443707583178, 0.17366877207465806, 0.16923608166524692, 0.16484980619624562, 0.1605134523338152, 0.15623052674411697, 0.15200453609331202, 0.14783898704756163, 0.1437373862730268, 0.13970324043586888, 0.1357400562022489, 0.13185134023832826, 0.12804059921026795, 0.1243113397842292, 0.12066706862637316, 0.11711129240286106, 0.11364751777985402, 0.11027925142351325, 0.10700999999999995],
        [0.4105890224018611, 0.4125621120455737, 0.4142160722724058, 0.4155595014210756, 0.41660099783030113, 0.4173491598388006, 0.41781258578529223, 0.41799987400849414, 0.41791962284712464, 0.4175804306399017, 0.41699089572554354, 0.41615961644276844, 0.41509519113029447, 0.4138062181268399, 0.4123012957711227, 0.4105890224018611, 0.40867799635777324, 0.4065768159775775, 0.404294079599992, 0.4018383855637345, 0.39921833220752373, 0.39644251787007745, 0.3935195408901141, 0.39045799960635164, 0.38726649235750843, 0.38395361748230245, 0.3805279733194518, 0.37699815820767507, 0.37337277048568995, 0.36966040849221493, 0.36586967056596803, 0.36200822416746736, 0.3580800132444323, 0.35408805086638123, 0.3500353501028332, 0.34592492402330755, 0.34175978569732274, 0.3375429481943981, 0.3332774245840524, 0.32896622793580454, 0.32461237131917353, 0.3202188678036784, 0.31578873045883804, 0.3113249723541714, 0.30683060655919725, 0.302308646143435, 0.29776190404425007, 0.29319239267039693, 0.2886019242984765, 0.2839923112050895, 0.2793653656668375, 0.2747228999603211, 0.2700667263621417, 0.26539865714890015, 0.26072050459719753, 0.2560340809836348, 0.25134119858481324, 0.24664366967733362, 0.24194330653779714, 0.2372419214428048, 0.2325413266689577, 0.2278435615345336, 0.22315157352451745, 0.21846853716557083, 0.21379762698435537, 0.2091420175075329, 0.20450488326176486, 0.1998893987737131, 0.19529873857003907, 0.19073607717740457, 0.18620458912247126, 0.1817074489319008, 0.1772478311323548, 0.17282891025049493, 0.1684538608129828, 0.1641258573464802, 0.15984807437764859, 0.1556236864331498, 0.15145586803964542, 0.14734779372379708, 0.1433026380122665, 0.13932357543171528, 0.1354137805088051, 0.13157642777019765, 0.12781469174255453, 0.12413174695253743, 0.12053076792680799, 0.11701492919202787, 0.1135874052748587, 0.1102513707019622, 0.10700999999999998],
        [0.408617515966851, 0.4106562402189131, 0.4123630234983122, 0.413747256878342, 0.4148183314322965, 0.41558563823346933, 0.4160585683551546, 0.4162465128706457, 0.41615886285323667, 0.41580500937622134, 0.4151943435128936, 0.41433625633654725, 0.41324013892047595, 0.4119153823379735, 0.4103713776623339, 0.408617515966851, 0.4066631883248183, 0.4045177858095299, 0.4021906994942796, 0.39969132045236105, 0.3970290397570682, 0.3942132484816949, 0.39125333769953485, 0.38815869848388196, 0.38493872190803, 0.38160279904527283, 0.37816032096890423, 0.374620678752218, 0.37099326346850797, 0.3672874661910678, 0.36351267799319165, 0.35967702754492453, 0.3557835939033182, 0.35183419372217517, 0.34783064365529826, 0.34377476035649074, 0.33966836047955523, 0.33551326067829457, 0.33131127760651186, 0.3270642279180097, 0.32277392826659124, 0.31844219530605916, 0.3140708456902165, 0.3096616960728659, 0.30521656310781053, 0.30073726344885326, 0.29622575352037306, 0.2916845488290558, 0.28711630465216303, 0.2825236762669566, 0.2779093189506985, 0.27327588798065044, 0.2686260386340744, 0.2639624261882322, 0.25928770592038564, 0.25460453310779646, 0.24991556302772672, 0.24522345095743822, 0.24053085217419273, 0.23584042195525212, 0.2311548155778783, 0.22647672573096994, 0.2218089947499734, 0.21715450238197176, 0.21251612837404837, 0.20789675247328632, 0.20329925442676874, 0.19872651398157892, 0.19418141088479998, 0.18966682488351522, 0.1851856357248078, 0.18074072315576079, 0.17633496692345743, 0.17197124677498096, 0.1676524424574145, 0.16338143371784142, 0.15916110030334463, 0.15499432196100746, 0.15088397843791312, 0.14683294948114475, 0.14284411483778556, 0.13892035425491872, 0.13506454747962748, 0.131279574258995, 0.1275683143401044, 0.12393364747003893, 0.12037845339588178, 0.11690561186471615, 0.11351800262362514, 0.11021850541969203, 0.10701],
        [0.4066042007909276, 0.4087010471078678, 0.4104545691391602, 0.4118748687644506, 0.412972047863385, 0.4137562083156094, 0.41423745200077, 0.4144258807985125, 0.4143315965884831, 0.41396470125032786, 0.41333529666369256, 0.4124534847082235, 0.4113293672635662, 0.40997304620936736, 0.4083946234252724, 0.4066042007909276, 0.40461188018597877, 0.40242776349007214, 0.40006195258285354, 0.3975245493439691, 0.39482565565306477, 0.3919753733897865, 0.3889838044337804, 0.38586105066469234, 0.3826172139621685, 0.3792623962058547, 0.37580669927539706, 0.3722602250504416, 0.3686330754106342, 0.36493535223562096, 0.36117715740504786, 0.3573670312178219, 0.35350726764989476, 0.34959859909647867, 0.345641757952786, 0.34163747661402954, 0.33758648747542164, 0.3334895229321747, 0.3293473153795013, 0.325160597212614, 0.3209301008267249, 0.3166565586170469, 0.31234070297879235, 0.30798326630717376, 0.3035849809974034, 0.2991465794446941, 0.29466924160112307, 0.2901559376462287, 0.28561008531641385, 0.2810351023480818, 0.27643440647763595, 0.27181141544147913, 0.2671695469760145, 0.2625122188176454, 0.2578428487027749, 0.25316485436780606, 0.24848165354914217, 0.24379666398318645, 0.23911330340634185, 0.2344349895550116, 0.22976514016559899, 0.22510704158169828, 0.22046345457566935, 0.21583700852706317, 0.2112303328154308, 0.20664605682032333, 0.20208680992129166, 0.1975552214978869, 0.19305392092966014, 0.1885855375961624, 0.18415270087694474, 0.1797580401515581, 0.1754041847995536, 0.17109376420048228, 0.16682940773389512, 0.16261374477934323, 0.15844940471637764, 0.1543390169245493, 0.15028521078340934, 0.14629061567250876, 0.14235786097139866, 0.13848957605963, 0.13468839031675384, 0.1309569331223213, 0.1272978338558833, 0.12371372189699094, 0.12020722662519526, 0.11678097742004728, 0.11343760366109802, 0.11017973472789858, 0.10700999999999995],
        [0.4045500000000001, 0.40669612888888906, 0.4084892311111112, 0.409940022857143, 0.4110592203174604, 0.41185753968253974, 0.41234569714285724, 0.4125344088888889, 0.4124343911111111, 0.4120563599999999, 0.41141103174603183, 0.41050912253968264, 0.4093613485714286, 0.4079784260317461, 0.40637107111111115, 0.40455000000000013, 0.4025259288888889, 0.40030957396825395, 0.3979116514285715, 0.39534287746031743, 0.3926139682539683, 0.38973564, 0.38671860888888887, 0.383573591111111, 0.3803113028571429, 0.3769424603174605, 0.37347777968253965, 0.3699279771428572, 0.36630376888888894, 0.3626158711111111, 0.358875, 0.3550900488888889, 0.3512626196825398, 0.3473924914285715, 0.34347944317460327, 0.33952325396825395, 0.3355237028571429, 0.3314805688888889, 0.32739363111111114, 0.3232626685714286, 0.3190874603174603, 0.3148677853968254, 0.3106034228571429, 0.30629415174603186, 0.3019397511111111, 0.29754, 0.2930953955555555, 0.28860930730158735, 0.28408582285714284, 0.27952902984126987, 0.27494301587301584, 0.27033186857142855, 0.26569967555555557, 0.2610505244444445, 0.2563885028571428, 0.25171769841269837, 0.2470421987301587, 0.24236609142857143, 0.23769346412698417, 0.2330284044444444, 0.228375, 0.22373706222222223, 0.21911729777777778, 0.21451813714285714, 0.20994201079365082, 0.2053913492063492, 0.20086858285714287, 0.19637614222222216, 0.19191645777777774, 0.18749195999999996, 0.18310507936507933, 0.1787582463492063, 0.17445389142857137, 0.17019444507936501, 0.1659823377777777, 0.16182, 0.15770986222222216, 0.1536543549206349, 0.14965590857142852, 0.1457169536507936, 0.1418399206349206, 0.13802723999999994, 0.13428134222222216, 0.13060465777777774, 0.1269996171428571, 0.12346865079365077, 0.12001418920634917, 0.11663866285714283, 0.1133445022222222, 0.11013413777777775, 0.10700999999999998],
        [0.4024557942192498, 0.4046413447216776, 0.40646604174972606, 0.4079411080666338, 0.4090777664356385, 0.40988723961997875, 0.4103807503828929, 0.41056952148761894, 0.4104647756973951, 0.4100777357754601, 0.40941962448505176, 0.40850166458940834, 0.4073350788517681, 0.4059310900353696, 0.4043009209034507, 0.4024557942192498, 0.40040693274600503, 0.39816555924695507, 0.3957428964853377, 0.39315016722439133, 0.39039859422735423, 0.38749940025746454, 0.3844638080779607, 0.38130304045208097, 0.3780283201430635, 0.37465086991414637, 0.37118191252856797, 0.36763267074956685, 0.3640143673403807, 0.3603382250642481, 0.35661546668440736, 0.35285527306169984, 0.349058657447381, 0.3452245911903093, 0.34135204563934335, 0.33743999214334175, 0.33348740205116295, 0.32949324671166547, 0.32545649747370803, 0.32137612568614915, 0.31725110269784745, 0.3130803998576614, 0.30886298851444977, 0.3045978400170709, 0.30028392571438345, 0.2959202169552459, 0.29150663240041125, 0.2870468799582098, 0.28254561484886576, 0.27800749229260346, 0.2734371675096478, 0.26883929572022286, 0.26421853214455343, 0.2595795320028637, 0.25492695051537817, 0.2502654429023213, 0.24559966438391767, 0.24093427018039162, 0.2362739155119677, 0.2316232555988702, 0.2269869456613239, 0.22236924646479447, 0.21777284095571398, 0.21320001762575588, 0.20865306496659367, 0.20413427146990074, 0.1996459256273507, 0.19519031593061684, 0.19076973087137272, 0.1863864589412918, 0.18204278863204754, 0.17774100843531346, 0.17348340684276295, 0.16927227234606945, 0.16510989343690652, 0.1609985586069476, 0.15694055634786613, 0.15293817515133556, 0.14899370350902943, 0.1451094299126211, 0.14128764285378415, 0.13753063082419195, 0.13384068231551802, 0.13022008581943584, 0.12667112982761883, 0.1231961028317405, 0.1197972933234743, 0.11647698979449367, 0.1132374807364721, 0.11008105464108303, 0.10700999999999997],
        [0.4003222940709509, 0.40253760569894026, 0.40438607506816865, 0.40587932583303227, 0.40702898164792634, 0.40784666616724674, 0.40834400304538915, 0.4085326159367493, 0.4084241284957227, 0.4080301643767054, 0.4073623472340928, 0.40643230072228076, 0.40525164849566475, 0.40383201420864073, 0.4021850215156042, 0.4003222940709509, 0.39825545552907643, 0.39599612954437685, 0.3935559397712475, 0.39094650986408414, 0.38817946347728244, 0.3852664242652382, 0.38221901588234714, 0.3790488619830048, 0.37576758622160705, 0.3723868122525494, 0.3689181637302277, 0.36537326430903755, 0.3617637376433746, 0.3581012073876346, 0.35439729719621343, 0.3506614114432114, 0.34689407738154965, 0.3430936029838539, 0.3392582962227496, 0.3353864650708631, 0.33147641750081996, 0.3275264614852459, 0.3235349049967669, 0.31950005600800835, 0.3154202224915966, 0.31129371242015713, 0.30711883376631577, 0.3028938945026984, 0.2986172026019307, 0.2942870660366385, 0.2899029281431749, 0.2854687737128018, 0.2809897229005085, 0.27647089586128404, 0.27191741275011755, 0.26733439372199835, 0.2627269589319155, 0.25810022853485814, 0.25345932268581567, 0.24880936153977695, 0.24415546525173146, 0.23950275397666826, 0.23485634786957654, 0.2302213670854453, 0.225602931779264, 0.22100567582866656, 0.21643228800186687, 0.21188497078972374, 0.20736592668309592, 0.2028773581728422, 0.19842146774982128, 0.194000457904892, 0.18961653112891327, 0.1852718899127436, 0.18096873674724204, 0.17670927412326715, 0.17249570453167776, 0.1683302304633327, 0.16421505440909076, 0.16015237885981062, 0.15614440630635115, 0.15219333923957107, 0.14830138015032918, 0.14447073152948428, 0.14070359586789508, 0.1370021756564204, 0.13336867338591904, 0.12980529154724976, 0.1263142326312713, 0.1228976991288425, 0.11955789353082209, 0.11629701832806888, 0.11311727601144159, 0.11002086907179903, 0.10700999999999998],
        [0.3981501676766503, 0.4003860858966342, 0.40225091549900305, 0.4037565807289214, 0.4049150058315536, 0.4057381150520639, 0.406237832635617, 0.4064260828273772, 0.40631478987250896, 0.40591587801617707, 0.40524127150354544, 0.40430289457977875, 0.40311267149004143, 0.4016825264794979, 0.4000243837933128, 0.39815016767665024, 0.3960718023746748, 0.39380121213255104, 0.3913503211954432, 0.38873105380851597, 0.38595533421693373, 0.3830350866658604, 0.37998223540046133, 0.3768087046659004, 0.3735264187073422, 0.37014730176995103, 0.3666832780988915, 0.36314627193932797, 0.35954820753642486, 0.3559010091353467, 0.35221660098125784, 0.34850455054122526, 0.3447649981699269, 0.3409957274439426, 0.33719452193985255, 0.333359165234237, 0.3294874409036762, 0.32557713252475007, 0.3216260236740392, 0.31763189792812335, 0.31359253886358285, 0.3095057300569979, 0.30536925508494883, 0.3011808975240154, 0.2969384409507781, 0.29263966894181714, 0.28828364853901645, 0.283874580645476, 0.2794179496295997, 0.2749192398597912, 0.2703839357044545, 0.26581752153199334, 0.26122548171081167, 0.25661330060931303, 0.25198646259590174, 0.24735045203898115, 0.2427107533069554, 0.23807285076822812, 0.23344222879120335, 0.22882437174428472, 0.22422476399587618, 0.21964833750983953, 0.2150978146318687, 0.21057536530311546, 0.20608315946473177, 0.20162336705786943, 0.19719815802368038, 0.19280970230331648, 0.18846016983792954, 0.18415173056867162, 0.17988655443669446, 0.17566681138314985, 0.17149467134918983, 0.16737230427596614, 0.16330188010463076, 0.15928556877633557, 0.1553255402322324, 0.15142396441347308, 0.14758301126120954, 0.14380485071659366, 0.14009165272077728, 0.1364455872149123, 0.1328688241401506, 0.12936353343764412, 0.12593188504854458, 0.12257604891400398, 0.11929819497517412, 0.11610049317320693, 0.11298511344925426, 0.10995422574446798, 0.10701],
        [0.39594008315789464, 0.3981879593907167, 0.4000621474747931, 0.40157477732688385, 0.4027379788637494, 0.4035638820021503, 0.404064616658847, 0.40425231275059975, 0.40413910019416915, 0.4037371089063156, 0.40305846880379953, 0.40211530980338117, 0.40091976182182115, 0.3994839547758798, 0.39782001858231736, 0.39594008315789464, 0.3938562784193717, 0.39158073428350926, 0.38912558066706754, 0.386502947486807, 0.38372496465948824, 0.3808037621018712, 0.3777514697307168, 0.3745802174627852, 0.37130213521483696, 0.3679293529036325, 0.36447400044593203, 0.36094820775849623, 0.3573641047580853, 0.35373382136145975, 0.35006948748537997, 0.3463807768635433, 0.342667538497394, 0.33892716520531313, 0.3351570498056821, 0.33135458511688154, 0.3275171639572932, 0.32364217914529775, 0.31972702349927656, 0.3157690898376106, 0.31176577097868113, 0.3077144597408693, 0.3036125489425563, 0.2994574314021233, 0.2952464999379509, 0.29097714736842095, 0.2866481593431057, 0.28226389283634457, 0.2778300976536674, 0.273352523600605, 0.2688369204826881, 0.26428903810544685, 0.25971462627441194, 0.2551194347951137, 0.2505092134730827, 0.24588971211384936, 0.24126668052294428, 0.23664586850589803, 0.2320330258682409, 0.22743390241550346, 0.22285424795321632, 0.21829921870431443, 0.21377159656135147, 0.20927356983428563, 0.2048073268330752, 0.20037505586767843, 0.19597894524805337, 0.19162118328415842, 0.18730395828595184, 0.18302945856339176, 0.17879987242643636, 0.17461738818504396, 0.17048419414917287, 0.16640247862878113, 0.16237442993382706, 0.15840223637426898, 0.1544880862600649, 0.15063416790117323, 0.14684266960755216, 0.1431157796891599, 0.13945568645595463, 0.13586457821789466, 0.1323446432849382, 0.1288980699670435, 0.12552704657416872, 0.12223376141627212, 0.11902040280331194, 0.11588915904524641, 0.11284221845203374, 0.1098817693336322, 0.10700999999999995],
        [0.3936927086362314, 0.39594440025714583, 0.3978213554281031, 0.3993358201995027, 0.400500040621744, 0.40132626274522676, 0.40182673262035046, 0.40201369629751477, 0.4018993998271188, 0.40149608925956265, 0.4008160106452457, 0.3998714100345673, 0.3986745334779271, 0.3972376270257248, 0.39557293672835975, 0.39369270863623146, 0.3916091887997395, 0.38933462326928364, 0.38688125809526325, 0.38426133932807777, 0.381487113018127, 0.3785708252158103, 0.3755247219715272, 0.37236104933567726, 0.36909205335866024, 0.36572998009087554, 0.3622870755827225, 0.358775585884601, 0.3552077570469103, 0.3515958351200501, 0.34795206615442, 0.34428617691796753, 0.3405978170488327, 0.33688411690270376, 0.33314220683526863, 0.3293692172022158, 0.325562278359233, 0.3217185206620087, 0.3178350744662307, 0.3139090701275875, 0.3099376380017669, 0.30591790844445715, 0.3018470118113465, 0.297722078458123, 0.29354023874047463, 0.2892986230140897, 0.2849958263106135, 0.28063630236551995, 0.2762259695902404, 0.2717707463962061, 0.26727655119484806, 0.26274930239759786, 0.2581949184158865, 0.2536193176611449, 0.24902841854480498, 0.2444281394782974, 0.23982439887305365, 0.23522311514050484, 0.23063020669208223, 0.22605159193921695, 0.22149318929334044, 0.2169603066080924, 0.21245580950594764, 0.20798195305158929, 0.2035409923097007, 0.19913518234496522, 0.19476677822206612, 0.19043803500568665, 0.18615120776051025, 0.18190855155122018, 0.17771232144249974, 0.17356477249903224, 0.16946815978550095, 0.1654247383665891, 0.1614367633069801, 0.15750648967135733, 0.15363617252440398, 0.14982806693080336, 0.14608442795523882, 0.14240751066239363, 0.1387995701169511, 0.13526286138359456, 0.13179963952700727, 0.1284121596118726, 0.12510267670287384, 0.12187344586469429, 0.11872672216201718, 0.11566476065952593, 0.11268981642190375, 0.109804144513834, 0.10700999999999997],
        [0.3914087122332074, 0.39365658257187863, 0.39553012379149705, 0.3970416139193605, 0.39820333098276656, 0.39902755300901316, 0.39952655802539805, 0.3997126240592187, 0.3995980291377731, 0.399195051288359, 0.398515968538274, 0.39757305891481587, 0.39637860044528256, 0.3949448711569715, 0.3932841490771805, 0.39140871223320745, 0.38933083865234985, 0.38706280636190576, 0.38461689338917265, 0.38200537776144844, 0.3792405375060307, 0.3763346506502173, 0.37329999522130597, 0.37014884924659436, 0.3668934907533804, 0.3635461977689616, 0.36011924832063574, 0.35662492043570065, 0.353075492141454, 0.3494832414651936, 0.34586044643421715, 0.3422168372122995, 0.3385519525091242, 0.3348627831708517, 0.33114632004364275, 0.3273995539736579, 0.32361947580705763, 0.3198030763900026, 0.31594734656865353, 0.3120492771891707, 0.308105859097715, 0.30411408314044674, 0.300070940163527, 0.29597342101311597, 0.2918185165353742, 0.2876032175764625, 0.28332601519670925, 0.27899140131311484, 0.2746053680568469, 0.27017390755907383, 0.26570301195096396, 0.26119867336368496, 0.25666688392840514, 0.25211363577629237, 0.24754492103851503, 0.2429667318462409, 0.23838506033063836, 0.23380589862287537, 0.22923523885412, 0.2246790731555403, 0.2201433936583045, 0.21563358841717462, 0.21115262918128927, 0.2067028836233809, 0.20228671941618223, 0.19790650423242573, 0.19356460574484396, 0.18926339162616956, 0.18500522954913504, 0.18079248718647306, 0.17662753221091615, 0.17251273229519679, 0.16845045511204768, 0.16444306833420128, 0.1604929396343903, 0.15660243668534723, 0.15277392715980465, 0.14900977873049506, 0.14531235907015114, 0.14168403585150546, 0.13812717674729055, 0.13464414943023897, 0.13123732157308327, 0.12790906084855616, 0.12466173492939008, 0.12149771148831764, 0.11841935819807141, 0.11542904273138396, 0.11252913276098785, 0.10972199595961567, 0.10701],
        [0.3890887620703693, 0.3913256804108722, 0.39319003699753874, 0.39469406305904003, 0.3958499898240467, 0.3966700485212298, 0.39716647037926034, 0.3973514866268091, 0.3972373284925469, 0.39683622720514516, 0.39616041399327445, 0.3952221200856058, 0.39403357671080996, 0.39260701509755797, 0.3909546664745208, 0.38908876207036935, 0.38702153311377435, 0.3847652108334071, 0.3823320264579383, 0.3797342112160389, 0.3769839963363798, 0.374093613047632, 0.3710752925784664, 0.36794126615755374, 0.3647037650135654, 0.36137502037517183, 0.3579672634710442, 0.3544927255298534, 0.3509636377802703, 0.34739223145096587, 0.3437907377706111, 0.3401688442543412, 0.3365260635631499, 0.332859364644495, 0.32916571644583453, 0.32544208791462653, 0.3216854479983288, 0.31789276564439933, 0.3140610098002961, 0.3101871494134772, 0.3062681534314004, 0.3023009908015239, 0.2982826304713055, 0.2942100413882033, 0.29008019249967504, 0.2858900527531788, 0.28163809175656346, 0.27732878175924125, 0.2729680956710154, 0.26856200640168887, 0.26411648686106504, 0.2596375099589471, 0.25513104860513786, 0.25060307570944085, 0.24605956418165895, 0.24150648693159546, 0.23694981686905356, 0.23239552690383636, 0.2278495899457469, 0.22331797890458846, 0.21880666669016424, 0.21432105132756193, 0.2098642313030085, 0.2054387302180154, 0.201047071674094, 0.19669177927275588, 0.19237537661551263, 0.18810038730387552, 0.18386933493935628, 0.17968474312346633, 0.17554913545771716, 0.17146503554362025, 0.16743496698268706, 0.16346145337642914, 0.15954701832635795, 0.15569418543398508, 0.15190547830082196, 0.14818342052838007, 0.14453053571817093, 0.14094934747170598, 0.1374423793904968, 0.13401215507605488, 0.13066119812989163, 0.1273920321535187, 0.12420718074844744, 0.12110916751618943, 0.11810051605825611, 0.11518374997615903, 0.11236139287140964, 0.10963596834551946, 0.10701],
        [0.38673352626926427, 0.3889528678500843, 0.39080267947879266, 0.39229507219112425, 0.393442157022814, 0.39425604500959693, 0.39474884718720843, 0.3949326745913831, 0.3948196382578561, 0.3944218492223627, 0.39375141852063766, 0.392820457188416, 0.3916410762614328, 0.3902253867754231, 0.38858549976612194, 0.3867335262692643, 0.38468157732058517, 0.38244176395581975, 0.38002619721070285, 0.3774469881209696, 0.3747162477223551, 0.3718460870505942, 0.36884861714142203, 0.36573594903057355, 0.3625201937537839, 0.3592134623467881, 0.35582786584532095, 0.3523755152851178, 0.3488685217019134, 0.3453189961314429, 0.34173904960944124, 0.3381382845518944, 0.3345162688957912, 0.33087006195837115, 0.3271967230568742, 0.32349331150854005, 0.3197568866306082, 0.3159845077403184, 0.3121732341549104, 0.30832012519162394, 0.30442224016769837, 0.3004766384003739, 0.2964803792068899, 0.2924305219044861, 0.2883241258104022, 0.28415825024187785, 0.2799314217453459, 0.27564803578401204, 0.27131395505027406, 0.2669350422365309, 0.262517160035181, 0.2580661711386228, 0.2535879382392548, 0.24908832402947548, 0.24457319120168333, 0.24004840244827674, 0.23551982046165437, 0.23099330793421458, 0.22647472755835588, 0.22196994202647666, 0.2174848140309756, 0.2130246825352556, 0.2085927915867376, 0.20419186150384727, 0.19982461260501017, 0.19549376520865172, 0.1912020396331975, 0.18695215619707317, 0.1827468352187042, 0.17858879701651617, 0.17448076190893458, 0.17042545021438496, 0.1664255822512929, 0.16248387833808398, 0.15860305879318362, 0.15478584393501751, 0.1510349540820111, 0.14735310955259, 0.1437430306651797, 0.14020743773820585, 0.13674905109009386, 0.13337059103926932, 0.1300747779041578, 0.1268643320031849, 0.1237419736547761, 0.1207104231773569, 0.11777240088935294, 0.11493062710918972, 0.11218782215529276, 0.10954670634608768, 0.10701],
        [0.38434367295143934, 0.38653931896547244, 0.38836963566782273, 0.38984654588819595, 0.39098197245629807, 0.39178783820183516, 0.39227606595451325, 0.39245857854403815, 0.3923472988001159, 0.3919541495524524, 0.3912910536307536, 0.39036993386472557, 0.3892027130840742, 0.38780131411850544, 0.38617765979772517, 0.3843436729514395, 0.3823112764093542, 0.3800923930011754, 0.377698945556609, 0.37514285690536087, 0.37243604987713713, 0.3695904473016436, 0.3666179720085865, 0.3635305468276714, 0.3603400945886045, 0.35705853812109173, 0.35369780025483905, 0.35026980381955214, 0.3467864716449375, 0.3432597265607006, 0.33970149139654765, 0.33612124461276105, 0.3325186871919295, 0.32889107574721826, 0.32523566689179245, 0.3215497172388173, 0.31783048340145814, 0.31407522199287996, 0.31028118962624823, 0.30644564291472787, 0.3025658384714842, 0.2986390329096826, 0.2946624828424881, 0.2906334448830659, 0.2865491756445812, 0.2824069317401994, 0.2782053709182272, 0.2739487554675393, 0.26964274881215156, 0.2652930143760802, 0.26090521558334145, 0.2564850158579513, 0.252038078623926, 0.24757006730528172, 0.24308664532603455, 0.23859347611020057, 0.234096223081796, 0.2296005496648371, 0.22511211928333974, 0.22063659536132021, 0.21617964132279469, 0.21174646923625665, 0.20734048574810882, 0.20296464614923157, 0.19862190573050495, 0.19431521978280916, 0.19004754359702453, 0.18582183246403103, 0.18164104167470901, 0.1775081265199386, 0.17342604229060016, 0.16939774427757354, 0.16542618777173912, 0.16151432806397714, 0.15766512044516767, 0.15388152020619106, 0.15016648263792728, 0.1465229630312567, 0.1429539166770594, 0.13946229886621564, 0.13605106488960556, 0.13272317003810938, 0.12948156960260726, 0.1263292188739795, 0.1232690731431061, 0.12030408770086737, 0.11743721783814348, 0.11467141884581462, 0.11200964601476093, 0.10945485463586267, 0.10701000000000001],
        [0.3819198702384413, 0.38408620783299385, 0.3858924899971927, 0.3873503887228378, 0.38847157600172844, 0.38926772382566444, 0.38975050418644536, 0.38993158907587117, 0.3898226504857411, 0.3894353604078549, 0.3887813908340125, 0.3878724137560132, 0.38672010116565675, 0.38533612505474296, 0.3837321574150712, 0.3819198702384413, 0.37991093551665284, 0.3777170252415055, 0.3753498114047989, 0.3728209659983328, 0.3701421610139066, 0.3673250684433202, 0.364381360278373, 0.3613227085108648, 0.3581607851325953, 0.3549072621353641, 0.3515738115109707, 0.348172105251215, 0.34471381534789636, 0.34121061379281464, 0.33767417257776944, 0.3341138109447427, 0.3305294371364462, 0.3269186066457737, 0.32327887496561913, 0.3196077975888767, 0.31590293000844016, 0.3121618277172035, 0.30838204620806076, 0.30456114097390574, 0.30069666750763263, 0.2967861813021352, 0.2928272378503075, 0.2888173926450435, 0.2847542011792371, 0.28063521894578225, 0.2764593050303771, 0.27223053288993565, 0.26795427957417606, 0.2636359221328166, 0.2592808376155756, 0.25489440307217115, 0.25048199555232137, 0.24604899210574446, 0.2416007697821588, 0.23714270563128234, 0.23268017670283353, 0.22821856004653032, 0.22376323271209117, 0.21931957174923394, 0.21489295420767715, 0.21048839862656604, 0.20610948950275423, 0.20175945282252278, 0.19744151457215245, 0.1931589007379242, 0.18891483730611894, 0.18471255026301747, 0.18055526559490087, 0.17644620928804983, 0.17238860732874534, 0.16838568570326828, 0.16444067039789953, 0.16055678739892, 0.15673726269261057, 0.15298532226525213, 0.1493041921031255, 0.14569709819251173, 0.14216726651969158, 0.13871792307094596, 0.13535229383255584, 0.13207360479080202, 0.1288850819319654, 0.12578995124232698, 0.12279143870816756, 0.11989277031576799, 0.11709717205140922, 0.11440786990137217, 0.11182808985193766, 0.10936105788938665, 0.10700999999999998],
        [0.37946278625181723, 0.381594708528606, 0.3833728268994671, 0.38480850526763277, 0.38591310753633473, 0.38669799760880513, 0.3871745393882762, 0.3873540967779795, 0.38724803368114724, 0.38686771400101183, 0.38622450164080474, 0.3853297605037582, 0.3841948544931041, 0.3828311475120747, 0.3812500034639017, 0.3794627862518173, 0.37748085977905343, 0.37531558794884223, 0.37297833466441566, 0.37048046382900557, 0.36783333934584417, 0.36504832511816343, 0.3621367850491952, 0.3591100830421718, 0.355979583000325, 0.3527566488268868, 0.3494526444250894, 0.3460789336981646, 0.34264688054934456, 0.3391678488818612, 0.33565320259894654, 0.3321120700556416, 0.3285446374142228, 0.3249488552887755, 0.3213226742933849, 0.3176640450421368, 0.3139709181491163, 0.31024124422840893, 0.30647297389409994, 0.3026640577602748, 0.29881244644101895, 0.2949160905504175, 0.29097294070255636, 0.2869809475115205, 0.2829380615913953, 0.27884223355626625, 0.2746925898369657, 0.2704929601313135, 0.26624834995387614, 0.2619637648192205, 0.2576442102419133, 0.2532946917365211, 0.24892021481761087, 0.24452578499974909, 0.24011640779750254, 0.2356970887254379, 0.231272833298122, 0.22684864703012145, 0.22242953543600302, 0.2180205040303333, 0.2136265583276792, 0.20925245790218497, 0.2049019785663061, 0.20057865019207574, 0.19628600265152688, 0.1920275658166928, 0.18780686955960652, 0.18362744375230114, 0.1794928182668099, 0.17540652297516582, 0.17137208774940213, 0.16739304246155173, 0.16347291698364802, 0.15961524118772394, 0.15582354494581266, 0.15210135812994732, 0.14845221061216102, 0.14487963226448686, 0.14138715295895796, 0.13797830256760749, 0.13465661096246856, 0.13142560801557426, 0.12828882359895777, 0.12524978758465213, 0.12231202984469056, 0.11947908025110607, 0.11675446867593184, 0.11414172499120102, 0.11164437906894667, 0.10926596078120193, 0.10700999999999997],
        [0.3769730891131142, 0.37906599512826644, 0.3808122308072099, 0.3822228000951638, 0.3833087069373467, 0.38408095527897784, 0.3845505490652762, 0.38472849224146066, 0.3846257887527501, 0.38425344254436383, 0.38362245756152064, 0.3827438377494394, 0.38162858705333913, 0.38028770941843887, 0.3787322087899576, 0.3769730891131143, 0.3750213543331278, 0.37288800839521724, 0.37058405524460164, 0.3681204988264997, 0.36550834308613067, 0.3627585919687134, 0.3598822494194667, 0.35689031938361004, 0.35379380580636194, 0.3506037126329415, 0.3473310438085678, 0.3439868032784597, 0.34058199498783615, 0.33712762288191617, 0.33363469090591874, 0.3301121084532594, 0.3265604067101407, 0.32297802231096123, 0.3193633918901201, 0.3157149520820162, 0.3120311395210486, 0.308310390841616, 0.30455114267811745, 0.3007518316649519, 0.29691089443651814, 0.29302676762721536, 0.28909788787144225, 0.28512269180359784, 0.281099616058081, 0.27702709726929076, 0.27290459109316345, 0.2687356292717854, 0.2645247625687803, 0.2602765417477718, 0.25599551757238403, 0.2516862408062403, 0.2473532622129647, 0.2430011325561807, 0.23863440259951227, 0.23425762310658296, 0.22987534484101668, 0.22549211856643722, 0.22111249504646824, 0.21674102504473333, 0.21238225932485655, 0.20804063425911465, 0.20372012865439668, 0.19942460692624525, 0.19515793349020255, 0.19092397276181097, 0.18672658915661283, 0.18256964709015056, 0.17845701097796648, 0.1743925452356028, 0.17038011427860209, 0.16642358252250652, 0.16252681438285854, 0.15869367427520037, 0.1549280266150745, 0.15123373581802327, 0.1476146662995889, 0.1440746824753138, 0.14061764876074034, 0.13724742957141087, 0.1339678893228677, 0.13078289243065322, 0.12769630331030973, 0.12471198637737964, 0.12183380604740526, 0.1190656267359289, 0.11641131285849293, 0.11387472883063973, 0.1114597390679116, 0.10917020798585092, 0.10701000000000002],
        [0.374451446943879, 0.3765012417079325, 0.37821228615298513, 0.37959517777801344, 0.3806605140819937, 0.3814188925639025, 0.3818809107227162, 0.38205716605741147, 0.3819582560669643, 0.3815947782503518, 0.3809773301065501, 0.3801165091345355, 0.37902291283328476, 0.377707138701774, 0.37617978423898, 0.3744514469438791, 0.3725327243154476, 0.3704342138526622, 0.3681665130544992, 0.3657402194199352, 0.36316593044794643, 0.36045424363750955, 0.35761575648760097, 0.35466106649719714, 0.35160077116527455, 0.34844546799080955, 0.3452057544727786, 0.34189222811015824, 0.3385154864019249, 0.33508612684705513, 0.3316147469445252, 0.3281100126453979, 0.3245728637090811, 0.3210023083470687, 0.31739735477085496, 0.3137570111919334, 0.3100802858217988, 0.30636618687194445, 0.30261372255386476, 0.29882190107905376, 0.2949897306590054, 0.2911162195052138, 0.287200375829173, 0.2832412078423769, 0.2792377237563194, 0.2751889317824949, 0.2710946745541401, 0.26695813239146365, 0.26278332003641675, 0.2585742522309507, 0.2543349437170171, 0.2500694092365673, 0.2457816635315526, 0.24147572134392442, 0.23715559741563416, 0.23282530648863306, 0.22848886330487267, 0.22415028260630435, 0.21981357913487934, 0.21548276763254917, 0.2111618628412652, 0.20685491489335586, 0.20256611548265813, 0.19829969169338596, 0.19405987060975338, 0.18985087931597464, 0.1856769448962635, 0.1815422944348341, 0.1774511550159005, 0.17340775372367678, 0.16941631764237688, 0.16548107385621483, 0.16160624944940474, 0.15779607150616054, 0.15405476711069638, 0.1503865633472263, 0.1467956872999642, 0.1432863660531242, 0.13986282669092037, 0.13652929629756666, 0.13329000195727708, 0.1301491707542658, 0.12711102977274674, 0.12417980609693403, 0.12135972681104162, 0.11865501899928359, 0.11606990974587394, 0.11360862613502674, 0.11127539525095598, 0.10907444417787572, 0.10701000000000001],
        [0.37189852786565847, 0.3739016223435614, 0.3755745773693566, 0.3769275428887645, 0.3779706688475051, 0.37871410519129917, 0.3791680018658671, 0.37934250881692905, 0.3792477759902054, 0.37889395333141673, 0.3782911907862833, 0.3774496383005257, 0.3763794458198638, 0.3750907632900186, 0.3735937406567099, 0.3718985278656586, 0.3700152748625846, 0.3679541315932086, 0.36572524800325107, 0.36333877403843207, 0.3608048596444722, 0.35813365476709175, 0.3553353093520111, 0.3524199733449506, 0.34939779669163096, 0.3462789293377721, 0.3430735212290945, 0.3397917223113188, 0.33644368253016516, 0.3330395518313539, 0.32958948016060563, 0.3261018691398589, 0.32257812709592554, 0.31901791403183566, 0.3154208899506194, 0.31178671485530696, 0.3081150487489285, 0.30440555163451394, 0.3006578835150935, 0.2968717043936974, 0.2930466742733558, 0.28918245315709856, 0.2852787010479562, 0.28133507794895857, 0.27735124386313575, 0.2733268587935181, 0.2692622059750659, 0.26516006157046057, 0.2610238249743137, 0.256856895581237, 0.2526626727858422, 0.24844455598274084, 0.24420594456654468, 0.23995023793186532, 0.23568083547331453, 0.23140113658550382, 0.22711454066304493, 0.22282444710054955, 0.21853425529262935, 0.2142473646338959, 0.20996717451896096, 0.2056972870009098, 0.20144211476672247, 0.19720627316185255, 0.19299437753175372, 0.18881104322187967, 0.18466088557768395, 0.18054851994462026, 0.17647856166814235, 0.17245562609370374, 0.16848432856675816, 0.16456928443275923, 0.16071510903716052, 0.15692641772541585, 0.1532078258429788, 0.14956394873530302, 0.1459994017478421, 0.14251880022604976, 0.13912675951537964, 0.13582789496128536, 0.13262682190922062, 0.12952815570463905, 0.12653651169299426, 0.12365650521973999, 0.12089275163032984, 0.11824986627021747, 0.11573246448485651, 0.11334516161970062, 0.11109257302020348, 0.1089793140318187, 0.10700999999999998],
        [0.3693149999999999, 0.3712683111111111, 0.3729006888888889, 0.37422180000000005, 0.37524131111111103, 0.3759688888888889, 0.3764142000000001, 0.37658691111111114, 0.3764966888888888, 0.37615319999999997, 0.37556611111111105, 0.37474508888888897, 0.3736998, 0.37243991111111113, 0.37097508888888897, 0.369315, 0.36746931111111103, 0.3654476888888889, 0.36325979999999997, 0.3609153111111112, 0.3584238888888889, 0.3557952, 0.35303891111111096, 0.3501646888888888, 0.3471821999999999, 0.34410111111111114, 0.3409310888888888, 0.3376818, 0.3343629111111111, 0.33098408888888886, 0.32755500000000004, 0.3240837644444443, 0.3205723155555556, 0.31702104, 0.31343032444444435, 0.3098005555555555, 0.30613211999999995, 0.3024254044444445, 0.29868079555555554, 0.29489867999999997, 0.2910794444444444, 0.2872234755555555, 0.28333116, 0.27940288444444444, 0.27543903555555554, 0.27144, 0.2674065511111111, 0.2633410088888889, 0.25924608000000005, 0.2551244711111111, 0.25097888888888886, 0.24681203999999998, 0.24262663111111113, 0.23842536888888888, 0.23421096000000002, 0.22998611111111106, 0.2257535288888889, 0.22151591999999998, 0.21727599111111112, 0.21303644888888879, 0.2088, 0.2045697377777778, 0.20035030222222222, 0.19614671999999997, 0.19196401777777777, 0.18780722222222226, 0.18368135999999996, 0.17959145777777774, 0.17554254222222218, 0.17153963999999997, 0.16758777777777778, 0.1636919822222222, 0.15985728000000002, 0.1560886977777778, 0.1523912622222222, 0.14877000000000004, 0.14522993777777782, 0.14177610222222226, 0.13841352000000004, 0.1351472177777778, 0.13198222222222225, 0.12892356000000002, 0.12597625777777782, 0.12314534222222229, 0.12043584000000009, 0.1178527777777778, 0.11540118222222227, 0.11308608000000005, 0.11091249777777779, 0.10888546222222223, 0.10701],
        [0.36670198084617606, 0.3686028947209103, 0.3701925870216816, 0.37148021062133624, 0.3724749183927204, 0.3731858632086809, 0.37362219794206386, 0.3737930754657156, 0.3737076486524827, 0.3733750703752114, 0.37280449350674827, 0.3720050709199395, 0.37098595548763136, 0.36975630008267063, 0.36832525757790335, 0.3667019808461763, 0.36489562276033505, 0.36291533619322697, 0.3607702740176979, 0.3584695891065943, 0.3560224343327627, 0.3534379625690491, 0.3507253266883004, 0.34789367956336265, 0.34495217406708245, 0.34190996307230587, 0.33877619945187964, 0.33556003607864976, 0.332270625825463, 0.3289171215651655, 0.3255086761706038, 0.3220531139739912, 0.31855294514501004, 0.3150093513127092, 0.3114235141061375, 0.30779661515434464, 0.30412983608637945, 0.3004243585312909, 0.29668136411812834, 0.2929020344759406, 0.28908755123377705, 0.28523909602068676, 0.28135785046571876, 0.2774449961979223, 0.2735017148463462, 0.26952918804003967, 0.2655287238627184, 0.26150213621676305, 0.2574513654592207, 0.25337835194713826, 0.2492850360375633, 0.2451733580875426, 0.24104525845412345, 0.2369026774943529, 0.232747555565278, 0.22858183302394597, 0.2244074502274039, 0.220226347532699, 0.21604046529687831, 0.21185174387698885, 0.207662123630078, 0.2034741312193922, 0.19929263853297657, 0.19512310376507558, 0.19097098510993402, 0.18684174076179633, 0.182740828914907, 0.1786737077635108, 0.17464583550185217, 0.17066267032417573, 0.166729670424726, 0.16285229399774778, 0.1590359992374853, 0.15528624433818333, 0.15160848749408648, 0.14800818689943931, 0.14449080074848628, 0.14106178723547208, 0.13772660455464122, 0.13449071090023837, 0.13135956446650796, 0.12833862344769473, 0.12543334603804315, 0.12264919043179781, 0.11999161482320332, 0.11746607740650421, 0.11507803637594509, 0.11283294992577056, 0.11073627625022511, 0.10879347354355338, 0.10700999999999998],
        [0.36406238541436453, 0.3659086104207766, 0.3674537655879795, 0.3687064640105242, 0.36967531878296206, 0.37036894299984396, 0.37079594975572167, 0.3709649521451459, 0.37088456326266805, 0.3705633962028394, 0.3700100640602109, 0.369233179929334, 0.3682413569047598, 0.36704320808103924, 0.36564734655272374, 0.36406238541436464, 0.36229693776051286, 0.36035961668571986, 0.35825903528453656, 0.3560038066515143, 0.35360254388120443, 0.35106386006815776, 0.3483963683069257, 0.34560868169205955, 0.3427094133181105, 0.3397071762796296, 0.33661058367116803, 0.333428248587277, 0.33016878412250783, 0.32684080337141147, 0.3234529194285395, 0.3200126487714787, 0.31652312140996053, 0.3129863707367515, 0.30940443014461905, 0.3057793330263301, 0.30211311277465164, 0.29840780278235074, 0.2946654364421943, 0.29088804714694955, 0.2870776682893834, 0.2832363332622627, 0.27936607545835496, 0.27546892827042696, 0.27154692509124545, 0.26760209931357776, 0.2636363307114228, 0.2596508845837071, 0.25564687261058894, 0.25162540647222675, 0.2475875978487793, 0.24353455842040445, 0.23946739986726107, 0.23538723386950736, 0.23129517210730194, 0.22719232626080285, 0.2230798080101689, 0.2189587290355584, 0.21483020101712968, 0.21069533563504117, 0.2065552445694514, 0.20241183851891273, 0.19827022425555424, 0.1941363075698988, 0.19001599425246943, 0.18591519009378918, 0.18183980088438098, 0.17779573241476782, 0.17378889047547277, 0.16982518085701878, 0.16591050934992888, 0.16205078174472604, 0.15825190383193324, 0.15451978140207348, 0.1508603202456698, 0.1472794261532452, 0.14378300491532262, 0.14037696232242508, 0.13706720416507556, 0.1338596362337971, 0.13076016431911272, 0.1277746942115453, 0.12490913170161796, 0.12216938257985366, 0.11956135263677536, 0.1170909476629061, 0.11476407344876886, 0.11258663578488663, 0.11056454046178242, 0.1087036932699792, 0.10701000000000001],
        [0.36139957809246864, 0.3631891080928987, 0.3646881002855627, 0.3659046063623482, 0.36684667801514353, 0.36752236693583634, 0.3679397248163146, 0.36810680334846624, 0.3680316542241791, 0.3677223291353411, 0.36718687977384024, 0.36643335783156433, 0.3654698150004013, 0.36430430297223915, 0.36294487343896564, 0.3613995780924687, 0.3596764686246362, 0.35778359672735627, 0.3557290140925167, 0.3535207724120053, 0.35116692337771016, 0.34867551868151886, 0.3460546100153197, 0.34331224907100016, 0.34045648754044866, 0.3374953771155528, 0.33443696948820045, 0.3312893163502794, 0.32806046939367806, 0.3247584803102838, 0.3213914007919849, 0.31796642878692044, 0.31448734726823513, 0.31095708546532486, 0.3073785726075859, 0.30375473792441393, 0.3000885106452053, 0.29638281999935584, 0.29264059521626173, 0.28886476552531876, 0.285058260155923, 0.2812240083374705, 0.2773649392993575, 0.27348398227097964, 0.26958406648173305, 0.26566812116101407, 0.2617386262840314, 0.25779626480924667, 0.25384127044093463, 0.24987387688336968, 0.24589431784082666, 0.2419028270175802, 0.2378996381179048, 0.23388498484607517, 0.22985910090636585, 0.22582222000305147, 0.22177457584040675, 0.2177164021227063, 0.21364793255422468, 0.20956940083923642, 0.20548104068201642, 0.20138410766893058, 0.197283944914711, 0.19318691741618138, 0.1890993901701652, 0.18502772817348595, 0.18097829642296737, 0.176957459915433, 0.17297158364770635, 0.16902703261661106, 0.16513017181897066, 0.16128736625160878, 0.1575049809113489, 0.15378938079501464, 0.15014693089942965, 0.14658399622141746, 0.14310694175780161, 0.1397221325054057, 0.13643593346105326, 0.133254709621568, 0.13018482598377332, 0.12723264754449287, 0.12440453930055029, 0.12170686624876911, 0.11914599338597287, 0.11672828570898516, 0.11446010821462961, 0.11234782589972973, 0.11039780376110911, 0.10861640679559134, 0.10701000000000002],
        [0.3587169232683918, 0.3604480376194656, 0.36189946681221147, 0.36307868387159303, 0.36399316182257335, 0.3646503736901157, 0.36505779249918374, 0.3652228912747405, 0.3651531430417493, 0.36485602082517377, 0.36433899764997707, 0.36360954654112243, 0.3626751405235732, 0.36154325262229287, 0.3602213558622447, 0.3587169232683919, 0.3570374278656977, 0.3551903426791258, 0.3531831407336395, 0.35102329505420166, 0.3487182786657762, 0.34627556459332604, 0.3437026258618146, 0.34100693549620537, 0.33819596652146144, 0.3352771919625464, 0.3322580848444233, 0.3291461181920557, 0.3259487650304067, 0.32267349838444, 0.3193277912791185, 0.31591851397033044, 0.31245012563766295, 0.30892648269162726, 0.30535144154273547, 0.30172885860149895, 0.29806259027842963, 0.294356492984039, 0.29061442312883884, 0.2868402371233406, 0.2830377913780563, 0.2792109423034973, 0.27536354631017534, 0.27149945980860224, 0.26762253920928947, 0.26373664092274884, 0.25984486520735156, 0.255947287712908, 0.2520432279370876, 0.24813200537756036, 0.2442129395319961, 0.24028534989806463, 0.2363485559734356, 0.23240187725577885, 0.22844463324276426, 0.22447614343206157, 0.22049572732134057, 0.21650270440827105, 0.2124963941905228, 0.20847611616576558, 0.20444118983166937, 0.20039218666203668, 0.19633468603520274, 0.1922755193056353, 0.18822151782780236, 0.18417951295617202, 0.18015633604521203, 0.17615881844939046, 0.1721937915231753, 0.16826808662103448, 0.16438853509743592, 0.16056196830684755, 0.15679521760373746, 0.15309511434257347, 0.14946848987782368, 0.14592217556395592, 0.1424630027554382, 0.13909780280673842, 0.13583340707232466, 0.13267664690666475, 0.12963435366422674, 0.12671335869947853, 0.12392049336688811, 0.12126258902092343, 0.1187464770160525, 0.11637898870674318, 0.11416695544746347, 0.11211720859268134, 0.11023657949686473, 0.10853189951448163, 0.10700999999999998],
        [0.35601778533003764, 0.35768904888266634, 0.3590917408657068, 0.36023274273304323, 0.3611189359385597, 0.3617572019361408, 0.3621544221796706, 0.36231747812303333, 0.3622532512201135, 0.3619686229247952, 0.3614704746909627, 0.3607656879725006, 0.3598611442232924, 0.35876372489722325, 0.3574803114481768, 0.3560177853300377, 0.35438302799668986, 0.35258292090201804, 0.35062434549990606, 0.3485141832442384, 0.34625931558889933, 0.34386662398777307, 0.34134298989474393, 0.338695294763696, 0.33593042004851387, 0.3330552472030817, 0.3300766576812836, 0.32700153293700396, 0.3238367544241271, 0.32058920359653725, 0.31726576190811867, 0.31387296427172307, 0.3104159594360727, 0.30689954960885696, 0.3033285369977655, 0.299707723810488, 0.2960419122547138, 0.29233590453813263, 0.28859450286843424, 0.28482250945330784, 0.28102472650044336, 0.2772059562175301, 0.2733710008122579, 0.26952466249231616, 0.2656717434653944, 0.2618170459391824, 0.2579643021081909, 0.2541129641142169, 0.25026141408587804, 0.24640803415179233, 0.24255120644057782, 0.2386893130808526, 0.23482073620123448, 0.2309438579303415, 0.22705706039679174, 0.22315872572920303, 0.21924723605619362, 0.2153209735063812, 0.21137832020838393, 0.20741765829081962, 0.20343736988230654, 0.19943732349082244, 0.19542333314178523, 0.19140269923997266, 0.18738272219016258, 0.18337070239713266, 0.17937394026566078, 0.17539973620052463, 0.17145539060650222, 0.1675482038883711, 0.1636854764509093, 0.15987450869889436, 0.15612260103710432, 0.15243705387031675, 0.14882516760330952, 0.1452942426408605, 0.1418515793877474, 0.13850447824874798, 0.13526023962864006, 0.13212616393220153, 0.12910955156421003, 0.12621770292944345, 0.12345791843267954, 0.12083749847869621, 0.11836374347227104, 0.11604395381818193, 0.11388542992120668, 0.11189547218612307, 0.11008138101770887, 0.10845045682074193, 0.10700999999999997],
        [0.3533055286653096, 0.3549157917646902, 0.35626879814382867, 0.35737082914148316, 0.3582281660964108, 0.3588470903473693, 0.35923388323311634, 0.359394826092409, 0.35933620026400526, 0.35906428708666255, 0.35858536789913836, 0.35790572404019033, 0.357031636848576, 0.3559693876630526, 0.354725257822378, 0.3533055286653097, 0.35171648153060514, 0.3499643977570219, 0.34805555868331756, 0.3459962456482497, 0.3437927399905757, 0.3414513230490533, 0.33897827616244, 0.33637988066949304, 0.3336624179089705, 0.3308321692196295, 0.3278954159402277, 0.32485843940952275, 0.321727520966272, 0.318508941949233, 0.31520898369716355, 0.3118338396411122, 0.3083893515812932, 0.3048812734102118, 0.3013153590203734, 0.2976973623042832, 0.29403303715444673, 0.2903281374633692, 0.2865884171235562, 0.28281963002751265, 0.2790275300677443, 0.2752178711367562, 0.271396407127054, 0.26756889193114297, 0.263741079441528, 0.25991872355071505, 0.2561061916133571, 0.2523023048326998, 0.2485044978741359, 0.24471020540305896, 0.2409168620848622, 0.23712190258493895, 0.23332276156868245, 0.22951687370148588, 0.22570167364874263, 0.22187459607584584, 0.2180330756481889, 0.21417454703116504, 0.2102964448901675, 0.20639620389058946, 0.20247125869782442, 0.19852076614787897, 0.19455077175921442, 0.19056904322090545, 0.1865833482220268, 0.18260145445165316, 0.17863112959885918, 0.17468014135271973, 0.1707562574023094, 0.16686724543670306, 0.16302087314497532, 0.15922490821620086, 0.1554871183394545, 0.15181527120381086, 0.14821713449834478, 0.14470047591213098, 0.14127306313424398, 0.13794266385375875, 0.13471704575974988, 0.13160397654129216, 0.12861122388746019, 0.12574655548732883, 0.12301773902997269, 0.12043254220446657, 0.11799873269988517, 0.11572407820530321, 0.11361634640979539, 0.11168330500243645, 0.10993272167230105, 0.10837236410846401, 0.10701],
        [0.350583517662111, 0.3521319161477255, 0.35343451434435746, 0.3544969892916973, 0.3553250180294345, 0.3559242775972595, 0.35630044503486175, 0.35645919738193155, 0.35640621167815856, 0.356147164963233, 0.3556877342768448, 0.3550335966586838, 0.35419042914844, 0.35316390878580334, 0.3519597126104636, 0.3505835176621111, 0.3490410009804354, 0.3473378396051267, 0.34547971057587484, 0.3434722909323699, 0.3413212577143016, 0.3390322879613602, 0.33661105871323543, 0.33406324700961715, 0.3313945298901957, 0.32861058439466057, 0.32571708756270196, 0.3227197164340099, 0.31962414804827405, 0.31643605944518455, 0.3131611276644315, 0.30980520002851186, 0.3063748049911532, 0.3028766412888898, 0.2993174076582563, 0.29570380283578723, 0.29204252555801735, 0.288340274561481, 0.28460374858271276, 0.28083964635824726, 0.2770546666246191, 0.27325550811836263, 0.2694488695760127, 0.26564144973410375, 0.2618399473291702, 0.25805106109774684, 0.25427978834965725, 0.25052432068788205, 0.2467811482886909, 0.2430467613283534, 0.23931764998313934, 0.23559030442931847, 0.2318612148431603, 0.22812687140093463, 0.22438376427891119, 0.22062838365335957, 0.21685721970054955, 0.21306676259675084, 0.209253502518233, 0.20541392964126579, 0.201544534142119, 0.19764376262579733, 0.19371788741224605, 0.18977513725014564, 0.18582374088817635, 0.1818719270750187, 0.17792792455935308, 0.17399996208985974, 0.17009626841521933, 0.166225072284112, 0.1623946024452183, 0.15861308764721857, 0.15488875663879317, 0.1512298381686225, 0.14764456098538697, 0.14414115383776704, 0.140727845474443, 0.13741286464409527, 0.1342044400954043, 0.13111080057705043, 0.1281401748377141, 0.12530079162607557, 0.12260087969081541, 0.12004866778061397, 0.11765238464415155, 0.11542025903010868, 0.11336051968716562, 0.11148139536400284, 0.10979111480930069, 0.1082979067717396, 0.10701],
        [0.34785511670834535, 0.3493410719139615, 0.3505927651650738, 0.3516152693784704, 0.35241365747093933, 0.3529930023592693, 0.35335837696024847, 0.3535148541906652, 0.3534675069673075, 0.3532214082069642, 0.35278163082642316, 0.35215324774247303, 0.35134133187190175, 0.3503509561314979, 0.34918719343804966, 0.3478551167083454, 0.34635979885917323, 0.3447063128073218, 0.3428997314695791, 0.34094512776273356, 0.3388475746035736, 0.33661214490888736, 0.3342439115954631, 0.3317479475800893, 0.3291293257795542, 0.326393119110646, 0.32354440049015315, 0.3205882428348639, 0.3175297190615666, 0.31437390208704935, 0.31112586482810073, 0.3077911053839362, 0.30437682258348137, 0.30089064043808905, 0.2973401829591119, 0.29373307415790295, 0.2900769380458149, 0.2863793986342005, 0.28264807993441265, 0.27889060595780424, 0.2751146007157279, 0.2713276882195366, 0.2675374924805833, 0.2637516375102205, 0.2599777473198011, 0.2562234459206781, 0.252494346943899, 0.24878802249929022, 0.2451000343163732, 0.24142594412466922, 0.2377613136536997, 0.23410170463298585, 0.23044267879204913, 0.22677979786041075, 0.22310862356759198, 0.21942471764311416, 0.21572364181649878, 0.21200095781726705, 0.20825222737494023, 0.20447301221903968, 0.20065887407908684, 0.19680756091716872, 0.192925565625636, 0.18902156732940512, 0.18510424515339258, 0.18118227822251476, 0.1772643456616881, 0.1733591265958292, 0.16947530014985443, 0.16562154544868019, 0.16180654161722302, 0.15803896778039933, 0.1543275030631256, 0.1506808265903183, 0.14710761748689383, 0.1436165548777687, 0.14021631788785932, 0.13691558564208217, 0.13372303726535373, 0.13064735188259044, 0.1276972086187087, 0.12488128659862506, 0.12220826494725591, 0.11968682278951775, 0.11732563925032705, 0.11513339345460015, 0.11311876452725361, 0.1112904315932039, 0.10965707377736739, 0.1082273702046606, 0.10701],
        [0.34512369019191624, 0.34654690894558754, 0.3477474263037578, 0.34872971559658666, 0.34949825015423325, 0.3500575033068572, 0.3504119483846177, 0.3505660587176742, 0.35052430763618636, 0.35029116847031344, 0.34987111455021486, 0.34926861920604996, 0.3484881557679783, 0.3475341975661591, 0.3464112179307521, 0.3451236901919163, 0.3436760876798112, 0.34207288372459654, 0.34031855165643154, 0.33841756480547547, 0.33637439650188794, 0.33419352007582825, 0.3318794088574559, 0.3294365361769302, 0.3268693753644108, 0.32418239975005686, 0.32138008266402784, 0.3184668974364832, 0.3154473173975823, 0.31232581587748465, 0.3091068662063496, 0.30579561565739927, 0.30239990727610677, 0.29892825805100764, 0.2953891849706377, 0.29179120502353273, 0.28814283519822836, 0.2844525924832602, 0.28072899386716416, 0.27698055633847585, 0.273215796885731, 0.26944323249746527, 0.2656713801622146, 0.26190875686851456, 0.2581638796049007, 0.254445265359909, 0.2507591220228895, 0.24710242108645006, 0.24346982494401273, 0.2398559959889998, 0.23625559661483356, 0.23266328921493618, 0.2290737361827299, 0.2254815999116368, 0.2218815427950793, 0.21826822722647954, 0.21463631559925966, 0.21098047030684206, 0.2072953537426487, 0.20357562830010198, 0.19981595637262412, 0.19601340901458433, 0.1921746919241401, 0.18830891946039602, 0.18442520598245665, 0.18053266584942648, 0.17664041342041015, 0.17275756305451215, 0.16889322911083712, 0.16505652594848946, 0.16125656792657395, 0.15750246940419488, 0.15380334474045695, 0.15016830829446481, 0.14660647442532282, 0.14312695749213572, 0.13973887185400782, 0.13645133187004396, 0.13327345189934844, 0.13021434630102602, 0.12728312943418107, 0.12448891565791828, 0.12184081933134218, 0.11934795481355731, 0.11701943646366822, 0.11486437864077945, 0.11289189570399555, 0.11111110201242114, 0.10953111192516066, 0.10816103980131876, 0.10701],
        [0.3423926025007268, 0.34375307712479214, 0.34490237345819014, 0.3458443741408308, 0.3465829618126243, 0.34712201911348084, 0.3474654286833104, 0.34761707316202295, 0.34758083518952876, 0.34736059740573794, 0.34696024245056056, 0.34638365296390644, 0.345634711585686, 0.34471730095580916, 0.34363530371418605, 0.3423926025007269, 0.34099307995534145, 0.33944061871794007, 0.3377391014284327, 0.33589241072672976, 0.33390442925274083, 0.3317790396463764, 0.32952012454754637, 0.32713156659616077, 0.32461724843212997, 0.3219810526953637, 0.31922686202577233, 0.31635855906326593, 0.31338002644775426, 0.31029514681914777, 0.30710780281735633, 0.303822790798915, 0.3004485619868579, 0.29699448132084355, 0.29346991374053094, 0.2898842241855789, 0.2862467775956466, 0.28256693891039236, 0.2788540730694754, 0.2751175450125543, 0.2713667196792881, 0.2676109620093356, 0.26385963694235587, 0.2601221094180073, 0.25640774437594904, 0.2527259067558398, 0.2490833682134364, 0.2454765272688875, 0.24189918915843933, 0.2383451591183383, 0.23480824238483108, 0.231282244194164, 0.22776096978258342, 0.22423822438633578, 0.22070781324166766, 0.21716354158482526, 0.2135992146520553, 0.21000863767960407, 0.20638561590371804, 0.20272395456064352, 0.19901745888662714, 0.1952625549106352, 0.19146615183251414, 0.18763777964483022, 0.1837869683401498, 0.1799232479110392, 0.17605614835006475, 0.17219519964979285, 0.16834993180278973, 0.16452987480162184, 0.16074455863885548, 0.1570035133070569, 0.15331626879879254, 0.14969235510662868, 0.14614130222313162, 0.1426726401408678, 0.1392958988524035, 0.13602060835030502, 0.13285629862713874, 0.12981249967547098, 0.1268987414878681, 0.12412455405689636, 0.12149946737512218, 0.1190330114351119, 0.11673471622943177, 0.11461411175064819, 0.11268072799132747, 0.11094409494403597, 0.10941374260133999, 0.10809920095580587, 0.10700999999999995],
        [0.3396652180226809, 0.3409632263337646, 0.3420614823261509, 0.3429632912059875, 0.343671958179421, 0.34419078845259876, 0.34452308723166797, 0.3446721597227757, 0.34464131113206903, 0.3444338466656952, 0.34405307152980136, 0.34350229093053464, 0.3427848100740421, 0.34190393416647086, 0.340862968413968, 0.3396652180226809, 0.3383139881987564, 0.33681258414834186, 0.33516431107758443, 0.33337247419263105, 0.3314403786996291, 0.3293713298047254, 0.32716863271406726, 0.32483559263380196, 0.3223755147700764, 0.319791704329038, 0.3170874665168335, 0.3142661065396103, 0.3113309296035154, 0.3082852409146961, 0.3051323456792994, 0.3018766907584977, 0.2985272896335635, 0.29509429744079474, 0.2915878693164891, 0.28801816039694456, 0.28439532581845883, 0.28072952071732965, 0.2770309002298549, 0.2733096194923323, 0.26957583364105975, 0.265839697812335, 0.26211136714245603, 0.25840099676772055, 0.254718741824426, 0.25107475744887076, 0.24747634014234723, 0.24391935186612876, 0.24039679594648308, 0.23690167570967838, 0.23342699448198276, 0.2299657555896642, 0.22651096235899076, 0.22305561811623048, 0.21959272618765133, 0.21611528989952147, 0.21261631257810884, 0.20908879754968163, 0.20552574814050778, 0.20192016767685528, 0.19826505948499232, 0.19455624659791274, 0.19080083087551403, 0.18700873388441983, 0.18318987719125335, 0.17935418236263823, 0.1755115709651978, 0.1716719645655555, 0.16784528473033491, 0.1640414530261593, 0.16027039101965224, 0.1565420202774371, 0.1528662623661374, 0.14925303885237648, 0.14571227130277783, 0.14225388128396496, 0.13888779036256121, 0.1356239201051901, 0.13247219207847497, 0.12944252784903942, 0.1265448489835068, 0.1237890770485005, 0.12118513361064408, 0.11874294023656096, 0.11647241849287457, 0.11438348994620826, 0.11248607616318564, 0.11079009871043002, 0.10930547915456491, 0.10804213906221374, 0.10700999999999995],
        [0.3369449011456819, 0.3381810064546937, 0.33922862860542097, 0.34009051298684106, 0.3407694049879313, 0.341268049997669, 0.3415891934050318, 0.3417355805989967, 0.3417099569685413, 0.34151506790264285, 0.3411536587902787, 0.34062847502042654, 0.33994226198206323, 0.33909776506416656, 0.3380977296557136, 0.3369449011456818, 0.33564202492304857, 0.3341918463767913, 0.33259711089588745, 0.3308605638693141, 0.32898495068604866, 0.32697301673506873, 0.32482750740535166, 0.3225511680858745, 0.320146744165615, 0.31761698103355035, 0.31496462407865783, 0.3121924186899148, 0.3093031102562989, 0.30629944416678717, 0.3031841658103571, 0.2999613754861613, 0.29664059313405267, 0.2932326936040595, 0.2897485517462098, 0.28619904241053207, 0.2825950404470542, 0.27894742070580436, 0.27526705803681106, 0.2715648272901021, 0.26785160331570596, 0.2641382609636507, 0.2604356750839644, 0.2567547205266755, 0.25310627214181197, 0.24950120477940207, 0.24594729243642938, 0.24243990569769974, 0.238971314294974, 0.23553378796001329, 0.23211959642457888, 0.22872100942043175, 0.22533029667933302, 0.22193972793304365, 0.21854157291332496, 0.21512810135193786, 0.21169158298064358, 0.20822428753120317, 0.20471848473537765, 0.20116644432492817, 0.1975604360316159, 0.19389573206900793, 0.1901796145778957, 0.1864223681808768, 0.18263427750054864, 0.1788256271595089, 0.17500670178035502, 0.17118778598568454, 0.16737916439809503, 0.16359112164018397, 0.1598339423345489, 0.15611791110378728, 0.15245331257049682, 0.1488504313572749, 0.1453195520867191, 0.14187095938142696, 0.13851493786399596, 0.13526177215702365, 0.13212174688310752, 0.1291051466648452, 0.12622225612483412, 0.12348335988567183, 0.1208987425699559, 0.11847868880028388, 0.11623348319925322, 0.11417341038946144, 0.11230875499350616, 0.11064980163398486, 0.10920683493349499, 0.10799013951463421, 0.10701],
        [0.334235016257633, 0.3354100673697685, 0.33640768799378035, 0.33723008567817614, 0.3378794679714634, 0.33835804242214973, 0.3386680165787427, 0.33881159798975, 0.33879099420367914, 0.3386084127690378, 0.3382660612343336, 0.33776614714807385, 0.3371108780587664, 0.33630246151491866, 0.33534310506503834, 0.33423501625763297, 0.33298040264121004, 0.3315814717642775, 0.3300404311753426, 0.32835948842291296, 0.32654085105549624, 0.32458672662159993, 0.32249932266973186, 0.32028084674839935, 0.3179335064061101, 0.31545950919137167, 0.31286106265269165, 0.3101403743385777, 0.30729965179753727, 0.304341102578078, 0.30126693422870754, 0.29808090493191974, 0.294792975406154, 0.2914146570038356, 0.28795746107739034, 0.2844328989792438, 0.28085248206182156, 0.27722772167754905, 0.2735701291788521, 0.26989121591815596, 0.26620249324788664, 0.2625154725204694, 0.25884166508832995, 0.2551925823038938, 0.2515797355195865, 0.24801463608783383, 0.24450547972249018, 0.2410471995831264, 0.23763141319074185, 0.23424973806633637, 0.23089379173090965, 0.22755519170546126, 0.22422555551099088, 0.2208965006684981, 0.21755964469898273, 0.21420660512344422, 0.21082899946288242, 0.20741844523829678, 0.20396655997068716, 0.20046496118105303, 0.19690526639039413, 0.19328225931651188, 0.1896033884644148, 0.18587926853591297, 0.1821205142328168, 0.1783377402569364, 0.17454156131008197, 0.17074259209406395, 0.16695144731069236, 0.16317874166177757, 0.15943508984912974, 0.15573110657455913, 0.15207740653987598, 0.14848460444689052, 0.14496331499741294, 0.1415241528932536, 0.13817773283622253, 0.13493466952813013, 0.13180557767078663, 0.12880107196600213, 0.125931767115587, 0.12320827782135145, 0.12064121878510563, 0.1182412047086599, 0.11601885029382442, 0.11398477024240941, 0.11214957925622515, 0.11052389203708184, 0.1091183232867897, 0.107943487707159, 0.10701],
        [0.33153892774643784, 0.3326540589611779, 0.3336025361890094, 0.334386055474777, 0.33500631286332516, 0.3354650043994987, 0.3357638261281421, 0.3359044740941, 0.3358886443422169, 0.3357180329173377, 0.3353943358643067, 0.3349192492279686, 0.3342944690531681, 0.3335216913847498, 0.33260261226755805, 0.33153892774643784, 0.3303323338662334, 0.32898452667178957, 0.3274972022079511, 0.32587205651956225, 0.32411078565146795, 0.3222150856485124, 0.32018665255554063, 0.318027182417397, 0.31573837127892634, 0.313321915184973, 0.31077951018038175, 0.308112852309997, 0.3053236376186636, 0.30241356215122606, 0.299384321952529, 0.29623933904578714, 0.292988939367696, 0.28964517483332114, 0.2862200973577281, 0.2827257588559825, 0.2791742112431499, 0.27557750643429596, 0.27194769634448623, 0.2682968328887863, 0.26463696798226194, 0.2609801535399784, 0.2573384414770016, 0.2537238837083969, 0.2501485321492299, 0.24662443871456635, 0.2431601566273371, 0.23975024434193468, 0.2363857616206167, 0.23305776822564098, 0.22975732391926534, 0.22647548846374763, 0.22320332162134549, 0.21993188315431667, 0.21665223282491913, 0.21335543039541038, 0.21003253562804844, 0.206674608285091, 0.20327270812879583, 0.1998178949214206, 0.19630122842522335, 0.19271707633301582, 0.1890730380598272, 0.18538002095124048, 0.181648932352839, 0.17789067961020602, 0.1741161700689246, 0.17033631107457797, 0.1665620099727495, 0.1628041741090222, 0.15907371082897942, 0.1553815274782043, 0.15173853140228002, 0.14815562994678982, 0.14464373045731693, 0.1412137402794446, 0.1378765667587559, 0.1346431172408342, 0.13152429907126253, 0.1285310195956242, 0.12567418615950243, 0.1229647061084804, 0.12041348678814133, 0.11803143554406842, 0.11582945972184491, 0.11381846666705393, 0.11200936372527875, 0.11041305824210257, 0.10904045756310854, 0.10790246903387996, 0.10700999999999995],
        [0.32886, 0.3299166311111111, 0.33081704888888885, 0.3315624685714286, 0.3321541053968254, 0.33259317460317456, 0.33288089142857136, 0.33301847111111105, 0.3330071288888887, 0.3328480799999999, 0.3325425396825396, 0.33209172317460317, 0.33149684571428567, 0.3307591225396825, 0.32987976888888887, 0.32886, 0.327701031111111, 0.32640407746031735, 0.32497035428571425, 0.32340107682539676, 0.3216974603174603, 0.31986072, 0.3178920711111111, 0.3157927288888889, 0.3135639085714286, 0.3112068253968254, 0.30872269460317464, 0.3061127314285714, 0.30337815111111116, 0.30052016888888894, 0.2975400000000001, 0.29444073777777774, 0.291232987936508, 0.28792923428571426, 0.2845419606349206, 0.28108365079365083, 0.27756678857142864, 0.2740038577777778, 0.2704073422222223, 0.2667897257142857, 0.2631634920634921, 0.2595411250793651, 0.25593510857142865, 0.25235792634920645, 0.24882206222222222, 0.24534, 0.24192057777777778, 0.23855805079365086, 0.2352430285714286, 0.2319661206349206, 0.22871793650793648, 0.22548908571428572, 0.2222701777777778, 0.2190518222222222, 0.2158246285714286, 0.21257920634920632, 0.20930616507936506, 0.20599611428571427, 0.20263966349206347, 0.19922742222222217, 0.19574999999999995, 0.1922014311111111, 0.18858944888888887, 0.1849252114285714, 0.1812198768253968, 0.17748460317460316, 0.17373054857142853, 0.16996887111111103, 0.16621072888888883, 0.16246727999999996, 0.1587496825396825, 0.15506909460317458, 0.15143667428571422, 0.14786357968253966, 0.14436096888888886, 0.14094, 0.1376118311111111, 0.13438762031746032, 0.13127852571428572, 0.1282957053968254, 0.12545031746031746, 0.12275352, 0.12021647111111111, 0.11785032888888891, 0.11566625142857145, 0.11367539682539683, 0.1118889231746032, 0.1103179885714286, 0.1089737511111111, 0.10786736888888887, 0.10701],
        [0.326203709062712, 0.3272034945224171, 0.3280571251409956, 0.32876536899849745, 0.3293289941749723, 0.32974876875047066, 0.33002546080504186, 0.3301598384187362, 0.33015266967160345, 0.3300047226436936, 0.3297167654150567, 0.32928956606574256, 0.3287238926758009, 0.32802051332528215, 0.32718019609423565, 0.3262037090627119, 0.3250918203107605, 0.32384529791843153, 0.3224649099657748, 0.32095142453284026, 0.3193056096996781, 0.3175282335463377, 0.3156200641528696, 0.31358186959932344, 0.3114144179657493, 0.30911847733219683, 0.30669481577871616, 0.3041442013853573, 0.30146740223217006, 0.2986651863992042, 0.29573832196651006, 0.2926895823038978, 0.2895297619402206, 0.2862716606940916, 0.28292807838412426, 0.27951181482893206, 0.2760356698471285, 0.2725124432573268, 0.26895493487814054, 0.265375944528183, 0.2617882720260678, 0.2582047171904082, 0.2546380798398176, 0.25110115979290965, 0.24760675686829742, 0.24416767088459465, 0.24079294741719176, 0.2374766150685884, 0.23420894819806085, 0.2309802211648861, 0.22778070832834071, 0.2246006840477013, 0.22143042268224458, 0.21826019859124707, 0.21508028613398564, 0.21188095966973666, 0.208652493557777, 0.20538516215738323, 0.20206923982783206, 0.19869500092839992, 0.19525271981836387, 0.1917361858392002, 0.18815324826118607, 0.1845152713367984, 0.18083361931851405, 0.1771196564588102, 0.17338474701016374, 0.16964025522505158, 0.1658975453559508, 0.1621679816553383, 0.15846292837569106, 0.15479374976948618, 0.15117181008920047, 0.14760847358731088, 0.14411510451629464, 0.14070306712862846, 0.1373837256767895, 0.13416844441325462, 0.13106858759050083, 0.1280955194610051, 0.12526060427724445, 0.12257520629169574, 0.12005068975683611, 0.11769841892514243, 0.11552975804909171, 0.11355607138116089, 0.111788723173827, 0.11023907767956702, 0.10891849915085781, 0.10783835184017647, 0.10700999999999997],
        [0.32358397760492386, 0.32452860318058674, 0.3253367573920944, 0.32600879212868056, 0.32654505927957905, 0.32694591073402357, 0.32721169838124775, 0.3273427741104857, 0.32733948981097055, 0.32720219737193673, 0.3269312486826176, 0.3265269956322469, 0.32598979011005835, 0.32531998400528594, 0.32451792920716327, 0.3235839776049238, 0.3225184810878018, 0.32132179154503065, 0.31999426086584415, 0.31853624093947613, 0.31694808365516025, 0.31523014090213036, 0.3133827645696201, 0.3114063065468633, 0.30930111872309357, 0.30706755298754485, 0.3047059612294506, 0.30221669533804485, 0.29960010720256125, 0.2968565487122334, 0.2939863717562953, 0.29099203870412427, 0.2878844538456749, 0.28467663195104465, 0.2813815877903317, 0.278012336133634, 0.27458189175104963, 0.2711032694126764, 0.2675894838886123, 0.26405354994895536, 0.26050848236380353, 0.2569672959032548, 0.2534430053374072, 0.2499486254363586, 0.24649717097020693, 0.24310165670905037, 0.23977126825524903, 0.23649987454021237, 0.23327751532761196, 0.2300942303811195, 0.22694005946440687, 0.2238050423411455, 0.22067921877500712, 0.21755262852966353, 0.21441531136878622, 0.21125730705604695, 0.2080686553551175, 0.2048393960296694, 0.20155956884337448, 0.19821921355990407, 0.19480836994293027, 0.19132065948893318, 0.18776403062562783, 0.18415001351353802, 0.18049013831318725, 0.1767959351850992, 0.17307893428979756, 0.16935066578780597, 0.16562265983964813, 0.16190644660584771, 0.15821355624692834, 0.15455551892341365, 0.1509438647958274, 0.14739012402469312, 0.14390582677053457, 0.14050250319387536, 0.13719168345523916, 0.13398489771514968, 0.13089367613413055, 0.12792954887270538, 0.12510404609139789, 0.12242869795073173, 0.11991503461123051, 0.117574586233418, 0.1154188829778178, 0.11345945500495354, 0.11170783247534893, 0.11017554554952762, 0.10887412438801325, 0.10781509915132947, 0.10701],
        [0.3210168399534749, 0.3219079718917706, 0.32267196143874616, 0.32330877117025686, 0.32381836366215794, 0.3242007014903049, 0.3244557472305531, 0.32458346345875777, 0.3245838127507743, 0.32445675768245835, 0.3242022608296649, 0.32382028476824953, 0.3233107920740674, 0.32267374532297405, 0.32190910709082476, 0.32101683995347485, 0.31999690648677964, 0.31884926926659474, 0.3175738908687754, 0.3161707338691766, 0.31463976084365447, 0.3129809343680635, 0.3111942170182598, 0.30927957137009815, 0.3072369599994345, 0.3050663454821236, 0.3027676903940211, 0.3003409573109825, 0.2977861088088628, 0.29510310746351764, 0.29229191585080233, 0.289354694284426, 0.2863023940295136, 0.2831481640890434, 0.2799051534659943, 0.276586511163345, 0.2732053861840738, 0.2697749275311595, 0.26630828420758074, 0.26281860521631595, 0.2593190395603441, 0.2558227362426434, 0.25234284426619275, 0.24889251263397072, 0.24548489034895576, 0.24213312641412676, 0.2388464926181914, 0.2356187518927754, 0.23243978995523343, 0.22929949252292026, 0.22618774531319083, 0.22309443404339993, 0.22000944443090237, 0.21692266219305278, 0.2138239730472063, 0.2107032627107174, 0.20755041690094117, 0.20435532133523227, 0.20110786173094558, 0.19779792380543582, 0.19441539327605797, 0.19095378522777137, 0.1874211322159538, 0.18382909616358756, 0.18018933899365516, 0.1765135226291389, 0.17281330899302133, 0.1691003600082847, 0.16538633759791144, 0.16168290368488403, 0.15800172019218478, 0.15435444904279608, 0.15075275215970024, 0.14720829146587985, 0.14373272888431715, 0.14033772633799466, 0.1370349457498946, 0.13383604904299956, 0.13075269814029175, 0.12779655496475367, 0.1249792814393677, 0.12231253948711623, 0.11980799103098161, 0.11747729799394634, 0.11533212229899269, 0.11338412586910311, 0.11164497062726002, 0.11012631849644575, 0.10883983139964272, 0.10779717125983332, 0.10701],
        [0.318518330435204, 0.3193576154621196, 0.3200787530775121, 0.3206813393315053, 0.3211649702742222, 0.32152924195578675, 0.3217737504263221, 0.32189809173595174, 0.3219018619347992, 0.3217846570729881, 0.32154607320064177, 0.32118570636788385, 0.3207031526248374, 0.32009800802162636, 0.31936986860837413, 0.318518330435204, 0.3175429895522395, 0.316443442009604, 0.31521928385742126, 0.31387011114581465, 0.3123955199249077, 0.31079510624482365, 0.3090684661556861, 0.30721519570761874, 0.3052348909507447, 0.30312714793518775, 0.3008915627110711, 0.2985277313285185, 0.2960352498376531, 0.2934137142885988, 0.29066272073147886, 0.287784136350772, 0.2847889128683796, 0.281690273140558, 0.2785014400235637, 0.2752356363736531, 0.27190608504708286, 0.2685260089001093, 0.2651086307889891, 0.26166717356997854, 0.25821486009933425, 0.2547649132333127, 0.2513305558281704, 0.24792501074016376, 0.24456150082554923, 0.24125324894058345, 0.23800957283226107, 0.23482416981053028, 0.23168683207607704, 0.22858735182958784, 0.225515521271749, 0.22246113260324663, 0.2194139780247671, 0.2163638497369967, 0.21330053994062165, 0.21021384083632824, 0.2070935446248028, 0.2039294435067316, 0.20071132968280084, 0.1974289953536968, 0.19407223272010588, 0.1906344962231761, 0.1871238892659031, 0.18355217749174418, 0.17993112654415688, 0.17627250206659853, 0.17258806970252658, 0.16888959509539847, 0.16518884388867155, 0.1614975817258033, 0.1578275742502511, 0.1541905871054724, 0.15059838593492458, 0.14706273638206502, 0.1435954040903512, 0.14020815470324055, 0.1369127538641904, 0.1337209672166583, 0.13064456040410158, 0.1276952990699776, 0.12488494885774387, 0.12222527541085776, 0.11972804437277668, 0.11740502138695813, 0.11526797209685943, 0.11332866214593802, 0.1115988571776513, 0.11009032283545678, 0.10881482476281171, 0.10778412860317366, 0.10700999999999995],
        [0.31610448337695063, 0.3168935486977846, 0.3175731481049539, 0.31814252982070523, 0.3186009420672854, 0.31894763306694107, 0.31918185104191915, 0.3193028442144664, 0.3193098608068296, 0.31920214904125566, 0.3189789571399913, 0.3186395333252833, 0.31818312581937847, 0.3176089828445234, 0.3169163526229652, 0.3161044833769506, 0.31517262332872625, 0.31412002070053885, 0.31294592371463553, 0.3116495805932628, 0.31023023955866774, 0.3086871488330967, 0.3070195566387969, 0.305226711198015, 0.30330786073299765, 0.30126225346599184, 0.2990891376192441, 0.2967877614150015, 0.2943573730755107, 0.29179722082301857, 0.2891065528797717, 0.2862869522091314, 0.2833493407389163, 0.2803069751380586, 0.2771731120754913, 0.2739610082201471, 0.27068392024095905, 0.2673551048068593, 0.26398781858678105, 0.26059531824965687, 0.2571908604644194, 0.25378770190000155, 0.25039909922533604, 0.24703830910935554, 0.24371858822099263, 0.24045319322918038, 0.23725146122370017, 0.23410705097772966, 0.23100970168529472, 0.2279491525404219, 0.22491514273713745, 0.22189741146946762, 0.21888569793143867, 0.21586974131707684, 0.2128392808204086, 0.20978405563546001, 0.2066938049562574, 0.20355826797682716, 0.20036718389119546, 0.19711029189338858, 0.19377733117743287, 0.19036172564260895, 0.18687163800921552, 0.18331891570280542, 0.17971540614893164, 0.1760729567731471, 0.17240341500100487, 0.16871862825805786, 0.16503044396985908, 0.16135070956196146, 0.15769127245991807, 0.15406398008928177, 0.1504806798756056, 0.14695321924444243, 0.1434934456213454, 0.14011320643186737, 0.1368243491015613, 0.13363872105598018, 0.13056816972067703, 0.12762454252120478, 0.1248196868831164, 0.12216545023196486, 0.11967367999330315, 0.11735622359268426, 0.11522492845566115, 0.11329164200778677, 0.11156821167461407, 0.1100664848816961, 0.10879830905458576, 0.10777553161883607, 0.10700999999999997],
        [0.313791333105554, 0.3145317864049165, 0.31517116231763254, 0.3157083758461358, 0.31614234199286007, 0.31647197576023967, 0.31669619215070854, 0.31681390616670074, 0.31682403281064997, 0.3167254870849905, 0.31651718399215645, 0.31619803853458145, 0.31576696571469975, 0.31522288053494524, 0.31456469799775194, 0.31379133310555396, 0.3129017008607851, 0.3118947162658794, 0.3107692943232711, 0.3095243500353939, 0.30815879840468197, 0.3066715544335692, 0.3050615331244896, 0.3033276494798773, 0.3014688185021662, 0.29948395519379034, 0.29737197455718356, 0.29513179159478004, 0.29276232130901375, 0.2902624787023185, 0.2876311787771286, 0.2848697291654736, 0.28198900801776633, 0.27900228611401523, 0.27592283423422886, 0.2727639231584157, 0.26953882366658405, 0.2662608065387426, 0.2629431425548999, 0.25959910249506435, 0.2562419571392444, 0.25288497726744863, 0.24954143365968562, 0.2462245970959637, 0.24294773835629138, 0.23972412822067726, 0.23656311011875086, 0.2334583180786262, 0.23039945877803822, 0.2273762388947219, 0.22437836510641246, 0.2213955440908447, 0.21841748252575394, 0.21543388708887504, 0.21243446445794303, 0.2094089213106929, 0.2063469643248598, 0.2032383001781788, 0.2000726355483847, 0.19683967711321265, 0.19352913155039786, 0.1901344066535315, 0.1866637146796306, 0.18312896900156847, 0.17954208299221844, 0.17591497002445367, 0.1722595434711477, 0.16858771670517358, 0.16491140309940483, 0.1612425160267147, 0.1575929688599764, 0.15397467497206335, 0.15039954773584877, 0.14687950052420598, 0.14342644671000834, 0.1400522996661292, 0.13676897276544167, 0.13358837938081924, 0.13052243288513515, 0.1275830466512627, 0.12478213405207518, 0.12213160846044593, 0.11964338324924827, 0.1173293717913555, 0.11520148745964087, 0.11327164362697774, 0.11155175366623939, 0.11005373095029918, 0.10878948885203031, 0.10777094074430613, 0.10701],
        [0.3115949139478531, 0.31228834338966616, 0.31288881151210896, 0.31339491061607566, 0.31380523300245944, 0.31411837097215445, 0.31433291682605446, 0.3144474628650532, 0.31446060139004445, 0.314370924701922, 0.3141770251015799, 0.31387749488991146, 0.3134709263678109, 0.3129559118361717, 0.3123310435958878, 0.311594913947853, 0.31074611519296097, 0.3097832396321058, 0.3087048795661809, 0.30750962729608017, 0.3061960751226977, 0.30476281534692684, 0.3032084402696617, 0.3015315421917958, 0.2997307134142232, 0.29780454623783764, 0.2957516329635327, 0.2935705658922023, 0.29125993732474037, 0.28881833956204045, 0.28624436490499644, 0.2835390545257674, 0.2807132450815729, 0.27778022210089803, 0.27475327111222764, 0.27164567764404657, 0.2684707272248398, 0.2652417053830923, 0.2619718976472888, 0.25867458954591455, 0.25536306660745406, 0.25205061436039256, 0.24875051833321485, 0.24547606405440592, 0.24224053705245047, 0.23905722285583372, 0.23593547184365501, 0.2328688937974726, 0.22984716334945907, 0.22685995513178728, 0.22389694377662997, 0.22094780391616, 0.21800221018254998, 0.2150498372079726, 0.2120803596246008, 0.2090834520646072, 0.20604878916016472, 0.2029660455434459, 0.1998248958466236, 0.19661501470187048, 0.19332607674135954, 0.18995147242340488, 0.18649945551088767, 0.1829819955928306, 0.1794110622582562, 0.17579862509618724, 0.1721566536956464, 0.1684971176456561, 0.16483198653523937, 0.16117322995341865, 0.1575328174892166, 0.15392271873165594, 0.15035490326975934, 0.1468413406925494, 0.1433940005890487, 0.1400248525482801, 0.13674586615926618, 0.13356901101102953, 0.1305062566925929, 0.12756957279297887, 0.12477092890121015, 0.12212229460630943, 0.1196356394972993, 0.11732293316320247, 0.1151961451930416, 0.1132672451758393, 0.11154820270061827, 0.1100509873564012, 0.10878756873221065, 0.10776991641706934, 0.10701],
        [0.3095312602306872, 0.31017923445818424, 0.31074211148494496, 0.31121816733880414, 0.3116056780475967, 0.31190291963915734, 0.3121081681413213, 0.31221969958192297, 0.31223578998879764, 0.3121547153897799, 0.3119747518127048, 0.311694175285407, 0.31131126183572144, 0.31082428749148316, 0.3102315282805267, 0.3095312602306873, 0.30872175936979934, 0.3078013017256981, 0.3067681633262183, 0.30562062019919467, 0.30435694837246235, 0.302975423873856, 0.30147432273121055, 0.2998519209723609, 0.29810649462514177, 0.2962363197173882, 0.29423967227693504, 0.2921148283316169, 0.2898600639092689, 0.2874736550377257, 0.2849538777448225, 0.2823015155959818, 0.27952738230697904, 0.27664479913117707, 0.2736670873219393, 0.27060756813262854, 0.2674795628166084, 0.2642963926272415, 0.2610713788178914, 0.25781784264192104, 0.2545491053526935, 0.25127848820357207, 0.2480193124479198, 0.2447848993390999, 0.24158857013047533, 0.23844364607540952, 0.23535949872465475, 0.23232970081852156, 0.2293438753947093, 0.22639164549091767, 0.2234626341448464, 0.22054646439419523, 0.2176327592766637, 0.21471114182995138, 0.2117712350917581, 0.20880266209978343, 0.20579504589172692, 0.20273800950528845, 0.19962117597816748, 0.19643416834806368, 0.19316660965267682, 0.1898118561196907, 0.18637819673672634, 0.18287765368138906, 0.1793222491312842, 0.17572400526401688, 0.17209494425719246, 0.16844708828841623, 0.1647924595352935, 0.16114308017542953, 0.15751097238642955, 0.15390815834589885, 0.1503466602314427, 0.14683850022066633, 0.14339570049117517, 0.14003028322057445, 0.13675427058646933, 0.13357968476646523, 0.13051854793816733, 0.12758288227918094, 0.1247847099671113, 0.12213605317956377, 0.11964893409414362, 0.11733537488845606, 0.11520739774010642, 0.11327702482669995, 0.11155627832584192, 0.11005718041513765, 0.10879175327219237, 0.1077720190746114, 0.10701],
        [0.30761640628089565, 0.3082204744166218, 0.30874707803270146, 0.3091941792226004, 0.3095597400797848, 0.3098417226977204, 0.3100380891698733, 0.310146801589709, 0.3101658220506938, 0.3100931126462935, 0.30992663546997407, 0.30966435261520137, 0.3093042261754413, 0.30884421824415975, 0.3082822909148224, 0.3076164062808957, 0.306844526435845, 0.30596461347313664, 0.30497462948623627, 0.3038725365686099, 0.3026562968137236, 0.30132387231504293, 0.29987322516603404, 0.2983023174601627, 0.2966091112908951, 0.2947915687516967, 0.2928476519360339, 0.2907753229373722, 0.2885725438491777, 0.2862372767649163, 0.2837674837780539, 0.28116369968208604, 0.2784367500706276, 0.2756000332373226, 0.2726669474758154, 0.2696508910797503, 0.2665652623427717, 0.26342345955852375, 0.260238881020651, 0.25702492502279745, 0.2537949898586077, 0.25056247382172586, 0.24734077520579636, 0.24414329230446338, 0.2409834234113713, 0.23787456682016447, 0.23482614308799235, 0.23183166182602574, 0.2288806549089405, 0.22596265421141254, 0.2230671916081179, 0.2201837989737325, 0.21730200818293222, 0.21441135111039308, 0.21150135963079092, 0.2085615656188018, 0.20558150094910152, 0.20255069749636614, 0.1994586871352716, 0.19629500174049372, 0.19304917318670864, 0.18971449090985038, 0.18629927459088613, 0.18281560147204132, 0.17927554879554133, 0.17569119380361162, 0.1720746137384776, 0.16843788584236452, 0.16479308735749798, 0.16115229552610325, 0.1575275875904058, 0.15393104079263095, 0.15037473237500415, 0.1468707395797509, 0.14343113964909648, 0.14006800982526638, 0.13679342735048583, 0.13361946946698045, 0.1305582134169755, 0.12762173644269645, 0.12482211578636863, 0.12217142869021756, 0.11968175239646853, 0.11736516414734703, 0.11523374118507841, 0.1132995607518881, 0.11157470009000146, 0.11007123644164397, 0.10880124704904093, 0.1077768091544178, 0.10701000000000001],
        [0.30586638642531744, 0.3064280780711293, 0.3069197269519394, 0.30733897947574335, 0.3076834820505367, 0.30795088108431523, 0.30813882298507445, 0.30824495416080994, 0.30826692101951736, 0.3082023699691924, 0.30804894741783073, 0.3078042997734278, 0.30746607344397947, 0.30703191483748116, 0.3064994703619286, 0.3058663864253174, 0.30513030943564307, 0.3042888858009014, 0.3033397619290882, 0.3022805842281984, 0.3011089991062286, 0.29982265297117355, 0.2984191922310293, 0.2968962632937915, 0.2952515125674557, 0.29348258646001757, 0.2915871313794725, 0.2895627937338165, 0.2874072199310449, 0.28511805637915355, 0.2826929494861379, 0.28013219409004914, 0.27744667874916157, 0.2746499404518044, 0.27175551618630717, 0.2687769429409998, 0.26572775770421153, 0.26262149746427194, 0.2594716992095108, 0.2562918999282574, 0.2530956366088415, 0.2498964462395926, 0.24670786580884024, 0.24354343230491404, 0.24041668271614342, 0.23734115403085812, 0.23432635725990966, 0.2313656995042378, 0.22844856188730445, 0.22556432553257133, 0.2227023715635005, 0.2198520811035536, 0.21700283527619246, 0.21414401520487902, 0.2112650020130751, 0.20835517682424243, 0.20540392076184305, 0.2024006149493386, 0.19933464051019104, 0.1961953785678621, 0.19297221024581376, 0.18965830996134525, 0.18626202530710645, 0.18279549716958454, 0.1792708664352668, 0.17570027399064053, 0.17209586072219304, 0.16846976751641154, 0.16483413525978333, 0.1612011048387957, 0.157582817139936, 0.1539914130496914, 0.15043903345454918, 0.14693781924099672, 0.14349991129552117, 0.1401374505046099, 0.1368625777547501, 0.1336874339324292, 0.13062415992413434, 0.12768489661635285, 0.12488178489557199, 0.12222696564827905, 0.1197325797609613, 0.11741076812010608, 0.11527367161220058, 0.1133334311237321, 0.11160218754118795, 0.1100920817510554, 0.10881525463982165, 0.1077838470939741, 0.10700999999999998],
        [0.3042972349907918, 0.30481806022785796, 0.3052760740392206, 0.30566860130651236, 0.30599296691136585, 0.3062464957354139, 0.3064265126602893, 0.3065303425676247, 0.30655531033905264, 0.30649874085620615, 0.30635795900071777, 0.30613028965422007, 0.305813057698346, 0.30540358801472806, 0.30489920548499905, 0.30429723499079186, 0.30359500141373885, 0.3027898296354729, 0.3018790445376268, 0.3008599710018331, 0.2997299339097248, 0.29848625814293417, 0.2971262685830942, 0.2956472901118376, 0.2940466476107971, 0.29232166596160525, 0.2904696700458948, 0.28848798474529863, 0.2863739349414492, 0.2841248455159792, 0.2817380413505217, 0.2792135861258403, 0.276562498719224, 0.27379853680709276, 0.27093545806586666, 0.2679870201719657, 0.26496698080180997, 0.26188909763181956, 0.2587671283384143, 0.2556148305980145, 0.25244596208704007, 0.24927428048191103, 0.24611354345904757, 0.24297750869486962, 0.23987993386579715, 0.23683457664825044, 0.23385109356664885, 0.23092273653741066, 0.22803865632495304, 0.2251880036936938, 0.22235992940805047, 0.2195435842324405, 0.21672811893128163, 0.21390268426899117, 0.2110564310099868, 0.20817850991868606, 0.20525807175950647, 0.20228426729686574, 0.19924624729518117, 0.19613316251887042, 0.19293416373235112, 0.18964224644163694, 0.1862657851191269, 0.18281699897881604, 0.17930810723469964, 0.17575132910077265, 0.1721588837910304, 0.1685429905194679, 0.16491586850008044, 0.16128973694686302, 0.15767681507381096, 0.1540893220949192, 0.15053947722418304, 0.1470394996755976, 0.14360160866315796, 0.1402380234008594, 0.1369609631026969, 0.13378264698266573, 0.130715294254761, 0.12777112413297784, 0.12496235583131139, 0.12230120856375684, 0.11979990154430932, 0.117470653986964, 0.11532568510571599, 0.11337721411456046, 0.11163746022749256, 0.11011864265850738, 0.10883298062160013, 0.10779269333076594, 0.10700999999999997],
        [0.30292498630415826, 0.3034064356929586, 0.303832135091106, 0.3041990779231863, 0.30450425761378513, 0.3047446675874886, 0.30491730126888233, 0.30501915208255226, 0.30504721345308433, 0.30499847880506437, 0.3048699415630781, 0.30465859515171156, 0.30436143299555035, 0.30397544851918046, 0.30349763514718786, 0.30292498630415815, 0.3022544954146773, 0.3014831559033313, 0.3006079611947058, 0.2996259047133867, 0.29853397988395985, 0.297329180131011, 0.29600849887912634, 0.2945689295528913, 0.29300746557689206, 0.2913211003757143, 0.2895068273739438, 0.28756163999616663, 0.28548253166696846, 0.2832664958109352, 0.28091052585265275, 0.27841446309542867, 0.27578954035745806, 0.27304983833565805, 0.27020943772694506, 0.2672824192282365, 0.2642828635364491, 0.26122485134849954, 0.25812246336130507, 0.2549897802717823, 0.2518408827768483, 0.24868985157342, 0.24555076735841425, 0.2424377108287479, 0.23936476268133786, 0.2363460036131011, 0.23339130433445215, 0.23049369560979677, 0.22764199821703804, 0.22482503293407935, 0.22203162053882405, 0.21925058180917542, 0.21647073752303658, 0.21368090845831111, 0.2108699153929021, 0.2080265791047128, 0.2051397203716468, 0.20219815997160714, 0.19919071868249724, 0.19610621728222016, 0.1929334765486796, 0.18966523351818687, 0.18630989026068703, 0.1828797651045333, 0.1793871763780789, 0.1758444424096771, 0.1722638815276812, 0.1686578120604444, 0.16503855233631998, 0.1614184206836612, 0.1578097354308213, 0.15422481490615353, 0.15067597743801117, 0.14717554135474745, 0.1437358249847156, 0.14036914665626898, 0.1370878246977607, 0.13390417743754415, 0.13083052320397245, 0.12787918032539894, 0.12506246713017682, 0.12239270194665942, 0.11988220310319993, 0.11754328892815165, 0.11538827774986778, 0.1134294878967016, 0.11167923769700638, 0.11014984547913537, 0.10885362957144176, 0.10780290830227891, 0.10701],
        [0.30176567469225557, 0.302209219272582, 0.3026039259041569, 0.30294644253404424, 0.30323341710930757, 0.3034614975770108, 0.30362733188421753, 0.30372756797799144, 0.30375885380539647, 0.30371783731349644, 0.3036011664493547, 0.30340548916003546, 0.30312745339260205, 0.3027637070941186, 0.30231089821164836, 0.3017656746922555, 0.3011246844830036, 0.3003845755309565, 0.2995419957831779, 0.29859359318673145, 0.297536015688681, 0.2963659112360902, 0.2950799277760229, 0.2936747132555428, 0.2921469156217136, 0.29049318282159914, 0.28871016280226297, 0.2867945035107692, 0.28474285289418116, 0.28255185889956286, 0.28021816947397793, 0.27774141230478305, 0.2751331340405066, 0.2724078610699699, 0.26958011978199403, 0.26666443656540045, 0.2636753378090105, 0.2606273499016453, 0.25753499923212614, 0.2544128121892744, 0.2512753151619112, 0.248137034538858, 0.245012496708936, 0.2419162280609664, 0.23886275498377052, 0.23586660386616976, 0.2329379418895615, 0.23006949940564891, 0.22724964755871108, 0.22446675749302744, 0.2217092003528773, 0.21896534728253986, 0.21622356942629445, 0.21347223792842027, 0.21069972393319675, 0.2078943985849031, 0.20504463302781858, 0.20213879840622256, 0.1991652658643943, 0.19611240654661297, 0.19296859159715796, 0.18972620435845639, 0.18639367696552625, 0.18298345375153335, 0.1795079790496436, 0.17597969719302284, 0.17241105251483682, 0.16881448934825147, 0.1652024520264326, 0.16158738488254606, 0.15798173224975773, 0.15439793846123337, 0.15084844785013882, 0.14734570474964004, 0.14390215349290272, 0.14053023841309284, 0.13724240384337613, 0.13405109411691846, 0.1309687535668857, 0.12800782652644369, 0.12518075732875822, 0.12249999030699514, 0.11997796979432034, 0.11762714012389966, 0.1154599456288989, 0.1134888306424839, 0.11172623949782053, 0.11018461652807465, 0.10887640606641201, 0.10781405244599851, 0.10701],
        [0.30083533448192307, 0.3012424257728787, 0.30160746227493446, 0.3019267283473653, 0.30219650834944634, 0.30241308664045247, 0.302572747579659, 0.30267177552634095, 0.30270645483977343, 0.3026730698792316, 0.3025679050039905, 0.30238724457332505, 0.3021273729465106, 0.30178457448282203, 0.3013551335415344, 0.30083533448192307, 0.30022146166326275, 0.2995097994448288, 0.29869663218589626, 0.2977782442457402, 0.2967509199836357, 0.29561094375885766, 0.2943545999306816, 0.2929781728583821, 0.2914779469012347, 0.2898502064185142, 0.28809123576949575, 0.28619731931345455, 0.2841647414096655, 0.28198978641740385, 0.27966873869594455, 0.27720102105987254, 0.2745986101450126, 0.2718766210424985, 0.26905016884346494, 0.26613436863904605, 0.26314433552037636, 0.2600951845785899, 0.2570020309048211, 0.25387998959020425, 0.25074417572587376, 0.2476097044029637, 0.2444916907126088, 0.24140524974594293, 0.23836549659410058, 0.23538754634821613, 0.23248195855821893, 0.22964107060921968, 0.226852664345124, 0.22410452160983765, 0.2213844242472664, 0.21868015410131597, 0.2159794930158921, 0.2132702228349005, 0.2105401254022469, 0.20777698256183702, 0.20496857615757672, 0.20210268803337167, 0.19916710003312757, 0.1961495940007501, 0.19303795178014518, 0.1898240921299069, 0.18651648146738403, 0.1831277231246136, 0.1796704204336328, 0.17615717672647882, 0.17260059533518876, 0.16901327959179974, 0.165407832828349, 0.16179685837687363, 0.15819295956941085, 0.15460873973799769, 0.15105680221467138, 0.14754975033146905, 0.14410018742042793, 0.14072071681358508, 0.13742394184297768, 0.13422246584064282, 0.13112889213861775, 0.12815582406893958, 0.1253158649636454, 0.12262161815477247, 0.12008568697435788, 0.1177206747544388, 0.1155391848270524, 0.11355382052423575, 0.11177718517802611, 0.11022188212046054, 0.10890051468357621, 0.10782568619941033, 0.10700999999999998],
        [0.3001500000000001, 0.30052207, 0.30085876, 0.3011559685714287, 0.30140959428571434, 0.3016155357142858, 0.3017696914285716, 0.30186796, 0.30190624, 0.30188043000000003, 0.30178642857142857, 0.30162013428571427, 0.3013774457142857, 0.30105426142857145, 0.30064648000000005, 0.30015000000000003, 0.29956072, 0.2988745385714285, 0.2980873542857143, 0.29719506571428567, 0.2961935714285714, 0.29507876999999993, 0.2938465599999999, 0.2924928399999999, 0.29101350857142855, 0.2894044642857143, 0.28766160571428573, 0.2857808314285714, 0.28375804, 0.28158912999999997, 0.27926999999999996, 0.2767998766666666, 0.2741912990476191, 0.27146013428571436, 0.2686222495238095, 0.26569351190476187, 0.2626897885714286, 0.2596269466666667, 0.25652085333333335, 0.2533873757142857, 0.25024238095238094, 0.24710173619047618, 0.2439813085714286, 0.2408969652380953, 0.23786457333333333, 0.23490000000000003, 0.23201430666666667, 0.22919933190476197, 0.2264421085714286, 0.22372966952380954, 0.22104904761904767, 0.21838727571428576, 0.21573138666666675, 0.21306841333333335, 0.2103853885714286, 0.2076693452380953, 0.2049073161904762, 0.20208633428571435, 0.19919343238095244, 0.19621564333333336, 0.19314000000000006, 0.18995783, 0.1866776400000001, 0.18331223142857145, 0.17987440571428573, 0.1763769642857143, 0.1728327085714286, 0.16925443999999998, 0.16565495999999996, 0.16204707000000002, 0.1584435714285714, 0.1548572657142857, 0.15130095428571427, 0.14778743857142856, 0.14432952, 0.14094, 0.13763167999999998, 0.13441736142857144, 0.1313098457142857, 0.12832193428571428, 0.12546642857142856, 0.12275612999999998, 0.12020383999999998, 0.11782235999999999, 0.11562449142857142, 0.11362303571428573, 0.1118307942857143, 0.11026056857142859, 0.10892516000000001, 0.10783736999999999, 0.10701],
        [0.2997214495696423, 0.3000600092610258, 0.30036975112050834, 0.30064616410848327, 0.30088473718534336, 0.3010809593114819, 0.3012303194472918, 0.30132830655316606, 0.30137040958949757, 0.30135211751667984, 0.30126891929510546, 0.30111630388516764, 0.30088976024725944, 0.3005847773417738, 0.30019684412910363, 0.2997214495696423, 0.29915408262378257, 0.29849023225191756, 0.2977253874144404, 0.2968550370717439, 0.2958746701842212, 0.2947797757122655, 0.2935658426162695, 0.2922283598566266, 0.2907628163937296, 0.28916470118797155, 0.2874295031997455, 0.28555271138944455, 0.2835298147174616, 0.28135630214418983, 0.2790276626300222, 0.2765429359654783, 0.27391536526158505, 0.27116174445949554, 0.268298867500363, 0.26534352832534097, 0.2623125208755826, 0.25922263909224097, 0.2560906769164697, 0.25293342828942206, 0.24976768715225117, 0.24661024744611038, 0.2434779031121531, 0.24038744809153248, 0.2373556763254019, 0.23439938175491468, 0.23153024475197087, 0.22873949141145838, 0.22601323425901174, 0.22333758582026558, 0.2206986586208547, 0.21808256518641356, 0.21547541804257692, 0.2128633297149792, 0.21023241272925536, 0.20756877961103976, 0.2048585428859672, 0.20208781507967222, 0.19924270871778962, 0.19630933632595376, 0.1932738104297996, 0.19012673189639911, 0.18687665495857508, 0.18353662219058764, 0.180119676166697, 0.17663885946116345, 0.17310721464824716, 0.1695377843022083, 0.16594361099730726, 0.162337737307804, 0.15873320580795894, 0.1551430590720322, 0.15158033967428414, 0.14805809018897467, 0.14458935319036434, 0.1411871712527132, 0.13786458695028148, 0.1346346428573294, 0.13151038154811723, 0.12850484559690517, 0.1256310775779534, 0.12290212006552208, 0.12033101563387154, 0.117930806857262, 0.11571453630995357, 0.11369524656620655, 0.11188598020028115, 0.11029977978643761, 0.10894968789893605, 0.10784874711203678, 0.10700999999999998],
        [0.2995444374992731, 0.29985147086675285, 0.3001360326559887, 0.30039318663665837, 0.30061799657843974, 0.3008055262510106, 0.3009508394240488, 0.30104899986723244, 0.301095071350239, 0.3010841176427466, 0.30101120251443325, 0.30087138973497646, 0.3006597430740542, 0.3003713263013442, 0.3000012031865245, 0.2995444374992731, 0.2989960930092674, 0.2983512334861857, 0.2976049226997055, 0.29675222441950494, 0.29578820241526177, 0.2947079204566537, 0.2935064423133589, 0.2921788317550549, 0.2907201525514197, 0.2891254684721313, 0.28738984328686723, 0.28550834076530546, 0.28347602467712407, 0.28128795879200064, 0.2789392068796132, 0.2764286339339991, 0.27377030984663475, 0.27098210573335557, 0.26808189270999744, 0.2650875418923964, 0.2620169243963881, 0.2588879113378081, 0.2557183738324924, 0.2525261829962767, 0.24932920994499688, 0.24614532579448867, 0.2429924016605879, 0.23988830865913022, 0.2368509179059514, 0.23389810051688742, 0.23104225619449464, 0.2282738989882126, 0.2255780715342013, 0.22293981646862107, 0.22034417642763207, 0.21777619404739443, 0.21522091196406828, 0.21266337281381384, 0.21008861923279123, 0.20748169385716062, 0.20482763932308223, 0.2021114982667162, 0.19931831332422273, 0.19643312713176186, 0.19344098232549398, 0.19033163478757645, 0.1871136933841562, 0.1838004802273775, 0.18040531742938465, 0.17694152710232183, 0.17342243135833343, 0.1698613523095636, 0.1662716120681567, 0.1626665327462569, 0.1590594364560085, 0.15546364530955575, 0.15189248141904294, 0.1483592668966143, 0.14487732385441415, 0.14145997440458677, 0.13812054065927626, 0.13487234473062706, 0.1317287087307833, 0.1287029547718894, 0.12580840496608947, 0.12305838142552782, 0.12046620626234879, 0.11804520158869655, 0.11580868951671541, 0.1137699921585496, 0.11194243162634339, 0.11033933003224114, 0.10897400948838691, 0.10785979210692515, 0.10701000000000001],
        [0.29960946209363193, 0.29988752462890766, 0.30014911787056375, 0.30038887552805305, 0.30060143131082784, 0.3007814189283407, 0.3009234720900444, 0.3010222245053913, 0.301072309883834, 0.30106836193482517, 0.3010050143678173, 0.3008769008922629, 0.30067865521761455, 0.300404911053325, 0.30005030210884653, 0.2996094620936318, 0.29907702471713343, 0.29844762368880406, 0.2977158927180961, 0.296876465514462, 0.29592397578735463, 0.2948530572462264, 0.29365834360052984, 0.29233446855971756, 0.29087606583324205, 0.289277769130556, 0.28753421216111175, 0.28564002863436216, 0.28358985225975947, 0.2813783167467567, 0.2790000558048058, 0.27645377508426444, 0.2737544679991077, 0.27092119990421565, 0.2679730361544685, 0.26492904210474594, 0.26180828310992815, 0.2586298245248951, 0.2554127317045267, 0.25217607000370307, 0.24893890477730402, 0.2457203013802097, 0.2425393251673001, 0.2394150414934551, 0.2363665157135547, 0.23341281318247908, 0.230567130585425, 0.22781918992885808, 0.2251528445495603, 0.22255194778431403, 0.22000035296990172, 0.21748191344310566, 0.21498048254070806, 0.21247991359949125, 0.2099640599562377, 0.2074167749477295, 0.20482191191074908, 0.2021633241820788, 0.19942486509850085, 0.19659038799679754, 0.19364374621375144, 0.190573756402206, 0.18738908847925165, 0.18410337567803978, 0.18073025123172215, 0.17728334837345017, 0.17377630033637567, 0.1702227403536501, 0.1666363016584252, 0.16303061748385259, 0.15941932106308382, 0.15581604562927048, 0.15223442441556417, 0.14868809065511657, 0.14519067758107926, 0.14175581842660392, 0.13839714642484205, 0.1351282948089454, 0.1319628968120654, 0.1289145856673538, 0.12599699460796218, 0.12322375686704219, 0.12060850567774539, 0.11816487427322342, 0.11590649588662785, 0.11384700375111036, 0.11200003109982251, 0.11037921116591598, 0.10899817718254226, 0.10787056238285306, 0.10701000000000002],
        [0.2999070216574585, 0.30015924035921593, 0.30040052002835627, 0.3006250701547664, 0.30082710022833237, 0.3010008197389414, 0.30114043817647984, 0.30124016503083456, 0.30129420979189225, 0.30129678194953946, 0.30124209099366306, 0.30112434641414954, 0.30093775770088566, 0.30067653434375813, 0.30033488583265344, 0.2999070216574585, 0.2993871513080598, 0.29876948427434413, 0.2980482300461983, 0.2972175981135086, 0.29627179796616215, 0.2952050390940453, 0.29401153098704486, 0.29268548313504744, 0.2912211050279399, 0.28961260615560874, 0.28785419600794065, 0.28594008407482235, 0.28386447984614044, 0.28162159281178173, 0.2792056324616328, 0.2766151639283094, 0.27386617491534404, 0.27097900876899755, 0.2679740088355316, 0.2648715184612073, 0.2616918809922862, 0.2584554397750295, 0.25518253815569825, 0.25189351948055416, 0.24860872709585838, 0.2453485043478722, 0.2421331945828571, 0.2389831411470742, 0.23591868738678481, 0.23296017664825044, 0.23012165751594926, 0.2273919995272284, 0.2247537774576515, 0.22218956608278256, 0.21968194017818568, 0.21721347451942463, 0.21476674388206352, 0.21232432304166607, 0.20986878677379636, 0.20738270985401824, 0.20484866705789567, 0.20224923316099266, 0.1995669829388731, 0.19678449116710087, 0.19388433262124, 0.1908543144689621, 0.18770317344636975, 0.18444487868167325, 0.18109339930308288, 0.17766270443880913, 0.17416676321706212, 0.17061954476605226, 0.16703501821398992, 0.16342715268908525, 0.15980991731954872, 0.1561972812335906, 0.1526032135594212, 0.14904168342525076, 0.14552665995928968, 0.14207211228974828, 0.13869200954483682, 0.13540032085276563, 0.13221101534174512, 0.1291380621399855, 0.12619543037569708, 0.12339708917709019, 0.12075700767237517, 0.11828915498976238, 0.11600750025746202, 0.11392601260368453, 0.11205866115664011, 0.11041941504453912, 0.10902224339559188, 0.10788111533800873, 0.10700999999999997],
        [0.3004276144954929, 0.30065768786940456, 0.30088175239348935, 0.30109360988889755, 0.3012870621767783, 0.3014559110782816, 0.3015939584145572, 0.30169500600675475, 0.3017528556760239, 0.3017613092435146, 0.3017141685303764, 0.3016052353577591, 0.30142831154681227, 0.30117719891868583, 0.3008456992945294, 0.3004276144954928, 0.2999167463427255, 0.2993068966573777, 0.2985918672605987, 0.29776545997353826, 0.29682147661734637, 0.29575371901317243, 0.2945559889821664, 0.293222088345478, 0.29174581892425683, 0.2901209825396526, 0.2883413810128152, 0.28640081616489416, 0.2842930898170394, 0.2820120037904005, 0.27955135990612723, 0.27690960497817013, 0.2741037657916838, 0.27115551412462274, 0.26808652175494263, 0.26491846046059847, 0.26167300201954524, 0.25837181820973826, 0.25503658080913266, 0.25168896159568355, 0.24835063234734595, 0.24504326484207517, 0.24178853085782637, 0.2386081021725545, 0.2355236505642148, 0.23255684781076247, 0.22972262657725462, 0.2270089630771572, 0.22439709441103806, 0.22186825767946503, 0.219403689983006, 0.216984628422229, 0.21459231009770188, 0.21220797210999257, 0.20981285155966892, 0.2073881855472987, 0.20491521117345005, 0.20237516553869078, 0.19974928574358877, 0.19701880888871193, 0.1941649720746282, 0.19117452671651886, 0.1880562814880189, 0.18482455937737677, 0.18149368337284086, 0.17807797646265958, 0.17459176163508136, 0.17104936187835457, 0.1674651001807277, 0.1638532995304491, 0.16022828291576724, 0.15660437332493057, 0.15299589374618738, 0.14941716716778616, 0.14588251657797532, 0.14240626496500333, 0.13900273531711846, 0.13568625062256925, 0.1324711338696041, 0.12937170804647138, 0.12640229614141948, 0.12357722114269692, 0.12091080603855205, 0.11841737381723327, 0.11611124746698907, 0.11400674997606776, 0.11211820433271784, 0.1104599335251877, 0.10904626054172568, 0.10789150837058031, 0.10700999999999997],
        [0.30116173891247466, 0.3013739369711992, 0.3015843282300858, 0.30178633410254574, 0.3019733760019903, 0.30213887534183065, 0.30227625353547805, 0.30237893199634375, 0.302440332137839, 0.302453875373375, 0.30241298311636283, 0.30231107678021385, 0.3021415777783395, 0.30189790752415047, 0.30157348743105844, 0.30116173891247455, 0.3006560833818099, 0.30004994225247583, 0.2993367369378836, 0.29850988885144436, 0.29756281940656937, 0.29648895001666975, 0.29528170209515686, 0.29393449705544183, 0.29244075631093613, 0.2907939012750506, 0.28898735336119663, 0.28701453398278565, 0.2848688645532287, 0.28254376648593704, 0.2800326611943218, 0.2773339027458819, 0.2744655758244668, 0.27145069776801295, 0.2683122859144573, 0.265073357601737, 0.2617569301677888, 0.25838602095054936, 0.25498364728795553, 0.25157282651794444, 0.24817657597845275, 0.24481791300741731, 0.2415198549427752, 0.23830541912246295, 0.2351976228844175, 0.23221948356657596, 0.2293868273605282, 0.22668671587247824, 0.22409901956228298, 0.2216036088897994, 0.21918035431488483, 0.2168091262973962, 0.21446979529719062, 0.21214223177412514, 0.20980630618805682, 0.20744188899884275, 0.20502885066634005, 0.20254706165040584, 0.199976392410897, 0.19729671340767077, 0.19448789510058423, 0.19153561087355056, 0.18844874580670753, 0.18524198790424917, 0.18193002517036935, 0.17852754560926215, 0.1750492372251215, 0.17150978802214123, 0.16792388600451552, 0.1643062191764382, 0.1606714755421032, 0.15703434310570458, 0.1534095098714362, 0.1498116638434921, 0.14625549302606616, 0.14275568542335249, 0.1393269290395449, 0.13598391187883735, 0.13274132194542387, 0.12961384724349845, 0.12661617577725492, 0.12376299555088743, 0.12106899456858974, 0.11854886083455599, 0.11621728235297998, 0.11408894712805578, 0.11217854316397732, 0.11050075846493856, 0.10907028103513343, 0.10790179887875594, 0.10701],
        [0.3020998932131434, 0.3022990574763259, 0.3024997608022678, 0.30269508216781005, 0.30287810054979286, 0.30304189492505734, 0.3031795442704441, 0.3032841275627937, 0.30334872377894695, 0.3033664118957448, 0.3033302708900277, 0.30323337973863634, 0.3030688174184115, 0.30282966290619395, 0.3025089951788243, 0.3020998932131433, 0.30159543598599164, 0.30098870247421006, 0.3002727716546393, 0.29944072250412007, 0.2984856339994929, 0.2974005851175987, 0.29617865483527817, 0.29481292212937193, 0.29329646597672066, 0.29162236535416536, 0.28978369923854636, 0.2877735466067046, 0.2855849864354807, 0.2832110977017153, 0.2806449593822493, 0.2778848617434801, 0.274949940210033, 0.2718645414960894, 0.2686530123158314, 0.26533969938344076, 0.26194894941309954, 0.2585051091189894, 0.2550325252152923, 0.25155554441618994, 0.24809851343586437, 0.24468577898849728, 0.24134168778827067, 0.2380905865493663, 0.23495682198596593, 0.2319647408122516, 0.22913104945695717, 0.22644189320702487, 0.22387577706394904, 0.2214112060292239, 0.21902668510434395, 0.21670071929080345, 0.21441181359009667, 0.21213847300371796, 0.20985920253316165, 0.20755250717992205, 0.20519689194549345, 0.2027708618313703, 0.20025292183904686, 0.19762157697001734, 0.19485533222577622, 0.1919387846687312, 0.1888808996049438, 0.18569673440138915, 0.18240134642504202, 0.1790097930428777, 0.1755371316218709, 0.17199841952899675, 0.1684087141312303, 0.1647830727955465, 0.16113655288892031, 0.1574842117783268, 0.15384110683074095, 0.15022229541313772, 0.14664283489249205, 0.14311778263577915, 0.1396621960099738, 0.1362911323820511, 0.13301964911898603, 0.1298628035877536, 0.1268356531553288, 0.12395325518868659, 0.12123066705480205, 0.11868294612065014, 0.11632514975320583, 0.11417233531944417, 0.11223956018634008, 0.11054188172086865, 0.1090943572900048, 0.10791204426072358, 0.10700999999999998],
        [0.30323257570223905, 0.30342411919651124, 0.30361956337415885, 0.3038116934567896, 0.3039932946660109, 0.30415715222343087, 0.30429605135065696, 0.3044027772692968, 0.30447011520095824, 0.3044908503672491, 0.3044577679897767, 0.3043636532901491, 0.30420129148997377, 0.30396346781085853, 0.3036429674744111, 0.303232575702239, 0.3027250777159499, 0.30211325873715184, 0.3013899039874523, 0.30054779868845877, 0.29957972806177935, 0.29847847732902144, 0.2972368317117928, 0.29584757643170134, 0.29430349671035444, 0.29259737776935996, 0.2907220048303256, 0.28867016311485894, 0.2864346378445678, 0.2840082142410598, 0.28138367752594273, 0.27855928648300055, 0.2755551941447224, 0.2723970271057738, 0.2691104119608204, 0.2657209753045276, 0.26225434373156115, 0.2587361438365862, 0.2551920022142686, 0.2516475454592736, 0.2481284001662669, 0.24466019292991395, 0.24126855034488034, 0.23797909900583158, 0.23481746550743302, 0.23180927644435043, 0.22897208245772865, 0.22629113037463086, 0.22374359106859934, 0.22130663541317672, 0.21895743428190556, 0.21667315854832833, 0.21443097908598746, 0.2122080667684255, 0.20998159246918507, 0.20772872706180845, 0.20542664141983838, 0.2030525064168172, 0.20058349292628752, 0.19799677182179176, 0.1952695139768726, 0.19238526583073515, 0.18935307608523627, 0.1861883690078955, 0.18290656886623255, 0.1795230999277668, 0.17605338646001792, 0.17251285273050546, 0.16891692300674907, 0.16528102155626823, 0.16162057264658258, 0.15795100054521163, 0.154287729519675, 0.15064618383749231, 0.14704178776618299, 0.14348996557326682, 0.1400061415262632, 0.13660573989269184, 0.13330418494007218, 0.1301169009359239, 0.1270593121477665, 0.12414684284311962, 0.12139491728950282, 0.11881895975443568, 0.11643439450543774, 0.11425664581002859, 0.11230113793572781, 0.11058329515005501, 0.10911854172052969, 0.10792230191467149, 0.10700999999999998],
        [0.30455028468450135, 0.3047401919434812, 0.30493524920988135, 0.3051280073415835, 0.30531101719646914, 0.3054768296324202, 0.30561799550731833, 0.3057270656790452, 0.3057965910054825, 0.3058191223445121, 0.3057872105540156, 0.30569340649187476, 0.30553026101597114, 0.30529032498418657, 0.30496614925440274, 0.30455028468450135, 0.304035282132364, 0.30341369245587263, 0.30267806651290885, 0.3018209551613542, 0.3008349092590907, 0.29971247966399983, 0.29844621723396336, 0.29702867282686296, 0.2954523973005805, 0.2937099415129974, 0.2917938563219956, 0.28969669258545677, 0.2874110011612625, 0.28492933290729466, 0.2822442386814349, 0.2793539814764784, 0.27627967282487503, 0.27304813639398795, 0.2696861958511803, 0.2662206748638154, 0.26267839709925667, 0.259086186224867, 0.2554708659080099, 0.25185925981604856, 0.2482781916163462, 0.24475448497626612, 0.24131496356317156, 0.23798645104442576, 0.23479577108739183, 0.23176974735943326, 0.22892671595402997, 0.22625106266912975, 0.22371868572879688, 0.22130548335709602, 0.21898735377809164, 0.21674019521584817, 0.21453990589443026, 0.2123623840379022, 0.21018352787032857, 0.2079792356157738, 0.20572540549830254, 0.20339793574197917, 0.2009727245708682, 0.19842567020903404, 0.19573267088054142, 0.19287627208823652, 0.18986560845009318, 0.18671646186286725, 0.18344461422331435, 0.18006584742819032, 0.17659594337425094, 0.1730506839582518, 0.16944585107694873, 0.16579722662709748, 0.1621205925054538, 0.1584317306087733, 0.15474642283381185, 0.1510804510773252, 0.14744959723606899, 0.1438696432067991, 0.140356370886271, 0.1369255621712408, 0.13359299895846394, 0.1303744631446963, 0.12728573662669354, 0.12434260130121148, 0.12156083906500585, 0.11895623181483236, 0.11654456144744677, 0.11434160985960477, 0.1123631589480621, 0.11062499060957462, 0.10914288674089791, 0.10793262923878776, 0.10701],
        [0.30604351846467, 0.30623834552896195, 0.30643833157355815, 0.30663586319429076, 0.306823326986992, 0.30699310954749426, 0.30713759747162983, 0.3072491773552308, 0.30732023579412954, 0.3073431593841584, 0.3073103347211496, 0.30721414840093536, 0.307046987019348, 0.3068012371722198, 0.30646928545538304, 0.30604351846466993, 0.3055163227959127, 0.3048800850449437, 0.3041271918075952, 0.3032500296796995, 0.3022409852570888, 0.3010924451355955, 0.2997967959110517, 0.2983464241792896, 0.29673371653614183, 0.29495105957744056, 0.2929908398990176, 0.2908454440967057, 0.28850725876633715, 0.28596867050374386, 0.28322206590475846, 0.2802657512359493, 0.2771217114468309, 0.27381785115765306, 0.2703820749886664, 0.26684228756012174, 0.263226393492269, 0.2595622974053589, 0.2558779039196418, 0.25220111765536807, 0.2485598432327881, 0.24498198527215248, 0.24149544839371154, 0.2381281372177156, 0.23490795636441514, 0.23186281045406076, 0.22901173953704812, 0.22633832538435503, 0.22381728519710456, 0.22142333617641982, 0.21913119552342417, 0.2169155804392405, 0.21475120812499215, 0.2126127957818021, 0.21047506061079369, 0.2083127198130898, 0.2061004905898138, 0.20381309014208887, 0.2014252356710379, 0.1989116443777842, 0.196247033463451, 0.19341302116990935, 0.19041882990202277, 0.18728058310540283, 0.1840144042256611, 0.18063641670840896, 0.17716274399925813, 0.17360950954382, 0.16999283678770624, 0.16632884917652824, 0.16263367015589766, 0.15892342317142602, 0.15521423166872478, 0.15152221909340552, 0.1478635088910798, 0.1442542245073591, 0.14071048938785502, 0.13724842697817907, 0.13388416072394274, 0.13063381407075766, 0.12751351046423529, 0.12453937334998716, 0.1217275261736249, 0.11909409238075995, 0.1166551954170039, 0.11442695872796824, 0.11242550575926455, 0.11066695995650434, 0.10916744476529913, 0.10794308363126051, 0.10700999999999995],
        [0.30770277534748475, 0.30790964976467977, 0.3081203237293121, 0.30832710038701083, 0.30852228288340455, 0.3086981743641224, 0.3088470779747932, 0.30896129686104595, 0.30903313416850947, 0.3090548930428127, 0.3090188766295845, 0.3089173880744539, 0.3087427305230497, 0.30848720712100086, 0.3081431210139362, 0.3077027753474847, 0.30715847326727513, 0.3065025179189366, 0.305727212448098, 0.3048248600003881, 0.30378776372143595, 0.3026082267568704, 0.3012785522523203, 0.2997910433534146, 0.2981380032057823, 0.2963117349550522, 0.2943045417468531, 0.2921087267268142, 0.2897165930405642, 0.287120443833732, 0.28431258225194656, 0.281291400273449, 0.2780796452069297, 0.27470615319369085, 0.2711997603750349, 0.2675893028922644, 0.26390361688668185, 0.26017153849958946, 0.2564219038722899, 0.2526835491460855, 0.24898531046227862, 0.24535602396217182, 0.2418245257870676, 0.23841965207826823, 0.23517023897707615, 0.23210512262479394, 0.22924394279797042, 0.2265695538141405, 0.2240556136260854, 0.22167578018658649, 0.21940371144842521, 0.21721306536438278, 0.2150774998872406, 0.21297067296977987, 0.21086624256478206, 0.20873786662502844, 0.20655920310330034, 0.20430390995237907, 0.20194564512504598, 0.19945806657408233, 0.1968148322522697, 0.19399673080442806, 0.19101307364353362, 0.1878803028746014, 0.18461486060264634, 0.18123318893268353, 0.17775172996972796, 0.1741869258187946, 0.17055521858489855, 0.16687305037305475, 0.16315686328827825, 0.15942309943558408, 0.15568820091998722, 0.15196860984650265, 0.14828076832014547, 0.14464111844593064, 0.14106610232887318, 0.1375721620739881, 0.13417573978629035, 0.1308932775707951, 0.12774121753251722, 0.1247360017764718, 0.12189407240767382, 0.11923187153113834, 0.11676584125188033, 0.11451242367491477, 0.11248806090525675, 0.11070919504792126, 0.10919226820792327, 0.1079537224902778, 0.10700999999999995],
        [0.3095185536376854, 0.3097451744623607, 0.30997273894126615, 0.31019355829184264, 0.31039994373153146, 0.3105842064777736, 0.3107386577480104, 0.3108556087596829, 0.3109273707302321, 0.31094625487709954, 0.310904572417726, 0.3107946345695528, 0.31060875255002096, 0.31033923757657167, 0.3099784008666461, 0.3095185536376854, 0.30895200710713056, 0.3082710724924229, 0.30746806101100366, 0.30653528388031365, 0.3054650523177942, 0.30424967754088655, 0.3028814707670317, 0.3013527432136708, 0.29965580609824505, 0.2977829706381956, 0.2957265480509635, 0.29347884955399, 0.29103218636471606, 0.288378869700583, 0.28551121077903197, 0.2824277331010128, 0.2791518093015117, 0.27571302429902295, 0.27214096301204116, 0.2684652103590614, 0.2647153512585782, 0.2609209706290861, 0.2571116533890798, 0.2533169844570542, 0.2495665487515037, 0.24588993119092312, 0.24231671669380725, 0.23887649017865054, 0.2355988365639478, 0.2325133407681937, 0.2296401153279841, 0.22696138325231974, 0.22444989516830247, 0.22207840170303422, 0.2198196534836169, 0.21764640113715253, 0.21553139529074283, 0.21344738657148982, 0.2113671256064954, 0.20926336302286144, 0.20710884944768987, 0.2048763355080826, 0.20253857183114157, 0.20006830904396855, 0.1974382977736657, 0.19462861872046677, 0.191648672877134, 0.1885151913095616, 0.1852449050836438, 0.1818545452652748, 0.17836084292034882, 0.17478052911476008, 0.17113033491440277, 0.16742699138517114, 0.16368722959295948, 0.15992778060366183, 0.15616537548317264, 0.15241674529738594, 0.14869862111219598, 0.14502773399349708, 0.14142081500718334, 0.137894595219149, 0.13446580569528835, 0.13115117750149557, 0.12796744170366484, 0.12493132936769039, 0.12205957155946646, 0.11936889934488733, 0.11687604378984708, 0.11459773596024003, 0.11255070692196036, 0.11075168774090231, 0.10921740948296008, 0.10796460321402788, 0.10700999999999998],
        [0.31148135164001167, 0.3117359894337311, 0.31198709047354284, 0.3122270762808853, 0.31244836837719714, 0.31264338828391675, 0.31280455752248276, 0.31292429761433344, 0.31299503008090734, 0.31300917644364323, 0.31295915822397935, 0.3128373969433543, 0.3126363141232064, 0.3123483312849744, 0.3119658699500966, 0.3114813516400116, 0.31088719787615776, 0.31017583017997385, 0.30933967007289814, 0.30837113907636915, 0.3072626587118255, 0.3060066505007056, 0.30459553596444794, 0.30302173662449094, 0.3012776740022734, 0.29935576961923344, 0.29724844499680975, 0.2949481216564408, 0.29244722111956517, 0.2897381649076211, 0.2868133745420475, 0.28367155423067636, 0.2803365389269167, 0.2768384462705707, 0.27320739390144116, 0.2694734994593304, 0.26566688058404114, 0.26181765491537584, 0.25795594009313705, 0.25411185375712725, 0.25031551354714904, 0.24659703710300498, 0.24298654206449757, 0.23951414607142943, 0.23620996676360284, 0.2331041217808207, 0.23021704671827614, 0.22753044899272623, 0.2250163539763186, 0.22264678704120094, 0.22039377355952114, 0.21822933890342697, 0.216125508445066, 0.21405430755658617, 0.2119877616101351, 0.20989789597786052, 0.20775673603191028, 0.2055363071444321, 0.20320863468757372, 0.20074574403348283, 0.19811966055430724, 0.1953099026466996, 0.1923259608053322, 0.18918481854938224, 0.1859034593980269, 0.18249886687044342, 0.1789880244858088, 0.17538791576330048, 0.17171552422209566, 0.1679878333813714, 0.164221826760305, 0.16043448787807352, 0.15664280025385427, 0.15286374740682446, 0.14911431285616122, 0.1454114801210418, 0.14177223272064332, 0.13821355417414308, 0.1347524280007182, 0.13140583771954595, 0.12819076684980343, 0.12512419891066792, 0.12222311742131657, 0.11950450590092662, 0.11698534786867526, 0.11468262684373962, 0.11261332634529697, 0.1107944298925245, 0.10924292100459933, 0.10797578320069878, 0.10700999999999998],
        [0.31358166765920326, 0.3138731644905169, 0.31415489159026494, 0.314419493726238, 0.3146596156662266, 0.314867902178021, 0.31503699802941193, 0.31515954798818985, 0.3152281968221451, 0.31523558929906853, 0.31517437018675026, 0.315037184252981, 0.31481667626555104, 0.31450549099225117, 0.31409627320087175, 0.31358166765920314, 0.31295431913503596, 0.3122068723961608, 0.31133197221036807, 0.31032226334544827, 0.30917039056919193, 0.3078689986493893, 0.30641073235383126, 0.30478823645030817, 0.3029941557066105, 0.3010211348905287, 0.29886181876985335, 0.2965088521123748, 0.2939548796858837, 0.2911925462581705, 0.2882144965970257, 0.285019668174475, 0.2816321692794846, 0.2780824009052559, 0.2744007640449902, 0.2706176596918891, 0.266763488839154, 0.26286865247998614, 0.25896355160758705, 0.255078587215158, 0.25124416029590063, 0.2474906718430161, 0.24384852284970607, 0.2403481143091717, 0.23701984721461442, 0.23389412255923575, 0.23099152656003377, 0.22829338632919358, 0.22577121420269672, 0.22339652251652492, 0.22114082360666, 0.21897562980908358, 0.21687245345977743, 0.21480280689472325, 0.21273820244990269, 0.21065015246129756, 0.20851016926488952, 0.20628976519666029, 0.2039604525925916, 0.20149374378866508, 0.19886115112086258, 0.19604180031180074, 0.1930452706306366, 0.18988875473316208, 0.18658944527516919, 0.18316453491245002, 0.17963121630079643, 0.1760066820960005, 0.17230812495385425, 0.16855273753014963, 0.16475771248067864, 0.16094024246123323, 0.1571175201276056, 0.15330673813558748, 0.14952508914097104, 0.14578976579954825, 0.14211796076711103, 0.1385268666994515, 0.13503367625236154, 0.13165558208163322, 0.12840977684305852, 0.12531345319242942, 0.12238380378553793, 0.11963802127817608, 0.11709329832613584, 0.11476682758520917, 0.11267580171118814, 0.11083741335986472, 0.10926885518703085, 0.10798731984847862, 0.10700999999999995],
        [0.3158100000000001, 0.31614776944444445, 0.3164676555555556, 0.31676265, 0.31702574444444437, 0.3172499305555555, 0.31742819999999994, 0.31755354444444434, 0.31761895555555547, 0.31761742499999984, 0.31754194444444434, 0.3173855055555555, 0.3171410999999999, 0.31680171944444446, 0.3163603555555555, 0.31581000000000004, 0.31514364444444426, 0.3143542805555555, 0.3134348999999999, 0.3123784944444443, 0.3111780555555555, 0.30982657499999994, 0.30831704444444435, 0.30664245555555547, 0.3047958, 0.3027700694444444, 0.30055825555555554, 0.29815335000000004, 0.2955483444444444, 0.29273623055555553, 0.28970999999999997, 0.28646887944444444, 0.28303703555555554, 0.27944487, 0.27572278444444437, 0.2719011805555555, 0.26801046, 0.2640810244444445, 0.26014327555555555, 0.25622761499999996, 0.2523644444444444, 0.24858416555555554, 0.24491718, 0.24139388944444448, 0.23804469555555557, 0.2349, 0.2319803444444444, 0.22926683055555555, 0.2267307, 0.22434319444444442, 0.22207555555555553, 0.21989902499999997, 0.21778484444444443, 0.21570425555555559, 0.21362850000000003, 0.21152881944444443, 0.20937645555555556, 0.20714265000000007, 0.20479864444444446, 0.20231568055555554, 0.19966500000000004, 0.19682552944444445, 0.19380693555555562, 0.19062657000000005, 0.18730178444444448, 0.1838499305555556, 0.18028835999999998, 0.1766344244444444, 0.17290547555555555, 0.169118865, 0.16529194444444448, 0.1614420655555556, 0.15758658000000003, 0.15374283944444445, 0.14992819555555556, 0.14616000000000004, 0.14245560444444447, 0.1388323605555556, 0.13530762000000002, 0.13189873444444447, 0.12862305555555556, 0.12549793499999998, 0.12254072444444443, 0.11976877555555557, 0.11719944000000002, 0.11485006944444445, 0.11273801555555556, 0.11088063000000001, 0.10929526444444443, 0.10799927055555553, 0.10700999999999998],
        [0.31815667932538527, 0.3185503983024511, 0.31891617546207385, 0.3192474791694744, 0.3195377777898738, 0.3197805396884929, 0.31996923323055276, 0.32009732678127434, 0.3201582887058786, 0.32014558736958654, 0.320052691137619, 0.31987306837519713, 0.31960018744754193, 0.31922751671987415, 0.318748524557415, 0.3181566793253851, 0.31744544938900576, 0.31660830311349786, 0.31563870886408235, 0.31453013500598004, 0.31327604990441216, 0.3118699219245996, 0.31030521943176326, 0.30857541079112416, 0.3066739643679033, 0.30459434852732153, 0.3023300316345999, 0.2998744820549594, 0.29722116815362104, 0.2943635582958056, 0.2912951208467342, 0.28801542907994937, 0.2845484759022805, 0.28092435912887814, 0.2771731765748933, 0.2733250260554767, 0.26941000538577925, 0.2654582123809516, 0.26149974485614474, 0.25756470062650944, 0.2536831775071966, 0.24988527331335683, 0.24620108586014117, 0.24266071296270042, 0.23929425243618524, 0.2361318020957466, 0.23319364910611792, 0.23046083803036355, 0.2279046027811301, 0.22549617727106464, 0.22320679541281407, 0.22100769111902518, 0.21887009830234497, 0.21676525087542017, 0.2146643827508977, 0.21253872784142447, 0.21035952005964734, 0.20809799331821321, 0.20572538152976905, 0.2032129186069615, 0.20053183846243772, 0.19766107861503848, 0.19461039100838184, 0.19139723119227947, 0.1880390547165436, 0.18455331713098616, 0.18095747398541887, 0.17726898082965395, 0.1735052932135033, 0.16968386668677876, 0.1658221567992924, 0.16193761910085627, 0.15804770914128213, 0.15416988247038202, 0.15032159463796793, 0.14652030119385182, 0.1427834576878457, 0.13912851966976136, 0.13557294268941092, 0.1321341822966063, 0.12882969404115946, 0.12567693347288234, 0.12269335614158688, 0.11989641759708515, 0.11730357338918904, 0.11493227906771045, 0.11279999018246144, 0.11092416228325393, 0.10932225091989985, 0.10801171164221118, 0.10700999999999995],
        [0.3206113657313173, 0.3210697418523196, 0.321488363716626, 0.3218612940827816, 0.3221825957093315, 0.3224463313548209, 0.32264656377779494, 0.32277735573679867, 0.3228327699903773, 0.32280686929707614, 0.3226937164154401, 0.3224873741040143, 0.32218190512134404, 0.32177137222597424, 0.3212498381764503, 0.32061136573131715, 0.3198500176491199, 0.3189598566884041, 0.3179349456077144, 0.31676934716559607, 0.31545712412059435, 0.31399233923125436, 0.3123690552561212, 0.31058133495373996, 0.30862324108265593, 0.3064888364014142, 0.30417218366855964, 0.30166734564263786, 0.2989683850821936, 0.29606936474577195, 0.29296434739191857, 0.28965330422967306, 0.28615984027005564, 0.2825134689745805, 0.27874370380476315, 0.2748800582221181, 0.2709520456881601, 0.266989179664404, 0.26302097361236454, 0.2590769409935566, 0.2551865952694951, 0.2513794499016946, 0.24768501835167006, 0.24413281408093626, 0.24075235055100797, 0.2375731412234, 0.23461502585335672, 0.2318591493710409, 0.2292769830003447, 0.2268399979651602, 0.2245196654893799, 0.222287456796896, 0.2201148431116005, 0.21797329565738588, 0.2158342856581443, 0.21366928433776797, 0.2114497629201492, 0.20914719262918016, 0.20673304468875303, 0.20417879032276018, 0.20145590075509384, 0.1985435197609257, 0.19545148132054568, 0.19219729196552346, 0.1887984582274283, 0.18527248663782978, 0.1816368837282973, 0.17790915603040044, 0.17410681007570866, 0.17024735239579145, 0.16634828952221828, 0.16242712798655856, 0.15850137432038186, 0.15458853505525763, 0.1507061167227553, 0.14687162585444444, 0.14310256898189447, 0.13941645263667493, 0.1358307833503552, 0.1323630676545049, 0.1290308120806934, 0.12585152316049017, 0.12284270742546478, 0.12002187140718669, 0.11740652163722533, 0.11501416464715021, 0.11286230696853079, 0.11096845513293661, 0.10935011567193706, 0.1080247951171017, 0.10700999999999997],
        [0.3231635516719977, 0.32369401507704365, 0.32417141255455434, 0.32459050228324576, 0.3249460424418328, 0.3252327912090309, 0.3254455067635554, 0.3255789472841216, 0.325627870949445, 0.3255870359382409, 0.32545120042922454, 0.32521512260111146, 0.3248735606326169, 0.3244212727024562, 0.3238530169893447, 0.3231635516719976, 0.3223476349291304, 0.3214000249394585, 0.3203154798816974, 0.31908875793456193, 0.3177146172767679, 0.3161878160870305, 0.3145031125440651, 0.3126552648265869, 0.3106390311133115, 0.30844916958295404, 0.30608043841423005, 0.3035275957858546, 0.3007853998765433, 0.2978486088650114, 0.29471198092997436, 0.2913759285696274, 0.2878634815600874, 0.28420332399695086, 0.2804241399758141, 0.2765546135922741, 0.2726234289419277, 0.26865927012037105, 0.2646908212232012, 0.2607467663460147, 0.256855789584408, 0.2530465750339779, 0.24934780679032126, 0.24578816894903438, 0.24239634560571408, 0.23920102085595704, 0.23622141913788608, 0.23343892625972903, 0.23082546837223986, 0.22835297162617268, 0.2259933621722815, 0.22371856616132035, 0.22150050974404334, 0.21931111907120424, 0.21712232029355744, 0.2149060395618567, 0.21263420302685615, 0.2102787368393099, 0.2078115671499718, 0.20520462010959598, 0.20242982186893657, 0.19946669566118233, 0.19632515304926204, 0.1930227026785392, 0.18957685319437723, 0.18600511324213975, 0.18232499146719036, 0.17855399651489245, 0.17470963703060965, 0.17080942165970553, 0.16687085904754353, 0.16291145783948724, 0.15894872668090015, 0.1550001742171458, 0.15108330909358778, 0.14721563995558967, 0.14341467544851483, 0.13969792421772692, 0.13608289490858938, 0.13258709616646588, 0.12922803663671992, 0.12602322496471485, 0.12299016979581448, 0.1201463797753822, 0.11750936354878153, 0.11509662976137607, 0.11292568705852929, 0.11101404408560478, 0.109379209487966, 0.10803869191097655, 0.10700999999999998],
        [0.3258027296016283, 0.32641143295961683, 0.32695251421120197, 0.3274215113141914, 0.32781396222639275, 0.32812540490561404, 0.328351377309663, 0.32848741739634735, 0.32852906312347463, 0.3284718524488532, 0.3283113233302903, 0.32804301372559386, 0.3276624615925717, 0.32716520488903156, 0.32654678157278105, 0.3258027296016283, 0.3249285869333806, 0.32391989152584616, 0.3227721813368325, 0.32148099432414745, 0.32004186844559884, 0.31845034165899433, 0.3167019519221418, 0.3147922371928489, 0.31271673542892353, 0.31047098458817335, 0.3080505226284062, 0.3054508875074299, 0.30266761718305185, 0.29969624961308033, 0.2965323227553228, 0.29317672577582493, 0.2896517526735833, 0.28598504865583235, 0.28220425892980644, 0.2783370287027399, 0.27441100318186734, 0.270453827574423, 0.26649314708764127, 0.2625566069287567, 0.25867185230500356, 0.25486652842361635, 0.2511682804918295, 0.24760475371687732, 0.24420359330599417, 0.24099244446641457, 0.23798977341143107, 0.23517733037856914, 0.2325276866114121, 0.23001341335354358, 0.22760708184854736, 0.22528126334000678, 0.22300852907150545, 0.22076145028662686, 0.2185125982289547, 0.2162345441420723, 0.21389985926956348, 0.2114811148550117, 0.2089508821420005, 0.2062817323741133, 0.20344623679493395, 0.20042444909488483, 0.19722635275174552, 0.19386941369013413, 0.1903710978346694, 0.1867488711099696, 0.18302019944065318, 0.17920254875133854, 0.17531338496664425, 0.17137017401118862, 0.16739038180959012, 0.16339147428646714, 0.1593909173664382, 0.15540617697412157, 0.1514547190341359, 0.14755400947109945, 0.14372151420963072, 0.13997469917434813, 0.13633103028987015, 0.13280797348081513, 0.12942299467180157, 0.12619355978744787, 0.12313713475237244, 0.12027118549119382, 0.11761317792853032, 0.11518057798900043, 0.11299085159722252, 0.11106146467781515, 0.10940988315539661, 0.10805357295458538, 0.10700999999999995],
        [0.32851839197441113, 0.32921021048303345, 0.3298188609219111, 0.3303407287189428, 0.33077219930202695, 0.3311096580990621, 0.33134949053794693, 0.33148808204658003, 0.3315218180528599, 0.3314470839846853, 0.3312602652699546, 0.33095774733656647, 0.33053591561241946, 0.3299911555254122, 0.32931985250344314, 0.3285183919744111, 0.32758315936621424, 0.32651054010675157, 0.32529691962392154, 0.3239386833456226, 0.3224322166997534, 0.3207739051142126, 0.31896013401689866, 0.31698728883571026, 0.3148517549985459, 0.3125499179333042, 0.3100781630678837, 0.30743287583018314, 0.3046104416481008, 0.3016072459495354, 0.2984196741623856, 0.29504911952427776, 0.2915170065117504, 0.287849767411069, 0.2840738345085002, 0.28021564009030986, 0.27630161644276435, 0.2723581958521293, 0.26841181060467134, 0.2644888929866562, 0.26061587528435026, 0.2568191897840193, 0.2531252687719298, 0.24956054453434753, 0.24615144935753877, 0.2429244155277696, 0.23989703312571714, 0.23705152340970254, 0.23436126543245775, 0.23179963824671485, 0.22934002090520617, 0.22695579246066358, 0.22462033196581932, 0.22230701847340537, 0.21998923103615395, 0.217640348706797, 0.21523375053806668, 0.21274281558269525, 0.21014092289341457, 0.20740145152295678, 0.20449778052405415, 0.20141062284110964, 0.19815002698521084, 0.19473337535911606, 0.19117805036558386, 0.1875014344073727, 0.18372090988724116, 0.17985385920794755, 0.1759176647722505, 0.17192970898290844, 0.1679073742426799, 0.16386804295432325, 0.1598290975205971, 0.1558079203442598, 0.15182189382806993, 0.14788840037478596, 0.14402482238716635, 0.14024854226796957, 0.1365769424199541, 0.13302740524587847, 0.12961731314850114, 0.12636404853058056, 0.12328499379487524, 0.12039753134414372, 0.11771904358114438, 0.11526691290863572, 0.11305852172937629, 0.1111112524461245, 0.10944248746163886, 0.10806960917867782, 0.10700999999999995],
        [0.3313000312445479, 0.3320785626302872, 0.33275764492202475, 0.3333345620408247, 0.3338065979077504, 0.3341710364438663, 0.3344251615702362, 0.3345662572079241, 0.3345916072779938, 0.3344984957015096, 0.334284206399535, 0.3339460232931344, 0.33348123030337123, 0.3328871113513099, 0.332160950358014, 0.33130003124454777, 0.330301637931975, 0.3291630543413596, 0.32788156439376576, 0.32645445201025713, 0.3248790011118979, 0.3231524956197517, 0.32127221945488277, 0.31923545653835506, 0.31703949079123245, 0.31468160613457874, 0.31215908648945806, 0.30946921577693437, 0.3066092779180715, 0.30357655683393336, 0.3003683364455841, 0.29698653349099846, 0.29345159597579545, 0.2897886047225045, 0.28602264055365595, 0.28217878429177906, 0.27828211675940395, 0.2743577187790603, 0.2704306711732779, 0.2665260547645866, 0.2626689503755161, 0.25888443882859624, 0.2551976009463568, 0.25163351755132773, 0.24821726946603848, 0.24497393751301913, 0.24192014273246956, 0.2390386670352706, 0.2363038325499731, 0.23368996140512804, 0.2311713757292864, 0.22872239765099914, 0.22631734929881714, 0.22393055280129134, 0.22153633028697284, 0.21910900388441232, 0.216622895722161, 0.2140523279287697, 0.21137162263278933, 0.20855510196277086, 0.2055770880472654, 0.20241905967893323, 0.19909112230687284, 0.19561053804429224, 0.19199456900439946, 0.18826047730040252, 0.18442552504550938, 0.18050697435292795, 0.1765220873358664, 0.17248812610753267, 0.16842235278113465, 0.16434202946988036, 0.1602644182869779, 0.1562067813456352, 0.15218638075906024, 0.1482204786404611, 0.1443263371030456, 0.1405212182600219, 0.13682238422459794, 0.1332470971099817, 0.12981261902938115, 0.12653621209600438, 0.12343513842305931, 0.12052666012375399, 0.11782803931129635, 0.11535653809889439, 0.11312941859975614, 0.11116394292708959, 0.10947737319410268, 0.10808697151400351, 0.10700999999999997],
        [0.33413713986624016, 0.3350047043843717, 0.33575605844688533, 0.3363894188231608, 0.3369030022825783, 0.3372950255945179, 0.3375637055283597, 0.33770725885348357, 0.33772390233926963, 0.33761185275509814, 0.3373693268703489, 0.33699454145440216, 0.3364857132766378, 0.335841059106436, 0.3350587957131767, 0.3341371398662401, 0.333074308335006, 0.3318685178888548, 0.33051798529716625, 0.3290209273293206, 0.3273755607546977, 0.32558010234267787, 0.3236327688626409, 0.3215317770839671, 0.3192753437760362, 0.3168616857082287, 0.3142890196499241, 0.31155556237050297, 0.3086595306393451, 0.30559914122583054, 0.3023726108993394, 0.29898239135199883, 0.2954478739669255, 0.2917926850499824, 0.2880404509070334, 0.28421479784394177, 0.2803393521665713, 0.27643774018078526, 0.2725335881924471, 0.2686505225074207, 0.2648121694315691, 0.2610421552707561, 0.2573641063308453, 0.2538016489176999, 0.25037840933718347, 0.24711801389515975, 0.24403604668341333, 0.2411159229374145, 0.23833301567855442, 0.23566269792822464, 0.2330803427078165, 0.23056132303872148, 0.22808101194233094, 0.22561478244003624, 0.22313800755322885, 0.2206260603033001, 0.21805431371164144, 0.21539814079964426, 0.21263291458869998, 0.20973400810019993, 0.20667679435553563, 0.2034436023874317, 0.20004458527394609, 0.1964968521044702, 0.1928175119683951, 0.18902367395511233, 0.185132447154013, 0.18116094065448834, 0.1771262635459298, 0.17304552491772862, 0.168935833859276, 0.1648142994599633, 0.16069803080918174, 0.1566041369963226, 0.1525497271107771, 0.1485519102419367, 0.14462779547919252, 0.1407944919119359, 0.13706910862955818, 0.13346875472145048, 0.1300105392770043, 0.12671157138561065, 0.12358896013666104, 0.12065981461954668, 0.1179412439236588, 0.11545035713838869, 0.1132042633531277, 0.11122007165726706, 0.109514891140198, 0.1081058308913119, 0.10700999999999997],
        [0.33701921029369003, 0.3379768507282811, 0.3388012937318355, 0.3394917066092762, 0.3400472566655261, 0.34046711120550843, 0.3407504375341463, 0.3408964029563627, 0.3409041747770807, 0.34077292030122336, 0.34050180683371384, 0.3400900016794753, 0.3395366721434304, 0.33884098553050257, 0.33800210914561474, 0.3370192102936899, 0.33589145627965117, 0.3346180144084218, 0.33319805198492464, 0.33163073631408285, 0.32991523470081957, 0.3280507144500577, 0.3260363428667203, 0.3238712872557305, 0.32155471492201154, 0.31908579317048624, 0.31646368930607766, 0.31368757063370906, 0.31075660445830344, 0.30766995808478365, 0.30442679881807305, 0.30103011678329156, 0.2974981933863477, 0.29385313285334635, 0.2901170394103931, 0.2863120172835932, 0.2824601706990517, 0.2785836038828742, 0.2747044210611659, 0.270844726460032, 0.26702662430557783, 0.26327221882390883, 0.2596036142411301, 0.2560429147833469, 0.25261222467666467, 0.24933364814718864, 0.246221689430274, 0.24326045279827563, 0.24042644253279813, 0.2376961629154464, 0.23504611822782515, 0.23245281275153917, 0.22989275076819313, 0.22734243655939182, 0.22477837440673992, 0.22217706859184225, 0.21951502339630352, 0.2167687431017285, 0.21391473198972197, 0.2109294943418885, 0.20778953443983308, 0.20447809374568168, 0.20100536244364556, 0.1973882678984574, 0.19364373747484986, 0.18978869853755562, 0.1858400784513073, 0.18181480458083749, 0.17772980429087892, 0.17360200494616418, 0.16944833391142602, 0.1652857185513969, 0.16113108623080963, 0.1570013643143967, 0.1529134801668909, 0.1488843611530249, 0.14493093463753118, 0.14107012798514254, 0.1373188685605915, 0.1336940837286108, 0.13021270085393305, 0.12689164730129088, 0.12374785043541697, 0.12079823762104396, 0.1180597362229045, 0.1155492736057312, 0.11328377713425669, 0.11128017417321372, 0.1095553920873348, 0.10812635824135265, 0.10700999999999997],
        [0.33993573498109925, 0.34098321664500914, 0.34188054301221804, 0.34262783294249494, 0.34322520529560885, 0.34367277893132925, 0.3439706727094253, 0.34411900548966584, 0.3441178961318202, 0.3439674634956577, 0.34366782644094745, 0.34321910382745846, 0.34262141451496003, 0.34187487736322114, 0.34097961123201115, 0.33993573498109914, 0.3387433674702542, 0.3374026275592456, 0.3359136341078426, 0.33427650597581393, 0.3324913620229292, 0.33055832110895755, 0.328477502093668, 0.32624902383682963, 0.32387300519821177, 0.32134956503758344, 0.31867882221471394, 0.31586089558937225, 0.3128959040213277, 0.3097839663703495, 0.3065252014962066, 0.30312313346088887, 0.29959490713526904, 0.29596107259244014, 0.2922421799054953, 0.28845877914752766, 0.2846314203916306, 0.28078065371089705, 0.27692702917842055, 0.27309109686729394, 0.26929340685061054, 0.26555450920146345, 0.26189495399294604, 0.25833529129815125, 0.2548960711901724, 0.25159784374210264, 0.2484540154247766, 0.24544941829999525, 0.24256174082730064, 0.2397686714662351, 0.23704789867634102, 0.23437711091716046, 0.23173399664823596, 0.22909624432910955, 0.22644154241932377, 0.22374757937842055, 0.22099204366594244, 0.21815262374143174, 0.21520700806443052, 0.2121328850944811, 0.20890794329112594, 0.20551637653275953, 0.2019684003731858, 0.19828073578506145, 0.19447010374104262, 0.19055322521378582, 0.18654682117594748, 0.1824676126001839, 0.1783323204591516, 0.17415766572550692, 0.1699603693719063, 0.16575715237100608, 0.16156473569546267, 0.15739984031793258, 0.1532791872110721, 0.14921949734753767, 0.14523749169998562, 0.1413498912410725, 0.13757341694345462, 0.13392478977978836, 0.13042073072273014, 0.12707796074493644, 0.12391320081906355, 0.12094317191776796, 0.11818459501370605, 0.11565419107953417, 0.11336868108790879, 0.11134478601148629, 0.10959922682292302, 0.10814872449487543, 0.10700999999999998],
        [0.3428762063826693, 0.34401201711754936, 0.3449809985233751, 0.34578420536614113, 0.3464226924118417, 0.34689751442647154, 0.34720972617602514, 0.34736038242649686, 0.34735053794388127, 0.34718124749417306, 0.34685356584336674, 0.3463685477574566, 0.3457272480024373, 0.34493072134430325, 0.3439800225490491, 0.34287620638266925, 0.34162032761115807, 0.3402134410005106, 0.33865660131672076, 0.3369508633257834, 0.3350972817936929, 0.33309691148644394, 0.33095080717003084, 0.32866002361044816, 0.3262256155736905, 0.3236486378257523, 0.320930145132628, 0.3180711922603123, 0.31507283397479946, 0.31193612504208434, 0.30866212022816114, 0.3052548650608029, 0.3017303681148965, 0.2981076287271071, 0.2944056462340999, 0.29064341997254006, 0.2868399492790929, 0.2830142334904236, 0.27918527194319737, 0.27537206397407954, 0.2715936089197351, 0.2678689061168294, 0.2642169549020278, 0.2606567546119952, 0.257207304583397, 0.25388760415289846, 0.2507099691186465, 0.2476599811247146, 0.24471653827665804, 0.2418585386800321, 0.23906488044039226, 0.23631446166329356, 0.23358618045429144, 0.23085893491894102, 0.22811162316279776, 0.22532314329141678, 0.2224723934103534, 0.21953827162516307, 0.21649967604140088, 0.21333550476462204, 0.21002465590038216, 0.20655229352774146, 0.20292864561978166, 0.19917020612308964, 0.19529346898425223, 0.19131492814985623, 0.18725107756648868, 0.18311841118073624, 0.17893342293918585, 0.17471260678842435, 0.1704724566750387, 0.16622946654561563, 0.16200013034674204, 0.1578009420250048, 0.15364839552699083, 0.14955898479928686, 0.1455492037884798, 0.1416355464411566, 0.137834506703904, 0.13416257852330887, 0.13063625584595814, 0.12727203261843864, 0.12408640278733722, 0.12109586029924074, 0.11831689910073609, 0.11576601313841006, 0.11345969635884955, 0.11141444270864147, 0.10964674613437256, 0.10817310058262979, 0.10700999999999997],
        [0.34583011695260246, 0.347051467128896, 0.34808985250065005, 0.3489472314235398, 0.34962556225324015, 0.3501268033454269, 0.3504529130557753, 0.35060584973996034, 0.3505875717536575, 0.35040003745254217, 0.3500452051922896, 0.349525033328575, 0.3488414802170736, 0.3479965042134609, 0.346992063673412, 0.34583011695260235, 0.34451262240670705, 0.3430415383914016, 0.3414188232623612, 0.3396464353752611, 0.3377263330857768, 0.3356604747495833, 0.3334508187223561, 0.3310993233597704, 0.3286079470175016, 0.3259786480512249, 0.3232133848166155, 0.3203141156693489, 0.31728279896510025, 0.3141213930595449, 0.31083185630835825, 0.30741873525904606, 0.3038969292264373, 0.3002839257171912, 0.2965972122379673, 0.2928542762954251, 0.2890726053962242, 0.28526968704702366, 0.28146300875448316, 0.2776700580252621, 0.27390832236602003, 0.27019528928341613, 0.26654844628411023, 0.2629852808747615, 0.25952328056202933, 0.2561799328525734, 0.2529664949636089, 0.24986930295457513, 0.2468684625954669, 0.2439440796562794, 0.2410762599070078, 0.23824510911764696, 0.23543073305819193, 0.232613237498638, 0.22977272820897995, 0.2268893109592128, 0.22394309151933192, 0.22091417565933213, 0.21778266914920855, 0.21452867775895615, 0.21113230725857007, 0.20757968750970415, 0.20388104474064794, 0.2000526292713497, 0.19611069142175774, 0.19207148151182046, 0.18795124986148615, 0.18376624679070308, 0.17953272261941974, 0.17526692766758425, 0.17098511225514507, 0.16670352670205046, 0.1624384213282488, 0.15820604645368835, 0.1540226523983175, 0.1499044894820846, 0.14586780802493787, 0.1419288583468257, 0.13810389076769639, 0.1344091556074983, 0.13086090318617974, 0.127475383823689, 0.12426884783997448, 0.1212575455549845, 0.11845772728866734, 0.11588564336097132, 0.11355754409184475, 0.11148967980123603, 0.1096983008090934, 0.10819965743536529, 0.10700999999999994],
        [0.34878695914510033, 0.3500897816620429, 0.35119429717938516, 0.35210331865801475, 0.3528196590588194, 0.35334613134268683, 0.3536855484705046, 0.3538407234031604, 0.3538144691015421, 0.3536095985265372, 0.35322892463903344, 0.3526752603999185, 0.35195141877008, 0.3510602127104057, 0.35000445518178325, 0.3487869591451003, 0.3474105375612444, 0.34587800339110353, 0.34419216959556515, 0.342355849135517, 0.34037185497184685, 0.3382430000654423, 0.3359720973771909, 0.33356195986798054, 0.3310154004986987, 0.3283352322302334, 0.3255242680234719, 0.32258532083930214, 0.31952120363861164, 0.3163347293822881, 0.3130287110312194, 0.30960816773163063, 0.3060869433710984, 0.30248108802253615, 0.298806651758858, 0.2950796846529779, 0.2913162367778096, 0.28753235820626705, 0.2837440990112644, 0.2799675092657152, 0.27621863904253346, 0.27251353841463316, 0.26886825745492826, 0.26529884623633254, 0.2618213548317597, 0.25845183331412414, 0.25520053741138915, 0.252054545471718, 0.24899514149832355, 0.24600360949441855, 0.24306123346321606, 0.24014929740792887, 0.2372490853317699, 0.23434188123795188, 0.2314089691296879, 0.22843163301019065, 0.2253911568826731, 0.22226882475034823, 0.21904592061642875, 0.21570372848412753, 0.2122235323566577, 0.20859240125772388, 0.20482054429299928, 0.20092395558864903, 0.19691862927083814, 0.19282055946573184, 0.18864574029949518, 0.1844101658982933, 0.1801298303882912, 0.17582072789565417, 0.17149885254654723, 0.1671801984671355, 0.16288075978358407, 0.15861653062205805, 0.1544035051087226, 0.15025767736974283, 0.1461950415312838, 0.14223159171951064, 0.13838332206058845, 0.1346662266806824, 0.13109629970595751, 0.12768953526257898, 0.12446192747671186, 0.12142947047452131, 0.11860815838217242, 0.11601398532583028, 0.11366294543166001, 0.11157103282582674, 0.10975424163449557, 0.1082285659838316, 0.10700999999999998],
        [0.3517362254143647, 0.3531151756999836, 0.354281524794923, 0.3552388746128908, 0.3559908270675946, 0.3565409840727423, 0.3568929475420421, 0.35705031938920134, 0.357016701527928, 0.3567956958719302, 0.3563909043349156, 0.3558059288305921, 0.35504437127266725, 0.35410983357484915, 0.35300591765084566, 0.35173622541436456, 0.35030435877911353, 0.3487139196588008, 0.3469685099671339, 0.34507173161782073, 0.34302718652456915, 0.340838476601087, 0.3385092037610822, 0.3360429699182624, 0.3334433769863356, 0.3307140268790096, 0.3278585215099922, 0.32488046279299126, 0.3217834526417147, 0.31857109296987013, 0.3152469856911658, 0.31181658615456886, 0.30829276345008666, 0.3046902401029853, 0.30102373863853177, 0.2973079815819925, 0.29355769145863436, 0.2897875907937237, 0.2860124021125273, 0.28224684794031174, 0.27850565080234363, 0.2748035332238896, 0.27115521773021645, 0.26757542684659064, 0.2640788830982787, 0.2606803090105475, 0.2573890409137124, 0.25419287035828464, 0.2510742026998242, 0.2480154432938911, 0.2449989974960456, 0.24200727066184757, 0.23902266814685713, 0.2360275953066343, 0.23300445749673923, 0.22993566007273183, 0.2268036083901723, 0.22359070780462054, 0.22027936367163675, 0.2168519813467809, 0.2132909661856131, 0.209584277550877, 0.20574209083405046, 0.201780135433795, 0.1977141407487723, 0.1935598361776437, 0.18933295111907084, 0.18504921497171517, 0.18072435713423826, 0.17637410700530165, 0.1720141939835669, 0.16766034746769543, 0.16332829685634886, 0.15903377154818862, 0.15479250094187633, 0.1506202144360735, 0.14653264142944156, 0.14254551132064214, 0.13867455350833674, 0.13493549739118688, 0.13134407236785406, 0.12791600783699983, 0.12466703319728571, 0.12161287784737328, 0.11876927118592398, 0.11615194261159935, 0.11377662152306094, 0.11165903731897031, 0.10981491939798889, 0.10825999715877829, 0.10701],
        [0.35466740821459725, 0.3561158642257121, 0.3573387275826062, 0.35834030683149193, 0.3591249105185808, 0.35969684719008505, 0.36006042539221644, 0.3602199536711871, 0.3601797405732088, 0.35994409464449373, 0.35951732443125356, 0.3589037384797005, 0.3581076453360464, 0.3571333535465031, 0.3559851716572827, 0.35466740821459714, 0.3531843717646583, 0.3515403708536782, 0.3497397140278688, 0.3477867098334419, 0.34568566681660967, 0.3434408935235839, 0.3410566985005768, 0.3385373902937999, 0.3358872774494656, 0.33311066851378557, 0.33021187203297175, 0.3271951965532363, 0.324064950620791, 0.32082544278184777, 0.3174809815826187, 0.31403741420387304, 0.31050674236460907, 0.3069025064183824, 0.3032382467187488, 0.299527503619264, 0.29578381747348365, 0.29202072863496314, 0.2882517774572584, 0.28449050429392503, 0.2807504494985187, 0.27704515342459496, 0.27338815642570974, 0.2697929988554184, 0.26627322106727674, 0.26284236341484046, 0.2595089499223038, 0.25626143929641615, 0.25308327391456514, 0.24995789615413874, 0.24686874839252482, 0.24379927300711135, 0.24073291237528605, 0.23765310887443683, 0.23454330488195163, 0.2313869427752182, 0.2281674649316246, 0.22486831372855853, 0.2214729315434079, 0.21796476075356058, 0.2143272437364045, 0.21054915916823982, 0.20664063092101614, 0.20261711916559527, 0.19849408407283908, 0.19428698581360948, 0.1900112845587683, 0.18568244047917748, 0.18131591374569891, 0.1769271645291944, 0.1725316530005259, 0.1681448393305552, 0.16378218369014425, 0.15945914625015487, 0.15519118718144903, 0.15099376665488853, 0.14688234484133525, 0.14287238191165108, 0.13897933803669787, 0.13521867338733756, 0.13160584813443196, 0.128156322448843, 0.12488555650143252, 0.12180901046306249, 0.11894214450459462, 0.11630041879689093, 0.11389929351081322, 0.11175422881722341, 0.10988068488698333, 0.1082941218909549, 0.10700999999999997],
        [0.35757000000000005, 0.3590800622222222, 0.3603530977777779, 0.361394022857143, 0.3622077536507937, 0.3627992063492063, 0.3631732971428572, 0.3633349422222222, 0.3632890577777777, 0.3630405599999999, 0.36259436507936504, 0.3619553892063492, 0.36112854857142856, 0.36011875936507926, 0.3589309377777778, 0.35757, 0.35604086222222214, 0.3543484406349206, 0.3524976514285713, 0.35049341079365076, 0.34834063492063494, 0.3460442399999999, 0.34360914222222216, 0.3410402577777777, 0.33834250285714285, 0.3355207936507937, 0.33258004634920635, 0.3295251771428571, 0.32636110222222225, 0.3230927377777778, 0.319725, 0.3162640755555555, 0.3127212330158731, 0.3091090114285715, 0.3054399498412698, 0.3017265873015873, 0.29798146285714283, 0.2942171155555556, 0.29044608444444453, 0.2866809085714286, 0.28293412698412695, 0.2792182787301587, 0.2755459028571429, 0.2719295384126985, 0.26838172444444447, 0.26491500000000007, 0.261537208888889, 0.25823741396825406, 0.254999982857143, 0.25180928317460327, 0.24864968253968261, 0.24550554857142867, 0.24236124888888896, 0.23920115111111118, 0.236009622857143, 0.23277103174603184, 0.2294697453968255, 0.22609013142857157, 0.22261655746031758, 0.21903339111111117, 0.2153250000000001, 0.21148088888888897, 0.20751111111111123, 0.20343085714285725, 0.19925531746031758, 0.19499968253968267, 0.19067914285714296, 0.18630888888888894, 0.18190411111111116, 0.17748000000000008, 0.1730517460317461, 0.16863453968253975, 0.16424357142857152, 0.15989403174603178, 0.1556011111111111, 0.15138000000000004, 0.14724588888888893, 0.14321396825396832, 0.1392994285714286, 0.13551746031746034, 0.131883253968254, 0.128412, 0.12511888888888886, 0.12201911111111113, 0.11912785714285715, 0.11646031746031747, 0.11403168253968254, 0.11185714285714289, 0.1099518888888889, 0.1083311111111111, 0.10701],
        [0.3604353264621498, 0.3619981577390462, 0.3633142728879864, 0.3643890844898096, 0.3652280051253553, 0.36583644737546345, 0.366219823820973, 0.36638354704272375, 0.3663330296215552, 0.3660736841383068, 0.36561092317381794, 0.36495015930892805, 0.36409680512447684, 0.3630562732013037, 0.36183397612024826, 0.3604353264621498, 0.35886573680784767, 0.35713061973818183, 0.35523538783399156, 0.3531854536761161, 0.3509862298453953, 0.3486431289226685, 0.3461615634887752, 0.34354694612455483, 0.34080468941084713, 0.33794020592849133, 0.33495890825832686, 0.3318662089811935, 0.3286675206779305, 0.3253682559293774, 0.32197382731637386, 0.3184907028589208, 0.31492957233366636, 0.31130218095641987, 0.307620273942991, 0.3038955965091891, 0.30013989387082424, 0.29636491124370523, 0.29258239384364226, 0.28880408688644454, 0.2850417355879216, 0.28130708516388325, 0.27761188083013894, 0.2739678678024982, 0.27038679129677046, 0.2668803965287654, 0.26345599782207557, 0.2601031859314261, 0.2568071207193248, 0.2535529620482796, 0.2503258697807987, 0.24711100377939013, 0.24389352390656174, 0.24065859002482154, 0.2373913619966776, 0.23407699968463785, 0.23070066295121036, 0.22724751165890317, 0.22370270567022418, 0.22005140484768143, 0.21627876905378302, 0.21237491882319987, 0.20834981737925576, 0.2042183886174371, 0.1999955564332307, 0.19569624472212305, 0.19133537737960085, 0.18692787830115096, 0.18248867138225983, 0.17803268051841406, 0.17357482960510037, 0.16913004253780548, 0.16471324321201591, 0.1603393555232184, 0.15602330336689954, 0.151780010638546, 0.1476244012336444, 0.1435713990476814, 0.13963592797614366, 0.13583291191451782, 0.1321772747582905, 0.12868394040294845, 0.12536783274397814, 0.1222438756768664, 0.11932699309709978, 0.11663210890016493, 0.11417414698154849, 0.11196803123673714, 0.11002868556121749, 0.10837103385047622, 0.10700999999999997],
        [0.36326204624212477, 0.3648692310918702, 0.36622167150960633, 0.36732517055602504, 0.3681855312918182, 0.3688085567776777, 0.36920005007429524, 0.36936581424236253, 0.36931165234257185, 0.36904336743561494, 0.36856676258218357, 0.36788764084296954, 0.3670118052786647, 0.36594505894996104, 0.3646932049175505, 0.36326204624212455, 0.36165738598437536, 0.3598850272049948, 0.35795077296467465, 0.35586042632410664, 0.35361979034398283, 0.3512346680849949, 0.3487108626078349, 0.34605417697319457, 0.3432704142417657, 0.3403653774742403, 0.3373448697313101, 0.33421469407366705, 0.3309806535620029, 0.3276485512570097, 0.324224190219379, 0.3207142646564441, 0.3171290333621026, 0.31347964627689334, 0.3097772533413551, 0.3060330044960271, 0.3022580496814478, 0.2984635388381564, 0.2946606219066914, 0.29086044882759177, 0.28707416954139664, 0.28331293398864466, 0.2795878921098748, 0.2759101938456257, 0.2722909891364364, 0.2687414279228459, 0.2652684389580042, 0.2618620662455074, 0.2585081326015629, 0.2551924608423781, 0.25190087378416043, 0.24861919424311713, 0.24533324503545567, 0.24202884897738347, 0.23869182888510795, 0.23530800757483628, 0.23186320786277612, 0.22834325256513485, 0.22473396449811972, 0.22102116647793807, 0.21719068132079747, 0.21323313840674557, 0.2091583933711919, 0.204981108413386, 0.20071594573257792, 0.1963775675280171, 0.19198063599895368, 0.1875398133446371, 0.18306976176431736, 0.17858514345724405, 0.17410062062266718, 0.1696308554598363, 0.16519051016800124, 0.16079424694641187, 0.1564567279943178, 0.152192615510969, 0.14801657169561505, 0.14394325874750585, 0.1399873388658911, 0.13616347425002057, 0.1324863270991441, 0.12897055961251136, 0.12563083398937228, 0.12248181242897647, 0.11953815713057378, 0.11681453029341396, 0.11432559411674682, 0.11208601079982206, 0.11011044254188945, 0.10841355154219885, 0.10701000000000001],
        [0.36605065121837754, 0.36769453566291826, 0.3690771575112185, 0.3702046141389642, 0.3710830029218413, 0.3717184212355359, 0.3721169664557343, 0.3722847359581219, 0.37222782711838537, 0.37195233731221067, 0.3714643639152838, 0.37077000430329055, 0.36987535585191744, 0.36878651593685, 0.3675095819337747, 0.36605065121837743, 0.3644158211663442, 0.36261118915336105, 0.3606428525551142, 0.3585169087472896, 0.3562394551055732, 0.35381658900565116, 0.35125440782320955, 0.3485590089339343, 0.3457364897135116, 0.34279294753762757, 0.339734479781968, 0.3365671838222192, 0.3332971570340669, 0.3299304967931974, 0.3264733004752967, 0.3229324384638921, 0.31931787317387583, 0.3156403400279812, 0.3119105744489415, 0.3081393118594903, 0.30433728768236096, 0.300515237340287, 0.2966838962560016, 0.2928539998522383, 0.2890362835517305, 0.2852414827772116, 0.281480332951415, 0.277763569497074, 0.27410192783692205, 0.2705061433936928, 0.2669828900896973, 0.2635225958455592, 0.26011162708148033, 0.25673635021766184, 0.2533831316743056, 0.250038337871613, 0.2466883352297856, 0.24331949016902502, 0.2399181691095329, 0.2364707384715106, 0.23296356467515972, 0.22938301414068205, 0.22571545328827888, 0.22194724853815187, 0.21806476631050262, 0.21405904640639803, 0.20993982215036702, 0.20572150024780378, 0.20141848740410256, 0.1970451903246576, 0.1926160157148631, 0.1881453702801134, 0.18364766072580282, 0.17913729375732537, 0.17462867608007546, 0.1701362143994474, 0.1656743154208353, 0.1612573858496335, 0.15689983239123617, 0.1526160617510376, 0.14842048063443206, 0.14432749574681378, 0.14035151379357697, 0.136506941480116, 0.13280818551182497, 0.1292696525940982, 0.12590574943232993, 0.12273088273191443, 0.11975945919824595, 0.1170058855367187, 0.11448456845272699, 0.112209914651665, 0.11019633083892696, 0.10845822371990725, 0.10701000000000001],
        [0.3688016332693613, 0.37047532483441503, 0.3718825947614036, 0.37302974832180164, 0.37392309078708386, 0.3745689274287254, 0.37497356351820094, 0.3751433043269854, 0.37508445512655353, 0.37480332118838017, 0.37430620778394025, 0.3735994201847088, 0.37268926366216015, 0.37158204348776946, 0.3702840649330116, 0.3688016332693612, 0.36714105376829326, 0.3653086317012826, 0.36331067233980413, 0.3611534809553325, 0.3588433628193428, 0.3563866232033097, 0.353789567378708, 0.3510585006170126, 0.34819972818969847, 0.3452195553682403, 0.34212428742411294, 0.3389202296287913, 0.33561368725375007, 0.3322109655704642, 0.3287183698504087, 0.32514290179703215, 0.3214943488416804, 0.3177831948476727, 0.31401992367832887, 0.31021501919696837, 0.30637896526691094, 0.30252224575147585, 0.29865534451398307, 0.29478874541775196, 0.2909329323261021, 0.287098389102353, 0.2832955996098246, 0.2795350477118361, 0.27582721727170717, 0.27218259215275764, 0.26860770901017783, 0.26509331566664324, 0.2616262127367, 0.2581932008348944, 0.2547810805757727, 0.25137665257388137, 0.24796671744376644, 0.24453807579997444, 0.24107752825705153, 0.23757187542954397, 0.23400791793199818, 0.23037245637896034, 0.2266522913849768, 0.2228342235645938, 0.21890505353235762, 0.21485614158902935, 0.21069708678022872, 0.20644204783779016, 0.20210518349354806, 0.1977006524793371, 0.19324261352699174, 0.1887452253683463, 0.18422264673523533, 0.17968903635949338, 0.1751585529729549, 0.17064535530745426, 0.166163602094826, 0.16172745206690467, 0.15735106395552462, 0.15304859649252045, 0.14883420840972653, 0.14472205843897742, 0.14072630531210753, 0.13686110776095134, 0.1331406245173434, 0.12957901431311813, 0.12619043588011, 0.12298904795015354, 0.11998900925508318, 0.11720447852673344, 0.1146496144969387, 0.11233857589753353, 0.11028552146035235, 0.10850460991722967, 0.10700999999999998],
        [0.37151548427352915, 0.37321285198858495, 0.37463984712874226, 0.37580290618771217, 0.3767084656592054, 0.37736296203693337, 0.37777283181460686, 0.3779445114859367, 0.37788443754463413, 0.37759904648440995, 0.3770947747989753, 0.37637805898204135, 0.3754553355273185, 0.3743330409285183, 0.37301761167935155, 0.37151548427352904, 0.36983309520476204, 0.3679768809667614, 0.3659532780532383, 0.3637687229579033, 0.361429652174468, 0.3589425021966428, 0.3563137095181391, 0.35354971063266766, 0.35065694203393954, 0.34764184021566585, 0.34451084167155743, 0.34127038289532535, 0.3379269003806804, 0.33448683062133383, 0.3309566101109966, 0.32734333217163153, 0.3236567174382108, 0.3199071433739579, 0.31610498744209664, 0.312260627105851, 0.3083844398284448, 0.30448680307310166, 0.3005780943030458, 0.2966686909815006, 0.2927689705716901, 0.28888931053683825, 0.2850400883401687, 0.2812316814449052, 0.2774744673142716, 0.2737788234114921, 0.27015125351246905, 0.26658276664382097, 0.2630604981448453, 0.2595715833548392, 0.2561031576131004, 0.25264235625892595, 0.2491763146316134, 0.24569216807045996, 0.24217705191476313, 0.23861810150382018, 0.23500245217692842, 0.2313172392733854, 0.22754959813248846, 0.22368666409353477, 0.21971557249582188, 0.21562792272151166, 0.2114331703242244, 0.20714523490044487, 0.2027780360466581, 0.1983454933593488, 0.19386152643500185, 0.18934005487010205, 0.18479499826113435, 0.18024027620458363, 0.17568980829693465, 0.17115751413467234, 0.16665731331428144, 0.16220312543224685, 0.15780887008505354, 0.1534884668691862, 0.14925583538112977, 0.14512489521736907, 0.14110956597438892, 0.13722376724867424, 0.13348141863670987, 0.12989643973498066, 0.1264827501399714, 0.12325426944816709, 0.12022491725605243, 0.11740861316011232, 0.11481927675683161, 0.1124708276426952, 0.11037718541418787, 0.10855226966779452, 0.10701],
        [0.3741926961093342, 0.3759083705076523, 0.37735077848181536, 0.3785264208198707, 0.37944179830986535, 0.380103411739847, 0.3805177618978626, 0.3806913495719595, 0.3806306755501849, 0.3803422406205863, 0.3798325455712109, 0.37910809119010574, 0.3781753782653182, 0.3770409075848956, 0.3757111799368852, 0.3741926961093342, 0.37249195689028985, 0.3706154630677995, 0.36856971542991046, 0.3663612147646699, 0.363996461860125, 0.3614819575043231, 0.3588242024853116, 0.3560296975911376, 0.3531049436098487, 0.35005644132949154, 0.3468906915381139, 0.3436141950237627, 0.34023345257448573, 0.3367549649783296, 0.333185233023342, 0.3295314071034575, 0.32580323603616146, 0.322011118244826, 0.31816545215282394, 0.3142766361835277, 0.31035506876030994, 0.30641114830654304, 0.30245527324559973, 0.29849784200085233, 0.29454925299567364, 0.290619904653436, 0.2867201953975121, 0.28286052365127434, 0.27905128783809535, 0.27530288638134776, 0.27162188138959364, 0.2679994897121539, 0.2644230918835392, 0.26088006843825995, 0.2573577999108269, 0.2538436668357505, 0.2503250497475413, 0.2467893291807098, 0.24322388566976674, 0.2396160997492225, 0.23595335195358774, 0.232223022817373, 0.2284124928750889, 0.22450914266124586, 0.2205003527103546, 0.21637788857071705, 0.21215105584580163, 0.207833545152868, 0.20343904710917596, 0.19898125233198527, 0.19447385143855567, 0.18993053504614701, 0.185364993772019, 0.18079091823343155, 0.17622199904764427, 0.171671926831917, 0.16715439220350958, 0.16268308577968157, 0.158271698177693, 0.15393392001480352, 0.1496834419082729, 0.14553395447536094, 0.14149914833332738, 0.13759271409943202, 0.13382834239093466, 0.13021972382509503, 0.12678054901917293, 0.12352450859042818, 0.12046529315612049, 0.11761659333350959, 0.11499209973985534, 0.11260550299241749, 0.11047049370845581, 0.10860076250523004, 0.10701000000000001],
        [0.37683376065522933, 0.3785631337738413, 0.3800172526892032, 0.3812026253014516, 0.38212575951072275, 0.382793163217153, 0.383211344320879, 0.383386810722037, 0.3833260703207636, 0.3830356310171952, 0.38252200071146825, 0.3817916873037191, 0.3808511986940842, 0.37970704278269996, 0.37836572746970276, 0.3768337606552292, 0.3751176502394156, 0.3732239041223985, 0.37115903020431423, 0.36892953638529924, 0.3665419305654899, 0.3640027206450227, 0.3613184145240341, 0.35849552010266056, 0.3555405452810385, 0.35245999795930427, 0.34926038603759435, 0.3459482174160451, 0.3425299999947931, 0.33901224167397465, 0.33540145035372637, 0.331704804108277, 0.32793216170822653, 0.3240940520982665, 0.3202010042230896, 0.3162635470273878, 0.31229220945585334, 0.30829752045317815, 0.30429000896405456, 0.30028020393317495, 0.296278634305231, 0.2922958290249152, 0.2883423170369197, 0.28442862728593654, 0.2805652887166578, 0.27676283027377596, 0.27302795043457445, 0.2693520258067036, 0.2657226025304048, 0.2621272267459199, 0.2585534445934905, 0.2549888022133583, 0.2514208457457649, 0.247837121330952, 0.24422517510916122, 0.24057255322063426, 0.23686680180561281, 0.2330954670043385, 0.22924609495705295, 0.22530623180399778, 0.22126342368541482, 0.2171095379035176, 0.21285372640840783, 0.20850946231215906, 0.20409021872684496, 0.19960946876453925, 0.19508068553731547, 0.1905173421572473, 0.18593291173640844, 0.18134086738687236, 0.17675468222071292, 0.1721878293500036, 0.16765378188681815, 0.16316601294323008, 0.15873799563131305, 0.15438320306314088, 0.150115108350787, 0.1459471846063252, 0.141892904941829, 0.13796574246937204, 0.13417917030102802, 0.13054666154887062, 0.12708168932497338, 0.12379772674141006, 0.12070824691025418, 0.11782672294357943, 0.11516662795345947, 0.11274143505196793, 0.11056461735117835, 0.10864964796316452, 0.10701000000000001],
        [0.3794391697896677, 0.3811783951693767, 0.38264113361948704, 0.3838338527156301, 0.3847630200334369, 0.38543510314853885, 0.3858565696365673, 0.3860338870731532, 0.3859735230339281, 0.3856819450945233, 0.38516562083056977, 0.38443101781769906, 0.3834846036315422, 0.3823328458477304, 0.38098221204189525, 0.37943916978966774, 0.377710186666679, 0.37580173024856056, 0.37372026811094367, 0.3714722678294594, 0.3690641969797392, 0.3665025231374141, 0.3637937138781156, 0.36094423677747467, 0.357960559411123, 0.3548491493546914, 0.35161647418381137, 0.3482690014741141, 0.34481319880123085, 0.34125553374079287, 0.3376024738684314, 0.33386120070185726, 0.3300417515271003, 0.32615487757226913, 0.3222113300654729, 0.318221860234821, 0.31419721930842226, 0.3101481585143857, 0.3060854290808208, 0.3020197822358362, 0.2979619692075413, 0.29392274122404494, 0.2899128495134566, 0.2859430453038848, 0.2820240798234391, 0.2781667043002284, 0.2743778184404347, 0.2706489158625315, 0.26696763866306533, 0.26332162893858246, 0.25969852878562966, 0.25608598030075314, 0.2524716255804994, 0.24884310672141488, 0.24518806582004596, 0.24149414497293908, 0.23774898627664084, 0.23394023182769758, 0.23005552372265572, 0.22608250405806166, 0.222008814930462, 0.21782636948678546, 0.2135441650754905, 0.20917547009541804, 0.20473355294540882, 0.20023168202430378, 0.19568312573094362, 0.19110115246416937, 0.1864990306228218, 0.18189002860574177, 0.17728741481177013, 0.17270445763974765, 0.16815442548851528, 0.16365058675691382, 0.15920620984378414, 0.15483456314796704, 0.1505489150683034, 0.14636253400363408, 0.14228868835279992, 0.13834064651464176, 0.13453167688800047, 0.13087504787171678, 0.12738402786463168, 0.12407188526558598, 0.1209518884734205, 0.11803730588697611, 0.11534140590509367, 0.11287745692661398, 0.11065872735037789, 0.1086984855752263, 0.10701000000000001],
        [0.3820094153911022, 0.3837554080764826, 0.38522428514124724, 0.3864224361455807, 0.3873562506496672, 0.38803211821369155, 0.3884564283978382, 0.38863557076229166, 0.38857593486723613, 0.38828391027285664, 0.38776588653933725, 0.3870282532268628, 0.3860773998956175, 0.38491971610578596, 0.38356159141755264, 0.3820094153911022, 0.380269577586619, 0.3783484675642876, 0.37625247488429236, 0.37398798910681796, 0.3715613997920489, 0.3689790965001695, 0.36624746879136455, 0.36337290622581825, 0.36036179836371524, 0.3572205347652401, 0.3539555049905773, 0.3505730985999112, 0.34707970515342657, 0.3434817142113075, 0.3397855153337389, 0.33599827439996577, 0.3321302625654774, 0.3281925273048232, 0.32419611609255305, 0.3201520764032168, 0.316071455711364, 0.31196530149154456, 0.30784466121830806, 0.30372058236620436, 0.2996041124097832, 0.2955062988235943, 0.2914381890821875, 0.2874108306601124, 0.2834352710319188, 0.2795225576721565, 0.27567984320019695, 0.2718987008146993, 0.2681668088591438, 0.2644718456770114, 0.2608014896117828, 0.2571434190069387, 0.25348531220595977, 0.2498148475523265, 0.24611970338951988, 0.24238755806102044, 0.23860608991030888, 0.23476297728086595, 0.2308458985161722, 0.22684253195970838, 0.22274055595495532, 0.21853188208739271, 0.21422535491049718, 0.20983405221974466, 0.2053710518106108, 0.20084943147857148, 0.19628226901910242, 0.19168264222767945, 0.18706362889977843, 0.18243830683087503, 0.17781975381644513, 0.17322104765196453, 0.16865526613290893, 0.16413548705475425, 0.1596747882129762, 0.1552862474030506, 0.15098294242045324, 0.14677795106065994, 0.14268435111914643, 0.13871522039138856, 0.1348836366728621, 0.13120267775904282, 0.12768542144540657, 0.12434494552742914, 0.12119432780058631, 0.11824664606035379, 0.11551497810220752, 0.11301240172162323, 0.11075199471407667, 0.10874683487504364, 0.10701000000000002],
        [0.384544989337986, 0.38629542587738347, 0.38776857112306445, 0.3889707086744781, 0.3899081221310729, 0.39058709509229816, 0.3910139111576028, 0.39119485392643544, 0.3911362069982453, 0.3908442539724815, 0.39032527844859255, 0.3895855640260276, 0.38863139430423543, 0.3874690528826652, 0.3861048233607656, 0.384544989337986, 0.3827958344137747, 0.3808636421875811, 0.37875469625885416, 0.3764752802270424, 0.37403167769159523, 0.3714301722519614, 0.3686770475075897, 0.36577858705792915, 0.3627410745024289, 0.35957079344053766, 0.35627402747170434, 0.35285706019537805, 0.34932617521100756, 0.3456876561180419, 0.34194778651593005, 0.33811370271836927, 0.33419595189605195, 0.3302059339339183, 0.3261550487169089, 0.32205469612996457, 0.3179162760580257, 0.3137511883860327, 0.30957083299892635, 0.30538660978164706, 0.3012099186191354, 0.29705215939633195, 0.2929247319981774, 0.28883903630961216, 0.2848064722155767, 0.28083843960101174, 0.2769423825068842, 0.2731099215982682, 0.2693287216962632, 0.26558644762196987, 0.2618707641964881, 0.2581693362409184, 0.25446982857636075, 0.25075990602391507, 0.24702723340468205, 0.24325947553976152, 0.2394442972502538, 0.23556936335725895, 0.23162233868187726, 0.22759088804520877, 0.2234626762683538, 0.21922957447221128, 0.21490027897687528, 0.21048769240223866, 0.20600471736819434, 0.20146425649463515, 0.19687921240145403, 0.19226248770854376, 0.18762698503579733, 0.18298560700310756, 0.1783512562303673, 0.1737368353374695, 0.16915524694430703, 0.1646193936707727, 0.16014217813675943, 0.15573650296216016, 0.15141527076686764, 0.14719138417077485, 0.1430777457937746, 0.13908725825575977, 0.13523282417662336, 0.13152734617625805, 0.1279837268745569, 0.12461486889141271, 0.12143367484671835, 0.11845304736036673, 0.11568588905225066, 0.1131451025422631, 0.11084359045029687, 0.10879425539624488, 0.10701000000000001],
        [0.38704638350877196, 0.38879970195430363, 0.39027585543351967, 0.3914810033854972, 0.39242130524931346, 0.393102920464046, 0.3935320084687719, 0.39371472870256874, 0.3936572406045137, 0.39336570361368417, 0.3928462771691574, 0.3921051207100108, 0.39114839367532156, 0.3899822555041672, 0.38861286563562486, 0.38704638350877196, 0.38528896856268574, 0.3833467802364436, 0.38122597796912283, 0.37893272119980065, 0.3764731693675547, 0.373853481911462, 0.37107981827059994, 0.3681583378840458, 0.3650952001908772, 0.36189656463017117, 0.35856859064100505, 0.3551174376624562, 0.351549265133602, 0.34787023249351967, 0.34408649918128664, 0.3402051631728351, 0.33623707659151836, 0.33219403009754395, 0.3280878143511198, 0.323930220012454, 0.3197330377417545, 0.31550805819922906, 0.31126707204508564, 0.30702186993953223, 0.30278424254277686, 0.29856598051502714, 0.29437887451649136, 0.29023471520737715, 0.28614529324789273, 0.28212239929824573, 0.27817379415351967, 0.2742911191482999, 0.2704619857520469, 0.2666740054342215, 0.26291478966428417, 0.25917194991169595, 0.2554330976459173, 0.25168584433640895, 0.24791780145263165, 0.24411658046404594, 0.2402697928401126, 0.23636505005029243, 0.23238996356404595, 0.22833214485083383, 0.22417920538011693, 0.21992294540811352, 0.2155719203380723, 0.21113887436, 0.20663655166390293, 0.20207769643978774, 0.1974750528776608, 0.19284136516752862, 0.18818937749939785, 0.18353183406327478, 0.1788814790491661, 0.17425105664707816, 0.16965331104701753, 0.1651009864389906, 0.16060682701300408, 0.15618357695906432, 0.1518439804671778, 0.1476007817273511, 0.14346672492959062, 0.13945455426390294, 0.13557701392029453, 0.13184684808877192, 0.12827680095934152, 0.12487961672200994, 0.1216680395667836, 0.11865481368366906, 0.11585268326267273, 0.1132743924938012, 0.11093268556706087, 0.10884030667245828, 0.10700999999999998],
        [0.3895140897819135, 0.39126948968946784, 0.39274800194119347, 0.39395565336181276, 0.39489847077604817, 0.39558248100862203, 0.3960137108842569, 0.3961981872276751, 0.39614193686359894, 0.3958509866167512, 0.39533136331185414, 0.3945890937736301, 0.3936302048268016, 0.39246072329609105, 0.39108667600622093, 0.38951408978191343, 0.3877489914478913, 0.3857974078288767, 0.38366536574959237, 0.3813588920347605, 0.37888401350910356, 0.37624675699734406, 0.3734531493242041, 0.3705092173144065, 0.3674209877926738, 0.3641944875837281, 0.36083574351229175, 0.3573507824030875, 0.3537456310808374, 0.3500263163702644, 0.3461988650960904, 0.34227033327913076, 0.3382518937245712, 0.3341557484336898, 0.32999409940776486, 0.3257791486480747, 0.32152309815589786, 0.3172381499325121, 0.31293650597919614, 0.30863036829722806, 0.3043319388878863, 0.30005341975244887, 0.2958070128921943, 0.2916049203084009, 0.2874593440023466, 0.2833824859753102, 0.2793824359331261, 0.2754508343998562, 0.271575209604118, 0.26774308977452965, 0.26394200313970945, 0.26015947792827515, 0.2563830423688448, 0.2526002246900363, 0.2487985531204678, 0.2449655558887572, 0.2410887612235226, 0.23715569735338207, 0.2331538925069534, 0.22907087491285463, 0.22489417279970397, 0.22061549366197145, 0.21624326205753594, 0.2117900818101285, 0.20726855674348013, 0.20269129068132205, 0.19807088744738516, 0.1934199508654005, 0.18875108475909924, 0.1840768929522123, 0.17940997926847088, 0.17476294753160593, 0.17014840156534838, 0.16557894519342956, 0.1610671822395803, 0.15662571652753185, 0.152267151881015, 0.14800409212376098, 0.14384914107950075, 0.13981490257196547, 0.13591398042488612, 0.1321589784619937, 0.1285625005070194, 0.12513715038369413, 0.12189553191574902, 0.11885024892691508, 0.11601390524092342, 0.11339910468150503, 0.11101845107239092, 0.10888454823731228, 0.10701000000000004],
        [0.3919486000358633, 0.39370604246510016, 0.39518687451466655, 0.3963969916865996, 0.3973422894829362, 0.39802866340571336, 0.3984620089569682, 0.3986482216387377, 0.39859319695305884, 0.3983028304019686, 0.3977830174875042, 0.39703965371170247, 0.3960786345766005, 0.3949058555842353, 0.39352721223664383, 0.3919486000358633, 0.39017591448393046, 0.38821505108288246, 0.3860719053347563, 0.3837523727415891, 0.38126234880541776, 0.3786077290282793, 0.3757944089122108, 0.3728282839592493, 0.36971524967143177, 0.3664612015507952, 0.3630720350993766, 0.3595536458192131, 0.3559119292123416, 0.35215278078079926, 0.34828209602662286, 0.34430689055302316, 0.34023866036790457, 0.3360900215803452, 0.33187359029942304, 0.32760198263421614, 0.3232878146938027, 0.31894370258726046, 0.31458226242366766, 0.3102161103121022, 0.3058578623616423, 0.3015201346813658, 0.2972155433803511, 0.2929567045676759, 0.2887562343524182, 0.2846267488436562, 0.28057666563872635, 0.2765976082879982, 0.2726770018300993, 0.26880227130365797, 0.26496084174730206, 0.26114013819965926, 0.25732758569935765, 0.2535106092850251, 0.24967663399528944, 0.24581308486877862, 0.2419073869441206, 0.23794696525994322, 0.2339192448548744, 0.22981165076754198, 0.22561160803657399, 0.22131071800065708, 0.21691728719871337, 0.21244379846972383, 0.20790273465266923, 0.20330657858653078, 0.1986678131102892, 0.1939989210629254, 0.18931238528342062, 0.18462068861075542, 0.17993631388391096, 0.17527174394186798, 0.17063946162360763, 0.16605194976811072, 0.16152169121435828, 0.15706116880133117, 0.15268286536801026, 0.14839926375337661, 0.14422284679641112, 0.14016609733609467, 0.13624149821140824, 0.13246153226133275, 0.12883868232484916, 0.12538543124093837, 0.12211426184858135, 0.11903765698675899, 0.11616809949445221, 0.11351807221064203, 0.11110005797430927, 0.10892653962443499, 0.10701000000000001],
        [0.3943504061490744, 0.3961106136634249, 0.3975943370225196, 0.3988073514430325, 0.39975543214163695, 0.4004443543350072, 0.4008798932398171, 0.40106782407274044, 0.401013922050451, 0.4007239623896228, 0.4002037203069297, 0.39945897101904543, 0.39849548974264404, 0.3973190516943991, 0.39593543209098464, 0.3943504061490746, 0.3925697490853425, 0.3905992361164625, 0.38844464245910854, 0.38611174332995435, 0.3836063139456737, 0.3809341295229406, 0.3781009652784288, 0.37511259642881206, 0.37197479819076457, 0.3686933457809601, 0.3652740144160721, 0.36172257931277496, 0.3580448156877422, 0.3542464987576478, 0.35033340373916566, 0.34631251251027945, 0.34219563359421296, 0.33799578217549975, 0.33372597343867344, 0.3293992225682678, 0.3250285447488163, 0.32062695516485246, 0.31620746900091007, 0.3117831014415227, 0.3073668676712238, 0.30297178287454735, 0.2986108622360266, 0.29429712094019533, 0.2900435741715872, 0.28586323711473577, 0.28176484106334343, 0.2777399817477875, 0.2737759710076143, 0.2698601206823698, 0.2659797426116004, 0.2621221486348521, 0.2582746505916711, 0.25442456032160365, 0.2505591896641957, 0.24666585045899364, 0.24273185454554358, 0.23874451376339165, 0.234691139952084, 0.23055904495116675, 0.22633554060018624, 0.22201211719104255, 0.21759697882505222, 0.21310250805588576, 0.20854108743721378, 0.2039250995227068, 0.19926692686603525, 0.1945789520208698, 0.18987355754088103, 0.18516312597973947, 0.18046003989111556, 0.1757766818286799, 0.17112543434610314, 0.16651867999705564, 0.1619688013352081, 0.157488180914231, 0.15308920128779488, 0.14878424500957033, 0.14458569463322782, 0.14050593271243803, 0.13655734180087137, 0.13275230445219843, 0.12910320322008975, 0.12562242065821594, 0.12232233932024747, 0.11921534175985493, 0.11631381053070883, 0.11363012818647975, 0.11117667728083823, 0.1089658403674548, 0.10701000000000002],
        [0.3967200000000002, 0.39848445666666676, 0.39997225333333347, 0.4011890657142859, 0.40214056952380967, 0.4028324404761906, 0.4032703542857144, 0.40345998666666677, 0.4034070133333334, 0.4031171100000001, 0.40259595238095264, 0.40184921619047637, 0.40088257714285735, 0.399701710952381, 0.3983122933333334, 0.39672000000000024, 0.3949305066666668, 0.39294948904761917, 0.39078262285714305, 0.388435583809524, 0.38591404761904785, 0.3832236900000001, 0.38037018666666683, 0.3773592133333334, 0.37419644571428584, 0.37088755952380975, 0.3674382304761906, 0.3638541342857145, 0.36014094666666685, 0.35630434333333355, 0.3523500000000003, 0.34828487666666685, 0.34412107047619067, 0.33987196285714305, 0.3355509352380954, 0.3311713690476193, 0.3267466457142859, 0.3222901466666669, 0.3178152533333336, 0.3133353471428573, 0.3088638095238098, 0.30441402190476213, 0.29999936571428587, 0.2956332223809526, 0.29132897333333346, 0.28710000000000024, 0.2829553200000001, 0.2788864957142859, 0.27488072571428585, 0.2709252085714287, 0.267007142857143, 0.26311372714285725, 0.25923216000000016, 0.2553496400000001, 0.25145336571428584, 0.24753053571428577, 0.24356834857142864, 0.23955400285714296, 0.2354746971428572, 0.23131763000000002, 0.22707000000000005, 0.22272319000000002, 0.21828532, 0.2137686942857143, 0.2091856171428571, 0.20454839285714288, 0.1998693257142857, 0.19516071999999993, 0.19043487999999997, 0.18570410999999995, 0.18098071428571427, 0.1762769971428571, 0.17160526285714287, 0.16697781571428572, 0.16240696, 0.15790500000000002, 0.15348424000000008, 0.1491569842857143, 0.14493553714285717, 0.1408322028571429, 0.13685928571428574, 0.13302909, 0.12935392, 0.12584608000000003, 0.12251787428571434, 0.11938160714285719, 0.1164495828571429, 0.11373410571428577, 0.11124748000000004, 0.10900201000000001, 0.10701000000000002],
        [0.3990576681593487, 0.40082845352342156, 0.4023219827683678, 0.40354386053604935, 0.4044996914683284, 0.4051950802070665, 0.4056356313941261, 0.405826949671369, 0.40577463968065713, 0.4054843060638525, 0.40496155346281726, 0.4042119865194132, 0.4032412098755023, 0.40205482817294663, 0.4006584460536081, 0.39905766815934873, 0.3972580991320304, 0.39526534361351523, 0.3930850062456652, 0.3907226916703421, 0.3881840045294084, 0.3854745494647254, 0.3825999311181556, 0.3795657541315607, 0.3763776231468028, 0.373041142805744, 0.369561917750246, 0.36594555262217104, 0.36219765206338095, 0.35832382071573754, 0.35432966322110326, 0.350222133570128, 0.3460135831486153, 0.34171771269115636, 0.337348222932343, 0.3329188146067668, 0.32844318844901943, 0.3239350451936922, 0.3194080855753769, 0.31487601032866475, 0.3103525201881478, 0.30585131588841724, 0.3013860981640649, 0.2969705677496821, 0.29261842537986055, 0.28834337178919184, 0.2841546731417112, 0.28004385731922915, 0.27599801763299947, 0.27200424739427653, 0.26804963991431424, 0.2641212885043667, 0.2602062864756883, 0.2562917271395326, 0.25236470380715414, 0.24841230978980672, 0.24442163839874465, 0.2403797829452219, 0.23627383674049254, 0.2320908930958107, 0.2278180453224305, 0.22344657932360232, 0.21898455137056258, 0.21444421032654373, 0.2098378050547785, 0.20517758441849948, 0.2004757972809393, 0.1957446925053306, 0.19099651895490605, 0.18624352549289822, 0.18149796098253987, 0.17677207428706349, 0.17207811426970174, 0.16742832979368732, 0.16283496972225284, 0.1583102829186309, 0.15386651824605418, 0.14951592456775525, 0.1452707507469668, 0.14114324564692143, 0.13714565813085178, 0.1332902370619905, 0.12958923130357025, 0.12605488971882367, 0.12269946117098328, 0.11953519452328176, 0.11657433863895182, 0.11382914238122607, 0.11131185461333704, 0.1090347241985175, 0.10701000000000001],
        [0.40136287596685094, 0.40314200094777203, 0.4046428664595991, 0.40587103375407085, 0.4068320640829256, 0.4075315186979021, 0.407974958850739, 0.4081679457931747, 0.4081160407769479, 0.4078248050537972, 0.4072997998754612, 0.4065465864936784, 0.4055707261601874, 0.4043777801267268, 0.40297330964503514, 0.40136287596685105, 0.39955204034391306, 0.39754636402795984, 0.39535140827072984, 0.3929727343239618, 0.3904159034393943, 0.38768647686876573, 0.3847900158638148, 0.3817320816762801, 0.3785182355579003, 0.37515403876041375, 0.3716450525355593, 0.3679968381350753, 0.3642149568107002, 0.3603049698141731, 0.35627243839723227, 0.3521243258973078, 0.34787320399459726, 0.3435330464549891, 0.33911782704437227, 0.33464151952863563, 0.330118097673668, 0.325561535245358, 0.3209858060095947, 0.3164048837322668, 0.31183274217926304, 0.30728335511647253, 0.3027706963097838, 0.29830873952508585, 0.2939114585282672, 0.28959282708521705, 0.28536232278145834, 0.2812114384810511, 0.27712717086768995, 0.27309651662506906, 0.26910647243688324, 0.26514403498682665, 0.2611962009585939, 0.2572499670358791, 0.2532923299023771, 0.24931028624178186, 0.24529083273778826, 0.2412209660740905, 0.237087682934383, 0.2328779800023602, 0.2285788539617167, 0.22418150457472608, 0.21969394391797933, 0.2151283871466471, 0.21049704941589967, 0.2058121458809075, 0.2010858916968409, 0.1963305020188703, 0.1915581920021663, 0.18678117680189915, 0.18201167157323916, 0.17726189147135699, 0.17254405165142286, 0.16787036726860724, 0.16325305347808053, 0.15870432543501314, 0.15423639829457547, 0.149861487211938, 0.14559180734227103, 0.1414395738407451, 0.13741700186253047, 0.1335363065627976, 0.129809703096717, 0.12624940661945894, 0.12286763228619395, 0.11967659525209236, 0.11668851067232462, 0.11391559370206109, 0.11137005949647219, 0.10906412321072836, 0.10701000000000004],
        [0.40363488345449267, 0.4054241243201722, 0.4069337409916828, 0.40816927616661225, 0.40913627254254836, 0.40984027281707963, 0.41028681968779396, 0.41048145585227946, 0.4104297240081241, 0.410137166852916, 0.4096093270842434, 0.40885174739969415, 0.4078699704968563, 0.40666953907331815, 0.40525599582666755, 0.4036348834544927, 0.4018117446543816, 0.39979212212392234, 0.39758155856070293, 0.3951855966623113, 0.3926097791263359, 0.3898596486503646, 0.3869407479319855, 0.3838586196687866, 0.38061880655835606, 0.3772268512982819, 0.3736882965861521, 0.3700086851195548, 0.36619355959607824, 0.3622484627133102, 0.358178937168839, 0.35399196935702626, 0.3497003204593303, 0.3453181953539822, 0.3408597989192137, 0.3363393360332568, 0.3317710115743428, 0.32716903042070344, 0.3225475974505703, 0.3179209175421752, 0.31330319557374947, 0.3087086364235252, 0.30415144496973373, 0.29964582609060664, 0.2952059846643756, 0.2908461255692724, 0.2865759041122142, 0.2823867773148599, 0.2782656526275538, 0.2741994375006407, 0.27017503938446497, 0.2661793657293711, 0.2621993239857038, 0.2582218216038072, 0.25423376603402603, 0.25022206472670466, 0.2461736251321877, 0.24207535470081967, 0.23791416088294493, 0.23367695112890793, 0.2293506328890534, 0.224926329295448, 0.220412026207048, 0.2158199251645318, 0.21116222770857807, 0.20645113537986517, 0.2016988497190718, 0.19691757226687626, 0.1921195045639572, 0.18731684815099311, 0.18252180456866257, 0.177746575357644, 0.17300336205861594, 0.16830436621225692, 0.1636617893592455, 0.1590878330402601, 0.15459469879597934, 0.15019458816708173, 0.1458997026942456, 0.14172224391814975, 0.13767441337947248, 0.1337684126188924, 0.13001644317708802, 0.12643070659473787, 0.12302340441252048, 0.11980673817111424, 0.11679290941119783, 0.11399411967344968, 0.11142257049854828, 0.10909046342717225, 0.10701000000000002],
        [0.40587295065426005, 0.40767384902107684, 0.40919344294927446, 0.41043727857193585, 0.4114109020221439, 0.41211985943298207, 0.4125696969375328, 0.41276596066887944, 0.4127141967601048, 0.41241995134429194, 0.411888770554524, 0.41112620052388366, 0.4101377873854541, 0.4089290772723183, 0.40750561631755927, 0.40587295065426, 0.40403662641550336, 0.4020021897343725, 0.3997751867439506, 0.3973611635773202, 0.39476566636756444, 0.39199424124776644, 0.3890524343510092, 0.38594579181037564, 0.38267985975894875, 0.3792601843298117, 0.3756923116560471, 0.3719817878707383, 0.3681341591069681, 0.36415497149781956, 0.36004977117637565, 0.3558255796581036, 0.3514953199880079, 0.3470733905934767, 0.34257418990189853, 0.338012116340662, 0.33340156833715573, 0.328756944318768, 0.32409264271288735, 0.3194230619469022, 0.3147626004482013, 0.31012565664417296, 0.30552662896220567, 0.3009799158296879, 0.29649991567400824, 0.2921010269225552, 0.2877930523269522, 0.2835674119357635, 0.27941093012178825, 0.27531043125782545, 0.2712527397166746, 0.2672246798711347, 0.26321307609400507, 0.25920475275808463, 0.25518653423617277, 0.25114524490106865, 0.2470677091255715, 0.2429407512824804, 0.23875119574459464, 0.23448586688471332, 0.23013158907563563, 0.2256794170278456, 0.22113732680256634, 0.2165175247987056, 0.21183221741517125, 0.20709361105087118, 0.2023139121047133, 0.1975053269756054, 0.19268006206245536, 0.18785032376417105, 0.18302831847966033, 0.17822625260783104, 0.17345633254759105, 0.1687307646978482, 0.16406175545751037, 0.15946151122548544, 0.15494223840068125, 0.15051614338200558, 0.14619543256836637, 0.14199231235867152, 0.13791898915182882, 0.13398766934674614, 0.1302105593423313, 0.1265998655374923, 0.12316779433113689, 0.1199265521221729, 0.11688834530950826, 0.11406538029205077, 0.11146986346870832, 0.1091140012383888, 0.10701],
        [0.40807633759813905, 0.4098902004309397, 0.41142080891702937, 0.41267373176830424, 0.4136545376966597, 0.414368795413992, 0.41482207363219714, 0.41501994106317064, 0.41496796641880884, 0.4146717184110074, 0.41413676575166253, 0.4133686771526696, 0.412373021325925, 0.41115536698332444, 0.4097212828367638, 0.4080763375981391, 0.40622609997934617, 0.40417613869228103, 0.4019320224488394, 0.3994993199609174, 0.39688359994041084, 0.3940904310992156, 0.3911253821492275, 0.38799402180234277, 0.3847019187704572, 0.3812546417654665, 0.37765775949926667, 0.3739168406837537, 0.37003745403082355, 0.36602516825237186, 0.3618855520602948, 0.35762567250936017, 0.3532585900258241, 0.3487988633788138, 0.34426105133745766, 0.33965971267088324, 0.33500940614821856, 0.33032469053859126, 0.3256201246111293, 0.32091026713496046, 0.3162096768792125, 0.3115329126130135, 0.30689453310549114, 0.3023090971257733, 0.29779116344298767, 0.29335529082626227, 0.28901140261864566, 0.2847508804588706, 0.28056047055959016, 0.2764269191334579, 0.2723369723931274, 0.2682773765512519, 0.26423487782048466, 0.2601962224134793, 0.2561481565428892, 0.25207742642136766, 0.24797077826156813, 0.24381495827614413, 0.23959671267774893, 0.2353027876790358, 0.23091992949265852, 0.22643913131399618, 0.2218683742693322, 0.21721988646767598, 0.2125058960180368, 0.20773863102942403, 0.20293031961084698, 0.19809318987131497, 0.1932394699198374, 0.18838138786542358, 0.18353117181708287, 0.17870104988382463, 0.17390325017465813, 0.16915000079859271, 0.16445352986463774, 0.15982606548180261, 0.1552798357590966, 0.15082706880552896, 0.14647999273010923, 0.1422508356418466, 0.1381518256497504, 0.13419519086283005, 0.13039315939009496, 0.12675795934055425, 0.12330181882321746, 0.12003696594709377, 0.11697562882119264, 0.11413003555452336, 0.11151241425609526, 0.10913499303491768, 0.10701],
        [0.41024430431811576, 0.4120722039302155, 0.41361467547960334, 0.4148773265539794, 0.4158657647410425, 0.4165855976284923, 0.4170424328040281, 0.41724187785534933, 0.417189540370155, 0.4168910279361451, 0.41635194814101845, 0.41557790857247484, 0.41457451681821333, 0.41334738046593344, 0.4119021071033345, 0.4102443043181158, 0.40837957969797684, 0.406313540830617, 0.40405179530373553, 0.4015999507050319, 0.3989636146222056, 0.3961483946429557, 0.3931598983549817, 0.39000373334598315, 0.3866855072036592, 0.38321082751570945, 0.37958530186983286, 0.3758145378537292, 0.3719041430550978, 0.3678597250616376, 0.36368689146104854, 0.359392763619616, 0.3549905180179722, 0.3504948449153347, 0.34592043457092186, 0.3412819772439518, 0.3365941631936427, 0.3318716826792125, 0.32712922595987953, 0.3223814832948617, 0.3176431449433773, 0.3129289011646444, 0.3082534422178813, 0.30363145836230576, 0.2990776398571361, 0.2946066769615905, 0.2902285901802676, 0.28593472099928896, 0.28171174115015646, 0.27754632236437216, 0.2734251363734383, 0.2693348549088567, 0.2652621497021296, 0.26119369248475893, 0.25711615498824675, 0.2530162089440951, 0.24888052608380606, 0.24469577813888163, 0.2404486368408239, 0.23612577392113487, 0.2317138611113167, 0.22720383569597669, 0.22260369717214332, 0.2179257105899505, 0.21318214099953212, 0.20838525345102202, 0.20354731299455395, 0.19868058468026195, 0.1937973335582798, 0.1889098246787414, 0.18403032309178058, 0.17917109384753116, 0.17434440199612708, 0.16956251258770208, 0.16483769067239015, 0.16018220130032515, 0.15560830952164081, 0.1511282803864711, 0.1467543789449499, 0.14249887024721092, 0.1383740193433882, 0.13439209128361546, 0.13056535111802667, 0.12690606389675566, 0.12342649466993623, 0.12013890848770231, 0.11705557040018774, 0.11418874545752637, 0.11155069870985203, 0.10915369520729865, 0.10701000000000002],
        [0.4123761108461763, 0.4142188848993579, 0.4157738792216519, 0.4170467537272239, 0.41804316833023986, 0.41876878294486575, 0.4192292574852674, 0.419430251865611, 0.4193774260000622, 0.41907643980278725, 0.41853295318795186, 0.417752626069722, 0.4167411183622636, 0.41550408997974264, 0.41404720083632474, 0.4123761108461763, 0.41049647992346294, 0.4084139679823507, 0.4061342349370055, 0.40366294070159314, 0.40100574519027987, 0.39816830831723116, 0.39515628999661345, 0.39197535014259227, 0.3886311486693337, 0.38512934549100364, 0.381475600521768, 0.3776755736757929, 0.3737349248672441, 0.36965931401028745, 0.36545440101908894, 0.36112736869769146, 0.35669149140964623, 0.35216156640838037, 0.34755239094732215, 0.3428787622798994, 0.33815547765953985, 0.3333973343396712, 0.3286191295737216, 0.3238356606151185, 0.3190617247172897, 0.3143121191336633, 0.3096016411176671, 0.3049450879227287, 0.300357256802276, 0.29585294500973697, 0.29144225020479125, 0.287116471672127, 0.28286220910268406, 0.2786660621874026, 0.2745146306172225, 0.270394514083084, 0.26629231227592687, 0.26219462488669126, 0.25808805160631715, 0.2539591921257446, 0.24979464613591354, 0.24558101332776405, 0.24130489339223626, 0.23695288602026987, 0.23251159090280532, 0.22797189371586435, 0.22334182407579742, 0.21863369758403675, 0.21385982984201465, 0.20903253645116357, 0.20416413301291578, 0.19926693512870342, 0.19435325839995918, 0.1894354184281151, 0.18452573081460363, 0.1796365111608571, 0.17478007506830778, 0.16996873813838803, 0.1652148159725302, 0.16053062417216657, 0.15592847833872944, 0.15142069407365125, 0.1470195869783642, 0.14273747265430067, 0.13858666670289302, 0.13457948472557352, 0.1307282423237745, 0.12704525509892836, 0.1235428386524674, 0.12023330858582387, 0.11712898050043019, 0.11424216999771865, 0.11158519267912152, 0.1091703641460712, 0.10701000000000001],
        [0.41447101721430657, 0.4163292687188218, 0.41789725672783007, 0.4191807040862996, 0.4201853336391985, 0.42091686823149466, 0.4213810307081565, 0.421583543914152, 0.42153013069444933, 0.4212265138940168, 0.42067841635782227, 0.4198915609308342, 0.4188716704580202, 0.4176244677843489, 0.4161556757547884, 0.41447101721430657, 0.4125762150078717, 0.41047699198045184, 0.4081790709770152, 0.40568817484253, 0.40301002642196426, 0.4001503485602861, 0.3971148641024637, 0.39390929589346513, 0.39053936677825885, 0.38701079960181256, 0.3833293172090946, 0.37950064244507303, 0.375530498154716, 0.37142460718299175, 0.36718869237486823, 0.36283000345240657, 0.3583618976460395, 0.35379925906329207, 0.34915697181168964, 0.3444499199987576, 0.3396929877320217, 0.33490105911900697, 0.33008901826723874, 0.3252717492842426, 0.32046413627754383, 0.31568106335466767, 0.3109374146231398, 0.30624807419048544, 0.3016279261642299, 0.2970918546518986, 0.2926500178851897, 0.2882936705924929, 0.2840093416263699, 0.27978355983938324, 0.2756028540840951, 0.2714537532130677, 0.2673227860788633, 0.26319648153404396, 0.25906136843117206, 0.25490397562280964, 0.2507108319615191, 0.24646846629986255, 0.24216340749040227, 0.23778218438570037, 0.23331132583831923, 0.2287416689157365, 0.22408128354509238, 0.2193425478684423, 0.21453784002784204, 0.2096795381653473, 0.20478002042301358, 0.1998516649428966, 0.194906849867052, 0.18995795333753543, 0.1850173534964026, 0.18009742848570898, 0.1752105564475103, 0.1703691155238622, 0.16558548385682031, 0.16087203958844037, 0.15624116086077788, 0.15170522581588852, 0.14727661259582794, 0.14296769934265183, 0.13879086419841574, 0.1347584853051754, 0.13088294080498636, 0.12717660883990436, 0.123651867551985, 0.12032109508328391, 0.11719666957585673, 0.11429096917175914, 0.11161637201304668, 0.1091852562417751, 0.10701000000000001],
        [0.41652828345449266, 0.4184023807690611, 0.4199836445827938, 0.4212778684294693, 0.4222908458428659, 0.42302837035676216, 0.42349623550493676, 0.42370023482116836, 0.42364616183923515, 0.423339810092916, 0.42278697311598945, 0.4219934444422338, 0.4209650176054278, 0.41970748613935005, 0.4182266435777787, 0.4165282834544927, 0.4146181993032703, 0.41250218465789046, 0.41018603305213136, 0.40767553801977163, 0.40497649309458994, 0.4020946918103646, 0.3990359277008743, 0.39580599429989766, 0.39241068514121313, 0.38885579375859924, 0.38514711368583454, 0.38129043845669763, 0.377291561604967, 0.3731562766644213, 0.3688903771688389, 0.36450118359258177, 0.360002124172346, 0.35540815408541065, 0.35073422850905495, 0.3459953026205583, 0.3412063315971998, 0.3363822706162589, 0.33153807485501474, 0.32668869949074647, 0.3218490997007336, 0.3170342306622553, 0.3122590475525907, 0.3075385055490192, 0.30288755982881993, 0.2983211655692724, 0.2938495284144363, 0.2894638558754946, 0.28515060593041086, 0.28089623655714846, 0.2766872057336713, 0.2725099714379426, 0.26835099164792586, 0.264196724341585, 0.26003362749688314, 0.255848159091784, 0.25162677710425113, 0.2473559395122482, 0.24302210429373852, 0.23861172942668568, 0.23411127288905337, 0.2295115248376702, 0.22482060414482574, 0.22005096186167467, 0.2152150490393717, 0.2103253167290715, 0.2053942159819289, 0.2004341978490984, 0.19545771338173493, 0.19047721363099313, 0.18550514964802767, 0.1805539724839932, 0.17563613319004454, 0.17076408281733627, 0.16595027241702326, 0.1612071530402601, 0.15654717573820154, 0.15198279156200228, 0.14752645156281705, 0.14319060679180048, 0.13898770830010737, 0.13493020713889237, 0.1310305543593102, 0.12730120101251563, 0.1237545981496633, 0.12040319682190788, 0.11725944808040414, 0.1143358029763068, 0.11164471256077052, 0.10919862788495002, 0.10701000000000002],
        [0.41854716959872057, 0.4204372464305302, 0.42203187937119846, 0.4233369375549948, 0.42435829011618903, 0.4251018061890508, 0.42557335490784975, 0.4257788054068557, 0.4257240268203384, 0.42541488828256757, 0.42485725892781273, 0.424057007890344, 0.4230200043044305, 0.42175211730434237, 0.4202592160243491, 0.4185471695987205, 0.41662184716172634, 0.4144891178476362, 0.4121548507907199, 0.4096249151252469, 0.4069051799854873, 0.4040015145057106, 0.4009197878201865, 0.39766586906318463, 0.39424562736897484, 0.39066493187182694, 0.3869296517060103, 0.3830456560057948, 0.3790188139054504, 0.3748549945392464, 0.37056006704145267, 0.36614142482703693, 0.3616125584337593, 0.3569884826800773, 0.3522842123844491, 0.3475147623653327, 0.3426951474411859, 0.3378403824304666, 0.33296548215163285, 0.32808546142314243, 0.32321533506345335, 0.31837011789102354, 0.31356482472431085, 0.3088144703817734, 0.30413406968186874, 0.2995386374430553, 0.2950384169855041, 0.2906245656362407, 0.286283469224004, 0.28200151357753267, 0.2777650845255661, 0.27356056789684274, 0.2693743495201017, 0.26519281522408183, 0.26100235083752205, 0.2567893421891611, 0.25254017510773813, 0.24824123542199197, 0.24387890896066133, 0.23943958155248524, 0.2349096390262027, 0.23027982502374272, 0.2255583144397955, 0.22075763998224146, 0.21589033435896113, 0.21096893027783478, 0.206005960446743, 0.20101395757356602, 0.19600545436618447, 0.1909929835324787, 0.1859890777803291, 0.1810062698176162, 0.1760570923522203, 0.17115407809202185, 0.16630975974490136, 0.16153667001873928, 0.15684734162141586, 0.15225430726081177, 0.14777009964480722, 0.14340725148128272, 0.13917829547811875, 0.13509576434319567, 0.13117219078439396, 0.12742010750959398, 0.1238520472266763, 0.12048054264352115, 0.11731812646800908, 0.11437733140802052, 0.11167069017143585, 0.10921073546613554, 0.10701],
        [0.4205269356789765, 0.4224328910836834, 0.4240407976776994, 0.4253566022611387, 0.4263862516341152, 0.4271356925967433, 0.4276108719491369, 0.4278177364914106, 0.4277622330236781, 0.427450308346054, 0.4268879092586524, 0.42608098256158733, 0.425035475054973, 0.4237573335389237, 0.42225250481355336, 0.4205269356789765, 0.41858657293530693, 0.4164373633826592, 0.4140852538211473, 0.41153619105088535, 0.40879612187198777, 0.4058709930845686, 0.40276675148874175, 0.3994893438846217, 0.39604471707232286, 0.3924388178519589, 0.38867759302364424, 0.38476698938749304, 0.3807129537436196, 0.3765214328921378, 0.37219837363316216, 0.3677512428645925, 0.36319358787547296, 0.3585404760526333, 0.35380697478290324, 0.3490081514531127, 0.34415907345009167, 0.33927480816066957, 0.33437042297167663, 0.3294609852699425, 0.3245615624422971, 0.31968722187557, 0.3148530309565915, 0.31007405707219127, 0.30536536760919875, 0.3007420299544442, 0.2962143187913662, 0.2917733379898391, 0.28740539871634596, 0.28309681213737, 0.2788338894193947, 0.2746029417289027, 0.2703902802323776, 0.26618221609630255, 0.26196506048716045, 0.25772512457143465, 0.25344871951560843, 0.24912215648616498, 0.2447317466495873, 0.24026380117235854, 0.2357046312209622, 0.2310449330160312, 0.22629294299479935, 0.22146128264865034, 0.21656257346896784, 0.21160943694713558, 0.20661449457453726, 0.2015903678425565, 0.1965496782425772, 0.19150504726598294, 0.18646909640415749, 0.1814544471484845, 0.1764737209903477, 0.1715395394211307, 0.16666452393221742, 0.16186129601499144, 0.1571424771608364, 0.15252068886113615, 0.14800855260727433, 0.14361868989063462, 0.13936372220260082, 0.13525627103455654, 0.13130895787788552, 0.1275344042239715, 0.12394523156419816, 0.1205540613899492, 0.11737351519260836, 0.11441621446355929, 0.11169478069418573, 0.10922183537587138, 0.10701],
        [0.42246684172724636, 0.4243883401089751, 0.4260092360869525, 0.42733555334616324, 0.4283733155715916, 0.4291285464482223, 0.4296072696610398, 0.42981550889502856, 0.42975928783517303, 0.42944463016645795, 0.42887755957386775, 0.4280640997423868, 0.42701027435699956, 0.42572210710269076, 0.4242056216644448, 0.42246684172724636, 0.42051179097607955, 0.41834649309592925, 0.41597697177178, 0.4134092506886159, 0.4106493535314218, 0.40770330398518223, 0.4045771257348817, 0.40127684246550427, 0.3978084778620351, 0.3941780556094584, 0.3903915993927586, 0.38645513289692024, 0.38237467980692796, 0.3781562638077662, 0.3738059085844194, 0.3693311534140687, 0.3647455999426809, 0.36006436540841963, 0.35530256704944807, 0.35047532210392995, 0.34559774781002855, 0.3406849614059073, 0.33575208012972957, 0.3308142212196589, 0.3258865019138589, 0.3209840394504927, 0.3161219510677239, 0.311315354003716, 0.30657936549663223, 0.30192910278463625, 0.29737486902499594, 0.2929077110513982, 0.28851386161663406, 0.28417955347349494, 0.2798910193747721, 0.275634492073257, 0.2713962043217409, 0.2671623888730147, 0.2629192784798702, 0.2586531058950984, 0.2543501038714906, 0.24999650516183838, 0.24557854251893277, 0.24108244869556505, 0.2364944564445267, 0.23180521235661292, 0.22702301837463515, 0.22216059027940874, 0.21723064385174934, 0.21224589487247228, 0.20721905912239297, 0.20216285238232692, 0.1970899904330897, 0.19201318905549652, 0.18694516403036301, 0.18189863113850452, 0.17688630616073653, 0.17192090487787448, 0.16701514307073384, 0.16218173652013007, 0.15743340100687855, 0.15278285231179478, 0.14824280621569424, 0.14382597849939227, 0.13954508494370446, 0.13541284132944617, 0.13144196343743286, 0.12764516704848003, 0.12403516794340307, 0.12062468190301744, 0.11742642470813858, 0.11445311213958197, 0.11171745997816306, 0.10923218400469724, 0.10701000000000001],
        [0.4243661477755162, 0.42630261888685916, 0.42793603118361284, 0.42927248160833065, 0.4303180671035654, 0.43107888461187077, 0.43156103107579985, 0.4317706034379059, 0.4317136986407421, 0.431396413626862, 0.43082484533881854, 0.4300050907191651, 0.4289432467104548, 0.42764541025524105, 0.4261176782960771, 0.4243661477755162, 0.4223969156361115, 0.42021607882041634, 0.41782973427098397, 0.4152439789303677, 0.4124649097411206, 0.40949862364579603, 0.40635121758694726, 0.40302878850712764, 0.3995374333488903, 0.39588324905478856, 0.3920723325673755, 0.38811078082920464, 0.38400469078282906, 0.37976015937080193, 0.37538328353567674, 0.37088167218428547, 0.36626898208057673, 0.3615603819527774, 0.3567710405291146, 0.3519161265378159, 0.3470108087071083, 0.34207025576521893, 0.3371096364403752, 0.3321441194608041, 0.327188873554733, 0.3222590674503889, 0.31736986987599924, 0.3125364495597911, 0.30777397522999167, 0.30309761561482823, 0.2985177028793664, 0.294025222936026, 0.289606325134065, 0.28524715882274143, 0.28093387335131365, 0.2766526180690399, 0.272389542325178, 0.2681307954689862, 0.26386252684972267, 0.25957088581664556, 0.2552420217190131, 0.2508620839060832, 0.24641722172711428, 0.24189358453136417, 0.2372773216680913, 0.23255902658756497, 0.22774706914410053, 0.22285426329302438, 0.21789342298966313, 0.21287736218934336, 0.20781889484739163, 0.20273083491913446, 0.19762599635989841, 0.19251719312501014, 0.18741723916979608, 0.18233894844958276, 0.17729513491969687, 0.17229861253546483, 0.16736219525221321, 0.1624986970252687, 0.15772093180995772, 0.15304171356160687, 0.14847385623554268, 0.14403017378709176, 0.13972348017158062, 0.1355665893443358, 0.13157231526068391, 0.12775347187595154, 0.12412287314546513, 0.12069333302455128, 0.11747766546853657, 0.11448868443274754, 0.11173920387251071, 0.1092420377431527, 0.10701000000000002],
        [0.426224113855772, 0.4281747527977901, 0.429820019552336, 0.4311660778459029, 0.4322190914049836, 0.43298522395607103, 0.4334706392256585, 0.4336815009402382, 0.43362397282630394, 0.4333042186103483, 0.43272840201886426, 0.43190268677834487, 0.4308332366152829, 0.42952621525617146, 0.4279877864275035, 0.4262241138557719, 0.42424136126746986, 0.42204569238908995, 0.41964327094712556, 0.41704026066806943, 0.41424282527841455, 0.4112571285046538, 0.40808933407328024, 0.4047456057107869, 0.4012321071436666, 0.3975550020984125, 0.3937204543015172, 0.389734627479474, 0.3856036853587758, 0.38133379166591547, 0.37693111012738606, 0.3724033148840632, 0.36776412173435397, 0.3630287568910476, 0.35821244656693374, 0.3533304169748022, 0.3483978943274425, 0.3434301048376441, 0.33844227471819666, 0.33344963018188983, 0.328467397441513, 0.32351080270985605, 0.31859507219970845, 0.3137354321238597, 0.3089471086950993, 0.3042453281262172, 0.2996404555474507, 0.2951234117588307, 0.2906802564778355, 0.2862970494219438, 0.28195985030863424, 0.2776547188553855, 0.27336771477967603, 0.26908489779898453, 0.2647923276307897, 0.2604760639925699, 0.2561221666018039, 0.2517166951759705, 0.24724570943254806, 0.24269526908901518, 0.2380514338628507, 0.2333047392509645, 0.2284636238679932, 0.22354100210800457, 0.21854978836506664, 0.21350289703324726, 0.20841324250661444, 0.20329373917923604, 0.19815730144518004, 0.19301684369851435, 0.1878852803333069, 0.18277552574362563, 0.17770049432353843, 0.17267310046711326, 0.16770625856841812, 0.16281288302152078, 0.15800588822048925, 0.15329818855939156, 0.1487026984322955, 0.14423233223326903, 0.13990000435638006, 0.13571862919569666, 0.1317011211452866, 0.12786039459921789, 0.12420936395155842, 0.12076094359637611, 0.11752804792773892, 0.11452359133971482, 0.11176048822637166, 0.10925165298177743, 0.10701],
        [0.42804000000000003, 0.4300037672222223, 0.43166003777777784, 0.43301503285714293, 0.4340749736507937, 0.4348460813492063, 0.4353345771428572, 0.43554668222222226, 0.4354886177777778, 0.435166605, 0.43458686507936506, 0.43375561920634914, 0.4326790885714286, 0.43136349436507937, 0.42981505777777784, 0.42804000000000003, 0.42604454222222216, 0.4238349056349206, 0.4214173114285714, 0.41879798079365077, 0.41598313492063493, 0.41297899499999996, 0.40979178222222223, 0.40642771777777775, 0.40289302285714285, 0.39919391865079373, 0.3953366263492064, 0.39132736714285715, 0.3871723622222223, 0.38287783277777776, 0.37845000000000006, 0.3738965972222222, 0.3692314063492064, 0.36446972142857154, 0.3596268365079365, 0.3547180456349206, 0.349758642857143, 0.3447639222222223, 0.33974917777777786, 0.33472970357142856, 0.32972079365079365, 0.3247377420634921, 0.31979584285714296, 0.3149103900793651, 0.3100966777777777, 0.30537000000000003, 0.30074076222222224, 0.2961998156349208, 0.2917331228571429, 0.2873266465079365, 0.28296634920634933, 0.27863819357142866, 0.2743281422222223, 0.27002215777777777, 0.26570620285714297, 0.2613662400793651, 0.2569882320634921, 0.25255814142857147, 0.24806193079365088, 0.24348556277777775, 0.238815, 0.2340407138888889, 0.22917121111111113, 0.22421950714285716, 0.21919861746031746, 0.21412155753968257, 0.2090013428571429, 0.20385098888888883, 0.19868351111111113, 0.193511925, 0.18834924603174602, 0.1832084896825397, 0.17810267142857142, 0.17304480674603173, 0.16804791111111114, 0.16312500000000002, 0.15828908888888887, 0.15355319325396824, 0.14893032857142857, 0.14443351031746032, 0.14007575396825395, 0.13587007499999995, 0.13182948888888887, 0.1279670111111111, 0.12429565714285715, 0.12082844246031746, 0.11757838253968254, 0.1145584928571429, 0.11178178888888889, 0.10926128611111112, 0.10701000000000002],
        [0.42981282756712225, 0.4317884892665271, 0.4334547565955799, 0.43481789655075537, 0.43588417612852753, 0.4366598623253711, 0.4371512221377606, 0.4373645225621705, 0.4373060305950751, 0.43698201323294933, 0.4363987374722674, 0.43556247030950374, 0.4344794787411329, 0.43315602976362944, 0.43159839037346764, 0.42981282756712214, 0.4278056083410675, 0.42558299969177815, 0.4231512686157285, 0.4205166821093931, 0.4176855071692464, 0.41466401079176285, 0.4114584599734172, 0.40807512171068344, 0.40452026300003674, 0.40080015083795095, 0.3969210522209009, 0.39288923414536087, 0.3887109636078056, 0.38439250760470933, 0.3799401331325469, 0.37536162531291295, 0.37067084176788745, 0.3658831582446695, 0.3610139504904591, 0.35607859425245625, 0.35109246527786064, 0.3460709393138721, 0.34102939210769057, 0.3359831994065157, 0.33094773695754776, 0.325938380507986, 0.3209705058050308, 0.31605948859588173, 0.3112207046277385, 0.30646952964780116, 0.3018164196357713, 0.29725215150135836, 0.29276258238677305, 0.28833356943422683, 0.28395096978593065, 0.2796006405840956, 0.27526843897093284, 0.27094022208865337, 0.2666018470794683, 0.2622391710855886, 0.25783805124922576, 0.2533843447125905, 0.24886390861789395, 0.24426260010734738, 0.23956627632316185, 0.23476533752288453, 0.22986835642540765, 0.22488844886495948, 0.2198387306757683, 0.21473231769206255, 0.2095823257480704, 0.20440187067802035, 0.19920406831614063, 0.19400203449665948, 0.1888088850538053, 0.18363773582180642, 0.17850170263489124, 0.1734139013272879, 0.16838744773322487, 0.16343545768693038, 0.1585710470226328, 0.15380733157456036, 0.14915742717694153, 0.14463444966400454, 0.14025151486997767, 0.1360217386290894, 0.13195823677556792, 0.12807412514364158, 0.12438251956753868, 0.12089653588148756, 0.11762928991971658, 0.11459389751645398, 0.11180347450592813, 0.10927113672236737, 0.10701],
        [0.43154066322380535, 0.433526952940746, 0.4352021833453311, 0.4365726552772164, 0.4376446695760569, 0.43842452708150825, 0.43891852863322595, 0.43913297507086513, 0.4390741672340813, 0.4387484059625299, 0.4381619920958664, 0.4373212264737462, 0.43623240993582457, 0.4349018433217571, 0.43333582747119864, 0.43154066322380535, 0.4295226514192321, 0.4272880928971348, 0.4248432884971684, 0.4221945390589883, 0.4193481454222503, 0.4163104084266093, 0.4130876289117213, 0.40968610771724107, 0.40611214568282444, 0.4023720436481266, 0.3984721024528031, 0.39441862293650926, 0.3902179059389005, 0.3858762522996322, 0.38139996285835975, 0.37679686689160913, 0.37208090742338956, 0.3672675559145797, 0.36237228382605946, 0.3574105626187083, 0.3523978637534053, 0.34734965869102996, 0.3422814188924618, 0.33720861581858, 0.33214672093026437, 0.32711120568839397, 0.32211754155384836, 0.3171811999875068, 0.3123176524502488, 0.30754237040295374, 0.3028658706766576, 0.29827885158302303, 0.29376705680386905, 0.28931623002101475, 0.2849121149162792, 0.2805404551714817, 0.27618699446844147, 0.2718374764889773, 0.2674776449149085, 0.2630932434280543, 0.2586700157102335, 0.25419370544326564, 0.24965005630896958, 0.2450248119891645, 0.24030371616566953, 0.23547709109237533, 0.23055357331145895, 0.22554637793716867, 0.2204687200837532, 0.21533381486546083, 0.21015487739654018, 0.20494512279123955, 0.19971776616380768, 0.19448602262849288, 0.1892631072995437, 0.18406223529120858, 0.17889662171773604, 0.1737794816933745, 0.16872403033237252, 0.16374348274897862, 0.15885105405744118, 0.15405995937200861, 0.14938341380692963, 0.1448346324764526, 0.1404268304948259, 0.13617322297629822, 0.13208702503511793, 0.1281814517855335, 0.1244697183417935, 0.12096503981814628, 0.11768063132884042, 0.1146297079881244, 0.11182548491024663, 0.10928117720945568, 0.10701000000000002],
        [0.43322133496365217, 0.4352169939808373, 0.43690015951760636, 0.438277154497445, 0.4393543018438387, 0.440137924480273, 0.4406343453302334, 0.4408498873172051, 0.4407908733646739, 0.440463626396125, 0.4398744693350443, 0.4390297251049171, 0.4379357166292288, 0.4365987668314649, 0.4350251986351109, 0.4332213349636522, 0.43119349874057444, 0.42894801288936296, 0.42649120033350346, 0.42382938399648123, 0.42096888680178174, 0.41791603167289054, 0.4146771415332932, 0.4112585393064751, 0.40766654791592166, 0.40390749028511863, 0.39998768933755113, 0.395913467996705, 0.39169114918606546, 0.3873270558291181, 0.38282751084934846, 0.37820038009911433, 0.3734597011462646, 0.3686210544875197, 0.36370002061960094, 0.35871218003922933, 0.3536731132431259, 0.34859840072801124, 0.3435036229906068, 0.3384043605276333, 0.33331619383581174, 0.3282547034118631, 0.3232354697525086, 0.318274073354469, 0.3133860947144652, 0.30858711432921837, 0.3038877197725581, 0.29927852692674867, 0.29474515875116253, 0.2902732382051729, 0.28584838824815273, 0.2814562318394745, 0.2770823919385112, 0.2727124915046358, 0.2683321534972209, 0.2639270008756395, 0.2594826565992644, 0.2549847436274685, 0.2504188849196246, 0.24577070343510538, 0.24102582213328408, 0.23617447901625455, 0.23122537225699674, 0.22619181507121192, 0.22108712067460123, 0.21592460228286586, 0.2107175731117071, 0.20547934637682602, 0.20022323529392397, 0.1949625530787021, 0.18971061294686156, 0.1844807281141036, 0.17928621179612952, 0.1741403772086404, 0.16905653756733746, 0.164048006087922, 0.15912809598609506, 0.15431012047755807, 0.14960739277801205, 0.14503322610315825, 0.14060093366869794, 0.13632382869033227, 0.1322152243837625, 0.12828843396468975, 0.1245567706488153, 0.12103354765184035, 0.11773207818946609, 0.11466567547739372, 0.11184765273132441, 0.10929132316695946, 0.10701000000000002],
        [0.43485267078026557, 0.4368564481227594, 0.43854652660298066, 0.4399292396723604, 0.4410109207823298, 0.44179790338432023, 0.4422965209297631, 0.44251310687008955, 0.4424539946567309, 0.44212551774111847, 0.4415340095746835, 0.44068580360885745, 0.43958723329507127, 0.43824463208475634, 0.4366643334293441, 0.43485267078026557, 0.4328159775889523, 0.43056058730683533, 0.4280928333853461, 0.425419049275916, 0.42254556842997604, 0.41947872429895766, 0.41622485033429196, 0.4127902799874105, 0.40918134670974443, 0.40540438395272504, 0.4014657251677836, 0.39737170380635123, 0.39312865331985947, 0.3887429071597394, 0.3842207987774224, 0.3795702230762324, 0.37480532076706474, 0.36994179401270694, 0.36499534497594677, 0.3599816758195723, 0.35491648870637144, 0.34981548579913163, 0.34469436926064095, 0.3395688412536872, 0.3344546039410579, 0.32936735948554113, 0.3243228100499249, 0.3193366577969966, 0.31442460488954427, 0.30960235349035586, 0.30488057135114977, 0.3002497885793687, 0.29569550087138585, 0.29120320392357474, 0.2867583934323087, 0.282346565093961, 0.27795321460490524, 0.2735638376615145, 0.2691639299601623, 0.26473898719722205, 0.2602745050690669, 0.2557559792720705, 0.2511689055026061, 0.24649877945704676, 0.2417310968317664, 0.23685600571341528, 0.2318822637497529, 0.22682328097881613, 0.22169246743864165, 0.21650323316726613, 0.21126898820272635, 0.20600314258305902, 0.2007191063463009, 0.19543028953048885, 0.19015010217365935, 0.1848919543138493, 0.17966925598909542, 0.17449541723743434, 0.16938384809690288, 0.1643479586055378, 0.15940115880137573, 0.15455685872245353, 0.14982846840680783, 0.14522939789247538, 0.14077305721749292, 0.13647285641989723, 0.13234220553772502, 0.12839451460901302, 0.12464319367179791, 0.1211016527641165, 0.11778330192400548, 0.11470155118950157, 0.11186981059864154, 0.10930149018946209, 0.10701000000000001],
        [0.4364324986672482, 0.43844315110247134, 0.44013912609202915, 0.4415267562628812, 0.4426123742419867, 0.44340231265630514, 0.44390290413279565, 0.4441204812984177, 0.4440613767801304, 0.4437319232048935, 0.44313845319966605, 0.4422872993914075, 0.4411847944070769, 0.4398372708736343, 0.43825106141803816, 0.4364324986672483, 0.43438791524822384, 0.4321236437879244, 0.42964601691330917, 0.4269613672513372, 0.42407602742896844, 0.42099633007316173, 0.4177286078108766, 0.41427919326907225, 0.4106544190747083, 0.40686061785474376, 0.4029041222361382, 0.39879126484585087, 0.39452837831084087, 0.3901217952580679, 0.3855778483144912, 0.3809044539637673, 0.3761158641163422, 0.3712279145393589, 0.3662564409999604, 0.3612172792652903, 0.3561262651024914, 0.35099923427870666, 0.3458520225610797, 0.3407004657167535, 0.335560399512871, 0.33044765971657564, 0.32537808209501035, 0.32036750241531825, 0.31543175644464255, 0.3105866799501265, 0.3058430298401095, 0.30119124758771715, 0.2966166958072711, 0.292104737113093, 0.28764073411950514, 0.28321004944082906, 0.2787980456913866, 0.27439008548549976, 0.2699715314374901, 0.26552774616167946, 0.2610440922723899, 0.2565059323839431, 0.2518986291106609, 0.24720754506686507, 0.24241804286687763, 0.2375201756027507, 0.23252275827745925, 0.2274392963717084, 0.22228329536620364, 0.21706826074165014, 0.21180769797875312, 0.20651511255821808, 0.2012040099607504, 0.19588789566705508, 0.19058027515783768, 0.18529465391380334, 0.1800445374156574, 0.17484343114410525, 0.16970484057985213, 0.16464227120360336, 0.1596692284960642, 0.15479921793794005, 0.15004574500993614, 0.14542231519275778, 0.14094243396711023, 0.13661960681369895, 0.13246733921322904, 0.12849913664640603, 0.12472850459393506, 0.12116894853652142, 0.11783397395487057, 0.11473708632968767, 0.11189179114167803, 0.10931159387154707, 0.10701000000000002],
        [0.43795864661820294, 0.43997493865593107, 0.441675799475327, 0.4430675497299267, 0.4441565100732664, 0.4449490011588825, 0.4454513436403111, 0.44566985817108823, 0.44561086540475026, 0.4452806859948336, 0.444685640594874, 0.44383204985840813, 0.4427262344389717, 0.44137451499010144, 0.439783212165333, 0.437958646618203, 0.43590713900224737, 0.4336350099710026, 0.43114858017800467, 0.4284541702767897, 0.4255581009208942, 0.42246669276385407, 0.41918626645920576, 0.41572314266048527, 0.4120836420212291, 0.40827408519497305, 0.4043007928352535, 0.40017008559560663, 0.39588828412956883, 0.391461709090676, 0.38689668113246445, 0.3822011309025227, 0.3773894290246489, 0.3724775561166928, 0.367481492796505, 0.36241721968193535, 0.3573007173908344, 0.352147966541052, 0.3469749477504386, 0.34179764163684423, 0.33663202881811927, 0.3314940899121138, 0.32639980553667813, 0.3213651563096622, 0.31640612284891645, 0.3115386857722911, 0.3067736996671145, 0.30210151499862764, 0.29750735620155006, 0.2929764477106009, 0.28849401396049973, 0.28404527938596597, 0.2796154684217186, 0.27518980550247724, 0.27075351506296114, 0.26629182153788955, 0.2617899493619821, 0.2572331229699579, 0.25260656679653637, 0.24789550527643686, 0.24308516284437873, 0.23816549310315419, 0.23314536632784755, 0.22803838196161588, 0.2228581394476164, 0.21761823822900636, 0.21233227774894275, 0.20701385745058282, 0.20167657677708378, 0.19633403517160275, 0.1909998320772969, 0.18568756693732336, 0.18041083919483933, 0.17518324829300197, 0.17001839367496843, 0.16492987478389595, 0.1599312910629416, 0.15503624195526264, 0.15025832690401605, 0.1456111453523592, 0.14110829674344907, 0.136763380520443, 0.13258999612649813, 0.1286017430047715, 0.12481222059842043, 0.12123502835060196, 0.11788376570447326, 0.11477203210319159, 0.11191342698991401, 0.10932154980779778, 0.10701],
        [0.4394289426267325, 0.4414496465190974, 0.44315438824344894, 0.44454946553441554, 0.4456411761266255, 0.44643581775470736, 0.44693968815328966, 0.4471590850570005, 0.4471003062004684, 0.446769649318322, 0.44617341214518985, 0.44531789241569986, 0.4442093878644806, 0.44285419622616085, 0.4412586152353685, 0.43942894262673254, 0.43737147613488075, 0.4350925134944422, 0.4325983524400451, 0.42989529070631766, 0.42698962602788837, 0.42388765613938584, 0.42059567877543824, 0.41711999167067426, 0.41346689255972224, 0.4096426791772105, 0.4056536492577674, 0.40150610053602176, 0.39720633074660144, 0.3927606376241353, 0.38817531890325163, 0.3834583120333028, 0.3786241133225371, 0.3736888587939266, 0.36866868447044365, 0.36357972637506064, 0.35843812053074975, 0.35326000296048304, 0.34806150968723276, 0.34285877673397125, 0.33766794012367063, 0.33250513587930325, 0.32738650002384145, 0.322328168580257, 0.3173462775715225, 0.31245696302061027, 0.30767118525984133, 0.3029792018589339, 0.29836609469695485, 0.29381694565297123, 0.2893168366060503, 0.28485084943525874, 0.280404066019664, 0.2759615682383329, 0.2715084379703325, 0.2670297570947299, 0.2625106074905922, 0.2579360710369864, 0.25329122961297945, 0.24856116509763845, 0.24373095937003064, 0.23879046263351877, 0.23374859838864953, 0.2286190584602655, 0.22341553467320913, 0.21815171885232323, 0.21284130282245012, 0.20749797840843232, 0.20213543743511272, 0.1967673717273336, 0.19140747310993744, 0.18606943340776705, 0.18076694444566482, 0.17551369804847328, 0.1703233860410352, 0.1652097002481929, 0.16018633249478897, 0.15526697460566613, 0.15046531840566674, 0.14579505571963342, 0.14126987837240876, 0.13690347818883536, 0.13270954699375562, 0.1287017766120123, 0.12489385886844778, 0.12129948558790468, 0.11793234859522557, 0.11480613971525301, 0.11193455077282952, 0.10933127359279764, 0.10701],
        [0.44084121468643983, 0.442865110427929, 0.4445727338869705, 0.4459703491372672, 0.4470642202525212, 0.4478606113064353, 0.44836578637271185, 0.4485860095250537, 0.4485275448371631, 0.4481966563827428, 0.4475996082354955, 0.44674266446912353, 0.4456320891573293, 0.44427414637381574, 0.44267510019228495, 0.4408412146864399, 0.43877875392998267, 0.4364939819966163, 0.4339931629600432, 0.43128256089396555, 0.4283684398720865, 0.42525706396810825, 0.4219546972557333, 0.4184676038086643, 0.4148020477006039, 0.41096429300525456, 0.40696060379631865, 0.40279724414749907, 0.39848047813249804, 0.39401656982501837, 0.3894117832987625, 0.3846740554969111, 0.3798180148405588, 0.3748599626202777, 0.3698162001266403, 0.3647030286502191, 0.3595367494815868, 0.3543336639113155, 0.349110073229978, 0.3438822787281465, 0.3386665816963935, 0.33347928342529176, 0.32833668520541354, 0.3232550883273312, 0.3182507940816173, 0.31334010375884463, 0.30853409104596746, 0.30382291921546994, 0.2991915239362178, 0.2946248408770772, 0.29010780570691447, 0.2856253540945955, 0.28116242170898625, 0.2767039442189529, 0.27223485729336155, 0.2677400966010782, 0.26320459781096905, 0.2586132965919, 0.2539511286127372, 0.2492030295423466, 0.24435393504959452, 0.23939358861273777, 0.23433096494759717, 0.2291798465793844, 0.22395401603331122, 0.2186672558345894, 0.21333334850843055, 0.20796607658004648, 0.20257922257464886, 0.1971865690174495, 0.19180189843366005, 0.18643899334849212, 0.18111163628715768, 0.17583360977486823, 0.17061869633683557, 0.16548067849827144, 0.16043333878438754, 0.1554904597203956, 0.1506658238315073, 0.14597321364293442, 0.14142641167988862, 0.13703920046758164, 0.13282536253122523, 0.1287986803960311, 0.12497293658721091, 0.12136191362997649, 0.11797939404953946, 0.11483916037111158, 0.11195499511990456, 0.10934068082113012, 0.10701],
        [0.4421932907909275, 0.444219166118384, 0.4459286778964666, 0.44732804599940007, 0.44842349030140966, 0.4492212306767205, 0.44972748699955784, 0.44994847914414654, 0.449890426984712, 0.44955955039547923, 0.4489620692506735, 0.4481042034245197, 0.4469921727912431, 0.44563219722506875, 0.44403049660022176, 0.4421932907909275, 0.4401267996714109, 0.437837243115897, 0.43533084099861113, 0.4326138131937783, 0.4296923795756236, 0.4265727600183723, 0.4232611743962494, 0.41976384258348004, 0.4160869844542896, 0.41223681988290284, 0.40821956874354515, 0.4040414509104415, 0.39970868625781697, 0.3952274946598969, 0.39060409599090634, 0.38584641943415177, 0.38096923140926614, 0.3759890076449634, 0.37092222386995766, 0.36578535581296334, 0.36059487920269434, 0.3553672697678648, 0.35011900323718925, 0.3448665553393815, 0.3396264018031559, 0.33441501835722653, 0.3292488807303075, 0.3241444646511132, 0.31911824584835735, 0.31418670005075466, 0.30936102145316957, 0.304631278115069, 0.29998225656207056, 0.2953987433197916, 0.29086552491385, 0.286367387869863, 0.28188911871344813, 0.27741550397022297, 0.2729313301658053, 0.2684213838258121, 0.2638704514758613, 0.25926331964157034, 0.2545847748485566, 0.24981960362243774, 0.24495259248883133, 0.23997337545970426, 0.23489097649242208, 0.22971926703069956, 0.22447211851825163, 0.21916340239879323, 0.21380699011603915, 0.2084167531137044, 0.20300656283550383, 0.19759029072515236, 0.1921818082263649, 0.18679498678285636, 0.18144369783834155, 0.17614181283653543, 0.17090320322115293, 0.16574174043590895, 0.16067129592451834, 0.15570574113069602, 0.15085894749815687, 0.14614478647061582, 0.14157712949178783, 0.13716984800538767, 0.13293681345513028, 0.12889189728473063, 0.12504897093790357, 0.12142190585836397, 0.11802457348982683, 0.11487084527600692, 0.11197459266061921, 0.1093496870873786, 0.10701],
        [0.44348299893379856, 0.44550964932642145, 0.44722006176251217, 0.44862040158173355, 0.4497168341237481, 0.45051552472821865, 0.45102263873480797, 0.45124434148317855, 0.45118679831299313, 0.45085617456391475, 0.45025863557560586, 0.44940034668772916, 0.4482874732399473, 0.44692618057192324, 0.4453226340233193, 0.44348299893379867, 0.44141344064302357, 0.43912012449065685, 0.4366092158163616, 0.4338868799598, 0.4309592822606352, 0.4278325880585295, 0.4245129626931457, 0.42100657150414666, 0.4173195798311952, 0.4134581530139537, 0.4094284563920851, 0.4052366553052521, 0.40088891509311714, 0.39639140109534315, 0.3917502786515929, 0.38697346198582855, 0.3820758608592113, 0.3770741339172013, 0.3719849398052593, 0.3668249371688458, 0.3616107846534216, 0.3563591409044468, 0.35108666456738225, 0.3458100142876884, 0.3405458487108259, 0.33531082648225513, 0.3301216062474368, 0.32499484665183137, 0.3199472063408992, 0.3149953439601012, 0.3101505809091247, 0.30540288960456524, 0.30073690521724533, 0.2961372629179877, 0.2915885978776146, 0.287075545266949, 0.28258274025681307, 0.2780948180180293, 0.27359641372142063, 0.26907216253780925, 0.26450669963801776, 0.2598846601928687, 0.25519067937318485, 0.2504093923497883, 0.2455254342935021, 0.2405283275933117, 0.23542714351085628, 0.23023584052593818, 0.22496837711835974, 0.2196387117679233, 0.21426080295443112, 0.20884860915768563, 0.2034160888574892, 0.19797720053364407, 0.19254590266595267, 0.1871361537342173, 0.18176191221824023, 0.17643713659782387, 0.17117578535277056, 0.16599181696288273, 0.1608991899079625, 0.15591186266781237, 0.15104379372223464, 0.1463089415510316, 0.14172126463400567, 0.13729472145095914, 0.13304327048169434, 0.1289808702060137, 0.12512147910371949, 0.12147905565461399, 0.1180675583384996, 0.11490094563517869, 0.11199317602445356, 0.10935820798612655, 0.10701000000000001],
        [0.44470816710865557, 0.4467343957879994, 0.44844472697568233, 0.4498452613451864, 0.4509420995699931, 0.4517413423235845, 0.4522490902794423, 0.45247144411104834, 0.4524145044918844, 0.45208437209543273, 0.4514871475951747, 0.45062893166459234, 0.44951582497716736, 0.4481539282063817, 0.44654934202571717, 0.44470816710865557, 0.4426365041286787, 0.4403404537592685, 0.4378261166739068, 0.4350995935460753, 0.43216698504925594, 0.42903439185693043, 0.425707914642581, 0.4221936540796888, 0.41849771084173626, 0.41462618560220493, 0.41058517903457675, 0.40638079181233344, 0.402019124608957, 0.39750627809792916, 0.3928483529527316, 0.38805324129274515, 0.3831360010209461, 0.3781134814862089, 0.3730025320374083, 0.3678200020234197, 0.3625827407931176, 0.3573075976953768, 0.3520114220790723, 0.346711063293079, 0.34142337068627154, 0.33616519360752495, 0.3309533814057143, 0.32580478342971403, 0.32073624902839903, 0.31576462755064455, 0.3109013738415096, 0.3061363647307922, 0.30145408254447426, 0.29683900960853815, 0.29227562824896636, 0.28774842079174073, 0.2832418695628438, 0.27874045688825777, 0.27422866509396476, 0.2696909765059471, 0.26511187345018705, 0.2604758382526669, 0.2557673532393687, 0.25097090073627487, 0.24607096306936777, 0.24105694943245304, 0.2359379764906314, 0.23072808777682713, 0.22544132682396464, 0.22009173716496797, 0.2146933623327616, 0.20926024586026964, 0.20380643128041653, 0.19834596212612646, 0.1928928819303237, 0.1874612342259326, 0.18206506254587743, 0.17671841042308234, 0.17143532139047177, 0.16622983898096996, 0.16111600672750112, 0.15610786816298955, 0.15121946682035958, 0.14646484623253547, 0.14185804993244144, 0.13741312145300186, 0.13314410432714088, 0.12906504208778302, 0.12518997826785233, 0.12153295640027316, 0.11810802001796981, 0.11492921265386653, 0.11201057784088764, 0.10936615911195734, 0.10701],
        [0.4458666233091015, 0.4478912412390767, 0.4496005150265524, 0.4510004707506777, 0.4520971344906016, 0.4528965323254731, 0.45340469033444136, 0.4536276345966552, 0.45357139119126405, 0.45324198619741674, 0.4526454456942625, 0.4517877957609501, 0.45067506247662875, 0.44931327192044745, 0.4477084501715554, 0.4458666233091015, 0.4437938174122348, 0.44149605856010443, 0.43897937283185945, 0.4362497863066487, 0.4333133250636217, 0.43017601518192694, 0.42684388274071394, 0.42332295381913154, 0.4196192544963288, 0.41573881085145475, 0.4116876489636584, 0.40747179491208907, 0.40309727477589546, 0.39857011463422687, 0.39389634056623213, 0.3890838154957058, 0.38414774972502286, 0.37910519040120355, 0.3739731846712683, 0.36876877968223754, 0.3635090225811315, 0.35821096051497037, 0.35289164063077477, 0.34756811007556493, 0.3422574159963613, 0.33697660554018377, 0.33174272585405334, 0.3265728240849899, 0.3214839473800138, 0.3164931428861456, 0.3116120046780016, 0.30683031454058374, 0.3021324011864893, 0.29750259332831636, 0.2929252196786626, 0.28838460895012585, 0.2838650898553038, 0.27935099110679423, 0.2748266414171949, 0.27027636949910355, 0.26568450406511807, 0.2610353738278362, 0.2563133074998556, 0.25150263379377397, 0.2465876814221894, 0.2415577453960215, 0.2364219859194793, 0.23119452949509367, 0.22588950262539553, 0.2205210318129159, 0.21510324356018568, 0.20965026436973586, 0.2041762207440975, 0.19869523918580137, 0.19322144619737863, 0.1877689682813601, 0.18235193194027682, 0.1769844636766597, 0.1716806899930398, 0.16645473739194802, 0.16132073237591524, 0.15629280144747257, 0.15138507110915086, 0.1466116678634812, 0.1419867182129944, 0.1375243486602215, 0.1332386857076935, 0.1291438558579413, 0.12525398561349593, 0.1215832014768883, 0.11814562995064934, 0.11495539753731011, 0.11202663073940146, 0.10937345605945444, 0.10701000000000001],
        [0.44695619552873894, 0.44897802141561166, 0.4506852674056971, 0.4520838752591263, 0.45317978673603004, 0.4539789435965394, 0.45448728760078516, 0.4547107605088982, 0.4546553040810096, 0.4543268600772502, 0.4537313702577511, 0.452874776382643, 0.4517630202120566, 0.45040204350612334, 0.4487977880249738, 0.44695619552873894, 0.44488320777754964, 0.442584766531537, 0.44006681355083177, 0.4373352905955648, 0.4343961394258673, 0.43125530180186994, 0.4279187194837037, 0.4243923342314994, 0.42068208780538824, 0.4167939219655008, 0.41273377847196824, 0.40850759908492135, 0.4041213255644911, 0.39958089967080834, 0.394892263164004, 0.39006324273551396, 0.38510920480199357, 0.38004740071140297, 0.3748950818117023, 0.369669499450852, 0.3643879049768122, 0.3590675497375432, 0.3537256850810051, 0.3483795623551583, 0.3430464329079628, 0.3377435480873789, 0.3324881592413671, 0.32729751771788723, 0.3221888748648996, 0.3171794820303647, 0.3122810778462775, 0.3074833500807734, 0.30277047378602245, 0.29812662401419504, 0.29353597581746116, 0.2889827042479915, 0.28445098435795585, 0.2799249911995245, 0.2753888998248679, 0.2708268852861561, 0.2662231226355594, 0.261561786925248, 0.2568270532073922, 0.25200309653416203, 0.24707409195772792, 0.24202921990291046, 0.23687768228513184, 0.23163368639246473, 0.2263114395129816, 0.22092514893475543, 0.2154890219458586, 0.2100172658343637, 0.20452408788834356, 0.1990236953958707, 0.19353029564501772, 0.18805809592385736, 0.18262130352046216, 0.17723412572290484, 0.17191076981925793, 0.16666544309759415, 0.16151235284598608, 0.15646570635250642, 0.15153971090522772, 0.14674857379222267, 0.14210650230156385, 0.13762770372132396, 0.13332638533957555, 0.1292167544443914, 0.12531301832384398, 0.12162938426600606, 0.11818005955895014, 0.114979251490749, 0.11204116734947515, 0.10938001442320128, 0.10701],
        [0.4479747117611708, 0.4499925720535628, 0.4516968256036915, 0.45309332033145117, 0.4541879041567355, 0.4549864249994385, 0.45549473077945407, 0.45571866941667644, 0.45566408883099935, 0.45533683694231686, 0.454742761670523, 0.4538877109355117, 0.4527775326571768, 0.4514180747554124, 0.44981518515011243, 0.44797471176117093, 0.4459025025084817, 0.44360440531193884, 0.4410862680914363, 0.4383539387668682, 0.43541326525812823, 0.4322700954851105, 0.42893027736770895, 0.42539965882581765, 0.4216840877793305, 0.41778941214814147, 0.41372147985214447, 0.4094861388112335, 0.40508923694530263, 0.4005366221742457, 0.3958341424179568, 0.3909895811529736, 0.3860184640824104, 0.3809382524660244, 0.3757664075635737, 0.37052039063481607, 0.36521766293950925, 0.35987568573741086, 0.3545119202882787, 0.3491438278518707, 0.34378886968794453, 0.33846450705625786, 0.3331882012165687, 0.3279774134286345, 0.32284960495221326, 0.31782223704706264, 0.31290719777401427, 0.3080940823981951, 0.3033669129858058, 0.2987097116030472, 0.2941065003161201, 0.2895413011912252, 0.28499813629456316, 0.2804610276923349, 0.2759139974507411, 0.2713410676359825, 0.26672626031425994, 0.26205359755177404, 0.2573071014147257, 0.25247079396931554, 0.24752869728174454, 0.2424698773720129, 0.23730357607532074, 0.23204407918066736, 0.2267056724770523, 0.22130264175347517, 0.21584927279893545, 0.21035985140243266, 0.20484866335296645, 0.19932999443953625, 0.19381813045114166, 0.18832735717678215, 0.18287196040545725, 0.17746622592616648, 0.1721244395279095, 0.1668608869996858, 0.16168985413049472, 0.15662562670933605, 0.1516824905252091, 0.14687473136711363, 0.14221663502404902, 0.13772248728501485, 0.13340657393901062, 0.12928318077503598, 0.12536659358209032, 0.12167109814917322, 0.11821098026528422, 0.11500052571942292, 0.1120540203005887, 0.10938574979778123, 0.10701000000000001],
        [0.4489200000000001, 0.450932728888889, 0.4526330311111112, 0.45402665142857157, 0.45511933460317483, 0.4559168253968255, 0.4564248685714287, 0.45664920888888905, 0.45659559111111114, 0.45626976000000014, 0.4556774603174604, 0.4548244368253969, 0.45371643428571434, 0.45235919746031755, 0.4507584711111113, 0.4489200000000001, 0.4468495288888889, 0.44455280253968255, 0.4420355657142857, 0.4393035631746032, 0.43636253968253963, 0.4332182399999999, 0.42987640888888895, 0.42634279111111106, 0.42262313142857144, 0.4187231746031746, 0.4146486653968254, 0.4104053485714286, 0.4059989688888889, 0.40143527111111105, 0.39671999999999996, 0.3918608888888888, 0.38687362539682546, 0.38177588571428567, 0.376585346031746, 0.37131968253968245, 0.36599657142857145, 0.3606336888888889, 0.3552487111111111, 0.3498593142857143, 0.34448317460317457, 0.33913796825396825, 0.33384137142857145, 0.3286110603174604, 0.32346471111111114, 0.31842000000000004, 0.31348896888888894, 0.3086611225396827, 0.3039203314285715, 0.29925046603174604, 0.29463539682539686, 0.29005899428571436, 0.28550512888888896, 0.2809576711111112, 0.27640049142857154, 0.2718174603174604, 0.2671924482539683, 0.26250932571428576, 0.2577519631746033, 0.2529042311111111, 0.2479500000000001, 0.24287822222222227, 0.23769817777777782, 0.23242422857142864, 0.22707073650793655, 0.22165206349206357, 0.21618257142857147, 0.21067662222222228, 0.20514857777777779, 0.19961280000000006, 0.19408365079365084, 0.1885754920634921, 0.18310268571428578, 0.17767959365079372, 0.1723205777777778, 0.16704000000000008, 0.1618522222222223, 0.15677160634920642, 0.15181251428571435, 0.146989307936508, 0.14231634920634928, 0.13780799999999999, 0.13347862222222223, 0.1293425777777778, 0.1254142285714286, 0.12170793650793657, 0.11823806349206352, 0.11501897142857148, 0.11206502222222224, 0.10939057777777779, 0.10701000000000002],
        [0.44978988823882915, 0.45179632765754824, 0.4534917254185306, 0.4548817140114061, 0.4559719259258044, 0.4567679936513552, 0.4572755496776889, 0.4575002264944348, 0.4574476565912228, 0.45712347245768314, 0.4565333065834453, 0.45568279145813934, 0.4545775595713948, 0.4532232434128416, 0.45162547547210985, 0.44978988823882926, 0.4477221142026293, 0.44542778585314047, 0.4429125356799922, 0.4401819961728143, 0.4372417998212368, 0.43409757911488933, 0.43075496654340184, 0.42721959459640435, 0.4234970957635266, 0.41959310253439813, 0.4155132473986491, 0.4112631628459092, 0.4068484813658084, 0.4022748354479763, 0.3975478575820431, 0.392675224084063, 0.3876727865757907, 0.382558440505404, 0.3773500813210821, 0.3720656044710038, 0.36672290540334784, 0.36133987956629277, 0.3559344224080175, 0.3505244293767006, 0.34512779592052095, 0.33976241748765723, 0.33444618952628846, 0.329197007484593, 0.32403276681074966, 0.3189713629529373, 0.3140249956185784, 0.30918308155206964, 0.30442934175705144, 0.29974749723716443, 0.2951212689960492, 0.2905343780373464, 0.2859705453646961, 0.28141349198173926, 0.27684693889211615, 0.27225460709946725, 0.26762021760743326, 0.2629274914196546, 0.2581601495397718, 0.2533019129714252, 0.2483365027182556, 0.24325275887243156, 0.23805999788023488, 0.23277265527647562, 0.22740516659596366, 0.22197196737350905, 0.2164874931439217, 0.21096617944201174, 0.2054224618025891, 0.19987077576046378, 0.1943255568504457, 0.1888012406073449, 0.18331226256597138, 0.1778730582611351, 0.17249806322764608, 0.1672017130003143, 0.16199844311394979, 0.15690268910336247, 0.15192888650336234, 0.14709147084875945, 0.14240487767436372, 0.13788354251498516, 0.13354190090543377, 0.12939438838051961, 0.12545544047505258, 0.12173949272384268, 0.11826098066169993, 0.1150343398234343, 0.11207400574385575, 0.10939441395777434, 0.10701000000000001],
        [0.45058220447126107, 0.4525812040954995, 0.45427075001652517, 0.455656353540874, 0.4567435259750812, 0.457537778625683, 0.45804462279921504, 0.45826956980221284, 0.4582181309412125, 0.45789581752274966, 0.45730814085336, 0.45646061223957934, 0.4553587429879432, 0.4540080444049878, 0.45241402779724843, 0.45058220447126107, 0.4485180857335614, 0.4462271828906852, 0.44371500724916824, 0.44098707011554616, 0.4380488827963549, 0.4349059565981299, 0.4315638028274073, 0.42802793279072254, 0.42430385779461166, 0.4203970891456102, 0.41631313815025384, 0.41205751611507857, 0.4076357343466199, 0.4030533041514138, 0.39831573683599586, 0.3934306448793007, 0.38841404544985825, 0.383284056888597, 0.3780587975364457, 0.372756385734333, 0.3673949398231877, 0.3619925781439382, 0.3565674190375133, 0.35113758084484165, 0.3457211819068519, 0.34033634056447276, 0.3350011751586329, 0.32973380403026104, 0.3245523455202855, 0.31947491796963534, 0.3145138823907595, 0.3096585704821897, 0.3048925566139775, 0.3001994151561754, 0.2955627204788351, 0.2909660469520086, 0.28639296894574795, 0.28182706083010517, 0.2772518969751322, 0.27265105175088095, 0.2680080995274036, 0.26330661467475214, 0.25853017156297836, 0.2536623445621343, 0.24868670804227214, 0.24359199174153406, 0.23838754687042382, 0.23308788000753547, 0.22770749773146284, 0.2222609066208002, 0.2167626132541415, 0.21122712421008072, 0.20566894606721203, 0.20010258540412937, 0.19454254879942676, 0.18900334283169823, 0.18349947407953787, 0.17804544912153966, 0.17265577453629766, 0.16734495690240594, 0.1621275027984584, 0.15701791880304922, 0.15203071149477235, 0.14718038745222187, 0.14248145325399175, 0.13794841547867606, 0.13359578070486888, 0.12943805551116422, 0.12548974647615604, 0.12176536017843843, 0.11827940319660543, 0.11504638210925106, 0.11208080349496932, 0.10939717393235428, 0.10701000000000002],
        [0.45129477669089857, 0.4532851939387011, 0.4549679463956699, 0.4563484154778939, 0.4574319826014621, 0.45822402918246363, 0.4587299366369874, 0.4589550863811226, 0.45890485983095813, 0.4585846384025833, 0.4579998035120868, 0.457155736575558, 0.4560578190090856, 0.4547114322287589, 0.4531219576506668, 0.4512947766908986, 0.449235270765543, 0.44694882129068925, 0.4444408096824263, 0.44171661735684314, 0.43878162573002905, 0.43564121621807284, 0.4323007702370637, 0.4287656692030905, 0.4250412945322426, 0.4211330276406087, 0.417046249944278, 0.4127863428593395, 0.4083586878018822, 0.40376866618799534, 0.3990216594337676, 0.3941252094154051, 0.38909549984958036, 0.38395087491308205, 0.37870967878269973, 0.37339025563522266, 0.3680109496474399, 0.36259010499614064, 0.357146065858114, 0.35169717641014925, 0.3462617808290355, 0.34085822329156207, 0.3355048479745182, 0.3302199990546928, 0.32502202070887504, 0.31992925711385445, 0.3149542336331094, 0.31008620037687673, 0.30530858864208216, 0.3006048297256519, 0.29595835492451195, 0.2913525955355885, 0.2867709828558075, 0.28219694818209473, 0.2776139228113767, 0.2730053380405791, 0.268354625166628, 0.2636452154864497, 0.25886054029697, 0.25398403089511495, 0.24899911857781076, 0.24389442524842297, 0.23867933523607632, 0.23336842347633502, 0.22797626490476328, 0.2225174344569255, 0.21700650706838584, 0.2114580576747086, 0.20588666121145813, 0.20030689261419862, 0.1947333268184945, 0.18918053875990978, 0.18366310337400898, 0.17819559559635617, 0.17279259036251576, 0.1674686626080521, 0.16223838726852924, 0.15711633927951163, 0.15211709357656344, 0.147255225095249, 0.1425453087711326, 0.1380019195397785, 0.13363963233675094, 0.12947302209761427, 0.12551666375793266, 0.12178513225327048, 0.11829300251919196, 0.11505484949126138, 0.112085248105043, 0.10939877329610112, 0.10701000000000001],
        [0.45192543289134446, 0.4539061329231116, 0.45558115604653987, 0.4569557452833851, 0.4580351436554038, 0.4588245941843522, 0.4593293398919865, 0.45955462380006284, 0.4595056889303376, 0.4591877783045673, 0.45860613494450775, 0.45776600187191574, 0.456672622108547, 0.45533123867615805, 0.4537470945965051, 0.45192543289134457, 0.4498714965824323, 0.4475905286915251, 0.4450877722403789, 0.44236847025074993, 0.4394378657443948, 0.43630120174306936, 0.4329637212685301, 0.42943066734253316, 0.42570728298683513, 0.4217988112231918, 0.41771049507335967, 0.41344757755909506, 0.409015301702154, 0.4044189105242929, 0.3996636470472682, 0.3947569758331805, 0.3897152476055089, 0.38455703462807683, 0.37930090916470777, 0.37396544347922567, 0.3685692098354538, 0.36313078049721564, 0.357668727728335, 0.3522016237926353, 0.3467480409539399, 0.34132655147607277, 0.3359557276228571, 0.3306541416581167, 0.3254403658456748, 0.32033297244935544, 0.3153446537733051, 0.3104645822829645, 0.30567605048409724, 0.30096235088246703, 0.2963067759838379, 0.2916926182939736, 0.2871031703186377, 0.2825217245635942, 0.2779315735346068, 0.27331600973743914, 0.2686583256778553, 0.2639418138616189, 0.25914976679449386, 0.2542654769822436, 0.24927223693063233, 0.2441585638119915, 0.23893387346492423, 0.23361280639460147, 0.22821000310619421, 0.2227401041048734, 0.21721774989580991, 0.21165758098417478, 0.20607423787513907, 0.20048236107387354, 0.1948965910855493, 0.18933156841533727, 0.18380193356840835, 0.17832232704993353, 0.1729073893650838, 0.16757176101903012, 0.1623300825169434, 0.15719699436399465, 0.15218713706535472, 0.14731515112619478, 0.14259567705168558, 0.1380433553469982, 0.1336728265173035, 0.12949873106777257, 0.1255357095035763, 0.1217984023298856, 0.11830145005187151, 0.11505949317470494, 0.11208717220355686, 0.10939912764359824, 0.10701000000000001],
        [0.45247200106620145, 0.4544418567846897, 0.45610822045971006, 0.45747618841826665, 0.4585508569873631, 0.45933732249400366, 0.45984068126519223, 0.4600660296279327, 0.4600184639092289, 0.45970308043608515, 0.45912497553550524, 0.4582892455344932, 0.4572009867600528, 0.45586529553918803, 0.4542872681989029, 0.4524720010662015, 0.4504245904680875, 0.4481501327315653, 0.44565372418363847, 0.442940461151311, 0.44001543996158715, 0.43688375694147047, 0.43355050841796516, 0.4300207907180753, 0.4262997001688047, 0.4223923330971573, 0.41830378583013705, 0.4140391546947479, 0.4096035360179939, 0.4050020261268789, 0.400239721348407, 0.3953240022734304, 0.3902713865481961, 0.3851006760827987, 0.3798306727873331, 0.3744801785718947, 0.3690679953465783, 0.36361292502147896, 0.35813376950669173, 0.35264933071231147, 0.3471784105484333, 0.3417398109251521, 0.3363523337525632, 0.3310347809407614, 0.3258059543998415, 0.3206846560398989, 0.3156837472390235, 0.3107923272472867, 0.30599355478275475, 0.30127058856349376, 0.29660658730757045, 0.2919847097330511, 0.28738811455800184, 0.28279996050048917, 0.2782034062785795, 0.273581610610339, 0.26891773221383414, 0.2641949298071313, 0.25939636210829675, 0.2545051878353968, 0.249504565706498, 0.2443829118511328, 0.23914967204469934, 0.2338195494740619, 0.2284072473260848, 0.22292746878763237, 0.21739491704556888, 0.2118242952867588, 0.20623030669806636, 0.20062765446635594, 0.1950310417784918, 0.18945517182133828, 0.1839147477817598, 0.17842447284662058, 0.172999050202785, 0.16765318303711735, 0.16240157453648202, 0.15725892788774323, 0.1522399462777654, 0.1473593328934129, 0.14263179092154993, 0.13807202354904086, 0.13369473396275008, 0.1295146253495419, 0.12554640089628055, 0.12180476378983049, 0.11830441721705597, 0.11506006436482132, 0.11208640841999092, 0.10939815256942902, 0.10701],
        [0.45293230920907246, 0.45489020125939367, 0.45654698112575565, 0.4579075903434572, 0.45897697044779673, 0.4597600629740731, 0.4602618094575851, 0.4604871514336311, 0.46044103043750995, 0.4601283880045205, 0.4595541656699614, 0.45872330496913105, 0.45764074743732824, 0.45631143460985185, 0.4547403080220003, 0.4529323092090725, 0.45089237970636675, 0.4486254610491822, 0.4461364947728173, 0.4434304224125707, 0.44051218550374127, 0.4373867255816275, 0.434058984181528, 0.4305339028387417, 0.4268164230885673, 0.42291148646630333, 0.41882403450724837, 0.41455900874670115, 0.41012135071996053, 0.4055160019623251, 0.4007479040090935, 0.39582434687695894, 0.39076201450819403, 0.38557993932646495, 0.3802971537554389, 0.3749326902187825, 0.3695055811401627, 0.364034858943246, 0.35853955605169957, 0.35303870488918976, 0.34755133787938364, 0.34209648744594795, 0.33669318601254955, 0.33136046600285507, 0.32611735984053136, 0.3209828999492452, 0.3159701184579415, 0.3110680463166771, 0.30625971418078657, 0.30152815270560507, 0.29685639254646745, 0.29222746435870844, 0.28762439879766294, 0.28303022651866583, 0.27842797817705195, 0.27380068442815614, 0.2691313759273133, 0.26440308332985835, 0.259598837291126, 0.25470166846645115, 0.24969460751116868, 0.24456597378474018, 0.23932524146313347, 0.23398717342644337, 0.22856653255476425, 0.223078081728191, 0.217536583826818, 0.21195680173074, 0.2063534983200517, 0.20074143647484763, 0.19513537907522238, 0.18955008900127066, 0.18400032913308703, 0.17850086235076612, 0.17306645153440262, 0.16771185956409104, 0.1624518493199261, 0.15730118368200244, 0.15227462553041457, 0.14738693774525718, 0.14265288320662486, 0.13808722479461233, 0.1337047253893141, 0.12952014787082491, 0.12554825511923928, 0.12180381001465188, 0.11830157543715733, 0.11505631426685024, 0.11208278938382524, 0.10939576366817694, 0.10701],
        [0.4533041853135601, 0.455249002083182, 0.4568952795352516, 0.45824779651987574, 0.45931133188716144, 0.4600906644872156, 0.4605905731701453, 0.4608158367860574, 0.46077123418505894, 0.4604615442172568, 0.4598915457327583, 0.4590660175816701, 0.4579897386140991, 0.4566674876801525, 0.4551040436299372, 0.45330418531356015, 0.4512726915811282, 0.44901434128274864, 0.4465339132685282, 0.4438361863885738, 0.4409259394929927, 0.43780795143189155, 0.4344870010553775, 0.4309678672135576, 0.42725532875653877, 0.42335416453442787, 0.41926915339733184, 0.4150050741953579, 0.4105667057786128, 0.4059588269972036, 0.40118621670123733, 0.39625606778457, 0.39118522931605476, 0.38599296440829356, 0.38069853617388855, 0.3753212077254419, 0.36988024217555593, 0.36439490263683244, 0.3588844522218738, 0.3533681540432819, 0.3478652712136591, 0.3423950668456075, 0.3369768040517293, 0.33162974594462635, 0.3263731556369009, 0.3212262962411553, 0.31620237185773614, 0.3112903505379694, 0.3064731413209251, 0.30173365324567397, 0.2970547953512866, 0.29241947667683316, 0.2878106062613841, 0.28321109314401, 0.27860384636378127, 0.27397177495976827, 0.26929778797104154, 0.26456479443667147, 0.25975570339572845, 0.2548534238872829, 0.24984086495040547, 0.24470625403170673, 0.23945909220795844, 0.23411419896347277, 0.22868639378256178, 0.2231904961495376, 0.21764132554871235, 0.21205370146439792, 0.20644244338090664, 0.20082237078255047, 0.19520830315364154, 0.18961505997849193, 0.18405746074141377, 0.17855032492671905, 0.17310847201871996, 0.16774672150172854, 0.1624798928600569, 0.15732280557801712, 0.15229027913992124, 0.14739713303008145, 0.14265818673280978, 0.1380882597324183, 0.1337021715132192, 0.12951474155952444, 0.12554078935564622, 0.12179513438589651, 0.11829259613458751, 0.1150479940860313, 0.11207614772453989, 0.10939187653442542, 0.10701],
        [0.4535854573732675, 0.45551609499201356, 0.4571509571787733, 0.4584946524084416, 0.4595517891559141, 0.4603269758960863, 0.46082482110385325, 0.46104993325411053, 0.46100692082175354, 0.4607003922816778, 0.4601349561087784, 0.45931522077795095, 0.4582457947640908, 0.4569312865420931, 0.45537630458685363, 0.4535854573732675, 0.4515633533762301, 0.449314601070637, 0.4468438089313835, 0.44415558543336475, 0.4412545390514766, 0.438145278260614, 0.43483241153567265, 0.4313205473515477, 0.4276142941831348, 0.4237182605053291, 0.419637054793026, 0.4153752855211211, 0.41093756116450947, 0.4063284901980867, 0.40155268109674824, 0.3966172231370673, 0.3915391288023306, 0.38633789137750174, 0.3810330041475455, 0.3756439603974258, 0.37019025341210726, 0.36469137647655386, 0.35916682287573004, 0.35363608589460005, 0.3481186588181281, 0.34263403493127853, 0.3372017075190157, 0.33184116986630374, 0.32657191525810697, 0.32141343697938973, 0.3163791118660845, 0.3114578509579974, 0.30663244884590235, 0.3018857001205737, 0.29720039937278564, 0.2925593411933126, 0.28794532017292856, 0.2833411309024078, 0.27872956797252463, 0.2740934259740531, 0.2694154994977676, 0.2646785831344422, 0.25986547147485134, 0.25495895910976885, 0.2499418406299694, 0.24480225701092573, 0.2395497347669061, 0.23419914679687742, 0.22876536599980674, 0.22326326527466092, 0.21770771752040707, 0.21211359563601198, 0.20649577252044282, 0.20086912107266644, 0.19524851419164982, 0.18964882477635994, 0.18408492572576377, 0.17857168993882827, 0.1731239903145204, 0.16775669975180715, 0.16248469114965547, 0.15732283740703235, 0.15228601142290468, 0.14738908609623957, 0.1426469343260039, 0.13807442901116462, 0.13368644305068875, 0.12949784934354328, 0.12552352078869508, 0.12177833028511119, 0.11827715073175854, 0.11503485502760416, 0.11206631607161494, 0.1093864067627579, 0.10701],
        [0.45377395338179716, 0.4556893157218468, 0.4573118555468954, 0.4586460034700736, 0.4596961901045115, 0.4604668460633399, 0.4609624019596891, 0.4611872884066896, 0.4611459360174719, 0.4608427754051665, 0.46028223718290384, 0.45946875196381426, 0.45840675036102835, 0.45710066298767654, 0.4555549204568893, 0.4537739533817971, 0.4517621923755304, 0.4495240680512197, 0.44706401102199544, 0.4443864519009881, 0.44149582130132803, 0.43839654983614584, 0.43509306811857196, 0.4315898067617368, 0.42789119637877093, 0.4240016675828048, 0.41992565098696877, 0.4156675772043933, 0.41123187684820905, 0.40662298053154616, 0.4018453188675355, 0.3969058710752549, 0.39182181079757333, 0.38661286028330705, 0.38129874178127265, 0.3758991775402867, 0.3704338898091656, 0.36492260083672573, 0.35938503287178364, 0.35384090816315567, 0.34830994895965844, 0.3428118775101084, 0.337366416063322, 0.33199328686811563, 0.3267122121733057, 0.3215429142277089, 0.3164989429106634, 0.3115691586235947, 0.30673624939845, 0.30198290326717686, 0.2972918082617225, 0.2926456524140342, 0.28802712375605927, 0.28341891031974514, 0.27880370013703903, 0.27416418123988817, 0.2694830416602402, 0.26474296943004216, 0.2599266525812415, 0.2550167791457854, 0.24999603715562144, 0.2448524871412904, 0.2395956796277081, 0.23424053763838426, 0.22880198419682812, 0.2232949423265493, 0.21773433505105735, 0.21213508539386164, 0.2065121163784718, 0.2008803510283973, 0.19525471236714761, 0.18965012341823226, 0.1840815072051607, 0.1785637867514425, 0.17311188508058709, 0.16774072521610411, 0.16246523018150288, 0.15730032300029304, 0.15226092669598398, 0.1473619642920853, 0.1426183588121065, 0.13804503327955697, 0.13365691071794633, 0.12946891415078404, 0.1254959666015796, 0.12175299109384255, 0.11825491065108232, 0.11501664829680845, 0.11205312705453042, 0.10937926994775779, 0.10701000000000001],
        [0.4538675013327519, 0.45576650000864, 0.45737581613019324, 0.45869969516569054, 0.45974238258341027, 0.4605081238516316, 0.46100116443863315, 0.4612257498126936, 0.4611861254420918, 0.4608865367951065, 0.4603312293400165, 0.45952444854510055, 0.4584704398786374, 0.45717344880890565, 0.4556377208041842, 0.4538675013327519, 0.45186703586288723, 0.4496405698628693, 0.4471923488009766, 0.444526618145488, 0.44164762336468233, 0.4385596099268382, 0.4352668233002344, 0.43177350895314975, 0.42808391235386306, 0.424202278970653, 0.42013285427179825, 0.4158798837255778, 0.4114476128002702, 0.4068402869641543, 0.40206215168550885, 0.3971200697399363, 0.3920313731323351, 0.38681601117492687, 0.3814939331799337, 0.3760850884595775, 0.3706094263260801, 0.36508689609166367, 0.3595374470685499, 0.35398102856896074, 0.3484375899051184, 0.34292708038924447, 0.3374694493335612, 0.3320846460502903, 0.32679261985165375, 0.32161332004987364, 0.3165604694191498, 0.31162288458159515, 0.3067831556213005, 0.30202387262235664, 0.2973276256688547, 0.29267700484488524, 0.2880546002345393, 0.28344300192190774, 0.2788247999910815, 0.2741825845261512, 0.269498945611208, 0.2647564733303427, 0.2599377577676461, 0.255025389007209, 0.2500019571331225, 0.24485544884169383, 0.23959543727809643, 0.23423689219972024, 0.22879478336395517, 0.22328408052819126, 0.21771975344981828, 0.2121167718862263, 0.20649010559480516, 0.2008547243329449, 0.1952255978580354, 0.18961769592746655, 0.18404598829862834, 0.17852544472891066, 0.17307103497570342, 0.16769772879639672, 0.1624204959483803, 0.15725430618904415, 0.15221412927577824, 0.14731493496597245, 0.14257169301701678, 0.1379993731863011, 0.13361294523121536, 0.12942737890914957, 0.12545764397749357, 0.12171871019363732, 0.11822554731497076, 0.11499312509888382, 0.11203641330276641, 0.10937038168400849, 0.10701000000000002],
        [0.4538639292197345, 0.4557454835883517, 0.4573406804192417, 0.45865357295621134, 0.4596882144430673, 0.4604486581236164, 0.4609389572416656, 0.4611631650410216, 0.4611253347654912, 0.46082951965888147, 0.460279772964999, 0.4594801479276507, 0.4584346977906432, 0.45714747579778353, 0.4556225351928783, 0.45386392921973456, 0.4518757111221589, 0.44966193414395833, 0.44722665152893953, 0.4445739165209094, 0.44170778236367475, 0.4386323023010423, 0.435351529576819, 0.43186951743481156, 0.42819031911882693, 0.42431798787267183, 0.42025657694015295, 0.41601013956507743, 0.41158272899125176, 0.40697839846248285, 0.40220120122257763, 0.3972578772719157, 0.39216591363716813, 0.38694548410157886, 0.38161676244839166, 0.37619992246085077, 0.3707151379222, 0.36518258261568315, 0.3596224303245443, 0.35405485483202725, 0.34850002992137596, 0.3429781293758344, 0.33750932697864666, 0.33211379651305645, 0.3268117117623076, 0.32162324650964436, 0.3165622958192207, 0.31161763987883256, 0.30677178015718565, 0.30200721812298603, 0.29730645524494, 0.2926519929917533, 0.2880263328321319, 0.28341197623478187, 0.27879142466840917, 0.27414717960171986, 0.2694617425034199, 0.26471761484221534, 0.2598972980868121, 0.25498329370591616, 0.24995810316823372, 0.2448096465310293, 0.23954751820580275, 0.2341867311926125, 0.2287422984915172, 0.22322923310257523, 0.21766254802584514, 0.2120572562613854, 0.20642837080925458, 0.2007909046695112, 0.1951598708422137, 0.18955028232742052, 0.18397715212519034, 0.17845549323558157, 0.17300031865865267, 0.16762664139446226, 0.16234947444306874, 0.15718383080453066, 0.1521447234789065, 0.14724716546625483, 0.14250616976663408, 0.13793674938010275, 0.13355391730671942, 0.12937268654654258, 0.12540807009963068, 0.12167508096604226, 0.11818873214583583, 0.1149640366390699, 0.11201600744580292, 0.10935965756609346, 0.10701000000000002],
        [0.45376106503634794, 0.4556241021969407, 0.45720428990461615, 0.45850548230255533, 0.4595315335339393, 0.46028629774194946, 0.46077362906976693, 0.4609973816605728, 0.4609614096575484, 0.46066956720387486, 0.4601257084427334, 0.4593336875173052, 0.45829735857077136, 0.45702057574631305, 0.45550719318711147, 0.45376106503634794, 0.45178604543720335, 0.44958598853285925, 0.4471647484664967, 0.4445261793812966, 0.44167413542044054, 0.43861247072710935, 0.43534503944448455, 0.43187569571574713, 0.4282082936840783, 0.42434668749265925, 0.42029473128467104, 0.4160562792032951, 0.4116351853917124, 0.40703530399310417, 0.4022604891506517, 0.39731735181199673, 0.3922235301426245, 0.38699941911248037, 0.3816654136915101, 0.3762419088496596, 0.3707492995568743, 0.3652079807830999, 0.3596383474982823, 0.35406079467236684, 0.3484957172752995, 0.3429635102770258, 0.33748456864749155, 0.3320792873566424, 0.3267680613744237, 0.32157128567078175, 0.31650302653855317, 0.3115520355621405, 0.3067007356488376, 0.3019315497059382, 0.29722690064073637, 0.29256921136052566, 0.2879409047726001, 0.2833244037842533, 0.2787021313027793, 0.2740565102354718, 0.2693699634896246, 0.2646249139725317, 0.25980378459148673, 0.2548889982537835, 0.24986297786671613, 0.24471358462819007, 0.23945043289855894, 0.2340885753287882, 0.22864306456984337, 0.22312895327268983, 0.21756129408829303, 0.21195513966761848, 0.20632554266163167, 0.20068755572129798, 0.19505623149758294, 0.18944662264145198, 0.18387378180387057, 0.1783527616358041, 0.17289861478821814, 0.1675263939120781, 0.16225115165834939, 0.15708794067799758, 0.152051813621988, 0.14715782314128623, 0.14242102188685765, 0.13785646250966774, 0.13347919766068195, 0.12930427999086583, 0.12534676215118473, 0.12162169679260412, 0.11814413656608952, 0.11492913412260636, 0.11199174211312006, 0.10934701318859613, 0.10701000000000002],
        [0.45355673677619474, 0.4554001915703652, 0.45696448607689133, 0.45825326866564103, 0.4592701877064829, 0.4600188915692855, 0.4605030286239171, 0.46072624724024613, 0.46069219578814086, 0.46040452263747, 0.45986687615810184, 0.4590829047199047, 0.458056256692747, 0.4567905804464972, 0.4552895243510236, 0.45355673677619474, 0.45159586609187885, 0.4494105606679446, 0.44700446887426026, 0.44438123908069416, 0.4415445196571149, 0.4384979589733905, 0.4352452053993898, 0.43178990730498107, 0.42813571306003273, 0.42428627103441313, 0.42024522959799054, 0.4160162371206337, 0.41160294197221076, 0.4070089925225901, 0.4022380371416403, 0.3972965515009833, 0.39220232047925613, 0.3869759562568489, 0.3816380710141521, 0.37620927693155626, 0.370710186189452, 0.36516141096822935, 0.359583563448279, 0.3539972558099913, 0.3484231002337568, 0.3428817088999658, 0.3373936939890089, 0.3319796676812764, 0.32666024215715866, 0.3214560295970464, 0.3163812660048239, 0.3114246826783528, 0.30656863473898827, 0.30179547730808587, 0.29708756550700127, 0.2924272544570897, 0.2877968992797068, 0.283178855096208, 0.2785554770279487, 0.2739091201962844, 0.2692221397225707, 0.26447689072816305, 0.2596557283344168, 0.25474100766268737, 0.24971508383433058, 0.24456576755206913, 0.23930269184409672, 0.23394094531997425, 0.22849561658926273, 0.22298179426152334, 0.21741456694631703, 0.21180902325320486, 0.20618025179174787, 0.2005433411715071, 0.19491338000204364, 0.1893054568929184, 0.18373466045369255, 0.17821607929392708, 0.172764802023183, 0.16739591725102143, 0.16212451358700333, 0.15696567964068978, 0.1519345040216418, 0.14704607533942046, 0.14231548220358672, 0.13775781322370173, 0.13338815700932646, 0.12922160217002204, 0.1252732373153494, 0.12155815105486958, 0.11809143199814372, 0.11488816875473279, 0.11196344993419781, 0.10933236414609987, 0.10701],
        [0.45324877243287787, 0.45507158744458404, 0.45661911042664227, 0.45789477750638774, 0.4589020248111552, 0.45964428846827987, 0.4601250046050967, 0.46034760934894065, 0.4603155388271469, 0.46003222916705055, 0.4595011164959866, 0.45872563694128987, 0.45770922663029573, 0.4564553216903389, 0.45496735824875456, 0.4532487724328778, 0.4513030003700435, 0.4491334781875869, 0.44674364201284295, 0.4441369279731465, 0.44131677219583293, 0.43828661080823705, 0.4350498799376939, 0.4316100157115385, 0.42797045425710617, 0.4241346317017316, 0.4201059841727499, 0.41588794779749627, 0.41148395870330556, 0.4068974530175129, 0.4021318668674533, 0.39719353447967937, 0.3921003824776153, 0.386873235583902, 0.3815329185211811, 0.376100256012094, 0.3705960727792823, 0.36504119354538717, 0.35945644303305013, 0.35386264596491274, 0.3482806270636163, 0.34273121105180226, 0.3372352226521121, 0.3318134865871872, 0.3264868275796689, 0.3212760703521989, 0.31619561864571016, 0.3112341922743032, 0.30637409007036986, 0.30159761086630227, 0.2968870534944926, 0.292224716787333, 0.2875928995772154, 0.28297390069653194, 0.27835001897767475, 0.27370355325303575, 0.26901680235500713, 0.26427206511598106, 0.25945164036834945, 0.25453782694450444, 0.2495129236768382, 0.24436469972155994, 0.23910280553014795, 0.23374236187789768, 0.22829848954010473, 0.22278630929206442, 0.2172209419090724, 0.21161750816642405, 0.20599112883941492, 0.20035692470334052, 0.19473001653349623, 0.18912552510517763, 0.1835585711936802, 0.17804427557429933, 0.17259775902233068, 0.16723414231306963, 0.16196854622181167, 0.1568160915238523, 0.15179189899448703, 0.14691108940901132, 0.14218878354272066, 0.13764010217091058, 0.1332801660688765, 0.12912409601191396, 0.12518701277531846, 0.12148403713438545, 0.11803028986441041, 0.1148408917406889, 0.1119309635385163, 0.10931562603318817, 0.10701],
        [0.4528350000000001, 0.45463612555555566, 0.45616600444444455, 0.4574278542857145, 0.45842489269841274, 0.4591603373015874, 0.4596374057142858, 0.45985931555555565, 0.45982928444444443, 0.45955052999999996, 0.4590262698412699, 0.45825972158730166, 0.4572541028571428, 0.4560126312698413, 0.4545385244444445, 0.45283500000000004, 0.45090527555555554, 0.4487525687301587, 0.44638009714285715, 0.44379107841269844, 0.44098873015873014, 0.43797627, 0.4347569155555555, 0.43133388444444437, 0.4277103942857143, 0.4238896626984128, 0.4198749073015873, 0.41566934571428577, 0.4112761955555556, 0.4066986744444444, 0.40194, 0.39700635888888886, 0.39191581396825403, 0.38668939714285716, 0.3813481403174603, 0.3759130753968254, 0.3704052342857143, 0.36484564888888893, 0.3592553511111111, 0.3536553728571429, 0.34806674603174603, 0.34251050253968246, 0.3370076742857143, 0.3315792931746032, 0.3262463911111111, 0.32103, 0.3159446888888889, 0.3109791753968254, 0.3061157142857143, 0.30133656031746026, 0.29662396825396825, 0.29196019285714286, 0.2873274888888889, 0.2827081111111111, 0.27808431428571434, 0.2734383531746032, 0.26875248253968254, 0.2640089571428572, 0.25919003174603183, 0.2542779611111111, 0.24925500000000003, 0.24410888555555557, 0.23884928444444448, 0.23349134571428576, 0.22805021841269843, 0.2225410515873016, 0.21697899428571432, 0.2113791955555555, 0.20575680444444444, 0.20012697, 0.19450484126984124, 0.18890556730158728, 0.18334429714285713, 0.17783617984126984, 0.17239636444444442, 0.16704000000000002, 0.16178223555555554, 0.1566382201587302, 0.15162310285714284, 0.1467520326984127, 0.1420401587301587, 0.13750262999999996, 0.1331545955555555, 0.12901120444444442, 0.1250876057142857, 0.12139894841269841, 0.11796038158730159, 0.1147870542857143, 0.11189411555555553, 0.10929671444444444, 0.10701]]
        
        return spline_stand[az][alt]


class WindSpeed(object):
    
    def terrain(self, terrainType):
        # Atmospheric boundary layer parameters based on terrain type
        if terrainType == None:
            # Default terrain value
            terrainType = "City Terrain"
            gradientHeightDiv = 921
            gradientHeight = 460
            a = 0.33
            yValues = [str(yLabel) for yLabel in range(0,500,50)]
            yAxisMaxRhinoHeight = 92
            nArrows = 10
            validTerrain = True
            printMsg = "Terrain has been set to a default of (0 = city)."
        else:
            if terrainType == "city" or int(terrainType) == 0:
                terrainType = "City Terrain"
                gradientHeightDiv = 921
                gradientHeight = 460
                a = 0.33
                yValues = [str(yLabel) for yLabel in range(0,500,50)]
                yAxisMaxRhinoHeight = 92
                nArrows = 10
                validTerrain = True
                printMsg = "Terrain set to (0 = city)"
            elif terrainType == "suburban" or int(terrainType) == 1:
                terrainType = "Suburban Terrain"
                gradientHeightDiv = 741
                gradientHeight = 370
                a = 0.22
                yValues = [str(yLabel) for yLabel in range(0,400,50)]
                yAxisMaxRhinoHeight = 72
                nArrows = 8
                validTerrain = True
                printMsg = "Terrain set to (1 = suburban)"
            elif terrainType == "country" or int(terrainType) == 2:
                terrainType = "Country Terrain"
                gradientHeightDiv = 541
                gradientHeight = 270
                a = 0.14
                yValues = [str(yLabel) for yLabel in range(0,300,50)]
                yAxisMaxRhinoHeight = 52
                nArrows = 6
                validTerrain = True
                printMsg = "Terrain set to (2 = country)"
            elif terrainType == "water" or int(terrainType) == 3:
                terrainType = "Water Terrain"
                gradientHeightDiv = 421
                gradientHeight = 210
                a = 0.10
                yValues = [str(yLabel) for yLabel in range(0,250,50)]
                yAxisMaxRhinoHeight = 42
                nArrows = 5
                validTerrain = True
                printMsg = "Terrain set to (3 = water)"
            else:
                terrainType = gradientHeightDiv = gradientHeight = a = yValues = yAxisMaxRhinoHeight = nArrows = None
                validTerrain = False
                printMsg = "Please choose one of three terrain types: 0=city, 1=urban, 2=country 3=water"
        
        return validTerrain, terrainType, gradientHeightDiv, gradientHeight, a, yValues, yAxisMaxRhinoHeight, nArrows, printMsg
    
    
    
    def readTerrainType(self, terrainType):
        checkData = True
        roughLength = None
        
        if round(terrainType, 1) == 3.0 or terrainType == "water":
            d = 210
            a = 0.10
        elif round(terrainType, 1) == 2.0 or terrainType == "country":
            d = 270
            a = 0.14
        elif round(terrainType, 1) == 1.0 or terrainType == "suburban":
            d = 370
            a = 0.22
        elif round(terrainType, 1) == 0.0 or terrainType == "urban":
            d = 460
            a = 0.33
        else:
            d = None
            a = None
            checkData = False
        
        return checkData, d, a
    
    def calcWindSpeedBasedOnHeight(self, vMet, height, d, a, metD, metA):
        #Calculate the wind speed.
        vHeight = ((height / d) ** a) * (vMet * (metD / 10) ** metA)
        
        return vHeight


class Photovoltaics(object):
    """ Set of methods for Photovoltaics and Solar hot water analysis """
    def NRELsunPosition(self, latitude , longitude, timeZone, year, month, day, hour):
        # sunZenith, sunAzimuth, sunAltitude angles
        # based on Michalsky (1988), modified to calculate sun azimuth angles for locations south of the equator using the approach described in (Iqbal, 1983)
        min = 30
        
        # leap year
        if year%4 == 0:
            k = 1
        else:
            k = 0
        
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        jdoy = int(numOfDays[int(month)-1] + int(day))
        
        # julian day of year
        if month > 2:
            jdoy = jdoy + k
        
        # current decimal time of day in UTC
        tutc = hour + min/60.0 - timeZone
        
        if tutc < 0:
            tutc = tutc + 24
            jdoy = jdoy - 1
        elif tutc > 24:
            tutc = tutc - 24
            jdoy = jdoy + 1
        
        julian = 32916.5 + 365*(year-1949) + int((year-1949)/4) + jdoy + (tutc/24) - 51545
        
        mnlong = 280.46 + 0.9856474*julian   # in degrees
        mnlong = mnlong - 360*int(mnlong/360)
        
        if (mnlong < 0):
            mnlong = (mnlong+360)
        
        mnanom = (357.528 + 0.9856003*julian)
        mnanom = mnanom - 360*int(mnanom/360)
        
        if (mnanom < 0):
            mnanom = (mnanom+360)
        mnanom = mnanom*(math.pi/180)   # in radians
        
        eclong = (mnlong + 1.915*math.sin(mnanom) + 0.02 * math.sin(2*mnanom))
        eclong = eclong - 360*int(eclong/360)
        
        if (eclong < 0):
            eclong = (eclong+360)
        eclong = eclong*(math.pi/180)
        
        obleq = (math.pi/180)*(23.439 - 0.0000004*julian)
        
        if (math.cos(eclong) < 0):
            ra = math.atan(((math.cos(obleq)*math.sin(eclong))/math.cos(eclong))) + math.pi
        elif (math.cos(obleq)*math.sin(eclong) < 0):
            ra = math.atan(((math.cos(obleq)*math.sin(eclong))/math.cos(eclong))) + 2*math.pi
        else:
            ra = math.atan(((math.cos(obleq)*math.sin(eclong))/math.cos(eclong)))
        
        beta = math.asin(math.sin(obleq)*math.sin(eclong))   # in radians
        
        gmst = 6.697375 + 0.0657098242*julian + tutc
        gmst = gmst - 24*int(gmst/24)
        
        if (gmst < 0):
            gmst = gmst + 24
        
        lmst = gmst + longitude/15
        lmst = lmst - 24*int(lmst/24)
        
        if (lmst < 0):
            lmst = lmst + 24
       
        b = 15*(math.pi/180) * lmst - ra
        
        if (b < -math.pi):
            HA = b + 2*math.pi   # in radians
        elif (b > math.pi):
            HA = b - 2*math.pi   # in radians
        else:
            HA = b
        
        # sun altitude, not corrected for radiation (in radians):
        a = math.sin(beta) * math.sin((math.pi/180)*latitude ) + math.cos(beta) * math.cos((math.pi/180)*latitude ) * math.cos(HA)
        
        if (a >= -1) and (a <= 1):
            alpha0 = math.asin(a)
        elif (a > 1):
            alpha0 = math.pi/2
        elif (a < -1):
            alpha0 = -math.pi/2
        
        # sun altitude, corrected for refraction (in radians):
        alpha0d = 180/math.pi * alpha0
        
        if (alpha0d > -0.56):
            r = 3.51561*((0.1594+0.0196*alpha0d+0.00002*(alpha0d**2))/(1+0.505*alpha0d+0.0845*(alpha0d**2)))
        elif (alpha0d <= -0.56):
            r = 0.56
        
        if (alpha0d+r > 90):
            sunAltitudeR = math.pi/2
        elif (alpha0d+r <= 90):
            sunAltitudeR = (math.pi/180) * (alpha0d+r)
        
        # sun azimuth angle (in radians):
        a = (math.sin(alpha0)*math.sin(math.pi/180*latitude ) - math.sin(beta))/(math.cos(alpha0)*math.cos(math.pi/180*latitude ))
        
        if (a >= -1) and (a <= 1):
            b = math.acos(a)
        elif (math.cos(alpha0) == 0) or (a < -1):
            b = math.pi
        elif (a > 1):
            b = 0
        
        if (HA < -math.pi):
            sunAzimuthR = b
        elif ((HA >= -math.pi) and (HA <= 0)) or (HA >= math.pi):
            sunAzimuthR = math.pi - b
        elif (HA > 0) and (HA < math.pi):
            sunAzimuthR = math.pi + b
        
        # sun zenith angle (in radians)
        sunZenithR = (math.pi/2) - sunAltitudeR
        
        sunZenithD = math.degrees(sunZenithR)
        sunAzimuthD = math.degrees(sunAzimuthR)
        sunAltitudeD = math.degrees(sunAltitudeR)
        
        return sunZenithD, sunAzimuthD, sunAltitudeD
    
    def POAirradiance(self, sunZenithD, sunAzimuthD, srfTiltD, srfAzimuthD, DNI, DHI, albedo):
        # pvwatts Plane-of-Array Irradiance by Perez 1990 algorithm
        
        if sunZenithD > 90:
            sunZenithD = 90
            sunAzimuthD = 0
        
        GHI = DHI + DNI * math.cos(math.radians(sunZenithD))
        
        # convert degree angles to radians:
        srfTiltR = math.radians(srfTiltD)
        srfAzimuthR = math.radians(srfAzimuthD)
        
        sunAzimuthR = math.radians(sunAzimuthD)
        sunZenithR = math.radians(sunZenithD)
        
        # Tracking
        #alphaFixed (angle of incidence in radians):
        AOI_R = math.acos( math.cos(sunZenithR)*(math.cos(srfTiltR)) + math.sin(srfTiltR) * (math.sin(sunZenithR)) * (math.cos(srfAzimuthR - sunAzimuthR)) )  # in radians
        
        if (AOI_R > math.pi):
            AOI_R = math.pi
        elif AOI_R < 0:
            AOI_R = 0
        AOI_D = math.degrees(AOI_R)  # in degrees
        
        # Eb beam irradiance
        Eb = DNI * math.cos(AOI_R)
        
        # Ed_sky (Perez 1990 Model modified model) diffuse sky irradiance
        a = max(0, math.cos(AOI_R))
        b = max(math.cos(math.radians(85)), math.cos(sunZenithR))
        
        k = 5.534*(10**(-6))  # for angles in degrees
        # sky clearness
        if DHI == 0:
            divison = 0
        elif DHI > 0:
            divison = ((DHI+DNI)/DHI)
        epsilon = ( divison + k*(sunZenithD**3)) / (1 + k*(sunZenithD**3))
        
        # Perez model coefficients for irradiance based on epsilon bins
        if epsilon <= 1.065:
            f11 = -0.0083117
            f12 = 0.5877285
            f13 = -0.0620636
            f21 = -0.0596012
            f22 = 0.0721249
            f23 = -0.0220216
        elif epsilon > 1.065 and epsilon <= 1.23:
            f11 = 0.1299457
            f12 = 0.6825954
            f13 = -0.1513752
            f21 = -0.0189325
            f22 = 0.065965
            f23 = -0.0288748
        elif epsilon > 1.23 and epsilon <= 1.5:
            f11 = 0.3296958
            f12 = 0.4868735
            f13 = -0.2210958
            f21 = 0.055414
            f22 = -0.0639588
            f23 = -0.0260542
        elif epsilon > 1.5 and epsilon <= 1.95:
            f11 = 0.5682053
            f12 = 0.1874525
            f13 = -0.295129
            f21 = 0.1088631
            f22 = -0.1519229
            f23 = -0.0139754
        elif epsilon > 1.95 and epsilon <= 2.8:
            f11 = 0.873028
            f12 = -0.3920403
            f13 = -0.3616149
            f21 = 0.2255647
            f22 = -0.4620442
            f23 = 0.0012448
        elif epsilon > 2.8 and epsilon <= 4.5:
            f11 = 1.1326077
            f12 = -1.2367284
            f13 = -0.4118494
            f21 = 0.2877813
            f22 = -0.8230357
            f23 = 0.0558651
        elif epsilon > 4.5 and epsilon <= 6.2:
            f11 = 1.0601591
            f12 = -1.5999137
            f13 = -0.3589221
            f21 = 0.2642124
            f22 = -1.127234
            f23 = 0.1310694
        elif epsilon > 6.2:
            f11 = 0.677747
            f12 = -0.3272588
            f13 = -0.2504286
            f21 = 0.1561313
            f22 = -1.3765031
            f23 = 0.2506212
        
        # absolute optical air mass
        AM0 = 1/(b + 0.15*(1/((93.9 - sunZenithD)**(1.253))))
        
        # sky brightness
        delta = DHI*(AM0/1367)
        
        F1 = max(0, (f11 + delta*f12 + sunZenithR*f13))
        F2 = f21 + delta*f22 + sunZenithR*f23
        
        # isotropic, circumsolar, and horizon brightening components of the sky diffuse irradiance:
        if (sunZenithD <= 87.5):
            Di = DHI*(1-F1)*((1+math.cos(srfTiltR))/2)
            Dc = DHI*F1*(a/b)
            Dh = DHI*F2*math.sin(srfTiltR)
        # only isotropic brightening component of the sky diffuse irradiance:
        elif (sunZenithD > 87.5):
            Di = (1+math.cos(srfTiltR))/2
            Dc = 0
            Dh = 0
        
        Ed_sky = Di + Dc + Dh
        
        # Eg ground reflected irradiance
        Eground = ((DNI * math.cos(sunZenithR)) + Ed_sky) * albedo * ((1-math.cos(srfTiltR))/2)
        
        Epoa = Eb + Eground + Ed_sky  # in Wh/m2
        
        if Epoa < 0 or ((DNI<=0) and (DHI<=0)):
            Epoa = Eb = Ed_sky = Eground = 0
        
        return Epoa, Eb, Ed_sky, Eground, AOI_R
    
    def pvwatts(self, nameplateDCpowerRating, DCtoACderateFactor, AOI_R, Epoa, Eb, Ed_sky, Eground, moduleType, Ta, ws, DNI, DHI):
        # PVWatts v1 Thermal, Module Temperature, Cell Temperature Module and Inverter models
        
        # Sandia PV Array Performance Module Cover
        # Module Cover Polynomial Coefficients
        b0 = 1
        b1 = -2.438e-3
        b2 = 3.103e-4
        b3 = -1.246e-5
        b4 = 2.112e-7
        b5 = -1.359e-9
        
        f = b0 + b1*AOI_R + b2*(AOI_R**2) + b3*(AOI_R**3) + b4*(AOI_R**4) + b5*(AOI_R**5)
        Etr = Epoa - (1-f)*Eb*math.cos(AOI_R)
        
        # Thermal Model by Fuentes (1987)
        if moduleType == 0:   # glass/cell/glass   close roof mount
            a = -2.98
            b = -0.0471
            deltaT = 1
        elif moduleType == 1:   # glass/cell/polymer sheet   insulated back
            a = -2.81
            b = -0.0455
            deltaT = 0
        elif moduleType == 2:   # glass/cell/polymer sheet   open rack
            a = -3.56
            b = -0.0750
            deltaT = 3
        elif moduleType == 3:   # for glass/cell/glass   open rack
            a = -3.47
            b = -0.0594
            deltaT = 3
        
        # Sandia Module Temperature Model
        Tm = Epoa * (math.exp(a+(b*ws))) + Ta  # in C degrees
        
        # Sandia Cell Temperature Model
        Tcell = Tm + (Epoa/1000)*deltaT  # in C degrees
        
        if ((DNI<=0) and (DHI<=0)):
            Pac = 0
            return Tm, Tcell, Pac
        
        # PVFORM version 3.3 adapted Module Model
        Pdc0 = nameplateDCpowerRating   # in kWatts
        gamma = -0.005   # default value for crystalline silicon PV modules
        
        if Etr > 125:
            Pdc = (Etr/1000)*Pdc0*(1+gamma*(Tcell-25))
        if Etr <= 125:
            Pdc = ((0.008*(Etr**2))/1000)*Pdc0*(1+gamma*(Tcell-25))
        
        # System Derates
        Eta_inv = 0.92  # default
        Pdc_ = Pdc*(DCtoACderateFactor/Eta_inv)
        
        # PVFORM version 3.3 adapted Inverter Model
        Pac0 = Pdc0
        Pinv_dc0 = Pac0/Eta_inv
        f = Pdc_/Pinv_dc0
        
        # Pac in kWh
        if (f >= 0.1) and (f <= 1):
            Eta_op = 0.774 + 0.663 * f - 0.952 * (f**2) + 0.426 * (f**3)
            Pac = Pdc_ * Eta_op * (Eta_inv/0.91)
        elif (f >= 0) and (f < 0.1):
            Eta_op = -0.015 + 8.46 * f
            Pac = Pdc_ * Eta_op * (Eta_inv/0.91)
        elif (f > 1):
            Pac = Pac0
        
        if Pac < 0: Pac = 0
        
        return Tm, Tcell, Pac
    
    def srfAzimuthAngle(self, PVsurface):
        # calculate PVsurface azimuth angle
        obj = rs.coercegeometry(PVsurface)
        objSrf = obj.Faces[0]
        reparematizedDomain = rc.Geometry.Interval(0,1)
        objSrf.SetDomain(0, reparematizedDomain)
        objSrf.SetDomain(1, reparematizedDomain)
        srfNormal = objSrf.NormalAt(0.5, 0.5)
        srfNormal.Unitize()
        
        if srfNormal == rc.Geometry.Vector3d(0,0,1):
            # "_PVsurface" surface is parallel to the XY plane, faced upward
            srfAzimuthD = 180
            surfaceTiltD = 0
        elif srfNormal == rc.Geometry.Vector3d(0,0,-1):
            # "_PVsurface" surface is parallel to the XY plane, faced downward
            srfAzimuthD = 180
            surfaceTiltD = 180
        else:
            # "_PVsurface" surface is not parallel to the XY plane
            if srfNormal.Z == 0:
                # "_PVsurface" surface is perpendicular to the XY plane, faced downward
                surfaceTiltD = 90
            else:
                # "_PVsurface" surface is not parallel nor perpendicular to XY plane
                surfaceTiltD = None
            # calculate the srfAzimuthD
            xyPlane = rc.Geometry.Plane(rc.Geometry.Point3d(0,0,0), rc.Geometry.Vector3d(0,0,1))
            
            projNormalPt = xyPlane.ClosestPoint(rc.Geometry.Point3d(srfNormal))
            projNormal = rc.Geometry.Vector3d(projNormalPt)
            projNormal.Unitize()
            
            angleToYaxis = rc.Geometry.Vector3d.VectorAngle(projNormal, rc.Geometry.Vector3d(0,1,0), xyPlane)
            srfAzimuthR = angleToYaxis
            srfAzimuthD = math.degrees(srfAzimuthR)
        
        return srfAzimuthD, surfaceTiltD
    
    def srfTiltAngle(self, PVsurface):
        # calculate PVsurface tilt angle
        obj = rs.coercegeometry(PVsurface)
        zeroZeroZeroPt = rc.Geometry.Point3d(0,0,0)
        zAxis = rc.Geometry.Vector3d(0,0,1)
        worldXYplane = rc.Geometry.Plane(zeroZeroZeroPt, zAxis)
        boundingBox = rc.Geometry.Brep.GetBoundingBox(obj, worldXYplane)
        boundingBoxBrep = boundingBox.ToBrep()
        lowerFaceBB = boundingBoxBrep.Faces[4].DuplicateFace(False)
        centroidLowerFaceBB = rc.Geometry.AreaMassProperties.Compute(lowerFaceBB).Centroid
        lowerFaceBBPlane = rc.Geometry.Plane(centroidLowerFaceBB, zAxis)
        transformMatrix = rc.Geometry.Transform.Translation(zeroZeroZeroPt-centroidLowerFaceBB)
        obj.Transform(transformMatrix)
        
        objSrf = obj.Faces[0]
        reparematizedDomain = rc.Geometry.Interval(0,1)
        objSrf.SetDomain(0, reparematizedDomain)
        objSrf.SetDomain(1, reparematizedDomain)
        centroidClosestPoint = objSrf.PointAt(0.5, 0.5)
        orientedSrfNormal = objSrf.NormalAt(0.5, 0.5)
        transformMatrix2 = rc.Geometry.Transform.PlanarProjection(worldXYplane)
        projectedSrf = rc.Geometry.Brep.DuplicateBrep(obj)
        projectedSrf.Transform(transformMatrix2)
        
        intersectPlane = rc.Geometry.Plane(centroidClosestPoint, zAxis, orientedSrfNormal)
        tol = rc.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        brepPlaneInterCrv1 = rc.Geometry.Intersect.Intersection.BrepPlane(obj, intersectPlane, tol)[1][0]
        brepPlaneInterCrv2 = rc.Geometry.Intersect.Intersection.BrepPlane(projectedSrf, intersectPlane, tol)[1][0]
        brepPlaneInterVec1 = rc.Geometry.Vector3d(brepPlaneInterCrv1.PointAtEnd - brepPlaneInterCrv1.PointAtStart)
        brepPlaneInterVec2 = rc.Geometry.Vector3d(brepPlaneInterCrv2.PointAtEnd - brepPlaneInterCrv2.PointAtStart)
        srfTitlR = rc.Geometry.Vector3d.VectorAngle(brepPlaneInterVec1, brepPlaneInterVec2)
    
        if orientedSrfNormal.Z < 0:
            srfTitlR = math.pi - srfTitlR
        srfTiltD = math.degrees(srfTitlR)
        
        return srfTiltD

    def inletWaterTemperature(self, dryBulbTemperature_C, method=0, depth_m=2, soilThermalDiffusivity_m2_s=2.5, minimalTemperature_C=1):
        # calculate cold (inlet) water temperature
        # soilThermalDiffusivity (m2/s) per material (valid for method "0" only):
        # 0.00000024 - dry sand
        # 0.00000074 - wet sand
        # 0.00000025 - dry clay
        # 0.00000051 - wet clay
        # 0.00000010 - dry peat
        # 0.00000012 - wet peat
        # 0.00000129 - dense rock
        preparation = Preparation()
        
        depth_ft = depth_m * 3.2808399  # to feet
        soilThermalDiffusivity_m2_s = soilThermalDiffusivity_m2_s * (10**(-7))  # convert from m2/s * 10**(-7) to m2/s
        soilThermalDiffusivity_ft2_hr = soilThermalDiffusivity_m2_s * 38750.077512  # to ft2/hr
        minimalTemperature_F = preparation.celsiusToFahrenheit(minimalTemperature_C)
        
        # Ta in Fahrenheit
        dryBulbTemperature_F = [preparation.celsiusToFahrenheit(TaC) for TaC in dryBulbTemperature_C]
        hoyForMonths = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760, 9000]
        hoyTaPerMonths_F = [[] for i in range(12)]
        HOYs = range(1,8761)
        for i,hoy in enumerate(HOYs):
            for k,item in enumerate(hoyForMonths):
                if hoy >= hoyForMonths[k]+1 and hoy <= hoyForMonths[k+1]:
                    hoyTaPerMonths_F[k].append(dryBulbTemperature_F[i])
        averageTa_perMonths_F = []
        numberOfDaysInMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
        for i in range(len(numberOfDaysInMonth)):
            averageTa_F = sum(hoyTaPerMonths_F[i])/(numberOfDaysInMonth[i]*24)
            averageTa_perMonths_F.append(averageTa_F)
        
        
        averageTa_perYear_F = sum(dryBulbTemperature_F)/len(dryBulbTemperature_F)  # annualAverageTa in F
        minAverageMonthlyTa = min(averageTa_perMonths_F)
        maxAverageMonthlyTa = max(averageTa_perMonths_F)
        
        if method == 0:
            # Carslaw and Jaeger semi-infinite medium conduction equations.
            # source: "Residential alternative calculation method reference manual", California energy commission, June 2013:
            averageTa_dec_JanToDec_perMonths = [averageTa_perMonths_F[-1]] + averageTa_perMonths_F[:-1]
            
            janToDecHOYs = dryBulbTemperature_F[:8017]
            decHOYs = dryBulbTemperature_F[8017:]
            dec_JanToDecHOYs = decHOYs + janToDecHOYs
            
            annualSurfaceTemperatureAmplitude = 0.5*(maxAverageMonthlyTa-minAverageMonthlyTa)
            pb = 8760 
            po = 0.6  # phase lag
            beta = math.sqrt(math.pi/(soilThermalDiffusivity_ft2_hr*pb))*depth_ft
            xb = math.exp(-beta) 
            cb = math.cos(beta) 
            sb = math.sin(beta) 
            gm = math.sqrt((xb*xb - 2*xb*cb + 1)/(2*beta*beta)) 
            phi = math.atan((1.-xb*(cb+sb)) / (1.-xb*(cb-sb))) 
            
            TinletPerHOY_F = []
            HOYs = range(1,8761)
            for i,hoy in enumerate(HOYs):
                 Tground = averageTa_perYear_F - annualSurfaceTemperatureAmplitude*math.cos((2*math.pi*(hoy/pb))-po-phi)*gm
                 last31Days = dec_JanToDecHOYs[i:(i+31)]
                 Tavg31 = sum(last31Days)/len(last31Days)
                 TinletF = Tground * 0.65 + Tavg31 * 0.35
                 if TinletF < minimalTemperature_F:  # preventing freezing of inlet water
                    TinletF = minimalTemperature_F
                 TinletPerHOY_F.append(TinletF)
        
        elif method == 1:
            # Christensen and Burch.
            # source: "Development of an Energy Savings Benchmark for All Residential End-Uses", NREL, August 2004
            montlyAvrMaximalDiff = maxAverageMonthlyTa - minAverageMonthlyTa
            offset = 6
            ratio = 0.4 + 0.01 * (averageTa_perYear_F - 44)
            lag = 35 - 1.0 * (averageTa_perYear_F - 44)
            TinletPerHOY_F = []
            for hoy in range(1,8761):
                day, month, dummyHour = preparation.hour2Date(hoy, True)
                julianDay = preparation.getJD(month+1, day)
                TinletF = (averageTa_perYear_F + offset) + ( ratio*(montlyAvrMaximalDiff/2) * math.sin(math.radians(0.986*(julianDay-15-lag)-90)) )
                if TinletF < minimalTemperature_F:  # preventing freezing of inlet water
                    TinletF = minimalTemperature_F
                TinletPerHOY_F.append(TinletF)
        
        elif method == 2:
            # RETScreen
            # source: "Solar water heating project analysis chapter", Minister of Natural Resources Canada, 2004
            averageTa_dec_JanToDec_perMonths = [averageTa_perMonths_F[-1]] + averageTa_perMonths_F[:-1]
            TinletPerHOY_F = []
            for hoy in range(1,8761):
                dummyDay, month, dummyHour = preparation.hour2Date(hoy, True)
                TinletF = averageTa_perYear_F + 0.35*(averageTa_dec_JanToDec_perMonths[month] - averageTa_perYear_F)
                if TinletF < minimalTemperature_F:  # preventing freezing of inlet water
                    TinletF = minimalTemperature_F
                TinletPerHOY_F.append(TinletF)
        
        # converting to Celsius
        TinletPerHOY_C = [preparation.fahrenheitToCelsius(Tinlet_F) for Tinlet_F in TinletPerHOY_F]
        TinletHOYminimal_C = preparation.fahrenheitToCelsius(min(TinletPerHOY_F))
        TinletHOYmaximal_C = preparation.fahrenheitToCelsius(max(TinletPerHOY_F))
        TinletAverageAnnual_C = preparation.fahrenheitToCelsius(sum(TinletPerHOY_F)/len(TinletPerHOY_F))
        
        return TinletPerHOY_C, TinletAverageAnnual_C, TinletHOYminimal_C, TinletHOYmaximal_C
    
    def shwdesign(self, activeArea, Ta, Tw, SR, Qload, Fr, FrUL, tankLoss, tankSize, tankArea, TdeliveryW, TmaxW, TdischargeW, pipingLosses, minSR=None):
        # based on "A simplified method for optimal design of solar water heating systems based on life-cycle energy analysis",
        # Renewable Energy journal, Yan, Wang, Ma, Shi, Vol 74, Feb 2015
        
        if SR > 0:
            collectorHeatLoss = FrUL*((Tw-Ta)/SR)
        else:
            collectorHeatLoss = 0
        
        if SR <= 0:
            collectorEfficiency = Fr
        else:
            collectorEfficiency = Fr-collectorHeatLoss
        if collectorEfficiency < 0:
            collectorEfficiency = Fr
        
        if minSR == None:
            minSR = (FrUL*(Tw-Ta))/Fr
        
        if SR > minSR:
            Qsolar = pipingLosses*(collectorEfficiency*SR*activeArea/1000)
        else:
            Qsolar = 0
        
        Qloss = tankLoss*tankArea*(Tw-Ta)/1000
        
        if Tw > TdeliveryW:
            Qsupply = pipingLosses*Qload
        else:
            Qsupply = 0
        
        if Tw > TdeliveryW:
            Qaux = 0
        else:
            Qaux = Qload
        
        if Tw > TmaxW:
            Qdis = (Tw-TdischargeW)*4.2*tankSize*1000/3600
        else:
            Qdis = 0
        
        dQ = Qsolar - Qloss - Qsupply - Qdis
        dt = dQ*3600/(4.2*tankSize*1000)
        Tw = Tw + dt
        
        return collectorHeatLoss, collectorEfficiency, Qsolar, Qloss, Qsupply, Qaux, Qdis, dQ, dt, Tw
    
    def WMMcoefficients(self, COFfilePath=None):
        # WMM coefficients extractor and WMM 2015-2020 coefficients
        # written by: Christopher Weiss (cmweiss@gmail.com), source: https://pypi.python.org/pypi/geomag
        
        if COFfilePath:
            wmm=[]
            with open(COFfilePath) as COFfile:
                for line in COFfile:
                    linevals = line.strip().split()
                    if len(linevals) == 3:
                        epoch = float(linevals[0])
                        model = linevals[1]
                        modeldate = linevals[2]
                    elif len(linevals) == 6:
                        linedict = {"n": int(float(linevals[0])),
                        "m": int(float(linevals[1])),
                        "gnm": float(linevals[2]),
                        "hnm": float(linevals[3]),
                        "dgnm": float(linevals[4]),
                        "dhnm": float(linevals[5])}
                        wmm.append(linedict)
            
            z = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            maxord = maxdeg = 12
            tc = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
            sp = z[0:14]
            cp = z[0:14]
            cp[0] = 1.0
            pp = z[0:13]
            pp[0] = 1.0
            p = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
            p[0][0] = 1.0
            dp = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
            a = 6378.137
            b = 6356.7523142
            re = 6371.2
            a2 = a*a
            b2 = b*b
            c2 = a2-b2
            a4 = a2*a2
            b4 = b2*b2
            c4 = a4 - b4
            
            c = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
            cd = [z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14],z[0:14]]
            
            for wmmnm in wmm:
                m = wmmnm["m"]
                n = wmmnm["n"]
                gnm = wmmnm["gnm"]
                hnm = wmmnm["hnm"]
                dgnm = wmmnm["dgnm"]
                dhnm = wmmnm["dhnm"]
                if (m <= n):
                    c[m][n] = gnm
                    cd[m][n] = dgnm
                    if (m != 0):
                        c[n][m-1] = hnm
                        cd[n][m-1] = dhnm
            
            # convert schmidt normalized gauss coefficients to unnormalized
            snorm = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
            snorm[0][0] = 1.0
            k = [z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13],z[0:13]]
            k[1][1] = 0.0
            fn = [0.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0]
            fm = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0]
            for n in range(1,maxord+1):
                snorm[0][n] = snorm[0][n-1]*(2.0*n-1)/n
                j=2.0
                m=0
                D1=1
                D2=(n-m+D1)/D1
                while (D2 > 0):
                    k[m][n] = (((n-1)*(n-1))-(m*m))/((2.0*n-1)*(2.0*n-3.0))
                    if (m > 0):
                        flnmj = ((n-m+1.0)*j)/(n+m)
                        snorm[m][n] = snorm[m-1][n]*math.sqrt(flnmj)
                        j = 1.0
                        c[n][m-1] = snorm[m][n]*c[n][m-1]
                        cd[n][m-1] = snorm[m][n]*cd[n][m-1]
                    c[m][n] = snorm[m][n]*c[m][n]
                    cd[m][n] = snorm[m][n]*cd[m][n]
                    D2=D2-1
                    m=m+D1
        
        else:
            # no COFfilePath inputted, use WMM 2015-2020.COF coefficients:
            epoch = 2015.0
            maxord = 12
            tc = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
            sp = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            cp = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            pp = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            p = [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
            dp = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
            re = 6371.2
            a2 = 40680631.5908
            b2 = 40408299.9841
            c2 = 272331.606682
            a4 = 1.65491378662e+15
            c4 = 2.20830790199e+13
            c = [[0.0, -29438.5, -3667.9500000000003, 3377.75, 3969.0, -1831.725, 1003.40625, 2187.8999999999996, 1206.5625, 512.7890625, -342.80898437499997, 1067.792578125, -1320.388671875, 0.0],
                 [4796.2, -1501.1, 5217.8030578012422, -7202.4184024360875, 4503.0043311382678, 3660.9859202943885, 1274.0706075900976, -2699.2368274123305, 576.46875, 1121.1505084935352, -1581.3594797464489, -699.57967039296318, -269.10823847557441, 0.0],
                 [-4928.7237780179967, -555.98830922960963, 1451.9781919849897, 2373.3641945559048, 470.74821096314326, 1478.63499552797, 1087.9401092201722, -196.93350797286885, -947.792009121047, 336.81512900689262, 42.138384060792873, -940.81033876221875, 318.05194427898653, 0.0],
                 [-353.03270917862551, 474.44045991040861, -425.56351611715962, 460.03234261299497, -700.70277222228833, -663.57598354483855, -1293.17423238808, 1062.82818860168, -132.54263465013815, -257.24680398006694, 99.168204275653849, 688.73281700535983, 843.98705644892641, 0.0],
                 [1568.3316055605076, -738.01423597380563, 378.37949700003571, -243.66853606641544, 51.987551093987875, -349.19660919745473, -158.24900029305081, 185.23396312164252, -550.76612412740872, 33.825443023013385, -70.122509721407624, -215.56257141023613, -438.22404854078866, 0.0],
                 [481.89595285185783, 1513.2184543630835, -561.92179032094839, 35.71833169046392, 70.226232078013382, 3.0167112680864894, 30.713942273827364, 57.422528567709179, 197.24679736884357, -448.08960423838624, 125.65654604793681, 95.054159320847774, 300.61921720066948, 0.0],
                 [-391.29468215304178, 496.148511347661, 585.813904964708, -362.8813282582027, 16.98574080294998, 41.980830586337255, -47.623054217140982, -6.781108869499149, 80.323160923011869, -1.739793057467611, -28.924059580399042, -65.882349610875536, 20.829891011946017, 0.0],
                 [-1918.905550105218, -561.83971392259639, 114.67895676626991, 301.31391334453849, 20.375735943380676, -66.600176396866644, -1.488697653361824, 4.336640990227923, -40.10922587136281, 65.541666851621656, 42.0906892135213, 9.920870589232127, 58.526941135745062, 0.0],
                 [683.71875, -1015.0908500053819, 546.73836793181977, -390.34880642039639, 240.25549754701245, 39.131796347108356, -22.8121222143376, 1.3787546393280967, -1.2534133084800878, -23.514197358553233, 18.819971145948287, 38.692064716680534, -23.410776454298027, 0.0],
                 [-2751.914884484132, 1173.4204494433677, 970.89922792476875, -383.35502092748504, -232.4675390409673, 135.70385848247366, 7.533524925473754, -10.077513153665672, 5.176919833491951, -6.395018617842998, -4.778612553812365, -1.762984967977451, -10.217300493286722, 0.0],
                 [802.84404356358175, -63.207576091189296, 760.28956611334615, 514.23173795698926, -583.93336104629464, -24.792051068913466, -82.17705989306539, -22.911269221154438, -2.9202632273297784, -5.164562879088187, -2.1370605016916637, 1.088137945966928, 1.8864941272538016, 0.0],
                 [-46.638644692864219, 859.00074408724333, -229.57760566845326, -263.46536505695531, 110.89651920765574, -18.823528460250156, -104.16914118693732, -34.140057102953413, -22.037312099718136, -5.44068972983464, -1.3339527900497614, 2.0299281587713764, -2.5033354595732336, 0.0],
                 [-897.027461585248, 397.56493034873313, 1168.5974627754365, -1071.2143408774834, 100.20640573355649, 145.80923708362209, -11.705388227149014, 17.558082340723519, 5.108650246643361, -8.489223572642107, -0.55629676879405199, 0.39743760848879944, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
            cd = [[0.0, 10.7, -12.899999999999999, 7.75, -1.75, -1.5750000000000002, -7.21875, 5.362500000000001, 0.0, 0.0, 0.0, 0.0, 66.019433593750009, 0.0],
                 [-26.8, 17.9, -5.715767664977294, -18.98354550656963, 4.427188724235731, 1.016658128379447, -3.780624948338568, -7.093920702791934, 6.703125, -12.740346687426538, 0.0, 0.0, 0.0, 0.0],
                 [-46.938576885116575, -11.518137870333034, 2.0784609690826525, -0.7745966692414834, -36.00069443774661, -10.759298304257577, -8.966539361704715, -11.584323998404052, -28.041183701806126, -10.865004161512665, -21.069192030396437, -40.904797337487778, 0.0, 0.0],
                 [25.71964229922337, -0.7745966692414834, 1.818309654596818, -8.221921916437788, 8.366600265340756, 0.0, 23.910771631212572, 26.621900677884089, 20.709786664084085, 33.193135997427994, 49.584102137826925, 32.796800809779043, 64.922081265302026, 0.0],
                 [-3.320391543176798, 20.73953049131055, 6.274950199005566, -3.9194028563034955, -3.1059418861272987, 2.884088894261062, -6.002548286977789, 2.4697861749552334, -5.347243923567074, -28.187869185844487, -11.687084953567938, 0.0, -48.691560948976523, 0.0],
                 [4.066632513517788, 12.296340919151518, -5.176833914179592, 7.321148731585772, 0.070156076002011389, 2.6659308880764323, 0.69804414258698555, -2.4697861749552334, 5.932234507333641, -6.738189537419342, -7.391561532231577, 0.0, 0.0, 0.0],
                 [0.0, -32.877310992917295, -6.973975059103666, 0.54568620790707179, 2.3268138086232852, 0.87320127619581489, 1.007539934072094, -2.1796421366247265, 1.373045485863451, 1.739793057467611, -4.132008511485578, 0.0, 20.829891011946017, 0.0],
                 [24.828722459771768, 14.480404998005064, -4.095677027366783, -1.2348930874776167, -4.322125806171658, 0.24218245962496965, 0.06472598492877496, 0.19417795478632488, -1.0027306467840702, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [-20.109375, 16.824710221083674, 12.42587199845045, 16.041731770701222, -1.4830586268334103, -1.373045485863451, 0.75204798508805271, 0.0, 0.18801199627201318, -0.51679554634182934, -1.63651923008246, 0.0, 0.0, 0.0],
                 [-25.480693374853075, -10.865004161512665, -16.596567998713997, 5.6375738371688975, 3.369094768709671, 0.0, -1.506704985094751, 1.0335910926836587, 0.1827148176526571, -0.06090493921755237, -0.26547847521179802, 0.0, 0.0, 0.0],
                 [24.3286073807146, -21.069192030396437, 0.0, 0.0, -14.783123064463155, 4.132008511485578, -2.0043185339772047, -1.63651923008246, 0.26547847521179802, -0.059362791713657326, -0.11872558342731465, -0.27203448649173201, 0.0, 0.0],
                 [0.0, 40.904797337487778, 0.0, 23.951396823359573, 0.0, 0.0, 4.9604352946160635, 0.0, -0.88149248398872548, 0.0, -0.057997947393467898, -0.057997947393467898, 0.0, 0.0],
                 [0.0, 0.0, -64.922081265302026, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
            k = [[0.0, -0.0, 0.33333333333333331, 0.26666666666666666, 0.25714285714285712, 0.25396825396825395, 0.25252525252525254, 0.25174825174825177, 0.25128205128205128, 0.25098039215686274, 0.25077399380804954, 0.25062656641604009, 0.25051759834368531],
                 [0.0, 1.0, 0.0, 0.20000000000000001, 0.22857142857142856, 0.23809523809523808, 0.24242424242424243, 0.24475524475524477, 0.24615384615384617, 0.24705882352941178, 0.24767801857585139, 0.24812030075187969, 0.2484472049689441],
                 [0.0, 0.0, -1.0, 0.0, 0.14285714285714285, 0.19047619047619047, 0.21212121212121213, 0.22377622377622378, 0.23076923076923078, 0.23529411764705882, 0.23839009287925697, 0.24060150375939848, 0.24223602484472051],
                 [0.0, 0.0, 0.0, -0.33333333333333331, 0.0, 0.11111111111111111, 0.16161616161616163, 0.1888111888111888, 0.20512820512820512, 0.21568627450980393, 0.22291021671826625, 0.22807017543859648, 0.2318840579710145],
                 [0.0, 0.0, 0.0, 0.0, -0.20000000000000001, 0.0, 0.090909090909090912, 0.13986013986013987, 0.16923076923076924, 0.18823529411764706, 0.20123839009287925, 0.21052631578947367, 0.21739130434782608],
                 [0.0, 0.0, 0.0, 0.0, 0.0, -0.14285714285714285, 0.0, 0.076923076923076927, 0.12307692307692308, 0.15294117647058825, 0.17337461300309598, 0.18796992481203007, 0.19875776397515527],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.11111111111111111, 0.0, 0.066666666666666666, 0.10980392156862745, 0.13931888544891641, 0.16040100250626566, 0.17598343685300208],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.090909090909090912, 0.0, 0.058823529411764705, 0.099071207430340563, 0.12781954887218044, 0.14906832298136646],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.076923076923076927, 0.0, 0.052631578947368418, 0.090225563909774431, 0.11801242236024845],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.066666666666666666, 0.0, 0.047619047619047616, 0.082815734989648032],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.058823529411764705, 0.0, 0.043478260869565216],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.052631578947368418, 0.0],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.047619047619047616]]
            fn = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
            fm = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
        
        return [epoch, maxord, tc, sp, cp, pp, p, dp, re, a2, b2, c2, a4, c4, c, cd, k, fn, fm]
    
    def GeoMag(self, dlat, dlon, elevation, time, coefficients):
        # NOAA Magnetic Declination calculator
        # written by: Christopher Weiss (cmweiss@gmail.com), source: https://pypi.python.org/pypi/geomag
        
        epoch, maxord, tc, sp, cp, pp, p, dp, re, a2, b2, c2, a4, c4, c, cd, k, fn, fm = coefficients
        time = time.year+((time - datetime.date(time.year,1,1)).days/365.0)
        alt = elevation/1000   # to kilometers
        
        otime = oalt = olat = olon = -1000.0
        
        dt = time - epoch
        glat = dlat
        glon = dlon
        rlat = math.radians(glat)
        rlon = math.radians(glon)
        srlon = math.sin(rlon)
        srlat = math.sin(rlat)
        crlon = math.cos(rlon)
        crlat = math.cos(rlat)
        srlat2 = srlat*srlat
        crlat2 = crlat*crlat
        sp[1] = srlon
        cp[1] = crlon
        
        # convert from geodetic coords. to spherical coords.
        if (alt != oalt or glat != olat):
            q = math.sqrt(a2-c2*srlat2)
            q1 = alt*q
            q2 = ((q1+a2)/(q1+b2))*((q1+a2)/(q1+b2))
            ct = srlat/math.sqrt(q2*crlat2+srlat2)
            st = math.sqrt(1.0-(ct*ct))
            r2 = (alt*alt)+2.0*q1+(a4-c4*srlat2)/(q*q)
            r = math.sqrt(r2)
            d = math.sqrt(a2*crlat2+b2*srlat2)
            ca = (alt+d)/r
            sa = c2*crlat*srlat/(r*d)
        
        if (glon != olon):
            for m in range(2,maxord+1):
                sp[m] = sp[1]*cp[m-1]+cp[1]*sp[m-1]
                cp[m] = cp[1]*cp[m-1]-sp[1]*sp[m-1]
        
        aor = re/r
        ar = aor*aor
        br = bt = bp = bpp = 0.0
        for n in range(1,maxord+1):
            ar = ar*aor
            m=0
            D3=1
            D4=(n+m+1)
            while D4>0:
            
                # compute unnormalized associated legendre polynomials and derivatives via recursion relations
                if (alt != oalt or glat != olat):
                    if (n == m):
                        p[m][n] = st * p[m-1][n-1]
                        dp[m][n] = st*dp[m-1][n-1]+ct*p[m-1][n-1]
                    
                    elif (n == 1 and m == 0):
                        p[m][n] = ct*p[m][n-1]
                        dp[m][n] = ct*dp[m][n-1]-st*p[m][n-1]
                    
                    elif (n > 1 and n != m):
                        if (m > n-2):
                            p[m][n-2] = 0
                        if (m > n-2):
                            dp[m][n-2] = 0.0
                        p[m][n] = ct*p[m][n-1]-k[m][n]*p[m][n-2]
                        dp[m][n] = ct*dp[m][n-1] - st*p[m][n-1]-k[m][n]*dp[m][n-2]
                
                # time adjust the gauss coefficients
                if (time != otime):
                    tc[m][n] = c[m][n]+dt*cd[m][n]
                    if (m != 0):
                        tc[n][m-1] = c[n][m-1]+dt*cd[n][m-1]
                
                # accumulate terms of the spherical harmonic expansions
                par = ar*p[m][n]
                
                if (m == 0):
                    temp1 = tc[m][n]*cp[m]
                    temp2 = tc[m][n]*sp[m]
                else:
                    temp1 = tc[m][n]*cp[m]+tc[n][m-1]*sp[m]
                    temp2 = tc[m][n]*sp[m]-tc[n][m-1]*cp[m]
                
                bt = bt-ar*temp1*dp[m][n]
                bp = bp + (fm[m] * temp2 * par)
                br = br + (fn[n] * temp1 * par)
                
                # special case:  north/south geographic poles
                if (st == 0.0 and m == 1):
                    if (n == 1):
                        pp[n] = pp[n-1]
                    else:
                        pp[n] = ct*pp[n-1]-k[m][n]*pp[n-2]
                    parp = ar*pp[n]
                    bpp = bpp + (fm[m]*temp2*parp)
                    
                D4=D4-1
                m=m+1
        
        if (st == 0.0):
            bp = bpp
        else:
            bp = bp/st
        
        # rotate magnetic vector components from spherical to geodetic coordinates
        bx = -bt*ca-br*sa
        by = bp
        bz = bt*sa-br*ca
        
        # compute declination (dec), inclination (dip) and total intensity (ti)
        bh = math.sqrt((bx*bx)+(by*by))
        ti = math.sqrt((bh*bh)+(bz*bz))
        dec = math.degrees(math.atan2(by,bx))
        dip = math.degrees(math.atan2(bz,bh))
        
        # compute magnetic grid variation if the current geodetic position is in the arctic or antarctic (i.e. glat > +55 degrees or glat < -55 degrees)
        # otherwise, set magnetic grid variation to -999.0
        gv = -999.0
        if (math.fabs(glat) >= 55.):
            if (glat > 0.0 and glon >= 0.0):
                gv = dec-glon
            if (glat > 0.0 and glon < 0.0):
                gv = dec+math.fabs(glon);
            if (glat < 0.0 and glon >= 0.0):
                gv = dec+glon
            if (glat < 0.0 and glon < 0.0):
                gv = dec-math.fabs(glon)
            if (gv > +180.0):
                gv = gv - 360.0
            if (gv < -180.0):
                gv = gv + 360.0
        
        otime = time
        oalt = alt
        olat = glat
        olon = glon
        
        return dec, dip, ti, bx, by, bz, time


try:
    checkIn.checkForUpdates(LB= True, HB= False, OpenStudio = False, template = False)
except:
    # no internet connection
    pass

now = datetime.datetime.now()

def checkGHPythonVersion(target = "0.6.0.3"):
    
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

GHPythonTargetVersion = "0.6.0.3"

try:
    if not checkGHPythonVersion(GHPythonTargetVersion):
        assert False
except:
    msg =  "Ladybug failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    checkIn.letItFly = False
    sc.sticky["ladybug_release"] = False


if checkIn.letItFly:
    # let's just overwrite it every time
    #if not sc.sticky.has_key("ladybug_release"):
    sc.sticky["ladybug_release"] = versionCheck()       
    sc.sticky["ladybug_Preparation"] = Preparation
    sc.sticky["ladybug_Mesh"] = MeshPreparation
    sc.sticky["ladybug_RunAnalysis"] = RunAnalysisInsideGH
    sc.sticky["ladybug_Export2Radiance"] = ExportAnalysis2Radiance
    sc.sticky["ladybug_ResultVisualization"] = ResultVisualization
    sc.sticky["ladybug_SunPath"] = Sunpath
    sc.sticky["ladybug_SkyColor"] = Sky
    sc.sticky["ladybug_Vector"] = Vector
    sc.sticky["ladybug_ComfortModels"] = ComfortModels
    sc.sticky["ladybug_WindSpeed"] = WindSpeed
    sc.sticky["ladybug_Photovoltaics"] = Photovoltaics
        
    if sc.sticky.has_key("ladybug_release") and sc.sticky["ladybug_release"]:
        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Ladybug is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Ladybug_DefaultFolder"]