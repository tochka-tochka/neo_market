import queue
import threading

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models.product import SKU, ProductStatus
from src.tests.fixtures import BaseTestUtil, product_factory, test_category


@pytest.mark.django_db(transaction=True)
class TestDeleteSKU(BaseTestUtil):
    def test_delete_sku_succeeds(self, jwt_client, product_factory, test_category):
        product = product_factory(
            status=ProductStatus.MODERATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="Test SKU",
            price=100,
            cost_price=80,
            stock_quantity=10,
        )

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

        moder_msg = self.get_rabbitmq_message("moder", timeout=0.1)
        assert moder_msg is None

    def test_delete_sku_with_active_reserves_returns_409(
        self, jwt_client, product_factory, test_category
    ):
        product = product_factory(
            status=ProductStatus.MODERATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="Test SKU",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=5,
        )

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    def test_last_sku_on_moderation_transitions_product_to_created(
        self, jwt_client, product_factory, test_category
    ):
        product = product_factory(
            status=ProductStatus.ON_MODERATION, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="Last SKU",
            price=100,
            cost_price=80,
            stock_quantity=10,
        )

        self._clear_queues()

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        product.refresh_from_db()
        assert product.status == ProductStatus.CREATED

        moder_msg = self.get_rabbitmq_message("moder")
        assert moder_msg is not None
        assert moder_msg["event"] == "DELETED"
        assert moder_msg["product_id"] == str(product.id)

    def test_delete_sku_hard_blocked_product_returns_403(
        self, jwt_client, product_factory, test_category
    ):
        product = product_factory(
            status=ProductStatus.HARD_BLOCKED, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="Blocked SKU",
            price=100,
            cost_price=80,
            stock_quantity=10,
        )

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_sku_out_of_stock_event_on_moderated_product(
        self, jwt_client, product_factory, test_category
    ):
        product = product_factory(
            status=ProductStatus.MODERATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="OOS SKU",
            price=100,
            cost_price=80,
            stock_quantity=5
        )

        self._clear_queues()

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        b2c_msg = self.get_rabbitmq_message("b2c")
        assert b2c_msg is not None
        assert b2c_msg["event"] == "SKU_OUT_OF_STOCK"
        assert b2c_msg["sku_id"] == str(sku.id)
        assert b2c_msg["product_id"] == str(product.id)

    def test_parallel_delete_operations(
        self, jwt_client, product_factory, test_category
    ):
        product = product_factory(
            status=ProductStatus.MODERATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product,
            name="OOS SKU",
            price=100,
            cost_price=80,
            stock_quantity=5,
        )

        self._clear_queues()
        url = reverse("specific-sku", args=[sku.id])

        auth_header = jwt_client._credentials.get("HTTP_AUTHORIZATION")

        q = queue.Queue()

        def worker(url, auth_header):
            thread_client = APIClient()
            if auth_header:
                thread_client.credentials(HTTP_AUTHORIZATION=auth_header)

            response = thread_client.delete(url)
            q.put(response)

        t1 = threading.Thread(target=worker, args=(url, auth_header))
        t2 = threading.Thread(target=worker, args=(url, auth_header))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        res1 = q.get()
        res2 = q.get()
        assert (res1.status_code == status.HTTP_204_NO_CONTENT) ^ (
            res2.status_code == status.HTTP_204_NO_CONTENT
        )
