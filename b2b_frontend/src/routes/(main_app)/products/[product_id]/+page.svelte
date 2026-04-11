<script lang="ts">
    import { goto } from "$app/navigation";
    import ProductDetailsCard from "$lib/components/organisms/ProductDetailCard.svelte";
    import ProductSkuList from "$lib/components/organisms/ProductSkuList.svelte";
    import type { ProductType, Image, Char, SkuType } from "$lib/types/index.js";
    import { currentProduct } from "$lib/stores/productStore";

    let { data } = $props();

    let product : ProductType = data?.product ?? {
        id: "0",
        title: "",
        description: "",
        status: "active",
        category: {
            id: "-" ,
            value: "-",
        },
        images: [] as Image[],
        characteristics: [] as Char[],
        skus: [] as SkuType[],
    };
    $effect(() => {
        currentProduct.set(product);
    });
    console.log(product)
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-gradient-to-b from-neutral-900 to-neutral-950 p-6">

            <ProductDetailsCard product={product} />
            <ProductSkuList skus={product.skus} productId={product.id} />
        </div>
    </div>
</div>