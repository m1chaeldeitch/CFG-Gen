import string, sys, os, re, time

toolname = "mupro11"
file_log = ""

for i in range(len(sys.argv)):
  if sys.argv[i] == "-i":
    filepath_input = sys.argv[i+1]
  elif sys.argv[i] == "-o":
    folder_output = sys.argv[i+1] ## here the appropriate raw_results folder
  elif sys.argv[i] == "-ft":
    folder_tools = sys.argv[i+1] ## the main folder for tools
  elif sys.argv[i] == "-codejob": # code job is either a code job or a pdb code
    code_job = sys.argv[i+1] 
  elif sys.argv[i] == "-jobdate": # jobdate
    job_date = sys.argv[i+1]

filepath_mupro = folder_tools+os.sep+"mupro11/bin/predict_regr_all.sh"

try:

    # prepare raising errors and logs them
    sys.path.append("/work/sprouts/scripts")
    import initWF, time
    wf = initWF.getFolderWF()
    start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    file_log = open(wf.folder_logs4run+os.sep+toolname+os.sep+code_job+"_"+job_date+"_mupro11_executable.txt", 'w')

    file_log.write(time.asctime(time.localtime(time.time())))
    file_log.write("\n")
    startTime = time.time()

    file_input = open(filepath_input, 'r')
    lines_input = file_input.readlines()
    file_input.close()
except:
    print os.path.basename(__file__) + ": ERROR UNEXPECTED or not caught"
    print os.path.basename(__file__) + ": Exit mupro11 - Unexpected error"
    print os.path.basename(__file__) + ":" + str(sys.exc_info())
    file_log.write("ERROR in "+sys.argv[0]+"\n for job :")
    file_log.write(str(start_time)+"\n"+str(sys.argv)+"\n"+str(sys.exc_info())+"\n")
    file_log.close()
    sys.exit(124)
