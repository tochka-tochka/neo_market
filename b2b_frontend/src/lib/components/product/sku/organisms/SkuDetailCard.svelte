<script lang="ts">
    import { goto } from "$app/navigation";
    import Status from "$lib/components/my_products/atoms/Status.svelte";
    import Characteristics from "$lib/components/common/atoms/Characteristics.svelte";
    import type { SkuType } from "$lib/types";

    let {
        sku,
        productId
    }: {
        sku: SkuType;
        productId: string;
    } = $props();

    let showDeleteConfirm = $state(false);

    function handleDelete() {
        // TODO: отправить запрос на удаление
        console.log("Удаление SKU:", sku.id);
        goto(`/my_products/${productId}`);
    }
</script>

<div class="pt-8">
    <div class="flex flex-row justify-between items-start pb-6">
        <h2 class="font-Manrope font-semibold text-3xl text-white">Информация о SKU</h2>
            <div>
                <button
                    type="button"
                    onclick={() => goto(`/my_products/${productId}/${sku.id}/edit`)}
                    class="px-6 py-3 bg-white cursor-pointer hover:bg-white/90"
                    style="cursor: pointer;"
                >
                    <span class="font-Manrope font-bold text-xl text-neutral">Редактировать SKU</span>
                </button>
                <button
                    type="button"
                    onclick={() => showDeleteConfirm = true}
                    class="px-6 py-3 ml-3 border border-red-500/50 text-red-400 cursor-pointer hover:bg-red-500/10"
                    style="cursor: pointer;"
                >
                    <span class="font-Manrope font-light text-lg">Удалить SKU</span>
                </button>
            </div>
    </div>

    <div class="grid grid-cols-[220px_1fr] gap-8 border-b-[0.5px] border-white/20 pb-8">
        <div class="w-[220px] h-[220px] bg-neutral overflow-hidden">
            <img
                src={sku.image}
                alt={sku.id}
                class="w-full h-full object-cover"
            />
        </div>

        <div class="grid grid-cols-2 gap-6 content-start">
            <div>
                <p class="font-Manrope font-light text-xl text-tx-secondary pb-2">SKU</p>
                <p class="font-Manrope font-semibold text-3xl text-white">{sku.id}</p>
            </div>

            <div>
                <p class="font-Manrope font-light text-xl text-tx-secondary pb-2">Цена</p>
                <p class="font-Manrope font-light text-2xl text-white">{sku.price}</p>
            </div>

            <div>
                <p class="font-Manrope font-light text-xl text-tx-secondary pb-2">Количество</p>
                <p class="font-Manrope font-light text-2xl text-white">{sku.quantity}</p>
            </div>
        </div>
        <div>
                <Characteristics chars={sku.chars} />
        </div>
    </div>
</div>