from multiprocessing import Pool
import json
import logging
import urllib3
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
from collections import defaultdict
from decimal import *


def err(err_content):
    return {
        "result": "error",
        "message": err_content
    }


class ResultFailReason(Enum):
    connectionTimeout = 1
    readTimeout = 2
    requestCreationError = 3
    connectionError = 4
    responseParsingError = 5
    unknown = 20


http_pool = None
thread_pool = None

logger = logging.getLogger("gamma_ipserv.hdlr")


class IpData:
    def __init__(self):
        self.country_code = None
        self.city = None
        self.country_name = None
        self.latitude = None
        self.longitude = None

class SingleIpRequest:

    def __init__(self, ip, server):
        self.ip = ip
        self.server = server
        self.ok = False
        self.reason = ResultFailReason.unknown
        self.data = IpData()


def init(max_threads, connection_timeout, read_timeout, retry_count):
    global thread_pool
    thread_pool = ThreadPoolExecutor(max_threads)
    logger.info("Thread pool inited, max threads set to {0}".format(max_threads))
    global http_pool
    http_pool = urllib3.PoolManager(timeout=urllib3.Timeout(connect=connection_timeout, read=read_timeout), retries=urllib3.Retry(retry_count))
    logger.info("Http pool inited, connection timeout: {0}, read timeout: {1}, retries: {2}".format(connection_timeout, read_timeout, retry_count))


def process_ip_json(jsons, servers):
    if http_pool is None:
        logger.critical("Http pool not inited, call init()")
        return err("Http pool not inited, call init()")
    if thread_pool is None:
        logger.critical("Thread pool not inited, call init()")
        return err("Thread pool not inited, call init()")

    start_time = datetime.now()
    logger.log(logging.DEBUG, "Got json: {0}, start processing at {1} with thread {2}".format(jsons, start_time, threading.get_ident()))
    try:
        ips = json.loads(jsons)
    except:
        logger.exception("Can't process input json")
        return err("Can't process input json")

    list_requests = [SingleIpRequest(ip, server) for ip in ips for server in servers]
    results = defaultdict(list)
    for r in thread_pool.map(make_request, list_requests):
        results[r.ip].append(r)
    ipdata = []
    for (ip, reqlist) in results.items():
        ipdata.append(make_votings(ip, reqlist))
    res = {"result": "processed", "ipdata": ipdata}
    logger.log(logging.DEBUG, "Processing finished in {0}, thread {1}".format(datetime.now() - start_time, threading.get_ident()))
    return res


def vote(lst, numeric=False):
    non_empty_lst_tmp = [l for l in lst if (l is not None and l != "")]
    non_empty_lst = []
    if numeric:
        for n in non_empty_lst_tmp:
            try:
                non_empty_lst.append(round(Decimal(n), 4))
            except:
                logger.debug("Error converting to number: {0}".format(n))
    else:
        non_empty_lst = non_empty_lst_tmp

    length = len(non_empty_lst)
    if length == 0:
        return {"value": None, "votes": 0, "total": 0}

    d = defaultdict(int)
    for l in non_empty_lst:
        d[str(l).upper()] += 1
    sorted_d = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    firstval = next(iter(sorted_d))
    return {"value": firstval[0], "votes": firstval[1], "total": length}


def make_votings(ip, reqlist):
    res = {"ip": ip}
    try:
        country_codes = []
        cities = []
        country_names = []
        latitudes = []
        longitudes = []
        for req in reqlist:
            if req.ok:
                country_codes.append(req.data.country_code)
                cities.append(req.data.city)
                country_names.append(req.data.country_name)
                latitudes.append(req.data.latitude)
                longitudes.append(req.data.longitude)
        res["country_code"] = vote(country_codes)
        res["city"] = vote(cities)
        res["country_name"] = vote(country_names)
        res["latitude"] = vote(latitudes, True)
        res["longitude"] = vote(longitudes, True)
    except:
        logger.exception("Error voting for {0}".format(ip))
        res["result"] = "error"
    return res


def make_request(request_param):
    try:
        if request_param.server.need_auth:
            request_string = request_param.server.request_mask.format(request_param.ip, request_param.server.api_key)
        else:
            request_string = request_param.server.request_mask.format(request_param.ip)
    except:
        logger.exception("Error getting request string for {0}")
        request_param.reason = ResultFailReason.requestCreationError
        return request_param

    #logger.debug("Sending response: on {0}: {1}".format(request_param.ip, request_string))
    try:
        r = http_pool.request("GET", request_string)
    except urllib3.exceptions.NewConnectionError:
        request_param.reason = ResultFailReason.connectionError
        logger.exception("Connection error")
        return request_param
    except urllib3.exceptions.ConnectTimeoutError:
        request_param.reason = ResultFailReason.connectionError
        logger.exception("Connect timeout error")
        return request_param
    except urllib3.exceptions.ReadTimeoutError:
        request_param.reason = ResultFailReason.connectionError
        logger.exception("Read timeout error")
        return request_param
    except:
        request_param.reason = ResultFailReason.unknown
        logger.exception("Request error")
        return request_param

    try:
        data = json.loads(r.data.decode('utf-8'))
    except:
        request_param.reason = ResultFailReason.responseParsingError
        logger.exception("Request parsing error")
        return request_param

    try:
        if request_param.server.response_mask["country_code"] not in data:
            logger.error("Cannot get country code for result from {0} for {1}".format(request_param.server.address, request_param.ip))
        else:
            request_param.data.country_code = data[request_param.server.response_mask["country_code"]]

        if request_param.server.response_mask["city"] not in data:
            logger.error("Cannot get city for result from {0} for {1}".format(request_param.server.address, request_param.ip))
        else:
            request_param.data.city = data[request_param.server.response_mask["city"]]

        if request_param.server.response_mask["country_name"] not in data:
            logger.error("Cannot get country name for result from {0} for {1}".format(request_param.server.address, request_param.ip))
        else:
            request_param.data.country_name = data[request_param.server.response_mask["country_name"]]

        if request_param.server.response_mask["latitude"] not in data:
            logger.error("Cannot get latitude for result from {0} for {1}".format(request_param.server.address, request_param.ip))
        else:
            request_param.data.latitude = data[request_param.server.response_mask["latitude"]]

        if request_param.server.response_mask["longitude"] not in data:
            logger.error("Cannot get longitude for result from {0} for {1}".format(request_param.server.address, request_param.ip))
        else:
            request_param.data.longitude = data[request_param.server.response_mask["longitude"]]
    except:
        logger.exception("Error parsing data from {0} for {1}".format(request_param.server.address, request_param.ip))

    request_param.ok = True
    return request_param