

dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = 'postgres'
dbname = 'db_20190422_v2'

# Send ips to data base
import psycopg2
def GetUnknown():
	conn = psycopg2.connect(user = dbuser, password = dbpass, host = dbhost, port = dbport, database = dbname)
	curs = conn.cursor()
	curs.callproc('public.unknown_ips')
	res = curs.fetchall()
	ip = ''
	for row in res:
		ip = row[0]
	curs.close()
	conn.close()
	print(ip)
	return ip

#
import requests
def GetRequest(ip):
	if ip:
#		r = "{'ipdata': [{'city': {'value': 'IRKUTSK', 'votes': 4, 'total': 5}, 'ip': '90.188.254.235', 'latitude': {'value': '52.2978', 'votes': 3, 'total': 5}, 'longitude': {'value': '104.2964', 'votes': 3, 'total': 5}, 'country_name': {'value': 'RUSSIA', 'votes': 5, 'total': 5}, 'country_code': {'value': 'RU', 'votes': 5, 'total': 5}}], 'result': 'processed'}"
#		r = ''
		r = requests.get('http://localhost:8080/?iplist=["' + ip + '"]')
		return r.json()
	return ''

def UpdateUnknown(ip, cntry, cde, city, lat, lon):
	conn = psycopg2.connect(user = dbuser, password = dbpass, host = dbhost, port = dbport, database = dbname)
	conn.set_session(autocommit = True)
	curs = conn.cursor()
	curs.callproc('public.update_ips', (ip, cntry, cde, city, lat, lon,))
	curs.close()
	conn.close()

import json
def ParseJson(jsn):
#	print('parse')
#	rspns = jsn.replace("'", '"')
	if jsn:
		rspns = json.dumps(jsn)
		rspns = json.loads(rspns)
		for doc in rspns['ipdata']:
			UpdateUnknown(doc['ip'], doc['country_name']['value'], doc['country_code']['value'], doc['city']['value'], doc['latitude']['value'], doc['longitude']['value'])
			print(doc['ip'], doc['country_name']['value'], doc['city']['value'])

# Main loop
import shutil, time
while True:
	ParseJson(GetRequest(GetUnknown()))
	time.sleep(1)

#

