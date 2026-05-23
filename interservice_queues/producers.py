import logging
import pika
import json
from typing import Dict, List
import os
from src.models.outbox import InterserviceOutbox
from django.db import transaction

class ServicesChannelProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.moder_access_key = os.environ.get('MODER_SERVICE_KEY')
        self.b2b_access_key = os.environ.get('B2B_SERVICE_KEY')
        self._connect()

    def resent_messages(self):
        unsent_messages = InterserviceOutbox.objects.all()
        for message in unsent_messages:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=message.queue,
                    body=json.dumps(message.message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                message.delete()
            except Exception as e:
                logging.debug(f"Failed to resent message {message.id}: {str(e)}. Message not deleted from outbox table")
            
    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue='moder', 
            durable=True, 
            arguments={'x-queue-type': 'quorum'}
        )
        self.channel.queue_declare(
            queue='b2c', 
            durable=True, 
            arguments={'x-queue-type': 'quorum'}
        )

        self.resent_messages()

    def _ensure_connection(self):
        if self.connection is None or self.connection.is_closed:
            self._connect()
        if self.channel is None or self.channel.is_closed:
            self._connect()

    @transaction.atomic
    def product_moder_notification(self, data: Dict[str, str], corrected: bool):
        try:
            if not self.moder_access_key:
                return Exception("Not Authorized")
            data['X-Service-Key'] = self.moder_access_key
            self._ensure_connection()
            self.channel.basic_publish(
                exchange='',
                routing_key='moder',
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.ConnectionClosedByBroker:
            self._connect()
            self.channel.basic_publish(
                exchange='',
                routing_key='moder',
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.AMQPConnectionError:
            logging.debug(f"Warning: RabbitMQ connection failed, message not sent for product {id}")
            InterserviceOutbox.objects.create(
                queue="moder",
                message=data
            )

    @transaction.atomic
    def product_b2c_notification(self, data: Dict[str, str | List[str]], corrected: bool):
        try:
            if not self.b2b_access_key:
                return Exception("Not Authorized")
            data['X-Service-Key'] = self.b2b_access_key
            self._ensure_connection()
            self.channel.basic_publish(
                exchange='',
                routing_key='b2c',
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.ConnectionClosedByBroker:
            self._connect()
            self.channel.basic_publish(
                exchange='',
                routing_key='b2c',
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.AMQPConnectionError:
            logging.debug(f"Warning: RabbitMQ connection failed, message not sent for product {id}")
            InterserviceOutbox.objects.create(
                queue="b2c",
                message=data
            )
        
services_channel_producer = ServicesChannelProducer()