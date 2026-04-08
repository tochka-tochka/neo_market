<script lang="ts">
    import type { ProductType } from "$lib/types";
    import KeyValueEditor from "$lib/components/common/molecules/KeyValueEditor.svelte";

    let { product }: { product: ProductType } = $props();

    let price: string = $state("");
    let properties = $state<Record<string, string>>({});
    let imagePreview: string = $state("");
    let image: File = $state(new File([], ""));

    function handleImageChange(e: Event) {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            image = file;
            imagePreview = URL.createObjectURL(file);
        }
    }
</script>

<div class="pt-8">
    <form>
        <div class="grid grid-cols-3 gap-6">
            <div class="col-span-3 border border-white/10 bg-neutral p-4">
                <p class="font-Manrope font-light text-lg text-tx-secondary pb-2">Товар</p>
                <p class="font-Manrope font-semibold text-2xl text-white">{product.title}</p>
                <p class="font-Manrope font-light text-lg text-tx-secondary pt-2">{product.category?.value || product.category}</p>
            </div>

            <div class="flex flex-col col-span-3 gap-1">
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

            <div class="flex flex-col col-span-1 gap-1">
                <label class="font-Manrope font-light text-lg text-tx-secondary mb-2" for="image">
                    Изображение
                </label>
                <label
                    for="image"
                    class="flex items-center justify-center w-48 h-48 border-2 border-dashed border-white/20 rounded-lg cursor-pointer hover:border-white/40 transition-colors overflow-hidden"
                >
                    <input
                        id="image"
                        type="file"
                        accept="image/*"
                        class="hidden"
                        onchange={handleImageChange}
                    />
                    {#if imagePreview}
                        <img 
                            src={imagePreview} 
                            alt="Preview" 
                            class="w-full h-full object-cover"
                        />
                    {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-12 h-12 text-tx-secondary">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                        </svg>
                    {/if}
                </label>
            </div>

            <div class="col-span-2">
                <label class="font-Manrope font-light text-lg text-tx-secondary mb-2" for="properties">
                    Свойства
                </label>
                <KeyValueEditor bind:properties keyPlaceholder="Например: Цвет" valuePlaceholder="Например: Черный" />
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