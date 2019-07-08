dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = 'postgres'
dbname = 'db_20190422_v2'


import logging
def logger():
    """Start logger."""
    logging.basicConfig(filename='recognizeip_python.log', filemode='w',format='%(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info('Start recognizeip')


# Send ips to data base
import psycopg2
def GetUnknown():
	"""Get unknown ip."""
	try:
		conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
		curs = conn.cursor()
		curs.callproc('public.unknown_ips1')
		res = curs.fetchall()
		ip = ''
		print(res)
		for row in res:
			ip = row[0]
		curs.close()
		conn.close()
		print(ip)
		return ip
	except:
		logging.info('Connection to the database interrupted')
		pass


#
import requests
def GetRequest(ip):
	"""Sending ip to the server and receiving json."""
	try:
		if ip:
			#		r = "{'ipdata': [{'city': {'value': 'IRKUTSK', 'votes': 4, 'total': 5}, 'ip': '90.188.254.235', 'latitude': {'value': '52.2978', 'votes': 3, 'total': 5}, 'longitude': {'value': '104.2964', 'votes': 3, 'total': 5}, 'country_name': {'value': 'RUSSIA', 'votes': 5, 'total': 5}, 'country_code': {'value': 'RU', 'votes': 5, 'total': 5}}], 'result': 'processed'}"
			#		r = ''
			r = requests.get('http://localhost:8080/?iplist=["' + ip + '"]')
			return r.json()
		return ''
	except:
		logging.info('Server is not available')
		pass


def UpdateUnknown(ip, cntry, cde, city, lat, lon):
	"""Update unknown ip in db."""
	try:
		print(ip, cntry, cde, city, lat, lon)
		conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
		conn.set_session(autocommit=True)
		curs = conn.cursor()
		curs.callproc('public.update_ips1', (ip, cntry, cde, city, lat, lon))
		curs.close()
		conn.close()
	except:
		logging.info('Not delivered to DB')
		pass


import json
def ParseJson(jsn):
	"""Parse json."""
	try:
		if jsn:
			rspns = json.dumps(jsn)
			rspns = json.loads(rspns)
			for doc in rspns['ipdata']:
				UpdateUnknown(doc['ip'], doc['country_name']['value'], doc['country_code']['value'],
							  doc['city']['value'], doc['latitude']['value'], doc['longitude']['value'])
				print(doc['ip'], doc['country_name']['value'], doc['city']['value'])
	except:
		logging.info('Can not parse')
		pass


# Main loop
import shutil, time
def scan():
	"""Waiting for unknown ip."""
	while True:
		ParseJson(GetRequest(GetUnknown()))
		time.sleep(1)


import threading
def main():
	"""Program for obtaining information on unknown IP addresses."""
	logger()
	th_1 = threading.Thread(target=scan())
	th_1.start()


if __name__ == '__main__':
	main()