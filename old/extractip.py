# Extract ips from IPB files from input directory to data base
indir = '../IN/IPB'
outdir = '../OUT/IPB'
dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = '1234'
dbname = 'db_20190422_v2'

# Get file list from directory
from os import walk
def InFiles(dpath):
	files = []
	for (dirpath, dirnames, filenames) in walk(dpath):
		files.extend(filenames)
		break
	return files

# Convert ip from integer
def IntToIP(ipnum):
	o1 = int(ipnum / 16777216) % 256
	o2 = int(ipnum / 65536) % 256
	o3 = int(ipnum / 256) % 256
	o4 = int(ipnum) % 256
	return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

# Extract ip from IPB struct
def ExtractIp(fpath):
	with open(fpath) as fp:
		ips = set()
		for line in fp:
			splited = line.split('::')
			if splited[0] == '1':
				ips.add(IntToIP(int(splited[5])))
				ips.add(IntToIP(int(splited[6])))
	return list(ips)

# Send ips to data base
import psycopg2
def WriteToDB(ips):
	conn = psycopg2.connect(user = dbuser, password = dbpass, host = dbhost, port = dbport, database = dbname)
	conn.set_session(autocommit = True)
	curs = conn.cursor()
	curs.callproc('public.check_ips', (ips,))
	curs.close()
	conn.close()

# Main loop
import shutil, time
while True:
	for f in InFiles(indir):
		ips = ExtractIp(indir + '/' + f)
		WriteToDB(ips)
		shutil.move(indir + '/' + f, outdir + '/' + f)
	time.sleep(.1)

#
