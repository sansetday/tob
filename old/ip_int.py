# Extract ips from IPB files from input directory to data base
indir = '../ipb1'
import os
import queue

q = queue.Queue()

# Get file list from directory
from os import walk
def InFiles(dpath):
	files = []
	for (dirpath, dirnames, filenames) in walk(dpath):
		files.extend(filenames)
		break
	return files


# Extract ip from IPB struct
def ExtractIp(fpath):
	with open(fpath) as fp:
		ips = ''
		for line in fp:
			splited = line.split('::')
			if splited[0] == '1':
				ips.replace(int(splited[5],q.get()))
				ips.replace(int(splited[6], q.get()))
	return list(ips)

# Main loop
import shutil, time
while True:
	for f in InFiles(indir):
        l = []
        with open('ip_int.txt') as f:
        l = f.read().splitlines()
      for i in l:
            q = q.put(i)

    shutil.move(indir + '/' + f, outdir + '/' + f)
	time.sleep(.1)

#
