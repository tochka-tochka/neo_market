import threading
import time
import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import SKU, BlockingReason, ProductFieldReport, ProductStatus
from src.serializers.product_serializers import ProductSerializer
from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    catalog_products,
    dummy_image,
    product_factory,
    sku_payload,
    test_category,
)


@pytest.fixture
def blocking_reason():
    r = BlockingReason.objects.create(title="test", comment="test")
    return r



@pytest.fixture
def moderation_worker():
    from interservice_queues.consumers.moder_decisions.moderation_decisions_consumer import (
        ModerationConsumer,
    )
    consumer_instance = ModerationConsumer()
    consumer_thread = threading.Thread(target=consumer_instance.start, daemon=True)
    consumer_thread.start()
    time.sleep(1)

    yield consumer_thread

    if consumer_instance:
        consumer_instance.stop()

    if consumer_thread:
        consumer_thread.join(timeout=5)


@pytest.mark.django_db(transaction=True)
class TestModerDecisionApply(BaseTestUtil):
    def test_moderated_event_clears_blocking_data(
        self, product_factory, moderation_worker, blocking_reason
    ):
        product = product_factory(
            status=ProductStatus.ON_MODERATION, blocking_reason_id=blocking_reason.id
        )
        ProductFieldReport.objects.create(
            product=product, field_name="title", comment="test"
        )

        msg_data = {
            "idempotency_key": str(uuid.uuid4()),
            "product_id": str(product.id),
            "status": "MODERATED",
        }

        self.send_moder_decision(msg_data)

        success = False
        for _ in range(10):
            product.refresh_from_db()
            if product.status == ProductStatus.MODERATED:
                success = True
                break
            time.sleep(0.5)

        assert success

        product.refresh_from_db()
        product_relations = ProductSerializer(product).data
        assert product.blocking_reason is None
        assert len(product_relations["field_reports"]) == 0

    @pytest.mark.parametrize("hard_blocked", [False, True])
    def test_moderation_blocking_descision(
        self, product_factory, moderation_worker, hard_blocked, blocking_reason
    ):
        product = product_factory(status=ProductStatus.ON_MODERATION)

        msg_data = {
            "idempotency_key": str(uuid.uuid4()),
            "product_id": str(product.id),
            "status": "BLOCKED",
            "hard_block": hard_blocked,
            "blocking_reason_id": str(blocking_reason.id),
            "field_reports": [
                {
                    "field_name": "description",
                    "sku_id": None,
                    "comment": "Текст описания скопирован с другого товара",
                }
            ],
        }

        self.send_moder_decision(msg_data)

        success = False
        for _ in range(10):
            product.refresh_from_db()
            if product.status == (
                ProductStatus.HARD_BLOCKED if hard_blocked else ProductStatus.BLOCKED
            ):
                success = True
                break
            time.sleep(0.5)

        assert success

        msg = self.get_rabbitmq_message("b2c")
        assert msg is not None
        assert msg["event"] == "PRODUCT_BLOCKED"
        assert msg["product_id"] == str(product.id)

    def test_edit_hard_blocked_returns_403(self, jwt_client, product_factory, base_data):
        product = product_factory(status=ProductStatus.HARD_BLOCKED)
        response = jwt_client.patch(
            reverse("product-detail", args=[product.id]), base_data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = jwt_client.delete(reverse("product-detail", args=[product.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_event_same_idempotency_key_no_side_effects(
        self, product_factory, moderation_worker, blocking_reason
    ):
        product = product_factory(
            status=ProductStatus.ON_MODERATION, blocking_reason_id=blocking_reason.id
        )
        ProductFieldReport.objects.create(
            product=product, field_name="title", comment="test"
        )

        idempotency_key = str(uuid.uuid4())
        msg_data = {
            "idempotency_key": idempotency_key,
            "product_id": str(product.id),
            "status": "MODERATED",
        }

        self.send_moder_decision(msg_data)

        success = False
        for _ in range(10):
            product.refresh_from_db()
            if product.status == ProductStatus.MODERATED:
                success = True
                break
            time.sleep(0.5)

        assert success

        product.refresh_from_db()
        product_relations = ProductSerializer(product).data
        assert product.blocking_reason is None
        assert len(product_relations["field_reports"]) == 0

        msg_data = {
            "idempotency_key": idempotency_key,
            "product_id": str(product.id),
            "status": "BLOCKED",
        }

        self.send_moder_decision(msg_data)

        success = False
        for _ in range(10):
            product.refresh_from_db()
            if product.status == ProductStatus.MODERATED:
                success = True
                break
            time.sleep(0.5)

        assert success
