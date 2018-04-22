import re
import os
import json
import time
import socket
import random
import string
import logging
import argparse


class Server:
    def __init__(self, port=5555, backup_file_path='backup.json', task_timeout=5*60):
        self._func_dict = {
            'add': self.add_task,
            'get': self.get_task,
            'ack': self.ack_status,
            'in': self.in_queue
        }

        self.queue_dict = {}
        self.timeouts_list = []
        self.port = port
        self.backup_file_path = backup_file_path
        self.load_backup()
        self._create_logger()
        self.task_timeout = task_timeout

    def _create_logger(self):
        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('{asctime} {levelname} {funcName:.>35} {message}', style='{')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)

    def load_backup(self):
        if not os.path.exists(self.backup_file_path):
            return

        with open(self.backup_file_path, 'r', encoding='utf8') as backup_file:
            backup_data = json.load(backup_file)
        self.queue_dict = backup_data["queue_dict"]
        self.timeouts_list = backup_data["timeouts_list"]

    def write_file(self):
        self.logger.info('saving data')
        backup_data = json.dumps({"queue_dict": self.queue_dict, "timeouts_list": self.timeouts_list}, indent='\t')
        with open(self.backup_file_path, 'w', encoding='utf8') as backup_file:
            backup_file.write(backup_data)

    def remove_logs(self):
        if not os.path.exists(self.backup_file_path):
            return

        self.logger.info('removing backup ')
        os.remove(self.backup_file_path)

    def check_timeouts(self):
        self.logger.info('checking timeouts')
        for given_task in self.timeouts_list:
            self.logger.info('checking timeout for task {}'.format(given_task['id']))
            # breaking the cycle because the most recent task are at the beginning of this queue
            if time.time() - given_task['timestamp'] < self.task_timeout:
                self.logger.info('time for this task is not out yet')
                break

            self.logger.info('time for this task is out!')
            for task in self.queue_dict[given_task['queue']]:
                if task['id'] == given_task['id']:
                    self.logger.info('returning is_available state to this task')
                    task['is_available'] = True
                    self.logger.info('removing this task from timeouts_list')
                    self.timeouts_list.remove(given_task)

    def run(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('127.0.0.1', self.port))
        connection.listen(10)
        self.logger.info('listening')
        while True:
            self.logger.info('==================')
            self.logger.info('waiting for a new connection')
            current_connection, address = connection.accept()
            self.logger.info('connection established: %s %s' % (current_connection, address))
            current_connection.setblocking(False)

            data_received_from_connection = b''
            while True:
                try:
                    self.logger.info('receiving data')
                    data = current_connection.recv(1024)
                    self.logger.info('data received')
                    self.logger.info(data)
                    if data:
                        data_received_from_connection += data
                    else:
                        self.logger.info('no data, stop receiving')
                        break
                except BlockingIOError:
                    self.logger.info('Receiving exception, stop receiving')
                    break
                self.logger.info('------------------')
            self.logger.info('data, received from connection: %s' % data_received_from_connection)

            response = self.process_task(data_received_from_connection)

            self.logger.info('proccesing finished')
            self.write_file()

            self.logger.info('RESPONSE: {}'.format(response))
            current_connection.send(response)

            self.logger.info('closing connection')
            current_connection.close()
            self.logger.info('end of all command processing operations')
            self.logger.info('==================')

    def process_task(self, command_bytes):
        task = command_bytes.strip()

        self.logger.info('command received')
        self.check_timeouts()

        match = re.match(b'(?P<command>.*?) (?P<request>.*)', task)
        if not match:
            raise ValueError('Wrong request')

        command = match.group('command').decode('utf8').lower()
        self.logger.info('this is {} command'.format(command))

        self.logger.info('start command processing')

        processing_function = self._func_dict.get(command)
        if not processing_function:
            raise ValueError('Wrong command.')

        request = match.group('request').lower().strip()
        response = processing_function(request)
        return response

    def add_task(self, request):
        match_req = re.match(b'^(?P<queue>\S+)\s+(?P<length>\d+)\s+(?P<data>\S+)$', request)  # TODO: data type
        if not match_req:
            raise ValueError('Wrong request structure')

        current_queue = match_req.group('queue').decode('utf8')

        if current_queue not in self.queue_dict:
            self.queue_dict[current_queue] = []

        task_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        for task_item in self.queue_dict[current_queue]:
            if task_id in task_item['id']:
                task_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.queue_dict[current_queue].append(
            {
                'id': task_id,
                'length': match_req.group('length').decode('utf8'),
                'data': list(match_req.group('data')),
                'is_available': True
            }
        )

        return task_id.encode('utf-8')

    def get_task(self, request):
        request = request.decode('utf8')

        match_req = re.match(r'^(?P<queue>\S+)$', request)
        if not match_req:
            raise ValueError('Wrong request structure')

        current_queue = match_req.group('queue')
        if current_queue not in self.queue_dict:
            return b'NONE'

        for task_item in self.queue_dict[current_queue]:
            if task_item['is_available']:
                task_item['is_available'] = False
                self.timeouts_list.append({'queue': current_queue, 'id': task_item['id'], 'timestamp': time.time()})
                return '{} {} '.format(task_item['id'], task_item['length']).encode('utf8') + bytes(task_item['data'])
            else:
                continue

        return b'NONE'

    def ack_status(self, request):
        request = request.decode('utf8')

        match_req = re.match(r'^(?P<queue>\S+)\s+(?P<id>\S+)$', request)
        if not match_req:
            raise ValueError('Wrong request structure')
        self.logger.info('confirmation of task {} in queue {}'.format(match_req.group('id'), match_req.group('queue')))
        current_queue_tasks = self.queue_dict.get(match_req.group('queue'))
        task_index = 0
        self.logger.info('finding this task')
        for task in current_queue_tasks:
            if task['id'] == match_req.group('id'):
                self.logger.info('task found, removing it from queue_dict and timeouts_list')
                del (self.queue_dict[match_req.group('queue')][task_index])
                self._remove_task_from_timeouts_list(match_req.group('id'))
                return b'YES'
            else:
                task_index += 1
        return b'NO'

    def _remove_task_from_timeouts_list(self, task_id):
        self.logger.info('removing task {} from timeouts_list'.format(task_id))
        for task_index in range(len(self.timeouts_list)):
            if self.timeouts_list[task_index]['id'] == task_id:
                del self.timeouts_list[task_index]
                self.logger.info('task deleted')

    def in_queue(self, request):
        request = request.decode('utf8')

        match_req = re.match(r'^(?P<queue>\S+)\s+(?P<id>\S+)$', request)
        if not match_req:
            raise ValueError('Wrong request structure')

        current_queue_tasks = self.queue_dict.get(match_req.group('queue'))
        for task in current_queue_tasks:
            if task['id'] == match_req.group('id'):
                return b'YES'
        return b'NO'


def parse_args():
    """argsparse configuring"""

    parser = argparse.ArgumentParser()
    parser.add_argument('port',
                        nargs='?',  # makes it positional and optional
                        type=int,
                        help='port, where server will be located')
    # parser.add_argument('--backup_remove', type=bool, default=False,
    #                     help='remove backup file on exit')
    parser.add_argument('--backup_path', type=str,
                        help='path to backup file')
    parser.add_argument('--task_timeout', type=int,
                        help='timeout on given task')

    return parser.parse_args()


def create_kwargs_for_server(args_from_argsparse):
    kwargs = {}
    args = [arg for arg in dir(args_from_argsparse) if not arg.startswith('_')]  # getting args names
    for arg in args:
        arg_value = getattr(args_from_argsparse, arg)

        if not arg_value:
            continue

        kwargs[arg] = arg_value
    return kwargs


if __name__ == '__main__':
    args = parse_args()
    kwargs_for_server = create_kwargs_for_server(args)

    server1 = Server(**kwargs_for_server)
    server1.run()
