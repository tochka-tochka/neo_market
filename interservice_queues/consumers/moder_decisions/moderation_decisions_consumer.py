import pika
import json
from django import db
import time
import logging

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from src.models.product import Product

class WrongMessageFormat(Exception):
    pass

class ProductNotFound(Exception):
    def __init__(self, message, product_id):
        super().__init__(message)
        self.product_id = product_id

class ModerationConsumer:
    def __init__(self):
        self.queue_name = 'moder_decisions'
        self.connection = None
        self.channel = None

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5672)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.queue_name, 
            durable=True, 
            arguments={'x-queue-type': 'quorum'},
        )
        self.channel.basic_qos(prefetch_count=1)

    def _callback(self, ch, method, properties, body):
        """Логика обработки сообщения"""
        try:
            data = json.loads(body.decode())
            print(data)
            
            product = Product.objects.filter(id=data["product_id"]).first()

            if product is None:
                raise ProductNotFound("product doesn't exists", data["product_id"])
            
            if data["status"] not in ["MODERATED", "BLOCKED", "HARD_BLOCKED"]:
                raise WrongMessageFormat("wrong message format")

            product.status = data["status"]
            product.save()
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except ProductNotFound as e:
            logging.info(f"product with this {e.product_id} doesn't exists")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except WrongMessageFormat as e:
            logging.info(str(e))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.info(f" [!] Ошибка при обработке: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        if not self.connection or self.connection.is_closed:
            self._connect()
            
        self.channel.basic_consume(
            queue=self.queue_name, 
            on_message_callback=self._callback
        )
        
        print(f" [*] Ожидание сообщений в {self.queue_name}. Для выхода нажмите CTRL+C")
        self.channel.start_consuming()

    def stop(self):
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()

moderation_decisions_consumer = ModerationConsumer()