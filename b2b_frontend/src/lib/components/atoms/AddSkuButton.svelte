<script lang="ts">
import { goto } from "$app/navigation";

let { productId }: { productId: string } = $props();
</script>
<button 
    type="button"
    onclick={() => goto(`${productId}/new_sku`)}
    class="px-6 py-4 bg-white cursor-pointer hover:bg-white/90"
    style="cursor: pointer;"
>
    <span class="font-Manrope font-bold text-xl text-neutral">Добавить SKU</span>
</button>