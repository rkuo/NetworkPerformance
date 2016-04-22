#!/usr/bin/env python
# vi: sw=4 ts=4:
#
# ---------------------------------------------------------------------------
#   Copyright (c) 2016 AT&T Intellectual Property
#
# ---------------------------------------------------------------------------
#

# Changelog:
#       Apr 20, 2015    Hal McCaskey            Initial Version

'''
parse_top -- parse top batched output into a pipe delimited format
		required 
			special top field format found in .toprc (.toprc shuld be placed in $HOME)
			header format configuration in hdr.py (in current directory)
		example
 			./parse_top.py -r "contrail|qemu-system"

@license:    license

@contact:    hm2727@.att.com
@deffield    updated: Updated
'''

# modules that MUST be imported are :

import time as tm
import re
import sys
import array

CPU_NODE={} # dictionary(s) declared ouside of def are global



###### EXAMPLE TOP OUTPUT using .toprc###################

#top - 18:01:38 up 88 days, 2:16, 27 users, load average: 0.00, 0.02, 0.05
#Tasks: 996 total, 1 running, 995 sleeping, 0 stopped, 0 zombie
#%Cpu(s): 0.0 us, 0.1 sy, 0.3 ni, 99.6 id, 0.0 wa, 0.0 hi, 0.0 si, 0.0 st
#KiB Mem: 10566300+total, 87667360 used, 96896262+free, 1046412 buffers
#KiB Swap: 20971516 total, 0 used, 20971516 free. 73720736 cached Mem
#
#PID USER PR NI VIRT RES SHR S %CPU %MEM TIME+ COMMAND
#44571 hom 20 0 124224 2172 1052 R 20.6 0.0 0:00.07 top
#90 root 20 0 0 0 0 S 5.2 0.0 243:39.10 rcu_sched
#1 root 20 0 201740 16888 2396 S 0.0 0.0 13:03.60 systemd

#top -b -u!root
#  PID  P nTH USER      PR  NI    VIRT    RES    DATA    SHR S  %CPU %MEM     TIME+ COMMAND
#53992 44   1 hom       20   0  124368   2192    1788   1060 R  20.2  0.0   0:00.08 top
# 5858 15   1 ravic     20   0  140708   2368    1016   1052 S        0.0   0:09.80 sshd

################################################################################################

##### BEGIN OF FUNCTION DEFs

def cpu_node ():
	
	# create a map of cpu number(core) to NUMA node number using sytem call lscpu

	import subprocess
	import re
	#NUMA node0 CPU(s):     0-9,20-29
	#NUMA node1 CPU(s):     10-19,30-39

	
	p = subprocess.Popen('lscpu', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
	        line=line[:-1]
		line=line.strip(' ')
	        #convert mutiple spaces to single space
	        line=re.sub(' +',' ',line)
	        #now we can spit on single space
	        f = line.split(' ')
		
		number_numa=0
		if re.search("NUMA",line)and re.search("CPU",line) :
			number_numa+=1
			node=f[1]
			node_number=re.sub('node','',node)
			cpu_list=f[3].split(",")
			for i in range(0,len(cpu_list)) :
				if re.search("-",cpu_list[i]):
					cpu_range=cpu_list[i].split("-")
					range_start=cpu_range[0]
					range_end=cpu_range[1]
				else :
					range_start=cpu_list
					range_end=cpu_list
					
				for j in range(int(range_start),int(range_end)+1) :
					CPU_NODE[j]=node_number
		retval = p.wait()
	return number_numa




def parse_cpu (line):
	#0        1 
	#%Cpu(s): 0.0 us, 0.1 sy, 0.3 ni, 99.6 id, 0.0 wa, 0.0 hi, 0.0 si, 0.0 st
	# 0       1       2       3        4       5       6       7
	# 0.0 us, 0.1 sy, 0.3 ni, 99.6 id, 0.0 wa, 0.0 hi, 0.0 si, 0.0 st

	#Shows the percentage of CPU time in user mode, system mode, niced tasks, iowait and idle.
	#(Niced tasks are only those whose nice value is positive.)
	#Time spent in niced tasks will also be counted in system and user time, so the total will be more than 100%. 
	#hi: hardware irq (or) % CPU time spent servicing/handling hardware interrupts
	#si: software irq (or) % CPU time spent servicing/handling software interrupts
	#st: steal time - - % CPU time in involuntary wait by virtual cpu while hypervisor is servicing another processor 
	#(or) % CPU time stolen from a virtual machine

	us=""
	sy=""
	ni=""
	id=""
	wa=""
	hi=""
	si=""
	st=""
	
	
	f = line.split(':')
	scope=f[0].replace("%","")
	ff = f[1].split(',')
	for i in range(0,len(ff)):
		ff[i]=ff[i].strip(' ')
		if re.search(" ",ff[i]) :fff=ff[i].split(' ')
		if re.search("%",ff[i]) :fff=ff[i].split('%')
		if re.search("us",fff[1]) : us=fff[0]
		if re.search("sy",fff[1]) : sy=fff[0]
		if re.search("ni",fff[1]) : ni=fff[0]
		if re.search("id",fff[1]) : id=fff[0]
		if re.search("wa",fff[1]) : wa=fff[0]
		if re.search("hi",fff[1]) : hi=fff[0]
		if re.search("si",fff[1]) : si=fff[0]
		if re.search("st",fff[1]) : st=fff[0]
	
	return scope, us,sy,ni,id,wa,hi,si,st

def parse_top (line):
	time_str="-1" 
	seconds= -1
	users= -1
	lavg5= -1
	lavg10= -1
	lavg15= -1

	#top - 18:01:38 up 88 days, 2:16, 27 users, load average: 0.00, 0.02, 0.05
	f = line.split('-')
	scope=f[0].replace(" ","")
	#0    1  
	#top - 18:01:38 up 88 days, 2:16, 27 users, load average: 0.00, 0.02, 0.05
	ff = f[1].split(',')
	#0                    1     2         3                  4      5
	# 18:01:38 up 88 days, 2:16, 27 users, load average: 0.00, 0.02, 0.05

	for i in range(0,len(ff)):
		ff[i]=ff[i].strip(' ')
		if re.search('up',ff[i]):
			fff = ff[i].split(' ')
			time_str=str(fff[0])
		if re.search('user',ff[i]):
			fff = ff[i].split(' ')
			users=str(fff[0])
		if re.search('load average',ff[i]):
			fff = ff[i].split(':')
			lavg5=fff[1].strip(" ")
			lavg10=ff[i+1].strip(" ")
			lavg15=ff[i+2].strip(" ")
	time_arr=time_str.split(":")
	seconds=3600*int(time_arr[0]) + 60 * int(time_arr[1]) + int(time_arr[2])

	return scope,time_str, seconds, users,lavg5,lavg10,lavg15
	

def parse_tasks (line):

	total_tasks=""
	runing_tasks=""
	sleeping_tasks=""
	stopped_tasks=""
	zombie_tasks=""

	f = line.split(':')
	scope=f[0].replace(" ","_")
	#0      1  
	#Tasks: 996 total, 1 running, 995 sleeping, 0 stopped, 0 zombie
	ff = f[1].split(',')
	#0          1         2              3         4    
	# 996 total, 1 running, 995 sleeping, 0 stopped, 0 zombie
	
	for i in range(0,len(ff)):
		ff[i]=ff[i].strip(' ')
		if re.search('total',ff[i]):
			fff = ff[i].split(' ')
			total_tasks=fff[0]
		if re.search('running',ff[i]):
			fff = ff[i].split(' ')
			running_tasks=fff[0]
		if re.search('sleeping',ff[i]):
			fff = ff[i].split(' ')
			sleeping_tasks=fff[0]
		if re.search('stopped',ff[i]):
			fff = ff[i].split(' ')
			stopped_tasks=int(fff[0])
		if re.search('zombie',ff[i]):
			fff = ff[i].split(' ')
			zombie_tasks=int(fff[0])
	return  scope,total_tasks,running_tasks,sleeping_tasks,stopped_tasks,zombie_tasks
def parse_mem (line):
	total_mem= -1
	used_mem= -1
	free_mem= -1
	buffers= -1
	#KiB Mem: 10566300+total, 87667360 used, 96896262+free, 1046412 buffers
	f = line.split(':')
	scope=f[0].replace(" ","_")
	#0       1
	#KiB Mem: 10566300+total, 87667360 used, 96896262+free, 1046412 buffers
	ff = f[1].split(',')
	#0               1              2              3
	# 10566300+total, 87667360 used, 96896262+free, 1046412 buffers

	for i in range(0,len(ff)):
		ff[i]=ff[i].strip(' ')
		if re.search('total',ff[i]):
			fff = ff[i].split(' ')
			total_mem=fff[0]
		if re.search('used',ff[i]):
			fff = ff[i].split(' ')
			used_mem=fff[0]
		if re.search('free',ff[i]):
			fff = ff[i].split(' ')
			free_mem=fff[0]
		if re.search('buffers',ff[i]):
			fff = ff[i].split(' ')
			buffers=fff[0]
	return scope, total_mem,used_mem,free_mem,buffers

def parse_swap (line):
	total_swap=-1
	used_swap=-1
	free_swap=-1
	cached_mem=-1
	#KiB Swap: 20971516 total, 0 used, 20971516 free. 73720736 cached Mem
	f = line.split(':')
	scope=f[0].replace(" ","_")
	#0        1
	#KiB Swap: 20971516 total, 0 used, 20971516 free. 73720736 cached Mem
	ff = f[1].split(',')
	#0               1       2          
	# 20971516 total, 0 used, 20971516 free. 73720736 cached Mem
	for i in range(0,len(ff)):
		ff[i]=ff[i].strip(' ')
		if re.search('total',ff[i]):
			fff = ff[i].split(' ')
			total_swap=fff[0]
		if re.search('used',ff[i]):
			fff = ff[i].split(' ')
			used_swap=fff[0]
		if re.search('free',ff[i]):
			fff = ff[i].split('.')
			for i in range(0,len(fff)):
				fff[i]=fff[i].strip(' ')
				if re.search('free',fff[i]):
					ffff = fff[i].split(' ')
					free_swap=ffff[0]
				if re.search('cached',fff[i]):
					ffff = fff[i].split(' ')
					cached_mem=ffff[0]
	return   scope,total_swap, used_swap, free_swap, cached_mem

def time_2_seconds (data_field):
	if  re.search(":",data_field)  :
		time_txt=re.sub(" ","",data_field)
		t=time_txt.split(":")
		if len(t) == 1: seconds= +float(t[0])
		if len(t) == 2: seconds=float(t[0])*60 +float(t[1])
		if len(t) == 3: seconds=float(t[0])*3600 + float(t[1])*60 +float(t[2])
		res= str(seconds)
		return res
	return ""
def get_top_output(top_args):
	import subprocess
	try:
		#cmd=' top -b -n 1 -d 10'
		cmd=' top -b '+top_args
		r = subprocess.check_output(cmd, shell=True)
	except subprocess.CalledProcessError, e:
		print "Error running command %s" % cmd
		print e.output
        return r
	

##### END OF FUNCTION DEFs


###### BEGIN MAIN BLOCK DEF


def cli_main(argv=None):
	
	import hdr as my
	import argparse
	import os

	lic=" "
	desc=" "

	prog_name = os.path.basename(sys.argv[0])
	prog_ver = "v1.0"

	ver_str = '%%prog %s' % (prog_ver)
	desc = '''Capture System Resource Usage Snapshot via top'''
	lic = "Copyright 2016 AT&T                                             \
			Licensed under the Apache License 2.0\n\
			http://www.apache.org/licenses/LICENSE-2.0p;"

	if argv is None:
		argv = sys.argv[1:]

	parser = argparse.ArgumentParser(epilog=desc, description=lic)

	parser.add_argument("-r", "--regex", default='.', help="Reg Exp for filtering on top process reporting")
	parser.add_argument("-t", "--top",default=" -n 1 -d 1",  help="optional arguments for top command -b is hardcoded", required=False)

	args = parser.parse_args()
	top_proc_filter=args.regex
	top_args=args.top
	print  top_proc_filter, top_args
	
	TOP={}
	TASKS={}
	CPU={}
	NCPU={}
	MEM={}
	SWAP={}
	PROC={}
	PROC_FOUND={}
	proc_hdr=""
	
	print "grep for " +  top_proc_filter
	
	
	# populate cpu NUMA node table
	number_numa=cpu_node()
	
	
	for line in get_top_output(top_args).split("\n") :
		line=line[:-1]
		
		if len(line) < 10 :continue	
	
		if re.search("top - ",line):
			scope,time,seconds,users,lavg5,lavg10,lavg15=parse_top(line)
			TOP[seconds]="|".join([str(time),str(users),str(lavg5),str(lavg10),str(lavg15)])
			#print scope,  TOP[seconds]
		elif re.search("Tasks: ",line):
			scope,total_tasks,running_tasks,sleeping_tasks,stopped_tasks,zombie_tasks=parse_tasks(line)
			TASKS[seconds]="|".join([str(time),str(total_tasks),str(running_tasks),str(sleeping_tasks),str(stopped_tasks),str(zombie_tasks)])
			#print scope, TASKS[seconds]
		elif re.search("Cpu|Node",line):
			scope,us,sy,ni,id,wa,hi,si,st=parse_cpu(line)
			if re.search("Cpu",scope) :
				CPU[seconds]="|".join([str(time),us,sy,ni,id,wa,hi,si,st])
				#print scope,CPU[seconds]
				if number_numa == 1 :
					key=("Node0",seconds)
					NCPU[key]="|".join([us,sy,ni,id,wa,hi,si,st])
			else:
				scope=re.sub(" ","",scope)
				key=(scope,seconds)
				NCPU[key]="|".join([str(time),us,sy,ni,id,wa,hi,si,st])
				#print scope,NCPU[key]
				
	
		elif re.search("Mem:",line):
			mem_scope,total_mem,used_mem,free_mem,buffers=parse_mem(line)
			MEM[seconds]="|".join([str(time),str(total_mem),str(used_mem),str(free_mem),str(buffers)])
			#print scope,  MEM[seconds]
	
		elif re.search("Swap:",line):
			swap_scope,total_swap, used_swap, free_swap, cached_mem=parse_swap(line)
			SWAP[seconds]="|".join([str(time),str(total_swap), str(used_swap), str(free_swap), str(cached_mem)])
			#print scope, SWAP[seconds]
		elif re.search("PID",line):
			if len(proc_hdr) < 2: 
				proc_hdr="proc_hdr|second|NUMA"
				for col_number in sorted(my.col_txt.keys(), key=int):
					hdr_txt=my.col_txt[col_number]
					if re.search("^PID$",hdr_txt) :pid_col=col_number
					if re.match("^P$",hdr_txt) :cpu_col=col_number
					if re.search("^TIME",hdr_txt) :time_col=col_number
					proc_hdr=proc_hdr+"|"+hdr_txt
			else: continue
		else : #process data
			#if len(line) > 2  and re.search(proc_filter,line):
			if len(line) > 2 :
				proc_id=str(line[my.col_start[pid_col]:my.col_end[pid_col]])
				proc_id=re.sub(" ","",proc_id)
				cpu_num=str(line[my.col_start[cpu_col]:my.col_end[cpu_col]])
				#print cpu_num
				cpu_num=re.sub(" ","",cpu_num)
				#print cpu_num
				PROC_FOUND[proc_id]=proc_id
	
				node="Node"+str(CPU_NODE[int(cpu_num)])
				key=(node,seconds)
	
				if key in NCPU.keys():
					proc_data="proc"+"|"+ str(seconds)+"|"+str(node)
					for col_number in sorted(my.col_txt.keys(), key=int):
						data_field=str(line[my.col_start[col_number]:my.col_end[col_number]])
						if col_number == time_col : data_field=time_2_seconds(data_field)
						data_field=re.sub(" ","",data_field)
						proc_data="|".join([proc_data,data_field])
					#proc_data=proc_data+"|"+NCPU[key]
					PROC[seconds,proc_id]= proc_data
	
			
	
	# end of read top data
	
	
	top_hdr="second|time|users|ld_avg_5|ld_avg_10|lg_avg_15"
	task_hdr="second|time|ttl_tsk|run_tsk|sleep_tsk|stop_tsk|zmb_tsk"
	cpu_numa_header="second|time|us|sys|ni|id|wa|hi|si|st"
	mem_hdr  ="|".join(["second","time",mem_scope, "used_mem", "free_mem", "buffers","ttl_"])
	swap_hdr="|".join(["second","time",swap_scope,"used_swap","free_swap","cach_mem"])
	
	print "|".join(["top_hdr",top_hdr,])
	print "|".join(["task_hdr",task_hdr,])
	print "|".join(["cpu_numa_hdr",cpu_numa_header])
	print "|".join(["mem_hdr",mem_hdr])
	print "|".join(["swap_hdr",swap_hdr])
	
	print proc_hdr
	
	for seconds in sorted(TOP,key=int):
	
		print "|".join(["top",str(seconds),TOP[seconds]])
		print "|".join(["task",str(seconds),TASKS[seconds]])
		print "|".join(["cpu",str(seconds),CPU[seconds]])
		print "|".join(["mem",str(seconds),SWAP[seconds]])
		print "|".join(["swap",str(seconds),MEM[seconds]])
	
		for scope,nseconds in sorted(NCPU):
			if nseconds==seconds :
				print "|".join(["numa", str(seconds),str(scope),NCPU[(scope,seconds)]])
		for proc_id in sorted(PROC_FOUND,key=int):
			key=(seconds,proc_id)
			if key in PROC:
				if re.search(top_proc_filter,PROC[key]) : print PROC[key]
	
	
##### END OF MAIN BLOCK DEF
	
	
	
	
	
if __name__ == "__main__":
    sys.exit(cli_main())
