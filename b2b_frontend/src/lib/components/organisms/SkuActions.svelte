<script lang="ts">
import { goto } from "$app/navigation";

let {
	productId,
	skuId,
}: {
	productId: string | number;
	skuId: string | number;
} = $props();
</script>

<div class="pt-8 flex flex-row gap-4">
    <button
        type="button"
        onclick={() => goto(`/products/${productId}`)}
        class="px-6 py-4 border border-white/20 cursor-pointer hover:bg-white/5"
        style="cursor: pointer;"
    >
        <span class="font-Manrope font-light text-xl text-white">К товару</span>
    </button>
</div>