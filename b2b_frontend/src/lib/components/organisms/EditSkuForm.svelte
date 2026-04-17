<script lang="ts">
    import { goto } from "$app/navigation";
    import type { ProductType, SkuType, Char } from "$lib/types";
    import KeyValueEditor from "$lib/components/molecules/KeyValueEditor.svelte";
    import { API_URL } from "$lib";

    let {
        product,
        sku
    }: {
        product: ProductType;
        sku: SkuType;
    } = $props();

    let SKU: string = $state(sku.name);
    let price: string = $state(String(sku.price));
    let active_quantity: string = $state(String(sku.active_quantity));
    let characteristics: Char[] = $state(sku.characteristics || []);

    async function handleSubmit() {
        const formData = new FormData();
        formData.append("name", SKU);
        formData.append("price", price);
        formData.append("active_quantity", active_quantity);
        formData.append("characteristics", JSON.stringify(characteristics));
        formData.append("product_id", product.id)

        await fetch(`${API_URL}/skus/${sku.id}/`, {
            method: "PUT",
            body: formData,
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
            }
        }
        )

        goto(`/products/${product.id}`);
    }
</script>

<div class="pt-8">
    <form onsubmit={handleSubmit}>
        <div class="grid grid-cols-3 gap-6">
            <div class="col-span-3 border border-white/10 bg-neutral p-4">
                <p class="font-Manrope font-light text-lg text-tx-secondary pb-2">Товар</p>
                <p class="font-Manrope font-semibold text-2xl text-white">{product.title}</p>
                <p class="font-Manrope font-light text-lg text-tx-secondary pt-2">{product.category?.value || product.category}</p>
            </div>

            <div class="flex flex-col col-span-3 gap-1">
                <label class="font-Manrope font-light text-lg text-tx-secondary" for="price">
                    SKU
                </label>
                <input
                    id="price"
                    type="text"
                    bind:value={SKU}
                    class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
                />
            </div>

            <div class="flex flex-row col-span-3 grid grid-cols-2 gap-6">
                <div class="flex flex-col gap-1 col-span-1">
                    <label class="font-Manrope font-light text-lg text-tx-secondary" for="price">
                        Цена
                    </label>
                    <input
                        id="price"
                        type="number"
                        bind:value={price}
                        placeholder="Введите цену"
                        class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
                    />
                </div>
                <div class="flex flex-col gap-1 col-span-1">
                    <label class="font-Manrope font-light text-lg text-tx-secondary" for="price">
                        Количество
                    </label>
                    <input
                        id="price"
                        type="number"
                        bind:value={active_quantity}
                        placeholder="Введите количество товара"
                        class="w-full border-b border-white/20 px-4 py-4  text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
                    />
                </div>
            </div>

            <div class="col-span-2">
                <label class="font-Manrope font-light text-lg text-tx-secondary mb-2" for="properties">
                    Свойства
                </label>
                <KeyValueEditor bind:characteristics keyPlaceholder="Например: Цвет" valuePlaceholder="Например: Черный" />
            </div>
        </div>

        <div class="pt-8">
            <button
                type="submit"
                class="px-6 py-4 bg-white cursor-pointer hover:bg-white/90"
                style="cursor: pointer;"
            >
                <span class="font-Manrope font-bold text-lg text-neutral">Сохранить</span>
            </button>
        </div>
    </form>
</div>