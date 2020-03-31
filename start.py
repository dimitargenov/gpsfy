#!/usr/bin/python3

from Tcx import *
import argparse
#import tcxparser
#from lxml import etree

#python3 start.py -i <input_file> -o <output_file> -d <date> -t <new_time> -b <new_hr> 

def parseArgs():
	parser = argparse.ArgumentParser(description='Process some params. Example: python3 start.py -i <input_file> -o <output_file> -d <date> -t <new_time> -b <new_hr>')
	parser.add_argument('-i', '--input')
	parser.add_argument('-o', '--output')
	parser.add_argument('-t', '--new_time')
	parser.add_argument('-b', '--new_hr')
	parser.add_argument('-d', '--date')
	
	args = parser.parse_args()


	return [args.input,args.output,args.date,args.new_time,args.new_hr]

if ( __name__ == "__main__"):
    arguments = parseArgs()
    
    params = {
    	'inputFile': arguments[0],
    	'outputFile': arguments[1],
    	'newActivityTime': arguments[3],
    	'newActivityDate': arguments[2],
        'newActivityHr': arguments[4]
    }
    print ('## TCX Edit ##')
    print ('Input: %s \nOutput: %s \nNew Time: %s \nNew Hr: %s \nDate: %s\n' % (arguments[0],arguments[1],arguments[3],arguments[4],arguments[2]))
    tcx = Tcx(**params)
    tcx.manipulate()
