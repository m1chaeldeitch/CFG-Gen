#!/usr/bin/python

#############################################################################################
#                                                                                           #
#          Script which launches several instances of MUpro given a sequence file           #
#                   ./launchmupro.py -i file_seq_fasta -o out_folder                        #
#                           Mathieu Lonquety, IMPMC, 01-2009                                #
#                                                                                           #
#############################################################################################

import string, sys, os, re, time

#for mupro
## -ft /work/sprouts/tools
## -i /work/sprouts/data/inputs/fasta/3oq2a.fa
#  -pdb /work/sprouts/data/inputs/pdb
#  -dssp /work/sprouts/data/inputs/dssp
## -o /work/sprouts/data/outputs/3oq2a/mupro11/raw_results       #different
#  -exe /work/sprouts/tools/mupro11/bin/predict_regr_all.sh      #different
## -codejob 3oq2a
## -jobdate 20120427_232114

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

    for index_line in range(len(lines_input)):
      if re.search("^>.+", lines_input[index_line]):

        sequence = re.findall("[A-Z]+", string.upper(lines_input[index_line+1]))
        print os.path.basename(__file__) + ": seqlen = "+str(len(sequence))
        print os.path.basename(__file__) + ": seqlen = "+str(len(sequence[0]))
        file_log.write("SEQLEN = "+str(len(sequence[0])))
        file_log.write("\n")

        for index_residue in range(len(sequence[0])):
          file_param = open(folder_output+os.sep+"param_"+lines_input[index_line][1:].rstrip(" \n\r")+"_"+str(index_residue+1)+lines_input[index_line+1][index_residue]+".txt", 'w')
          file_param.write(lines_input[index_line][1:].rstrip(" \n\r")+"\n")         # the fasta header
          sequence = re.findall("[A-Z]+", string.upper(lines_input[index_line+1]))
          file_param.write(sequence[0]+"\n")                                         # the sequence
          file_param.write(str(index_residue+1)+"\n")                                # residue index (starting at 1)
          file_param.write(lines_input[index_line+1][index_residue]+"\n")            # wildtype residue at index
          file_param.write("*")                                                      # a *
          file_param.close()

          print os.path.basename(__file__) + ": ***"+code_job+"*** processing residue "+str(index_residue)+" ["+sequence[0][index_residue]+"]"
          file_log.write("processing residue "+str(index_residue)+"["+sequence[0][index_residue]+"]")

          os.system("%s %s > %s " %(filepath_mupro, folder_output+os.sep+"param_"+lines_input[index_line][1:].rstrip(" \n\r")+"_"+str(index_residue+1)+lines_input[index_line+1][index_residue]+".txt", folder_output+"/"+lines_input[index_line][1:].rstrip(" \n\r")+"_"+str(index_residue+1)+lines_input[index_line+1][index_residue]+".txt"))
          file_log.write("... Done\n")
          print os.path.basename(__file__) + ": ***"+code_job+"*** processing residue "+str(index_residue)+" ["+sequence[0][index_residue]+"] --> Done"

          os.remove(folder_output+os.sep+"param_"+lines_input[index_line][1:].rstrip(" \n\r")+"_"+str(index_residue+1)+lines_input[index_line+1][index_residue]+".txt")
          filepath_output_raw = folder_output+"/"+lines_input[index_line][1:].rstrip(" \n\r")+"_"+str(index_residue+1)+lines_input[index_line+1][index_residue]+".txt"
          file_output_raw = open(filepath_output_raw, 'r').readlines()
          res_ok = False
          confirmation = 0
          for line in file_output_raw:
            if "amino acid is not standard amino acid" in line:
                confirmation = 21
                print os.path.basename(__file__) + ": NOT STD AA"
                continue

            if len(line) > 25 and ("DECREASE" in line or "INCREASE" in line):
                confirmation +=1

          if confirmation >= 21:
              pass
          else:
              raise StandardError("NO RESULT or ERROR in Results File with "+toolname)

    ## End of the 'FOR' loop here
    file_log.write(time.asctime(time.localtime(time.time())))
    file_log.write("\n")
    duration = time.time()-startTime
    file_log.write("duration (sec(s)) = "+str(duration)+"\n")
    file_log.close()

except IOError, (errno, strerror):
    print os.path.basename(__file__) + ": Exit mupro11 - IOerror"
    print os.path.basename(__file__) + ":" + str(sys.exc_info())
    print os.path.basename(__file__) + ":" + str(errno), str(strerror)
    file_log.write(str(start_time)+"\n"+str(sys.argv)+"\n"+str(sys.exc_info())+"\n")
    file_log.write(str(strerror)+" -- err #"+str(errno)+"\n")
    file_log.close()
    sys.exit(124)
except:
    print os.path.basename(__file__) + ": ERROR UNEXPECTED or not caught"
    print os.path.basename(__file__) + ": Exit mupro11 - Unexpected error"
    print os.path.basename(__file__) + ":" + str(sys.exc_info())
    file_log.write("ERROR in "+sys.argv[0]+"\n for job :")
    file_log.write(str(start_time)+"\n"+str(sys.argv)+"\n"+str(sys.exc_info())+"\n")
    file_log.close()
    sys.exit(124)
