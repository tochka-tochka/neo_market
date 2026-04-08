<script lang="ts">
    import { goto } from "$app/navigation";
    import ProductDetailsCard from "$lib/components/product/organisms/ProductDetailCard.svelte";
    import ProductSkuList from "$lib/components/product/organisms/ProductSkuList.svelte";
    import type { ProductType } from "$lib/types/index.js";
    import { currentProduct } from "$lib/stores/productStore";

    let { data } = $props();

    // mock-данные, если с сервера пока не приходят
    let product = data.product as ProductType
    $effect(() => {
        currentProduct.set(product);
    });
    console.log(product)
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-neutral-900 p-6">

            <ProductDetailsCard product={product} />
            <ProductSkuList skus={product.skus} productId={product.id} />
        </div>
    </div>
</div>