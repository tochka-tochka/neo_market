<script lang="ts">
import type { ProductType, SkuType } from "$lib/types";
import Product from "../atoms/Product.svelte";

let { products }: { products: ProductType[] } = $props();
</script>

<table class="w-full">
    <thead class="text-lg text-tx-secondary border-b border-white/20">
        <tr>
            <th scope="col" class="py-4 px-2 text-left text-tx-primary text-xl"><p class="font-Manrope font-light">Товар</p></th>
            <th scope="col" class="py-4 px-2"><p class="font-Manrope font-light">Кол-во SKU</p></th>
            <th scope="col" class="py-4 px-2"><p class="font-Manrope font-light">Категория</p></th>
            <th scope="col" class="py-4 px-2"><p class="font-Manrope font-light">Статус</p></th>
        </tr>
    </thead>
    <tbody class="font-Manrope font-regular">
        {#each products as product}
            <Product product={product} />
        {/each}
    </tbody>
</table>

