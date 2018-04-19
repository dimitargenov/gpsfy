#!/usr/bin/python3

from Tcx import *
import argparse
#import tcxparser
#from lxml import etree

def parseArgs():
	parser = argparse.ArgumentParser(description='Process some params.')
	parser.add_argument('-i', '--input')
	parser.add_argument('-o', '--output')
	parser.add_argument('-r', '--result')
	parser.add_argument('-d', '--date')
	
	args = parser.parse_args()

	return [args.input,args.output,args.result,args.date]

if ( __name__ == "__main__"):
    arguments = parseArgs()
    params = {
    	'inputFile': arguments[0],
    	'outputFile': arguments[1],
    	'newActivityResult': arguments[2], 
    	'newActivityDate': arguments[3]
    }
    tcx = Tcx(**params)
