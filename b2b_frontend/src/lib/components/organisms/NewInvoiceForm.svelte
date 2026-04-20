<script lang="ts">
import { goto } from "$app/navigation";
import { API_URL, authorized } from "$lib";
import type { InvoiceItem, ProductType, SkuType } from "$lib/types";
import InvoiceFormRow from "../molecules/InvoiceFormRow.svelte";

let { products } = $props();

let formItems: InvoiceItem[] = $state([]);

const dummyProduct: ProductType = {
	id: "",
	title: "",
	description: "",
	category: {
		id: "",
		value: "Выберите категорию",
	},
	status: "inspection",
	images: [],
	characteristics: [],
	skus: [],
};

const dummySku: SkuType = {
	id: "",
	name: "",
	price: 0,
	active_quantity: 0,
	characteristics: [],
};

async function submitForm(e: SubmitEvent) {
	e.preventDefault();

	const clippedFormItems = formItems.map((item) => ({
		product_id: item.product.id,
		sku_id: item.sku.id,
		quantity: item.quantity,
	}));

	console.log(clippedFormItems);

	await authorized(fetch)(`${API_URL}/invoices/`, {
		method: "POST",
		body: JSON.stringify(clippedFormItems),
		headers: {
			Authorization: `Bearer ${localStorage.getItem("token")}`,
			"Content-Type": "application/json",
		},
	});

	goto("/invoices");
}
</script>

<div class="pt-8">
    <form onsubmit={submitForm}>
        {#each formItems as item, index}
            <div class="flex flex-row items-center gap-4 mb-4">
                <InvoiceFormRow products={products} bind:item={formItems[index]} />
                <button
                    type="button"
                    onclick={() => formItems = formItems.filter((_, i) => i !== index)}
                    class="text-red-500 hover:text-red-700 transition-colors px-3 py-1 border-[0.5px] border-red-900/50 hover:text-red-900 rounded"
                >
                    -
                </button>

            </div>
        {/each}

        <button
            type="button"
            onclick={() => formItems = [...formItems, { product: dummyProduct, sku: dummySku, quantity: 0 }]}
            class="mt-3 text-lg text-tx-secondary hover:text-white transition-colors"
        >
            + Добавить запись в накладную
        </button>


        <div class="pt-8">
            <button
                type="submit"
                class="px-6 py-4 bg-white cursor-pointer hover:bg-white/90"
                style="cursor: pointer;"
            >
                <span class="font-Manrope font-bold text-lg text-neutral">Сохранить</span>
            </button>
        </div>
    </form>
</div>