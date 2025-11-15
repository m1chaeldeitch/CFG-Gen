import os
import time

input = "data.txt"
output = "tool1-output.txt"
final = "tool2-output.txt"

#print "%s -i0 %s" % ("tool0", "file0.txt")

os.system("tool1 -i " + input  + " -o " + output)

tmp_handler = open(output, 'a')
tmp_handler.write(">" + str(time.asctime(time.localtime(time.time()))))
tmp_handler.close()

os.system("tool2 -i " + output + " -o " + final)



