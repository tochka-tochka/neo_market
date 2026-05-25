import uuid
import json
import logging
import os
from datetime import datetime

from config.settings import RABBITMQ_HOST
from interservice_queues.producers import services_channel_producer

import django
import pika
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from src.models.product import (
    ModerationDecisions,
    Product,
    ProductFieldReport,
    ProductStatus,
    BlockingReason
)
from src.serializers.product_serializers import ProductSerializer


class WrongMessageFormat(Exception):
    pass


class ProductNotFound(Exception):
    def __init__(self, message, product_id):
        super().__init__(message)
        self.product_id = product_id


class ModerationConsumer:
    def __init__(self):
        self.queue_name = "moder_decisions"
        self.connection = None
        self.channel = None

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={"x-queue-type": "quorum"},
        )
        self.channel.basic_qos(prefetch_count=1)

    @transaction.atomic
    def _callback(self, ch, method, properties, body):
        """Логика обработки сообщения"""
        try:
            data = json.loads(body.decode())
            if (
                ModerationDecisions.objects.filter(idempotency_key=data["idempotency_key"]).first()
                is not None
            ):
                return

            match data["status"]:
                case "MODERATED":
                    product = Product.objects.filter(id=data["product_id"]).first()

                    if product is None:
                        raise ProductNotFound(
                            "product doesn't exists", data["product_id"]
                        )
                    product.blocking_reason = None
                    product.status = "MODERATED"
                    product.save()

                    ProductFieldReport.objects.filter(product=product).delete()
                case "BLOCKED":
                    product = Product.objects.filter(id=data["product_id"]).first()
                    blocking_reason = BlockingReason.objects.get(id=data["blocking_reason_id"])

                    if product is None:
                        raise ProductNotFound(
                            "product doesn't exists", data["product_id"]
                        )

                    product.blocking_reason = blocking_reason

                    for report in data["field_reports"]:
                        ProductFieldReport.objects.create(
                            product=product,
                            field_name=report["field_name"],
                            sku=report["sku_id"],
                            comment=report["comment"],
                        )

                    if data["hard_block"]:
                        product.status = ProductStatus.HARD_BLOCKED
                    else:
                        product.status = ProductStatus.BLOCKED

                    product.save()

                    product_relations = ProductSerializer(product).data

                    services_channel_producer.product_b2c_notification(data={
                        "idempotency_key": str(uuid.uuid4()),
                        "event": "PRODUCT_BLOCKED",
                        "product_id": str(product.id),
                        "sku_ids": list(map(lambda sku: sku["id"], product_relations["skus"])),
                        "date": str(datetime.now())
                    }, corrected=False)

                case _:
                    raise WrongMessageFormat("wrong message format")

            ModerationDecisions.objects.create(idempotency_key=data["idempotency_key"])

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except ProductNotFound as e:
            logging.info(f"product with this {e.product_id} doesn't exists")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except WrongMessageFormat as e:
            logging.info(str(e))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f" [!] Ошибка при обработке: {e}")
            logging.info(f" [!] Ошибка при обработке: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        if not self.connection or self.connection.is_closed:
            self._connect()

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self._callback
        )
        self.channel.start_consuming()

    def stop(self):
        """Вызывается из основного потока теста"""
        if self.connection and self.connection.is_open:
            self.connection.add_callback_threadsafe(self._really_stop)

    def _really_stop(self):
        """Выполняется внутри потока воркера"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()


moderation_decisions_consumer = ModerationConsumer()
