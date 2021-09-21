#!/usr/bin/env python3

from itertools import cycle
from os import getenv
from subprocess import run
from threading import Thread

from client import Client

CORES = int(getenv('CORES', 1))

tasks_queue = Client(getenv('TASKS_QUEUE', 'tasks_queue'))
tasks_output = Client(getenv('TASKS_OUTPUT', 'tasks_output'))
workers = cycle([Client('worker_queue' + str(i)) for i in range(CORES)])
worker_output = Client(getenv('OUTPUT_QUEUE', 'output_queue'))


def results_callback(body):
    tasks_output.send(body)


def return_results():
    worker_output.set_callback(results_callback)
    worker_output.consume()


def receive_task(body):
    if 'task_id' not in body:
        run([
            'socat',
            '-u',
            'UDP4-RECVFROM:6666,ip-add-membership=224.1.0.1:192.168.5.12',
            'STDOUT',
            '>',
            body['filename'],
        ])
        return
    worker = next(workers)
    worker.send(body)


def main():
    results = Thread(None, return_results, daemon=True)
    results.start()
    tasks_queue.set_callback(receive_task)
    tasks_queue.consume()


if __name__ == '__main__':
    main()
