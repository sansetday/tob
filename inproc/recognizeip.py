import time
import json
import requests
import psycopg2
import logging

dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = 'postgres'
dbname = 'project_0'

Sleep = 86400

def logger():
    """
    @brief Запуск логгера.
    """
    logging.basicConfig(filename='recognizeip_python.log', filemode='w',format='%(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info('Start recognizeip')


# Send ips to data base

def GetUnknown():
	"""
	@brief Получение неизвестных IP из базы данных.
	"""
	try:
		conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
		curs = conn.cursor()
		curs.callproc('public.unknown_ips')
		res = curs.fetchall()
		ip = ''
		#print(res)
		#for row in res:
		#	ip = row[0]
		curs.close()
		conn.close()
		#print(ip)
		return res
	except:
		logging.info('Connection to the database interrupted')
		pass



def GetRequest(res):
	"""
	@brief Отправка IP на сервер и получение json'a с информацией об этих IP.
	"""
	try:
		ip = ''
		ips = list()
		for row in res:
			ip = row[0]
			if ip:
		#		r = "{'ipdata': [{'city': {'value': 'IRKUTSK', 'votes': 4, 'total': 5}, 'ip': '90.188.254.235', 'latitude': {'value': '52.2978', 'votes': 3, 'total': 5}, 'longitude': {'value': '104.2964', 'votes': 3, 'total': 5}, 'country_name': {'value': 'RUSSIA', 'votes': 5, 'total': 5}, 'country_code': {'value': 'RU', 'votes': 5, 'total': 5}}], 'result': 'processed'}"
		#		r = ''
					r = requests.get('http://localhost:8080/?iplist=["' + ip + '"]')
					ips.append(r.json())
		return ips
	except:
		logging.info('Server is not available')
		pass


def UpdateUnknown(ip, cntry, cde, city, lat, lon):
	"""
	@brief Обновление IP в базе данных.
	"""
	try:
		#print(ip, cntry, cde, city, lat, lon)
		conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
		conn.set_session(autocommit=True)
		curs = conn.cursor()
		curs.callproc('public.update_ips', (ip, cntry, cde, city, lat, lon))
		curs.close()
		conn.close()
	except:
		logging.info('Not delivered to DB')
		pass


def ParseJson(ips):
	"""
	@brief Чтение json'a.
	"""
	try:
		#number = len(ips)
		#print(number)
		for jsn in ips:
			try:
				if jsn:
					rspns = json.dumps(jsn)
					rspns = json.loads(rspns)
					for doc in rspns['ipdata']:
						UpdateUnknown(doc['ip'], doc['country_name']['value'], doc['country_code']['value'],
									  doc['city']['value'], doc['latitude']['value'], doc['longitude']['value'])
						#print(doc['ip'], doc['country_name']['value'], doc['city']['value'])
			except:
				logging.info('Can not parse')
				pass

	except:
		pass


# Main loop

def scan():
	"""
	@brief Ожидание неизвестх IP.
	"""
	while True:
		ParseJson(GetRequest(GetUnknown()))
		time.sleep(1)


def updatedate():
	"""
	Обновление даты IP в базе данных.
	"""
	while True:
		try:
			conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
			conn.set_session(autocommit=True)
			try:
				curs = conn.cursor()
				curs.callproc('public.update_days')
				curs.close()
				logging.info('___')
				time.sleep(Sleep)
			except:
				logging.info('---')
				continue
		except:
			logging.info('---')
			continue


import threading
def main():
	"""
	@brief Программа для получения информации о неизвестных IP-адресов.
	"""
	logger()
	th_1, th_2 = threading.Thread(target=scan), threading.Thread(target=updatedate)
	th_1.start(), th_2.start()


if __name__ == '__main__':
	main()