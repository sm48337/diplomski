#!/usr/bin/env python3

from itertools import count
from os import getenv
from os.path import splittext
from subprocess import run
from threading import Thread

from client import Client

tasks_queue = Client(getenv('TASKS_QUEUE', 'tasks_queue'))
output_queue = Client(getenv('OUTPUT_QUEUE', 'output_queue'), exchange='fanout')

TASKS = dict()
task_id_iter = count()
file_id_iter = count()

UPLOAD_TASKS = dict()
FILES = dict()


def listener_callback(body):
    task_id = body['task_id']
    print(f'{task_id = }')
    print(f'Command "{TASKS[task_id]}" returned:')
    print(body)
    del TASKS[body['task_id']]


def listen():
    output_queue.set_callback(listener_callback)
    output_queue.consume()


def send_file(f):
    run([
        'socat',
        '-u', f'FILE:{f}',
        'UDP4-DATAGRAM:224.1.0.1:6666,range=192.168.10.0/24',
    ])


def main():
    # run daemon receiver (threading.Thread)
    listener = Thread(None, listen, daemon=True)
    listener.start()
    try:
        while True:
            cmd = input('> ')
            if cmd == '':
                continue
            split = cmd.split()
            if split[0] == 'upload':
                filename, ext = splittext(''.join(split[1:]))
                generated_filename = next(file_id_iter) + ext
                FILES[(filename, ext)] = generated_filename
                print(f'File named {generated_filename}.')
                task = {
                    'filename': generated_filename
                }
                tasks_queue.broadcast(task)
                send_file(filename)
                continue
            task_id = next(task_id_iter)
            print(f'Queuing task {task_id}.')
            task = {
                'task_id': task_id,
                'cmd': split,
            }
            TASKS[task_id] = task
            tasks_queue.send(task)
    except EOFError:
        pass


if __name__ == '__main__':
    main()
