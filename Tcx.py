import sys
import time
from datetime import datetime,timedelta
import xml.sax
from xml.dom.minidom import parse
from xml.dom import minidom
from pprint import pprint

from lxml import etree
import xml.etree.ElementTree as ET

from lxml import objectify
#ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
#ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'        
nso = {
    'ts': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'g': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
}
#edited_folder = 'edited';
#originals_folder = 'originals'
ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
ns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
xsi="http://www.w3.org/2001/XMLSchema-instance"
ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1"

class Tcx():
    def __init__(self, **data):
        self.ns = {
            'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
            'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        }

        #TODO check if exists
        self.inputFile = data['inputFile']
        #TODO created default
        self.outputFile = data['outputFile']
        #TODO abort if empty
        self.newActivityTime = data['newActivityTime']
        #TODO use file value if not available
        self.newActivityDate = data['newActivityDate']
        #TODO
        self.newActivityHr = data['newActivityHr']

        tree = objectify.parse(self.inputFile)
        self.root = tree.getroot()
        self.activity = self.root.Activities.Activity
        self.offsetTimeDiff = self.getOffsetTimeDiff()
        self.diffInPercent = self.calculateDiffInPercent()
        self.hRDiffCoeficient = self.calculatehRDiffCoeficient()
        
    def calculateDiffInPercent(self):
        return round(float(self.getTimeInSeconds(self.newActivityTime) / self.duration), 3)   

    def calculatehRDiffCoeficient(self):
        if self.newActivityHr.isnumeric():
            return round(int(self.newActivityHr) / self.heartRate, 2)
        else:
            return 1

    @property
    def activityType(self):
        return self.activity.attrib['Sport'].lower()

    @property    
    def duration(self):
            """Returns duration of workout in seconds."""
            return sum(lap.TotalTimeSeconds for lap in self.activity.Lap)

    @property    
    def distance(self):
            """Returns distance of workout in meteres."""
            return sum(lap.DistanceMeters for lap in self.activity.Lap)

    @property    
    def heartRate2(self):
            """Returns distance of workout in meteres."""
            return sum(lap.DistanceMeters for lap in self.activity.Lap)        

    @property    
    def heartRate1(self):
            """Returns heart rate of workout in bpm."""
            return sum(lap.AverageHeartRateBpm.Value for lap in self.activity.Lap)

    @property
    def heartRate(self):
        ns = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
        _sum = sum([int(x.text) for x in self.root.xpath('//ns:HeartRateBpm/ns:Value', namespaces={'ns': ns})])
        _len = len([int(x.text) for x in self.root.xpath('//ns:HeartRateBpm/ns:Value', namespaces={'ns': ns})])

        return int(round(_sum / _len))
                      
    
    @property    
    def diff(self):
        return self.duration - self.getTimeInSeconds(self.newActivityTime)

    def manipulate(self):
        newData = self.loadNewData()
        self.saveNewFile(newData)

    def loadNewData(self):
        newData = {}
        tcxFile = ET.parse(self.inputFile)
        root = tcxFile.getroot()
        activity = root.find('./tcx:Activities/tcx:Activity', self.ns)
        activityId = root.find('./tcx:Activities/tcx:Activity/tcx:Id', self.ns)
        newData['ActivityId'] = self.newActivityDate if self.newActivityDate != None else activityId.text
        newData['Lap'] = self.processLaps(activity)
        
        return newData

    def processLaps(self, activity):
        laps = []
        oldLap = None
        for lap in activity.iterfind('./tcx:Lap', self.ns):
            lastTrackpoint = {}
            newLap = {}
            newLap['TotalTimeSeconds'] = self.newTimeInSeconds(
                lap.find('./tcx:TotalTimeSeconds', self.ns).text
            )
            if oldLap == None:
                newLap['StartTime'] = lap.attrib['StartTime']
                newLap['Track'] = []
            else:
                #get last trackpoint time of previous lap
                newLap['StartTime'] = oldLap['Track'][-1]['Time']
            
            newLap['DistanceMeters'] = lap.find('./tcx:DistanceMeters', self.ns).text
            newLap['Calories'] = lap.find('./tcx:Calories', self.ns).text
            newLap['MaximumSpeed'] = lap.find('./tcx:MaximumSpeed', self.ns).text
            
            if (lap.find('./tcx:AverageHeartRateBpm', self.ns) != None):
                newLap['AverageHeartRateBpm'] = self.newHeartRate(
                    lap.find('./tcx:AverageHeartRateBpm/tcx:Value', self.ns).text
                )
            
            if (lap.find('./tcx:MaximumHeartRateBpm', self.ns) != None):
                newLap['MaximumHeartRateBpm'] = self.newHeartRate(
                    lap.find('./tcx:MaximumHeartRateBpm/tcx:Value', self.ns).text
                )
            newLap['Intensity'] = lap.find('./tcx:Intensity', self.ns).text
            newLap['TriggerMethod'] = lap.find('./tcx:TriggerMethod', self.ns).text
            newLap['Track'] = self.processTrackpoints(lap, oldLap, newLap)
            
            #TODO 
            if lap.find('./tcx:Extensions/ns3:LX', self.ns) != None:
                newLap['Extensions'] = {}
                newLap['Extensions']['AvgSpeed'] = lap.find('./tcx:Extensions/ns3:LX/ns3:AvgSpeed', self.ns).text
                newLap['Extensions']['AvgRunCadence'] = lap.find('./tcx:Extensions/ns3:LX/ns3:AvgRunCadence', self.ns).text
                newLap['Extensions']['MaxRunCadence'] = lap.find('./tcx:Extensions/ns3:LX/ns3:MaxRunCadence', self.ns).text

            laps.append(newLap)
            oldLap = newLap

        return laps        
        
    def processTrackpoints(self, lap, oldLap, newLap):
        trackpoints = []
        track = lap.find('./tcx:Track', self.ns)
        updatedOldTrackpoint = None
        originalOldTrackpoint = None
        for index,trackpoint in enumerate(track.iterfind('./tcx:Trackpoint', self.ns)):
            newTrackpoint = {}
            if updatedOldTrackpoint == None:
                newTrackpoint['Time'] = newLap['StartTime']#trackPoint.find('./tcx:Time', self.ns).text
            else:
                newTrackpoint['Time'] = self.newDatetime(
                    trackpoint.find('./tcx:Time', self.ns).text,
                    updatedOldTrackpoint['Time'],
                    originalOldTrackpoint.find('./tcx:Time', self.ns).text
                )

            if trackpoint.find('./tcx:DistanceMeters', self.ns) != None:
                newTrackpoint['DistanceMeters'] = trackpoint.find('./tcx:DistanceMeters', self.ns).text
            
            if trackpoint.find('./tcx:Position', self.ns) != None:
                newTrackpoint['Position'] = {}
                newTrackpoint['Position']['LatitudeDegrees'] = trackpoint.find('./tcx:Position/tcx:LatitudeDegrees', self.ns).text    
                newTrackpoint['Position']['LongitudeDegrees'] = trackpoint.find('./tcx:Position/tcx:LongitudeDegrees', self.ns).text
            
            if trackpoint.find('./tcx:AltitudeMeters', self.ns) != None:
                newTrackpoint['AltitudeMeters'] = trackpoint.find('./tcx:AltitudeMeters', self.ns).text
            
            if trackpoint.find('./tcx:HeartRateBpm', self.ns) != None:
                newTrackpoint['HeartRateBpm'] = self.newHeartRate(
                    trackpoint.find('./tcx:HeartRateBpm/tcx:Value', self.ns).text
                )

            newTrackpoint['Extensions'] = {}

            if trackpoint.find('./tcx:Extensions/ns3:TPX/ns3:Speed', self.ns) != None:
                newTrackpoint['Extensions']['Speed'] = trackpoint.find('./tcx:Extensions/ns3:TPX/ns3:Speed', self.ns).text

            if trackpoint.find('./tcx:Extensions/ns3:TPX/ns3:RunCadence', self.ns) != None:
                newTrackpoint['Extensions']['RunCadence'] = trackpoint.find('./tcx:Extensions/ns3:TPX/ns3:RunCadence', self.ns).text
                    
            trackpoints.append(newTrackpoint)
            originalOldTrackpoint = trackpoint
            updatedOldTrackpoint = newTrackpoint
            
        return trackpoints

    def parse(self, tag, path):
        if (tag.find(path, self.ns) != None):
            return tag.find(path).text
        else:
            return ''

    def saveNewFile(self, data):
        root = ET.Element('TrainingCenterDatabase')
        # Tell the library to set up the long element names.

        root.set(
            'xsi:schemaLocation',
            ' '.join([
                'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd',
            ])
        )
        root.set('xmlns', 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2')
        root.set('xmlns:ns2', 'http://www.garmin.com/xmlschemas/UserProfile/v2')
        root.set('xmlns:ns3', 'http://www.garmin.com/xmlschemas/ActivityExtension/v2')
        root.set('xmlns:ns4', 'http://www.garmin.com/xmlschemas/ProfileExtension/v1')
        root.set('xmlns:ns5', 'http://www.garmin.com/xmlschemas/ActivityGoals/v1')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        activities = ET.SubElement(root, 'Activities')
        activity = ET.SubElement(activities, 'Activity')
        activity.set('Sport', 'Running')
        activityId = ET.SubElement(activity, 'Id')
        activityId.text = data['ActivityId']
        for item in data['Lap']:
            lap = ET.SubElement(activity, 'Lap')
            offsetTime = self.getOffsetTime(item['StartTime'])
            lap.set('StartTime', offsetTime)
            totalTimeSeconds = ET.SubElement(lap, 'TotalTimeSeconds')
            totalTimeSeconds.text = item['TotalTimeSeconds']
            distanceMeters = ET.SubElement(lap, 'DistanceMeters')
            distanceMeters.text = item['DistanceMeters']
            maximumSpeed = ET.SubElement(lap, 'MaximumSpeed')
            maximumSpeed.text = item['MaximumSpeed']
            calories = ET.SubElement(lap, 'Calories')
            calories.text = item['Calories']
            intensity = ET.SubElement(lap, 'Intensity')
            intensity.text = item['Intensity']
            triggerMethod = ET.SubElement(lap, 'TriggerMethod')
            triggerMethod.text = item['TriggerMethod']
            #
            averageHeartRateBpm = ET.SubElement(lap, 'AverageHeartRateBpm')
            if 'AverageHeartRateBpm' in item.keys():
                value = ET.SubElement(averageHeartRateBpm, 'Value')
                value.text = item['AverageHeartRateBpm']
            #
            maxmumHeartRateBpm = ET.SubElement(lap, 'MaximumHeartRateBpm')
            if 'MaximumHeartRateBpm' in item.keys():
                value = ET.SubElement(maxmumHeartRateBpm, 'Value')
                value.text = item['MaximumHeartRateBpm']
            #
            track = ET.SubElement(lap, 'Track')
            for index,point in enumerate(item['Track']):
                if (index % 2) != 0:
                    continue
                trackpoint = ET.SubElement(track, 'Trackpoint')
                time = ET.SubElement(trackpoint, 'Time')
                offsetTime = self.getOffsetTime(point['Time'])
                time.text = offsetTime
                #
                if 'DistanceMeters' in point.keys():
                    distance = ET.SubElement(trackpoint, 'DistanceMeters')
                    distance.text = point['DistanceMeters']
                #
                if 'Position' in point.keys():
                    position = ET.SubElement(trackpoint, 'Position')
                    lat = ET.SubElement(position, 'LatitudeDegrees')
                    lat.text = point['Position']['LatitudeDegrees']
                    lng = ET.SubElement(position, 'LongitudeDegrees')
                    lng.text = point['Position']['LongitudeDegrees']
                #
                if 'AltitudeMeters' in point.keys():
                    alt = ET.SubElement(trackpoint, 'AltitudeMeters')
                    alt.text = point['AltitudeMeters']
                #
                if 'HeartRateBpm' in point.keys():
                    heartRateBpm = ET.SubElement(trackpoint, 'HeartRateBpm')
                    value = ET.SubElement(heartRateBpm, 'Value')
                    value.text = point['HeartRateBpm']
                #    
                extension = ET.SubElement(trackpoint, 'Extensions')
                tpx = ET.SubElement(extension, 'ns3:TPX')    
                if 'Speed' in point['Extensions'].keys():
                    speed = ET.SubElement(tpx, 'Speed')
                    speed.text = point['Extensions']['Speed']
                #    
                if 'RunCadence' in point['Extensions'].keys():
                    cadence = ET.SubElement(tpx, 'RunCadence')
                    cadence.text = point['Extensions']['RunCadence']

            if 'Extensions' in item.keys():
                extension = ET.SubElement(lap, 'Extensions')
                ns3Lx = ET.SubElement(extension, 'ns3:LX')
                avgSpeed = ET.SubElement(ns3Lx, 'AvgSpeed')
                avgSpeed.text = item['Extensions']['AvgSpeed']
                avgRunCadence = ET.SubElement(ns3Lx, 'AvgSpeed')
                avgRunCadence.text = item['Extensions']['AvgRunCadence']
                maxRunCadence = ET.SubElement(ns3Lx, 'MaxRunCadence')
                maxRunCadence.text = item['Extensions']['MaxRunCadence']
        
        # author = ET.SubElement(root, 'Author')
        # author.set('xsi:type', 'Application_t')
        # name = ET.SubElement(author, 'Name')
        # name.text = 'Connect Api'
        # build = ET.SubElement(author, 'Build')
        # version = ET.SubElement(build, 'Version')
        # versionMajor = ET.SubElement(version, 'VersionMajor')
        # versionMajor.text = '0'
        # versionMinor = ET.SubElement(version, 'VersionMinor')
        # versionMinor.text = '0'
        # buildMajor = ET.SubElement(version, 'BuildMajor')
        # buildMajor.text = '0'
        # buildMinor = ET.SubElement(version, 'BuildMinor')
        # buildMinor.text = '0'
        # langID = ET.SubElement(author, 'LangID')
        # langID.text = 'en'
        # partNumber = ET.SubElement(author, 'PartNumber')
        # partNumber.text = '006-D2449-00'

        orig_stdout = sys.stdout
        f = open(self.outputFile, 'w')
        sys.stdout = f

        print(minidom.parseString(ET.tostring(root)).toprettyxml())
        
        sys.stdout = orig_stdout
        f.close()

    def getOffsetTimeDiff(self):
        if self.newActivityDate == '':
            return 0

        generaleFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
        newTimestamp = int(datetime.strptime(self.newActivityDate, generaleFormat).strftime('%s'))
        oldTimestamp = int(datetime.strptime(self.activity.Id.text, generaleFormat).strftime('%s'))
        
        return int(newTimestamp - oldTimestamp)

    def getOffsetTime(self, oldTime):
        if self.offsetTimeDiff == 0:
            return oldTime

        generaleFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
        updateTime = datetime.strptime(oldTime, generaleFormat) + timedelta(seconds=self.offsetTimeDiff)
        
        return updateTime.strftime(generaleFormat)

    def newHeartRate(self, oldHeartRate):
        return str(int(int(oldHeartRate) * self.hRDiffCoeficient))

    def newDatetime(self, currentTime, updatedOldTime, originalOldTime):
        generaleFormat = '%Y-%m-%dT%H:%M:%S.%fZ'

        currentTimestamp = float(datetime.strptime(currentTime, generaleFormat).strftime('%s.%f'))
        updatedOldTimestamp = float(datetime.strptime(updatedOldTime, generaleFormat).strftime('%s.%f'))
        originalOldTimestamp = float(datetime.strptime(originalOldTime, generaleFormat).strftime('%s.%f'))
        ## FORMULA ##
        #(currentTime-oldTime)*percent+updatedOldTime

        newTime = (currentTimestamp - originalOldTimestamp)*self.diffInPercent + updatedOldTimestamp
        
        try:
            return datetime.fromtimestamp(newTime).strftime(generaleFormat)
        except OverflowError:
            print(OverflowError)
            exit()

    def newTimeInSeconds(self, currentTime):
        return str(round(float(currentTime) * self.diffInPercent, 1))   

    def getTimeInSeconds(self, timestr):
        ftr = [3600,60,1]

        return sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])

    def time_diff(self, timeStart, endTime):
        tdelta = datetime.strptime(endTime, FMT) - datetime.strptime(timeStart, FMT)
        print(tdelta)    
            
    def time_values(self):
        return [x.text for x in self.root.xpath('//ns:Time', namespaces={'ns': namespace})]

    def cadence_values(self):
        return [int(x.text) for x in self.root.xpath('//ns:RunCadence', namespaces={'ns': ns3})]

    def altitude_points(self):
        return [float(x.text) for x in self.root.xpath('//ns:AltitudeMeters', namespaces={'ns': namespace})]
            
    def laps_values(self):
        return [float(x.text) for x in self.root.xpath('//g:TotalTimeSeconds/text()', namespace={'ns': nso})]

    def hr_values(self):
        ns = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
        return [int(x.text) for x in self.root.xpath('//ns:HeartRateBpm/ns:Value', namespaces={'ns': ns})]

    @property
    def descent(self):
        """Returns descent of workout in meters"""
        total_descent = 0.0
        altitude_data = self.altitude_points()
        for i in range(len(altitude_data) - 1):
            diff = altitude_data[i+1] - altitude_data[i]
            if diff < 0.0:
                total_descent += abs(diff)

        return total_descent    

    @property
    def cadence_max(self):
        """Returns max cadence of workout"""
        cadence_data = self.cadence_values()
        return max(cadence_data)*2

class TcxHandler(xml.sax.ContentHandler):
    def __init__(self):
        print('test')
