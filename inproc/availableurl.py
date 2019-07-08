import urllib.request
import logging
import psycopg2
import time


dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = '1234'
dbname = 'project_0'

def logger():
    """
    @brief Запуск логгера.
    """
    logging.basicConfig(filename='availableurl_python.log', filemode='w',format='%(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info('Start availibleurl')

'''
def GetUrl():
    """Get url from DB"""
    try:
        conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
        curs = conn.cursor()
        curs.callproc('GET_URL')
        res = curs.fetchall()
        url = ''
        for row in res:
            url = row[0]
        curs.close()
        conn.close()
        print(url)
        return url
    except:
        logging.info('Connection to the database interrupted')
        pass
'''

def Access():
    """
    @brief Проверка доступности URL-адресов.
    """
    urls = ['http://bdu.fstec.ru/documents/files/vulxml.zip', 'http://cve.mitre.org/data/downloads/allitems.xml.gz']
    while True:
        for url in urls:
            try:
                urllib.request.urlopen(url)
                logging.info('Url available %s' % url)
                print(url)
            except:
                logging.info('Unavailable %s' % url)
                print('Адреса не существует')
        time.sleep(600)

def main():
    logger()
    Access()

if __name__ == '__main__':
    main()
