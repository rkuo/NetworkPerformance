#!/usr/bin/env python
# vi: sw=4 ts=4:
#
# ---------------------------------------------------------------------------
#   Copyright (c) 2016 AT&T Intellectual Property
#
# ---------------------------------------------------------------------------
#

# Changelog:
#       Jan 14, 2015    Kaustubh Joshi          Initial version created
#       Jan 25, 2015    Paul Carver             Added initial collector
#       Apr 20, 2015    Hal McCaskey            Significant modifications

'''
netenv -- document environmental parameters of VM-based packet processing
    pipeline in a standardized JSON format to facilitate comparison across
    network benchmark results

@license:    license

@contact:    krj@research.att.com
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

#import paramiko         # SSH framework
#from novaclient.client import Client

from __builtin__ import True

__all__ = []
__version__ = 1.1
__date__ = '2016-04-20'

########### Begin DEFs ###################################
##########################################################

###################


# find absolute location of file
def find_bin_path(script) :
	import os
	#find absolute path of script and split on /
	path_elements=os.path.abspath(script).split("/")

	# build absolute path of script without script name
	bin_path="/"
	for i in range(1,len(path_elements) -1) :
		bin_path=bin_path + path_elements[i] + "/"

	# does Directory exist?
	if not os.path.isdir(bin_path) :
		print >> sys.stderr, "BIN PATH \"" +bin_path + "\" does not exist\nExiting now!"
		sys.exit(2)

	return bin_path



### Capture node name to build json file name

def get_node_name():
	try:
		cmd='uname -n'
		r = subprocess.check_output(cmd, shell=True)
	except subprocess.CalledProcessError, e:
		print "Error running command %s" % cmd
		print e.output
	else:
		node_name=r.replace("\n", "")
	return node_name

###################
### Is this server running Contrail and is Contrail using dpdk

def get_node_type():
	try:
		cmd='ps -aux|grep contrail-vrouter-dpdk'
		r = subprocess.check_output(cmd, shell=True)
	except subprocess.CalledProcessError, e:
		print "Error running command %s" % cmd
		print e.output
	else:
		node_type="unknown"
		if re.search("contrail-vrouter",r): node_type="contrail-vrouter"
		if re.search("contrail-vrouter-dpdk",r): node_type="contrail-vrouter-dpdk"
	return node_type


###################
### Define the main function block
### to be executed at end of this script with "if __name__ == "__main__":"

def cli_main(argv=None):
	'''Command line options.'''
	# MAIN BODY #
	import argparse
	import stat

	prog_name = os.path.basename(sys.argv[0])
	prog_ver = "v1.1"
	now = datetime.datetime.now()

	ver_str = '%%prog %s' % (prog_ver)
	desc = '''Get network environment in standardized JSON format for network benchmarking'''
	lic = "Copyright 2016 AT&T                                             \
			Licensed under the Apache License 2.0\n\
			http://www.apache.org/licenses/LICENSE-2.0p;"

	if argv is None:
		argv = sys.argv[1:]
	

	parser = argparse.ArgumentParser(epilog=desc, description=lic)
	parser.add_argument("-d", "--dest", default='../data',  help="Ouput File Destination, default = ../data")

	parser.add_argument("-r", "--regex", default='contrail|libvirt|qemu-system', help="Reg Exp for filtering on top process reporting, default = \"contrail|libvirt|qemu-system\"")

	args = parser.parse_args()

	script=sys.argv[0]
	top_proc_filter="\""+args.regex+"\""
	output_dest=args.dest+"/"

	bin_path=find_bin_path(script)
	print bin_path

	# does ouputfile Directory exist?
	if not os.path.isdir(args.dest) :
		print >> sys.stderr, "Ouput File Directory \"" +args.dest + "\" does not exist\nExiting now!"
		sys.exit(2)


	# does ouputfile Directory ve write permission?
	st=os.stat(output_dest)
	if not bool(st.st_mode & stat.S_IRGRP) :
		print >> sys.stderr, "Ouput File Directory \"" +args.dest + "\" does not have write permission\nExiting now!"
		sys.exit(3)
		


	print "Gathering Inventory"
	inventory = {}
	result= {}

	node_name=get_node_name();
	node_type=get_node_type();
	inventory['node_name']=get_node_name();
	inventory['node_type']=get_node_type();

	########Build specific node type - list of environment capture commands
	########If this is a Contrail Node add these commands to json data file
	########
	if re.search("contrail-vrouter",node_type): 
		type_commands=[ 'vrouter --info',
			'contrail-status',
			'vif --list',
			'vrouter --info',
			'vrmemstats',
			'vrfstats --dump',
			'flow -l |egrep "Created"',
			'dropstats',
			'vxlan --dump',
			bin_path+'parse_top.py -r '+ top_proc_filter ,
			'ps -aux |egrep "contrail|qemu-system"|grep -v grep']
	########Otherwise assmume OVS
	######## This is a place holder for now
	########
	else :
		type_commands=[ 'ovs-vsctl show|grep ovs_version',
			'top -b -n 1 -d 10|./parse_top.py "ovs" ']
	

	######## dump all bios info into a binary file
	######## command will show location of the binary file
	######## To conver to text "dmidecode --from-dump binary_file"
	########
	dmidecode_bin_file=output_dest+node_name+"_"+now.strftime('%Y-%m-%d_%H:%M:%S') +"_dmidecode" '.bin'
	command="dmidecode  --dump-bin "+  dmidecode_bin_file
	print "Running command %s" % command
	dmidecode_instr="BIOS Setting, use-\> dmidecode -t X --from-dump  "+ dmidecode_bin_file+" \<- where X=type 0,1,2,..."
	try:
		r = subprocess.check_output(command, shell=True)
	except subprocess.CalledProcessError, e:
			print "Error running command %s" % command
	#sys.exit()

	######## Place all kernel parameters accessible via sysctl in a file
	######## command will show location of the text file
	########
	sysctl_file=output_dest+node_name+"_"+now.strftime('%Y-%m-%d_%H:%M:%S') +"_sysctl" '.txt'
	command="sysctl -a > " +sysctl_file
	print "Running command %s" % command
	sysctl_instr="Kernel Parameters in "+sysctl_file+" in txt format"
	try:
		r = subprocess.check_output(command, shell=True)
	except subprocess.CalledProcessError, e:
			print "Error running command %s" % command
	########Build list of generic environment capture commands
	########
	commands = ['uname -a',
			'echo ' + dmidecode_instr,
			'echo ' + sysctl_instr,
			'ntpq -p',
			'ntpq -pn',
			'lscpu',
			'dmidecode -t 1|grep Product',
			'dmidecode -t 4|egrep "Socket Designation|Version|Core Count|Thread Count"',
			'lspci|grep "Ethernet controller"',
			'netstat',
			'ifconfig',
			'iptables --list',
			'ip link',
			'ip a']

	########Run commands and place in a dictionary for later writing to a json file
	########Command is the hash key for the dictionary "inventory{}"
	########Generic commands
	########
	for command in commands:
		print "Running command %s" % command
		try:
			r = subprocess.check_output(command, shell=True)
		except subprocess.CalledProcessError, e:
			print "Error running command %s" % command
			print e.output
		else:
			inventory[command] = r

	########Type Specific commands
	########
	for command in type_commands:
		print "Running command %s" % command
		try:
			r = subprocess.check_output(command, shell=True)
		except subprocess.CalledProcessError, e:
			print "Error running command %s" % command
			print e.output
		else:
			inventory[command] = r

	print "Done running commands"

	########Create json file and dump inventory
	########
	json_file_name=output_dest+node_name+"_"+now.strftime('%Y-%m-%d_%H:%M:%S') + '.json'
	with open(json_file_name, 'w+') as f:
	 	json.dump(inventory, f, indent=4)

	########Print to stdout the loactions of the files created
	########
	print "output found in following files"
	print json_file_name
	print dmidecode_bin_file
	print sysctl_file
	print dmidecode_instr
	print sysctl_instr

########## END OF DEFs###############################
#####################################################


####### Execute Main Function Block
###

if __name__ == "__main__":
    sys.exit(cli_main())

