
from concurrent import futures
import grpc
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from proto.moder import moder_pb2, moder_pb2_grpc
from google.protobuf import empty_pb2
from src.models.product import Product
from src.serializes import ProductSerializer

class ModerServicer(moder_pb2_grpc.ProductsServicer):

    def GetNextProduct(self, request, context):
        print('GetNextProduct call')
        id = request.product_id
        product = Product.objects.get(id=id)
        serializer = ProductSerializer(product)
        print(serializer.data)
        return moder_pb2.Product(
            id=str(serializer.data['id']),
            title=serializer.data['title'],
            description=serializer.data['description'],
            category=moder_pb2.Product.Category(
                id=str(serializer.data['category']['id']),
                value=serializer.data['category']['value']
            ),
            characteristics=serializer.data['characteristics'],
            status=getattr(moder_pb2.Product.Status, serializer.data['status'].upper(), 0),
            seller=moder_pb2.Product.Seller(
                id=str(serializer.data['seller']['id']),
                username=serializer.data['seller']['username']
            ),
            images=[
                moder_pb2.Product.Image(
                    id=str(img.id),
                    url=img.url,
                    order=img.order,
                    created_at=str(img.created_at)
                )
                for img in serializer.data['images']
            ],
            skus=[
                moder_pb2.Product.SKU(
                    id=str(sku.id),
                    name=sku.name,
                    price=sku.price,
                    characteristics=sku.characteristics,
                    active_quantity=sku.active_quantity
                )
                for sku in serializer.data['skus']
            ]
        )

    def AcceptProduct(self, request, context):
        id = request.product_id
        product = Product.objects.get(id=id)
        product.status = 'accepted'
        product.save()
        return empty_pb2.Empty()

    def DeclineProduct(self, request, context):
        id = request.product_id
        product = Product.objects.get(id=id)
        product.status = 'blocked'
        product.save()
        return empty_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    moder_pb2_grpc.add_ProductsServicer_to_server(ModerServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print('GRPC MODER: listen port 50051')
    logging.info('GRPC MODER: listen port 50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()