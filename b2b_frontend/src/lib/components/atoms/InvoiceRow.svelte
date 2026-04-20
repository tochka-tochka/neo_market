<script lang="ts">
import type { InvoiceItem } from "$lib/types";

let {
	item,
}: {
	item: InvoiceItem;
} = $props();

const sku = item.product.skus.find((s: any) => s.id === item.sku.id);
</script>
<tr class="text-center">
    <td class="text-center align-middle py-2 px-2 font-Manrope font-semibold text-lg">
        {item.product.title}
    </td>
    <td class="text-center align-middle py-3 px-2 font-Manrope font-light text-lg">{sku?.name ?? 'N/A'}</td>
    <td class="text-center align-middle py-3 px-2 font-Manrope font-light text-lg">{item.quantity}</td>
    <td class="text-center align-middle py-3 px-2 font-Manrope font-light text-lg">{(sku?.price || 0) * item.quantity}</td>
</tr>