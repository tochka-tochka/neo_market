<script lang="ts">
import NewSkuForm from "$lib/components/organisms/NewSkuForm.svelte";
import type { Char, Image, ProductType, SkuType } from "$lib/types/index.js";

let { data } = $props();
let product: ProductType = data?.product ?? {
	id: "0",
	title: "",
	description: "",
	status: "active",
	category: {
		id: "-",
		value: "-",
	},
	images: [] as Image[],
	characteristics: [] as Char[],
	skus: [] as SkuType[],
};
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-gradient-to-b from-neutral-900 to-neutral-950 p-6">
            <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Добавление SKU</h1>
            </div>

            <NewSkuForm product={product} />
        </div>
    </div>
</div>