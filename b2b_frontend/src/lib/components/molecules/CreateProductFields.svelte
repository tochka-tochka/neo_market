<script lang="ts">
    let { categories }: { categories: string[] } = $props();
</script>

<div class="grid grid-cols-1 gap-6">
    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="title">
            Название
        </label>
        <input
            id="title"
            type="text"
            placeholder="Введите название товара"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light outline-none placeholder:text-tx-secondary"
        />
    </div>

    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="description">
            Описание
        </label>
        <textarea
            id="description"
            rows="5"
            placeholder="Введите описание товара"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light outline-none placeholder:text-tx-secondary"
        ></textarea>
    </div>

    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="category">
            Категория
        </label>
        <select
            id="category"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light outline-none"
        >
            {#each categories as category}
                <option value={category}>{category}</option>
            {/each}
        </select>
    </div>

    <div class="flex flex-col gap-3">
        <label class="font-Manrope font-light text-xl text-tx-secondary" for="image">
            Изображение
        </label>
        <input
            id="image"
            type="file"
            accept="image/*"
            class="w-full bg-neutral border border-white/20 px-4 py-4 text-white text-xl font-Manrope font-light file:mr-4 file:border-0 file:bg-white file:px-4 file:py-2 file:text-neutral"
        />
    </div>
</div>