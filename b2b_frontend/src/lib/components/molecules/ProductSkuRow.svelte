<script lang="ts">
    import type { SkuType } from "$lib/types";
    import { goto, invalidate } from "$app/navigation";
    import { API_URL } from "$lib";

    let {
        sku,
        productId,
    }: {
        sku: SkuType;
        productId: string;
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
        {sku.active_quantity}
    </td>

    <td>
        <button
            type="button"
            onclick={() => goto(`/products/${productId}/${sku.id}/edit`)}
            class="px-4 py-2 cursor-pointer"
            style="cursor: pointer;"
        >
            <span class="font-Manrope font-bold text-md text-white/90 hover:text-white/70">Редактировать</span>
        </button>
    </td>
    <td>
        <button
            type="button"
            onclick={async () => {
                const response = await fetch(`${API_URL}/skus/${sku.id}/`, {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    }
                });
                
                invalidate('skus:update')
            }}
            class="px-4 py-2 border border-red-500/50 text-red-400 cursor-pointer hover:bg-red-500/10"
            style="cursor: pointer;"
        >
            <span class="font-Manrope font-light text-md">Удалить</span>
        </button>
    </td>
</tr>