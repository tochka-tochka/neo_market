import pika

class ModerQueue:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Создаёт соединение и канал"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue='moder', 
            durable=True, 
            arguments={'x-queue-type': 'quorum'}
        )

    def _ensure_connection(self):
        """Проверяет и восстанавливает соединение при необходимости"""
        if self.connection is None or self.connection.is_closed:
            self._connect()
        if self.channel is None or self.channel.is_closed:
            self._connect()

    def product_moder_notification(self, id: str):
        try:
            self._ensure_connection()
            self.channel.basic_publish(
                exchange='',
                routing_key='moder',
                body=id,
                properties=pika.BasicProperties(delivery_mode=2)  # persistent
            )
        except pika.exceptions.ConnectionClosedByBroker:
            self._connect()
            self.channel.basic_publish(
                exchange='',
                routing_key='moder',
                body=id,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except pika.exceptions.AMQPConnectionError:
            # Логгируем ошибку, но не прерываем создание продукта
            print(f"Warning: RabbitMQ connection failed, message not sent for product {id}")
        
moder_queue = ModerQueue()