#!/usr/bin/python3

from Tcx import *
import argparse
#import tcxparser
#from lxml import etree

#python3 fake.py -i <input_file> -o <output_file> -d <date> -t <new_time> -b <new_hr> 
#python3 fake.py -i ~/Downloads/_Morning_Run\ \(31\).tcx -o ~/Downloads/test_new.tcx -d "2020-04-17T04:01:02.000Z" -t "00:09:03" -b 179

def parseArgs():
    parser = argparse.ArgumentParser(description='Process some params. Example: python3 fake.py -i <input_file> -o <output_file> -d <date> -t <new_time> -b <new_hr>')
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-t', '--new_time')
    parser.add_argument('-b', '--new_hr')
    parser.add_argument('-d', '--date')
    parser.add_argument('-st', '--strava')
    parser.add_argument('-ca', '--cadence')
    args = parser.parse_args()

    return [args.input,args.output,args.date,args.new_time,args.new_hr,args.strava,args.cadence]

if ( __name__ == "__main__"):
    arguments = parseArgs()
    
    params = {
    	'inputFile': arguments[0],
    	'outputFile': arguments[1],
    	'newActivityTime': arguments[3],
    	'newActivityDate': arguments[2],
        'newActivityHr': arguments[4],
        'forStrava': arguments[5],
        'cadence': arguments[6],
    }
    print ('## TCX Edit ##')
    print ('Input: %s \nOutput: %s \nNew Time: %s \nNew Hr: %s \nDate: %s\nCadence: %s\n'
     % (arguments[0],arguments[1],arguments[3],arguments[4],arguments[2],arguments[6]))
    tcx = Tcx(**params)
    tcx.manipulate()
