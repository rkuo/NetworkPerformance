#!/usr/bin/env python
# vi: sw=4 ts=4:
#
# ---------------------------------------------------------------------------
#   Copyright (c) 2016 AT&T Intellectual Property
#
# ---------------------------------------------------------------------------
#

# Changelog: 	
#	Apr 20, 2016	Hal McCaskey		initial version

'''
netenv -- Convert json format files creatred with get_env.py to text format 
	   output to stdout, several option use -h to explore


@license:    license

@contact:    h2727@.att.com
@deffield    updated: Updated
'''

import sys
import os
import re

from collections import deque

import subprocess
import json
import datetime

import logging          # Logging


from __builtin__ import True

__all__ = []
__version__ = 0.1
__date__ = '2016-04-20'



def cli_main(argv=None):
	'''Command line options.'''
	import os
	import argparse

	prog_name = os.path.basename(sys.argv[0])
	prog_ver = "v1.0"

	ver_str = '%%prog %s' % (prog_ver)
	desc = '''Convert network environment in standardized JSON format created by get_env.py to text'''
	lic = "Copyright 2016 AT&T                                             \
			Licensed under the Apache License 2.0\n\
			http://www.apache.org/licenses/LICENSE-2.0p;"

	if argv is None:
		argv = sys.argv[1:]

	parser = argparse.ArgumentParser(epilog=desc, description=lic)
	parser.add_argument("-f", "--file",  help="json file created by get_env.py", required=True)
	parser.add_argument("-l", "--list", action='store_true',  help="List of Commands with data in the json file",required=False)
	parser.add_argument("-i", "--indx", default=False,  help="Display the text output of this one command" )

	args = parser.parse_args()

	file_name=args.file
	list_all=args.list
	indx=args.indx

	#print file_name, list_all, cmd
	#sys.exit()
       
	cmd_index={}
	index_cmd={}
	with open(file_name, 'r') as f:
		result= json.load(f)

	index=1
	for command in sorted(result.keys()) : 
		cmd_index[command]=index
		index_cmd[index]=command
		index+=1

	if list_all :
		print "\nIndex to Commands in file "+file_name+"\n"
		for command in sorted(result.keys()) : 
			print '%3d' % cmd_index[command], command
				
	elif indx:  
		cmd=index_cmd[int(indx)]
		print "\nOutput from command "+cmd+" in file "+file_name+"\n"
		if cmd in  result.keys() : print  result[cmd]
		else: print cmd,"Not Recognized"
	else: 
		for command in result.keys() : print  result[command]

if __name__ == "__main__":
	sys.exit(cli_main())

