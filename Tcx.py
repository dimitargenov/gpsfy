import xml.sax
from xml.dom.minidom import parse
import xml.dom.minidom
from pprint import pprint

#import xml.etree.ElementTree as ET
import lxml.etree as ET

ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
edited_folder = 'edited';
originals_folder = 'originals'

class Tcx():
    def __init__(self, **data):
        #TODO check if exists
        self.inputFile = data['inputFile']
        #TODO created default
        self.outputFile = data['outputFile']
        #TODO abort if empty
        self.newActivityResult = data['newActivityResult']
        #TODO use file value if not available
        self.newActivityDate = data['newActivityDate']
        self.loadLaps()
        #result = self.garminize()
        #print(result)

    def loadLaps(self):
        tree = ET.parse(self.inputFile)
        root = tree.getroot()
        laps = []

        for lap in tree.iter("{%s}Lap"%ns1):
            print(lap)
            break
            lap.text = str(2*int(watts.text))

        return    
        for element in root.iter():
            if element.tag == '{%s}Lap' % ns1:
                for lap in element:
                    if lap.tag == '{%s}Track' % ns1:
                        for track in lap:
                            if track.tag == '{%s}Trackpoint' % ns1:
                                print(track.tag)
                                break
                        #process_trackpoint(child, lever)
                #laps.append(element)



    def garminize(self):
        laps = {}
        counter = 0
        totalDistance = 0
        totalTime = 0
        averageSpeed = 0.0

        for lap in self.laps:
            laps.update({
                'TotalTimeSeconds': lap.getElementsByTagName('TotalTimeSeconds')[0].tagName,
            #    'DistanceMeters': lap.getElementsByTagName('DistanceMeters'),
            #    'MaximumSpeed': lap.getElementsByTagName('MaximumSpeed'),
            })
            #totalDistance = totalDistance + float(lap.getElementsByTagName('DistanceMeters'))
            #totalTime += float(lap.getElementsByTagName('TotalTimeSeconds'))
            #averageSpeed = totalDistance / totalTime
            counter += 1
            continue

        return [totalDistance, totalTime, averageSpeed, laps]

class TcxHandler(xml.sax.ContentHandler):
    def __init__(self):
        print('test')