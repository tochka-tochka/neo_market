import pytest
from django.urls import reverse
from rest_framework import status

from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    sku_payload,
    product_with_skus,
    product,
    product_factory,
    test_category,
)

@pytest.mark.django_db
class TestCreateSKU(BaseTestUtil):

    def test_delete_sets_deleted_true(self, jwt_client, product):
        response = jwt_client.delete(reverse('product-detail', args=[product.id]))
        
        self._clear_queues()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert product.deleted is True

    def test_delete_emits_event_to_moderation(self, jwt_client, test_user, product):
        jwt_client.delete(reverse('product-detail', args=[product.id]))
        
        msg = self.get_rabbitmq_message('moder')
        self.get_rabbitmq_message('b2c', timeout=0.1)
        
        assert msg and msg['event'] == 'DELETED'
        assert msg['product_id'] == str(product.id)

    def test_delete_emits_product_deleted_to_b2c(self, jwt_client, product_with_skus):
        sku_ids = list(product_with_skus.skus.values_list('id', flat=True))
        jwt_client.delete(reverse('product-detail', args=[product_with_skus.id]))

        self.get_rabbitmq_message('moder', timeout=0.1)
        msg = self.get_rabbitmq_message('b2c')
        
        assert msg and msg['event'] == 'PRODUCT_DELETED'
        assert set(msg['sku_ids']) == set([str(sid) for sid in sku_ids])

    def test_delete_already_deleted_returns_400(self, jwt_client, product):
        product.deleted = True
        product.save()
        response = jwt_client.delete(reverse('product-detail', args=[product.id]))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deleted_product_not_in_seller_list(self, jwt_client, test_user, product, product_factory):
        product_factory(title="Active Product")
        
        product.deleted = True
        product.save()
        
        response = jwt_client.get(reverse('my-products'))
        data = response.json()
        
        assert len(data['products']) == 1
        assert str(product.id) not in [p['id'] for p in data['products']]