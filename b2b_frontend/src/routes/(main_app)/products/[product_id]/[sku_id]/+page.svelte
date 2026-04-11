<script lang="ts">
    import SkuDetailsCard from "$lib/components/product/sku/organisms/SkuDetailCard.svelte";
    import ParentProductInfo from "$lib/components/product/sku/organisms/ParentProductInfo.svelte";
    import SkuActions from "$lib/components/product/sku/organisms/SkuActions.svelte";

    let { data } = $props();

    let product = data?.product

    let sku = data?.sku
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-neutral-900 p-6">

            <SkuDetailsCard sku={sku} productId={product.id} />
            <ParentProductInfo product={product} />
            <SkuActions productId={product.id} skuId={sku.id} />
        </div>
    </div>
</div>