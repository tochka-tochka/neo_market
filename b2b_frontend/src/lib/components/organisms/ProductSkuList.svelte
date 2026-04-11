<script lang="ts">
    import { goto } from "$app/navigation";
    import ProductSkuRow from "$lib/components/molecules/ProductSkuRow.svelte";
    import AddSkuButton from "$lib/components/atoms/AddSkuButton.svelte";
    import type { SkuType } from "$lib/types";

    let {
        skus,
        productId
    }: {
        skus: SkuType[];
        productId: string;
    } = $props();
</script>

<div class="pt-8">
    <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary pb-6">
        <h2 class="font-Manrope font-semibold text-3xl text-white">SKU товара</h2>
        <AddSkuButton productId={productId}/>
    </div>

    <table class="w-full pt-6">
        <thead class="text-xl text-tx-secondary border-b border-white/20">
            <tr>
                <th scope="col" class="py-4 px-2">
                    <p class="font-Manrope font-light">SKU</p>
                </th>
                <th scope="col" class="py-4 px-2">
                    <p class="font-Manrope font-light">Цена</p>
                </th>
                <th scope="col" class="py-4 px-2">
                    <p class="font-Manrope font-light">Количество</p>
                </th>
                <th></th>
            </tr>
        </thead>

        <tbody>
            {#each skus as sku}
                <ProductSkuRow sku={sku} productId={productId} />
            {/each}
        </tbody>
    </table>
</div>