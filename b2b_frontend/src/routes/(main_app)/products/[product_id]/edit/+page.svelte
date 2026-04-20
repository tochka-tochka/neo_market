<script lang="ts">
import { onMount } from "svelte";
import { API_URL, authorized } from "$lib";
import EditProductForm from "$lib/components/organisms/EditProductForm.svelte";
import { currentProduct } from "$lib/stores/productStore";
import type { Char, ProductType } from "$lib/types/index.js";

let { data } = $props();

let categoryOptions = data.categories ?? [];
let product: ProductType | null = $state(null);
let isLoading = $state(true);

let displayProduct = $derived($currentProduct ?? product);

onMount(async () => {
	if ($currentProduct) {
		product = $currentProduct;
		isLoading = false;
		return;
	}

	const res = await authorized(fetch)(
		`${API_URL}/products/${data.productId}/`,
	).then((res) => res.json());
	const productData = res.product;
	productData.characteristics = JSON.parse(
		productData.characteristics,
	) as Char[];
	product = productData;
	currentProduct.set(productData);
	isLoading = false;
});
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen py-6 px-60">
        <div class="w-full bg-gradient-to-b from-neutral-900 to-neutral-950 p-6">
            <div class="border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Редактирование товара</h1>
            </div>

            {#if isLoading}
                <div class="flex items-center justify-center h-64">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
                </div>
            {:else if displayProduct}
                <EditProductForm 
                    product={displayProduct} 
                    categories={categoryOptions} 
                />
            {:else}
                <p class="text-red-400">Не удалось загрузить товар</p>
            {/if}
        </div>
    </div>
</div>