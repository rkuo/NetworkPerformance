
1. As root
2. Find a place to keep the scripts, Either existing or create a new directory 
	mkdir $HOME/perf_tools/bin
	For now this is called the "Source Directory"

3. Copy the following files to the Source Directory
	get_env.py
	parse_top.py
	hdr.py
	disp_json_env.py
	.toprc
4. Set permission on all files to r-w------
	 chmod 500  "Source Directory"/.
5. Copy .toprc to $HOME
	cp "Source Directory"/.toprc $HOME/.
6. Required Linux utilities
	Various server instances may or may not have all the required Linux utilties installed on the server
	On the first execution of get_env.py the OS will issue an error message if a utility is missing.
	Typically this message includes the instructions to install the utility
	
7. get_env.py captures the data 
	data placed in three files
		json formated commands
		dmidecode binary dump
		kernel parametrs from sysctl -a
	get_env.py -h produces 
		usage: get_env.py [-h] [-d DEST] [-r REGEX]
	
		Copyright 2016 AT&T Licensed under the Apache License 2.0
		http://www.apache.org/licenses/LICENSE-2.0p;
		
		optional arguments:
	  	-h, --help            show this help message and exit
	  	-d DEST, --dest DEST  Ouput File Destination, default = ../data
	  	-r REGEX, --regex REGEX
	                        	Reg Exp for filtering on top process reporting,
	                        	default = "contrail|libvirt|qemu-system"
	
		Get network environment in standardized JSON format for network benchmarking
8.	disp_json_env.py produces text display of the data in the json files

 	./disp_json_env.py -h
		usage: disp_json_env.py [-h] -f FILE [-l] [-i INDX]

		Copyright 2016 AT&T Licensed under the Apache License 2.0
		http://www.apache.org/licenses/LICENSE-2.0p;
		
		optional arguments:
		  -h, --help            show this help message and exit
		  -f FILE, --file FILE  json file created by get_env.py
		  -l, --list            List of Commands with data in the json file
		  -i INDX, --indx INDX  Display the text output of this one command
		
		Convert network environment in standardized JSON format created by get_env.py
		to text
9. parse_top.py --  captured the batch mode top coomand output and formats the output. Also uses lscpu to attach Numa Node number to CPU number
	Runs for 1 time period , as default option -b -n 1 -d 1
	"|" delimeted ouput. First Column contains type of record, ex proc for process record, proc_hdr = header for process record type. 

	Depends on this .toprc being in the $HOME of the user running the command		
	Depends on this hdr.py in the Source Directory - defines the headers for the format provided by .toprc
	If changes are made to .toprc (via interactive top) hdr.py must be changed to match		

	Can be run independently of get_env.py

	./parse_top.py -h
	usage: parse_top.py [-h] [-r REGEX] [-t TOP]

	Copyright 2016 AT&T Licensed under the Apache License 2.0
	http://www.apache.org/licenses/LICENSE-2.0p;
	
	optional arguments:
  	-h, --help            show this help message and exit
  	-r REGEX, --regex REGEX
                        	Reg Exp for filtering on top process reporting
  	-t TOP, --top TOP     optional arguments for top command -b is hardcoded

	Capture System Resource Usage Snapshot via top

				
10. Examples


# ./get_env.py  -d $HOME/perf_tools/data
/root/perf_tools/bin/
Gathering Inventory
Running command dmidecode  --dump-bin /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin
Running command sysctl -a > /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt
Running command uname -a
Running command echo BIOS Setting, use-\> dmidecode -t X --from-dump  /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin \<- where X=type 0,1,2,...
Running command echo Kernel Parameters in /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt in txt format
Running command ntpq -p
Running command ntpq -pn
Running command lscpu
Running command dmidecode -t 1|grep Product
Running command dmidecode -t 4|egrep "Socket Designation|Version|Core Count|Thread Count"
Running command lspci|grep "Ethernet controller"
Running command netstat
Running command ifconfig
Running command iptables --list
Running command ip link
Running command ip a
Running command vrouter --info
Running command contrail-status
Running command vif --list
Running command vrouter --info
Running command vrmemstats
Running command vrfstats --dump
Running command flow -l |egrep "Created"
Running command dropstats
Running command vxlan --dump
Running command /root/perf_tools/bin/parse_top.py -r "contrail|libvirt|qemu-system"
Running command ps -aux |egrep "contrail|qemu-system"|grep -v grep
Done running commands
output found in following files
/root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json
/root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin
/root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt
BIOS Setting, use-\> dmidecode -t X --from-dump  /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin \<- where X=type 0,1,2,...
Kernel Parameters in /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt in txt format
# ./disp_json_env.py  -l -f /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

Index to Commands in file /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

  1 /root/perf_tools/bin/parse_top.py -r "contrail|libvirt|qemu-system"
  2 contrail-status
  3 dmidecode -t 1|grep Product
  4 dmidecode -t 4|egrep "Socket Designation|Version|Core Count|Thread Count"
  5 dropstats
  6 echo BIOS Setting, use-\> dmidecode -t X --from-dump  /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin \<- where X=type 0,1,2,...
  7 echo Kernel Parameters in /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt in txt format
  8 flow -l |egrep "Created"
  9 ifconfig
 10 ip a
 11 ip link
 12 iptables --list
 13 lscpu
 14 lspci|grep "Ethernet controller"
 15 netstat
 16 node_name
 17 node_type
 18 ntpq -p
 19 ntpq -pn
 20 ps -aux |egrep "contrail|qemu-system"|grep -v grep
 21 uname -a
 22 vif --list
 23 vrfstats --dump
 24 vrmemstats
 25 vrouter --info
 26 vxlan --dump
# ./disp_json_env.py  -i 1 -f /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

Output from command /root/perf_tools/bin/parse_top.py -r "contrail|libvirt|qemu-system" in file /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

contrail|libvirt|qemu-system  -n 1 -d 1
grep for contrail|libvirt|qemu-system
top_hdr|second|time|users|ld_avg_5|ld_avg_10|lg_avg_15
task_hdr|second|time|ttl_tsk|run_tsk|sleep_tsk|stop_tsk|zmb_tsk
cpu_numa_hdr|second|time|us|sys|ni|id|wa|hi|si|st
mem_hdr|second|time|GiB_Mem|used_mem|free_mem|buffers|ttl_
swap_hdr|second|time|GiB_Swap|used_swap|free_swap|cach_mem
proc_hdr|second|NUMA|PID|P|nTH|USER|PR|NI|VIRT|RES|DATA|SHR|S|%CPU|%MEM|TIME+|COMMAND
top|47095|13:04:55|1|9.12|9.30|9.4
task|47095|13:04:55|533|1|532|0|
cpu|47095|13:04:55|29.0|6.1|0.0|64.9|0.0|0.0|0.0|
mem|47095|13:04:55|0.000|0.000|000|327
swap|47095|13:04:55|251.547|227.932|23.615|-1
numa|47095|Node0|13:04:55|39.8|8.9|0.0|51.3|0.0|0.0|0.0|
numa|47095|Node1|13:04:55|18.1|3.2|0.0|78.7|0.0|0.0|0.0|
proc|47095|Node1|0610|20|4|libvirt+|20|0|6810740|47532|2341404|8940|S|6.3|0.0|25150.52|qemu-system-x8
proc|47095|Node0|1616|10|4|libvirt+|20|0|6811920|43104|2342584|8940|S|6.3|0.0|262564.0|qemu-system-x8
proc|47095|Node0|2121|8|4|libvirt+|20|0|6876284|42304|2406948|8940|S|6.3|0.0|263930.0|qemu-system-x8
proc|47095|Node0|2548|10|4|libvirt+|20|0|6942976|43948|2473640|8940|S|6.3|0.0|263958.0|qemu-system-x8
proc|47095|Node0|2820|9|4|libvirt+|20|0|6810888|44548|2341552|8940|S|6.3|0.0|287650.0|qemu-system-x8
proc|47095|Node0|2888|10|4|libvirt+|20|0|6810892|42080|2341556|8940|S|6.3|0.0|287460.0|qemu-system-x8
proc|47095|Node0|2960|8|4|libvirt+|20|0|6810892|48048|2341556|8940|S|6.3|0.0|288161.0|qemu-system-x8
proc|47095|Node0|3061|6|4|libvirt+|20|0|6810892|43432|2341556|8936|S|6.3|0.0|288032.0|qemu-system-x8
proc|47095|Node0|3076|6|4|libvirt+|20|0|6942988|48184|2473652|8940|S|6.3|0.0|263734.0|qemu-system-x8
proc|47095|Node1|4767|22|11|root|20|0|1081948|16580|809800|8760|S||0.0|2234.31|libvirt
proc|47095|Node1|4852|22|4|libvirt+|20|0|6810732|44048|2341396|8940|S|12.7|0.0|282586.0|qemu-system-x8
proc|47095|Node1|4955|22|4|libvirt+|20|0|6810740|44432|2341404|8940|S|6.3|0.0|284021.0|qemu-system-x8
proc|47095|Node1|5138|12|4|libvirt+|20|0|6876284|46872|2406948|8940|S|6.3|0.0|279862.0|qemu-system-x8
proc|47095|Node1|5160|19|15|root|20|0|0.496t|8212|972764|2740|S|791.4|0.0|5979776.0|contrail-vrout
proc|47095|Node0|5259|10|1|libvirt+|20|0|28200|960|356|712|S||0.0|0.01|dnsmas
proc|47095|Node1|5284|18|4|libvirt+|20|0|6876284|49080|2406948|8936|S|6.3|0.0|281417.0|qemu-system-x8
proc|47095|Node0|5302|8|17|root|20|0|16.326g|0.014t|15.166g|14064|S|6.3|5.8|69289.0|contrail-vrout
proc|47095|Node1|5583|15|4|libvirt+|20|0|6810748|42840|2341412|8940|S|6.3|0.0|281781.0|qemu-system-x8
proc|47095|Node1|6469|17|4|libvirt+|20|0|6876276|45116|2406940|8940|S|12.7|0.0|256487.0|qemu-system-x8
proc|47095|Node1|6608|20|4|libvirt+|20|0|6876280|44556|2406944|8940|S|6.3|0.0|223435.0|qemu-system-x8
proc|47095|Node1|6869|14|4|libvirt+|20|0|6876284|43768|2406948|8940|S||0.0|223935.0|qemu-system-x8
proc|47095|Node1|7257|19|4|libvirt+|20|0|6876284|45276|2406948|8940|S|6.3|0.0|224096.0|qemu-system-x8
proc|47095|Node1|7675|21|4|libvirt+|20|0|6876284|46280|2406948|8940|S|12.7|0.0|223233.0|qemu-system-x8
proc|47095|Node1|7755|17|4|libvirt+|20|0|6810748|41980|2341412|8940|S|12.7|0.0|253528.0|qemu-system-x8
proc|47095|Node1|8118|17|4|libvirt+|20|0|6876276|45996|2406940|8940|S|6.3|0.0|222544.0|qemu-system-x8

# ./disp_json_env.py  -i 6 -f /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

Output from command echo BIOS Setting, use-\> dmidecode -t X --from-dump  /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin \<- where X=type 0,1,2,... in file /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

BIOS Setting, use-> dmidecode -t X --from-dump /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin <- where X=type 0,1,2,...

# dmidecode -t 0 --from-dump /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin
# dmidecode 2.12
Reading SMBIOS/DMI data from file /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_dmidecode.bin.
SMBIOS 2.8 present.

Handle 0x0008, DMI type 0, 24 bytes
BIOS Information
        Vendor: HP
        Version: P89
        Release Date: 03/05/2015
        Address: 0xF0000
        Runtime Size: 64 kB
        ROM Size: 16384 kB
        Characteristics:
                PCI is supported
                PNP is supported
                BIOS is upgradeable
                BIOS shadowing is allowed
                ESCD support is available
                Boot from CD is supported
                Selectable boot is supported
                EDD is supported
                5.25"/360 kB floppy services are supported (int 13h)
                5.25"/1.2 MB floppy services are supported (int 13h)
                3.5"/720 kB floppy services are supported (int 13h)
                Print screen service is supported (int 5h)
                8042 keyboard services are supported (int 9h)
                Serial services are supported (int 14h)
                Printer services are supported (int 17h)
                CGA/mono video services are supported (int 10h)
                ACPI is supported
                USB legacy is supported
                BIOS boot specification is supported
                Function key-initiated network boot is supported
                Targeted content distribution is supported
                UEFI is supported
        BIOS Revision: 1.32
        Firmware Revision: 2.10
# ./disp_json_env.py  -i 7  -f /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

Output from command echo Kernel Parameters in /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt in txt format in file /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54.json

Kernel Parameters in /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt in txt format

# head /root/perf_tools/data/mtpnjrsv138_2016-04-21_13:04:54_sysctl.txt
abi.vsyscall32 = 1
debug.exception-trace = 1
debug.kprobes-optimization = 1
dev.cdrom.autoclose = 1
dev.cdrom.autoeject = 0
dev.cdrom.check_media = 0
dev.cdrom.debug = 0
dev.cdrom.info = CD-ROM information, Id: cdrom.c 3.20 2003/12/17
dev.cdrom.info =
dev.cdrom.info = drive name:

