import time
import shutil
import psycopg2
import queue
import os
import threading
import concurrent.futures
import logging
import datetime



indir = '../IN/IPB'
fDir = '..//IN//IPB'
outdir = '../OUT/IPB'
rBack = '../IN/'
dbhost = 'localhost'
dbport = '5432'
dbuser = 'postgres'
dbpass = 'postgres'
dbname = 'project_0'

q = queue.Queue()

def logger():
    """
    @brief Запуск логгера.
    """
    logging.basicConfig(filename='extractip_python.log',filemode='w', format='%(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info('Start extractip')

def IntToIP(ipnum):
    """
    @brief Преобразование из INTEGER в IP.
    """
    o1 = int(ipnum / 16777216) % 256
    o2 = int(ipnum / 65536) % 256
    o3 = int(ipnum / 256) % 256
    o4 = int(ipnum) % 256
    return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

def extractIp(fpath):
    """
    @brief Создание набора IP.
    """
    try:
        with open(fpath) as fp:
            ips = set()
            for line in fp:
                splited = line.split('::')
                if splited[0] == '1':
                    ips.add(IntToIP(int(splited[5])))
                    ips.add(IntToIP(int(splited[6])))
        return ips
    except:
        logging.info('I can not read the file %s' % fpath)

def register(f):
    """
    @brief Перенос файлов из IN/IPB в OUT/IPB.
    @detailed Файлы которые невозможно прочесть выбрасываются в родительскую папку IN.
    """
    ips = extractIp(fDir + '/' + f)
    if ips is not None:
        shutil.move(indir + '/' + f, outdir + '/' + f)
        return ips
    else:
        shutil.move(indir + '/' + f, rBack + '/' + f)
        return ips
        pass

def sendDB():
    """
    @brief Второй поток - отправка в базу дананных.
    @detailed Получение элементов из очереди.
    Создание соединения с базой данных.
    Отправка полученного набора IP в базу данных.
    Ожидание следующего списка элементов.
    """
    while True:
        try:
            ips = q.get()
            try:
                start_time = time.time()
                conn = psycopg2.connect(user=dbuser, password=dbpass, host=dbhost, port=dbport, database=dbname)
                conn.set_session(autocommit=True)
                elements = list(ips)
                log=len(elements)
                try:
                    curs = conn.cursor()
                    curs.callproc('public.check_ips', (elements,))
                    curs.close()
                    logging.info('Delivered to DB %s ip' % log)
                except:
                    logging.info('Not delivered to DB')
                    continue
                logging.info("Delivered %s seconds" % (time.time() - start_time))
                print("Delivered %s seconds" % (time.time() - start_time), datetime.datetime.now())
            except:
                logging.info('Connection to the database interrupted')
                continue
        except:
            time.sleep(0.1)
            continue

def prog():
    """
    @brief Первый поток - обработка файлов.
    @detailed
    Ищет входящие файлы и запускает еще шесть потоков для первых 1000 файлов.
    Добавляет результаты в очередь и исключает повторные IPs.
    Обработка следующих 1000 файлов.
    Если нет входящих файлов, то ждем появления элементов.
    """
    while True:
        s = set()
        files = os.listdir(fDir)
        number_files = len(files)
        if number_files > 0:
            start_time = time.time()
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                    results = [pool.submit(register, fileName[:1000]) for fileName in os.listdir(fDir)]
                for out in concurrent.futures.as_completed(results):
                    r = set(out.result())
                    s = s.union(r)
                q.put(s)
            except:
                logging.info('Threads not started')
                continue
            logging.info("File processing --- %s seconds ---" % (time.time() - start_time))
            print("File processing %s seconds " % (time.time() - start_time), datetime.datetime.now())
        time.sleep(0.1)

def main():
    """
    Программа для чтения и преобразования файлов с IP и записи их в базу данных. При запуске запускается логгер и 2 основных потока.
    """
    logger()
    th_1, th_2 = threading.Thread(target=prog), threading.Thread(target=sendDB)
    th_1.start(), th_2.start()


if __name__ == '__main__':
    main()
