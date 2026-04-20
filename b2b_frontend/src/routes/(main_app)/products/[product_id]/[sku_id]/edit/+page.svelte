<script lang="ts">
import EditSkuForm from "$lib/components/organisms/EditSkuForm.svelte";

let { data } = $props();

// mock, если серверные данные пока не приходят
let product = data?.product ?? {
	id: 1,
	title: "iPhone 15 Pro",
	category: "Смартфоны",
};

let sku = data?.sku ?? {
	id: 101,
	name: "IPH15P-BLK-128",
	price: 120000,
	active_quantity: 4,
	status: "active",
	image: "/mock/iphone-black.jpg",
};
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-neutral-900 p-6">
            <div class="border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Редактирование SKU</h1>
            </div>

            <EditSkuForm product={product} sku={sku} />
        </div>
    </div>
</div>