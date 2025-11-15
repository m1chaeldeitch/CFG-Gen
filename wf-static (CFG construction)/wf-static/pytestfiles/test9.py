#!/usr/bin/python

import  os, sys, threading, time, datetime
#mainSproutFolder = os.environ([$sproutenv]) ## does not work well with some python module
#sys.path.append(mainSproutFolder)
sys.path.append("/work/sprouts/")
import scripts.initWF as gfwf #gfwf stands for get files workflow
import scripts.utils.dicoUnpickling as udp
import scripts.webservice.imel

#RA: my code!
import traceback
from ftplib import FTP

## wff object : in order to get all the information about the 
## folders involved in the Workflow and any useful information
wff = gfwf.getFolderWF() # wff workflow files

def fetch_webserver_jobs(folder_server, folder_target):
    """
    Connects to the UTO SDML web server and copies job files to the local to_do folder.
    """
    __author__ = 'Ruben Acuna'

    print os.path.basename(__file__) + ": fetch_jobs() started."

    try:
        ftp = FTP('bioinformatics.engineering.asu.edu')
        #ftp.set_debuglevel(2)
        ftp.set_pasv(False)
        ftp.login('workflow@bioinformatics.engineering.asu.edu', 'ZZZZZZ')
        ftp.cwd(folder_server)
        #ftp.dir()

        filenames = ftp.nlst("")
        filenames = [x for x in filenames if ".txt" in x]

        for filename in filenames:

            #print 'Getting ' + filename

            fhandle = open(folder_target + os.sep + filename, 'wb')
            ftp.retrbinary('RETR ' + filename, fhandle.write)
            fhandle.close()

            ftp.delete(filename)

        ftp.quit()

    except:
        print os.path.basename(__file__) + ": fetch_jobs() encountered exception:"
        print os.path.basename(__file__) + ": " + str(sys.exc_info())
        print os.path.basename(__file__)+ ": " + str(traceback.format_tb(sys.exc_info()[2], 5))

    print os.path.basename(__file__) + ": fetch_jobs() exited."

def crontab():
	## 
	# check if data are in the To-Do list:
	# check if processes from previous workflow are still running
	# if so, this script stops
	# if not start one workflow 
	##

	#get new jobs from web server.
	fetch_webserver_jobs("/public_html/SPROUTS_WF/workflow/jobs_submitted", wff.folder_to_do)
	
	#variables
	# we assume that this folder contains files created by the workflow only. Otherwise errors. No folder please.
	list_to_do = os.listdir(wff.folder_to_do)
	list_to_do.remove(".svn")
	list_to_do = [x for x in list_to_do if not "~" in x]
	list_to_do.sort()
		
	if list_to_do == []:
		print "The todo folder "+wff.folder_to_do+" is empty. Exiting..."
		sys.exit()
	else:
		print "There are jobs waiting to be processed:"
		print "\n".join(list_to_do)

		# get and check if wf processes already running
		process_01 = os.popen("ps ax -o pid,args | grep running_tools.py").read().splitlines()
		process_02 = os.popen("ps ax -o pid,args | grep startWF.py").read().splitlines()
		process_03 = os.popen("ps ax -o pid,args | grep crontab.py").read().splitlines()

		process_01 = [line for line in process_01 if not "gedit" in line]
		process_02 = [line for line in process_02 if not "gedit" in line]
		process_03 = [line for line in process_03 if not "gedit" in line]
		# we had to check the three processes because multiple submission might collide

		if len(process_01) > 2 or len(process_02) > 2 or len(process_03) > 4:
			print "A started job is still running from a former instance"
			print "\nP1\n", "\n".join(process_01), "\nP2\n", "\n".join(process_02), "\nP3\n", "\n".join(process_03)
			print "Exiting..."
			sys.exit()
		else: 
			print "No Sprouts Process Running... Let's Start One ..."
			f2do = wff.folder_to_do
			dico_file_2_process = ""
			for i in range(len(list_to_do)):
				if not os.path.isfile(os.path.abspath(f2do+os.sep+list_to_do[i])) or os.path.abspath(f2do+os.sep+list_to_do[i]).endswith('~'):
					continue
				else: dico_file_2_process = f2do+os.sep+list_to_do[i]; break
			
			dico = udp.dicoUnpickle(dico_file_2_process) ## this rebuilds the dico containing information about the submission
			# for debugging we print dico + items
			print "Job dictionary: ", dico

			#check for jobdate in dict
			if "jobdate" in dico:
				print "Dictionary already contains jobdate."
			else:
				print "Dictionary does not contain jobdate, inserting."
				ra_jobdate = os.path.splitext(dico_file_2_process)[0].split(os.sep)[-1:][0]
				dico["jobdate"] = ra_jobdate

			#we init the logs here
			wff.dico = dico
			wff.initLogsFiles()
			for item in dico:
				print item, dico[item]
				
			##Init the variable of the email reply to submitter
			## note the formatting of the email should be in HTML so use <br> instead of "\n"
			#Objects
			## imel object is created to add information about the workflow in an email that
			## will be sent back to the submitter in order to tell them what was going on withthe workflow.
			import time
			imelbody = scripts.webservice.imel.imelbody()
			imelbody.resetList()
			imelbody.addmsg("Workflow Started at "+time.strftime("%a %d %b %Y %H:%M:%S", time.gmtime())+"(GMT)<br>")
			imelbody.printList()
			print imelbody.getList()
			imelbody.writeInFile(imelbody.getList()) ## to avoid any loss of information in case of power shutdown
			if dico.has_key("pdb_ids_list"):
				imel = scripts.webservice.imel.imel(dico, pdblist=True)
			elif dico.has_key("file_fasta"):
				imel = scripts.webservice.imel.imel(dico, userinput=True)

			#RA HACK: display dico only for me
			if "racuna1" in dico["email"]:
			    for key, value in dico.items():
			        imelbody.addmsg(str(key) + ":" + str(value) + "<br>")

			# we start a thread for a new wf instance
			import scripts.main.startWF as s
			# RA: th is startWF object
			print "Static: crontab()->Creating startWF object."
			th = s.startWF(dico, wff)
			th.setName("th4_job_"+dico['jobdate'])
			import time
			starttimeWF = time.time()
			# try and raise exception form here
			print "Static: crontab()->Starting startWF object."
			th.start()
			
			while th.isAlive():
				#print str(th.getName().upper())+" is still ALIVE"
				time.sleep(wff.sleeptime)
			print "Static: crontab()->startWF object is not alive anymore."
			# we should check here if thread finishes correctly using an Exception for threads for Example
			# before deleting the dico
			import shutil
			## check the log file. if every exit Value equals Zero, we move the
			## job file into the right done folder otherwise in failed folder
                        
                        # RA: check for existing output
                        filepath_finaldico = wff.folder_analysis_done+os.sep+os.path.basename(dico_file_2_process)
                        if os.path.exists(os.path.abspath(filepath_finaldico)):
                                print "Static: crontab()->filepath_finaldico already exists, removing."
                                os.remove(filepath_finaldico)                        
                        
			shutil.move(dico_file_2_process, wff.folder_analysis_done)
			endtime = time.time()
			duration = endtime-starttimeWF
			#f = open(str(ti)+"cronhasrun_and_ENDED_Normally.txt" , 'w')
			#f.close()

		#print "is thread "+th.getName().upper()+" still alive?: "+str(th.isAlive())
		## HERE below We should use the Modulo to get correct Times.
		print "END of crontab.py for the Job "+str(dico['jobdate'])
		wff.pil(wff.logsWFs, "##########\nEND of crontab.py for the Job "+str(dico['jobdate'])\
		+"\nTotal Duration of the RUN (hh:mm:ss)  = "+str(datetime.timedelta(seconds=duration))\
		+"##########")
		wff.text4email.append("Thank you for using our Webservice.<br>")
		wff.text4email.append("Do not hesitate to send your feedback or suggestions to the following email address: <br>")
		wff.text4email.append("<a href=\"mailto:springs.team@gmail.com?subject=SPROUTS WF\">springs.team@gmail.com</a><br>")
		wff.text4email.append("Regards,<br>")
		wff.text4email.append("<b>The SPROUTS TEAM</b>")
		
		### FORMATTING/PRINTING of ALL the MESSAGE added to LIST representing THE EMAIL BODY
		for item in wff.text4email:
			imelbody.addmsg(str(item).strip() + "<br>")
		imelbody.addmsg("Workflow Ended at "+time.strftime("%a %d %b %Y %H:%M:%S", time.gmtime())+"(GMT) <br>")
		imelbody.addmsg("Workflow Duration: (hh:mm:ss) ="+str(datetime.timedelta(seconds=round(duration))))
		
		#### EMAIL SENDING HERE
		#remove comment for production
		imel.send()
		
#	sys.exit()



def usage():
	print "USAGE: "+sys.argv[0]+" -sleeptime timevalue_integer -with_mir false/true/n/no -with_tools False/True/no/n/N"
	print "reminder: All the arguments are optional\n"

## start Crontab (if use as a script)
if __name__ == "__main__":
	print "SPROUTS Workflow has started."

	if len(sys.argv) > 7: 
		usage(); 
		sys.exit()

	for i in range(len(sys.argv)):
		op = sys.argv[i]
		if op == "-with_mir":
			wff.withMIR = sys.argv[i+1]
		if op == "-sleeptime":
			try:
				wff.sleeptime = int(sys.argv[i+1])
			except:
				print "The sleep time has to be an INTEGER"
				print sys.exc_info()
				usage(); sys.exit()
		if op == "-with_tools":
			wff.withTools = sys.argv[i+1]

	## Start crontab() ###
	crontab()
