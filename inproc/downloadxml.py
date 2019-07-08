import wget
import time
import logging
import psycopg2
import os
import patoolib
import shutil

dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = '1234'
dbname = 'project_0'

SaveDir = '../IN/CIC/'
MoveDir = '../OUT/CIC/'


urls = ['http://bdu.fstec.ru/documents/files/vulxml.zip', 'http://cve.mitre.org/data/downloads/allitems.xml.gz']
Sleep = 86400


def logger():
    """
    @brief Запуск логгера.
    """
    logging.basicConfig(filename='downloadxml_python.log', filemode='w',format='%(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info('Start downloadxml')

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


def Sender(file):
    """
    @brief Перемещение файлов и отправка в базу данных.

    Отправка полученного файла базу данных. Перемещение файлов из папки '../IN/CIC/' в '../OUT/CIC/'
    """
    for files in os.listdir(SaveDir):
        shutil.move(SaveDir + files, MoveDir + files)




def FileList():
    """
    @brief Получение списка xml-файлов.
    """
    for root, dir, files in os.walk(SaveDir):
        for file in files:
            if file.endswith(".xml"):
                print(file)
    Sender(file)


def Download():
    """
    @brief  Скачивание списоков угроз. Распаковка архивов.
    """
    while True:
        for url in urls:
            try:
                filename = wget.download(url)
                os.rename(filename, SaveDir + filename)
                patoolib.extract_archive(SaveDir + filename, outdir=SaveDir)
                os.remove(SaveDir + filename)
                logging.info('Download xml %s' % url)
            except:
                logging.info('Unavailable %s' % url)
        FileList()
        for trash in os.listdir(MoveDir):
            trashpath = os.path.join(MoveDir, trash)
            try:
                shutil.rmtree(trashpath)
            except:
                os.remove(trashpath)
        time.sleep(Sleep)

def main():
    logger()
    Download()

if __name__ == '__main__':
    main()