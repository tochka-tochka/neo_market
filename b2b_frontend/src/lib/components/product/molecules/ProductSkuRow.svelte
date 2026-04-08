<script lang="ts">
    import type { SkuType } from "$lib/types";

    let {
        sku
    }: {
        sku: SkuType;
    } = $props();
</script>

<tr>
    <td class="text-center align-middle py-8 px-2 font-Manrope font-normal text-lg text-white">
        {sku.name}
    </td>

    <td class="text-center align-middle py-8 px-2 font-Manrope font-normal text-lg text-white">
        {sku.price}
    </td>

    <td class="text-center align-middle py-8 px-2 font-Manrope font-normal text-lg text-white">
        {sku.quantity}
    </td>
</tr>