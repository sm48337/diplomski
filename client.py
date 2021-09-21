#!/usr/bin/env python3

from pika import BlockingConnection

from json import dumps, loads


class Client:
    def __init__(self, channel_name, exchange=''):
        self.channel_name = channel_name
        self.exchange = exchange
        self.connection = BlockingConnection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.channel_name)
        if self.exchange == 'fanout':
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='fanout'
            )

    def set_callback(self, callback):
        def callback_handler(channel, method_frame, properties, body):
            callback(loads(body))
            self.channel.basic_ack(method_frame.delivery_tag)

        self.channel.basic_consume(
            queue=self.channel_name, on_message_callback=callback_handler
        )

    def send(self, message):
        self.channel.basic_publish(
            exchange='', routing_key=self.channel_name, body=dumps(message)
        )

    def broadcast(self, message):
        self.channel.basic_publish(
            exchange=self.exchange, routing_key=self.channel_name, body=dumps(message)
        )

    def receive(self):
        frame, properties, body = self.channel.basic_get(self.channel_name)
        if body:
            return (frame, properties, loads(body))

    def consume(self):
        self.channel.start_consuming()
