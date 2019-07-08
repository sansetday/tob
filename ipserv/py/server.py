import http.server
import socketserver
import time
import logging
import logging.handlers
import argparse
import os.path
from urllib.parse import urlparse, parse_qs
import ipserv_iphandler
import ipserv_server
import json

ip_servers = []

class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            query_components = parse_qs(urlparse(self.path).query)
            # test
            if "test_count" in query_components:
                import test_client
                res = test_client.test_proc(int(query_components["test_count"][0]), 5)
            # test end
            else:
                iplist = query_components["iplist"][0]
                res = ipserv_iphandler.process_ip_json(iplist, ip_servers)
        except:
            logger.exception("Error processing request")
            res = ipserv_iphandler.err("Error processing request")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Run server in debug mode", action="store_true", required=False)
    parser.add_argument("-p", "--port", help="Port to start server", type=int, default=8080, required=False)
    parser.add_argument("-c", "--config", help="Path to configuration file", type=str, default="ipservers.json", required=False)
    parser.add_argument("--httptimeoutconn", help="Http connection timeout, seconds", type=float, default=2.0, required=False)
    parser.add_argument("--httptimeoutread", help="Http read timeout, seconds", type=float, default=2.0, required=False)
    parser.add_argument("--httptretries", help="Max connection retries count", type=int, default=2, required=False)
    parser.add_argument("-t", "--threads", help="Number of threads to make requests", type=int, default=256, required=False)
    args = parser.parse_args()

    baseLogger = logging.getLogger("gamma_ipserv")
    baseLogger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    fh = logging.handlers.RotatingFileHandler(os.path.join("..", "logs", "server.log"), maxBytes=pow(2, 20) * 100, backupCount=10)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    baseLogger.addHandler(fh)

    logger = logging.getLogger("gamma_ipserv.main")

    logger.debug("Getting config from {0}...".format(args.config))
    try:
        ip_servers = ipserv_server.getServers(args.config)
    except:
        logger.exception("Can't load config")
        print("Can't load config, exiting")
        exit(1)

    logger.debug("Initing iphandler...")
    ipserv_iphandler.init(args.threads, args.httptimeoutconn, args.httptimeoutread, args.httptretries)

    server = ThreadedHTTPServer(('0.0.0.0', args.port), Handler)
    print('Starting server on port {0}, use <Ctrl-C> to stop'.format(str(args.port)))
    logger.info("Server is starting on port {0}".format(args.port))
    server.serve_forever()
