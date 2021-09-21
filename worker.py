#!/usr/bin/env python3

from os import getenv
from subprocess import run

from client import Client

worker_queue = Client(getenv('WORKER_QUEUE', 'worker_queue0'))
output_queue = Client(getenv('OUTPUT_QUEUE', 'output_queue0'))


def callback(cmd):
    output = run(cmd, capture_output=True, text=True)
    msg = {
        'stdout': output.stdout,
        'stderr': output.stderr,
    }
    output_queue.send(msg)


def main():
    worker_queue.set_callback(callback)
    worker_queue.consume()


if __name__ == '__main__':
    main()
