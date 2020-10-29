import sys
import time
import subprocess
import socket
import json

import requests

DEBUG = True

SERVER_PATH = './node/server.js'
PORT_RANGE = range(8000, 8100)
HEADERS = {'Content-Type': 'application/json'}


class Calculator:
    server = None
    port = None
    address = 'localhost'

    cache = {
        'calcs': {},
        'hits': 0,
        'misses': 0
    }

    def __init__(self):
        for port in PORT_RANGE:
            if self._start_server(port):
                self.port = port
                return

        sys.stderr.write('Could not find an open port! Server was not started.\n')


    def __del__(self):
        self._stop_server()

    def _start_server(self, port):
        self.server = subprocess.Popen(['node', SERVER_PATH, str(port)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)

        time.sleep(0.2)

        while True:
            line = self.server.stdout.readline()
            if not line:
                return False

            if b'Smogon calculator listening on port' in line:
                print(line.decode('utf-8'))
                return True

    def _stop_server(self):
        if self.server:
            self.server.terminate()
            try:
                self.server.wait(timeout=0.2)
                print('Calculator server exited with code: {}'.format(self.server.returncode))
            except subprocess.TimeoutExpired:
                print('Calculator server did not exit in time.')

            if DEBUG:
                print('Cache hits: {}'.format(self.cache['hits']))
                print('Cache misses: {}'.format(self.cache['misses']))

    def _to_json(self, data):
        return json.dumps(data, sort_keys=True)

    def _cache_key(self, data):
        return hash(data)


    def _send_request(self, json_data, endpoint):
        response = requests.get(
            'http://{}:{}{}'.format(self.address, self.port, endpoint),
            data=json_data,
            headers=HEADERS
        )

        return response.json()


    def calc(self, data):
        json_data = self._to_json(data)

        key = self._cache_key(json_data)

        if key in self.cache['calcs']:
            self.cache['hits'] += 1
            return self.cache['calcs'][key]

        response = self._send_request(json_data, '/calc')

        self.cache['misses'] += 1
        self.cache['calcs'][key] = response

        return response

    def calc_batch(self, data):
        ret = []
        ret_keys = []
        batch_job = {}

        for i, elem in enumerate(data):
            json_data = self._to_json(elem)
            key = self._cache_key(json_data)
            ret_keys.append(key)

            if key in self.cache['calcs']:
                self.cache['hits'] += 1
            else:
                batch_job[key] = elem
                self.cache['misses'] += 1
                self.cache['calcs'][key] = None

        response = self._send_request(self._to_json(batch_job), '/calc-batch')

        for key in response:
            self.cache['calcs'][int(key)] = response[key]

        for key in ret_keys:
            ret.append(self.cache['calcs'][key])

        return ret
