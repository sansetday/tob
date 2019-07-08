import json
import logging
import urllib3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

test_logger = logging.getLogger("gamma_ipserv.test")
http_pool = urllib3.PoolManager(timeout=urllib3.Timeout(connect=4.0, read=4.0), retries=urllib3.Retry(2))
thread_pool = ThreadPoolExecutor(250)

class request_params:

    def __init__(self, batch, request, start_time):
        self.batch = batch
        self.request = request
        self.start_time = start_time
        self.elapsed = -1


def test_proc(batchCount, requestsPerBatch):
    start_time = datetime.now()
    print("==============================")
    print("STARTING AT: {0}".format(start_time))
    try:
        listParams = [request_params(batch, req, start_time) for batch in range(1, batchCount + 1) for req in range(1, requestsPerBatch + 1)]
        for r in thread_pool.map(make_request, listParams):
            print("Batch {0} request {1} in {2}".format(r.batch, r.request, r.elapsed))
    except:
        test_logger.exception("Test fail")
        return {"test": "error"}
    return {"test": "ok {0} batches {1} requests ({2} total) in {3}".format(batchCount, requestsPerBatch, batchCount * requestsPerBatch, datetime.now() - start_time)}


def make_request(req_params):
    http_pool.request("GET", "http://httpbin.org/delay/1")
    req_params.elapsed = datetime.now() - req_params.start_time
    return req_params
