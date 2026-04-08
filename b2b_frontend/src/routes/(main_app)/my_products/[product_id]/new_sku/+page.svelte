<script lang="ts">
    import NewSkuForm from "$lib/components/product/new_sku/organisms/NewSkuForm.svelte";

    let { data } = $props();
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="w-full bg-neutral-900 p-6">
            <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Добавление SKU</h1>
            </div>

            <NewSkuForm product={data.product} />
        </div>
    </div>
</div>