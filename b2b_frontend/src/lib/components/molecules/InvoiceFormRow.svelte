<script lang="ts">
    import ProductSelect from "$lib/components/molecules/ProductSelect.svelte";
    import SkuSelect from "$lib/components/molecules/SkuSelect.svelte";

    let { 
        products, 
        item = $bindable() 
    } = $props();
</script>


<div class="grid grid-cols-5 gap-6 p-3">
    <div class="flex flex-col col-span-2 gap-1">
        <ProductSelect bind:value={item.product} options={products}/>
    </div>

    <div class="flex flex-col col-span-2 gap-1">
        <SkuSelect bind:value={item.sku} options={item.product?.skus || []} />
    </div>

    <div class="flex flex-col col-span-1 gap-1">
        <label class="font-Manrope font-light text-lg text-tx-secondary" for="category">
            Количество
        </label>
        <input
            bind:value={item.quantity}
            id="quantity"
            placeholder="Количество"
            type="number"
            class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
        />
    </div>
</div>
