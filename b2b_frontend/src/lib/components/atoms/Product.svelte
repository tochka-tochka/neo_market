<script lang="ts">
import type { ProductType } from "$lib/types";
import MainInfo from "./MainInfo.svelte";
import Status from "./Status.svelte";

let {
	product,
}: {
	product: ProductType;
} = $props();
</script>

<tr class="border-b-[0.5px] border-tx-secondary/10 text-center">
    <td class="text-center align-middle py-8 px-2">
            <MainInfo
                id={product.id}
                title={product.title}
                image={product?.images[0]?.url ?? "/placeholder.jpg"}
            />
    </td>
    <td class="text-center align-middle py-8 px-2 font-Manrope font-semibold text-lg">{product.skus.length}</td>
    <td class="text-center align-middle py-8 px-2 font-Manrope font-semibold text-lg">{product.category.value}</td>
    <td class="text-center align-middle py-8 px-2 font-Manrope font-semibold text-lg"><Status status={product.status} /></td>
</tr>