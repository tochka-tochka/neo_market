<script lang="ts">
    import type { SkuType } from "$lib/types";

    let {
        products,
        selectedValue = $bindable()
    }: {
        products: SkuType[];
        selectedValue: string;
    } = $props();
</script>

<div class="flex flex-col gap-3 pb-8">
    <label class="font-Manrope font-light text-xl text-tx-secondary" for="product-selector">
        Товар
    </label>

    <select
        id="product-selector"
        bind:value={selectedValue}
        class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light outline-none"
    >
        <option value="new">Добавить новый товар</option>
        {#each products as product}
            <option value={String(product.id)}>
                {product.title}
            </option>
        {/each}
    </select>
</div>