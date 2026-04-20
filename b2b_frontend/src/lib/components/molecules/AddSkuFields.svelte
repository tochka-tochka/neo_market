<script lang="ts">
import type { ProductType, SkuType } from "$lib/types";

let { product }: { product: ProductType } = $props();
</script>

<div class="grid grid-cols-1 gap-6">
    <div class="border border-white/10 bg-neutral p-4">
        <p class="font-Manrope font-light text-lg text-tx-secondary pb-2">Выбранный товар</p>
        <p class="font-Manrope font-semibold text-2xl text-white">{product.title}</p>
        <p class="font-Manrope font-light text-lg text-tx-secondary pt-2">{product.category}</p>
    </div>

    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="price">
            Цена
        </label>
        <input
            id="price"
            type="number"
            placeholder="Введите цену"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light outline-none placeholder:text-tx-secondary"
        />
    </div>

    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="sku-image">
            Изображение варианта товара
        </label>
        <input
            id="sku-image"
            type="file"
            accept="image/*"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light file:mr-4 file:border-0 file:bg-white file:px-4 file:py-2 file:text-neutral"
        />
    </div>
</div>