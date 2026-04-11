<script lang="ts">
    import { fade } from 'svelte/transition';
    import type { Char } from "$lib/types";
    let {
        chars = $bindable([]),
        keyPlaceholder = "Ключ",
        valuePlaceholder = "Значение"
    }: {
        chars?: Char[];
        keyPlaceholder?: string;
        valuePlaceholder?: string;
    } = $props();

    let entries = $state<Char[]>(chars ? [...chars] : []);

    $effect(() => {
        if (chars) {
            entries = [...chars];
        }
    });

    function addChar() {
        entries = [...entries, { name: "", value: "" }];
        chars = entries;
    }

    function removeChar(index: number) {
        entries = entries.filter((_, i) => i !== index);
        chars = entries;
    }

    function updateChar() {
        chars = entries;
    }
</script>

<div class="flex flex-col gap-4">
    <div class="flex flex-row justify-end items-center">
        <button
            type="button"
            onclick={addChar}
            class="text-white duration-100 hover:opacity-80 font-Manrope font-light text-lg cursor-pointer"
        >
            + Добавить
        </button>
    </div>

    {#if entries.length > 0}
        <div 
            class="flex flex-col gap-3"
            transition:fade={{ duration: 100 }}
        >
            {#each entries as entry, index (index)}
                <div 
                    class="flex flex-row gap-3 items-center"
                    transition:fade={{ duration: 100 }}
                >
                    <input
                        type="text"
                        placeholder={keyPlaceholder}
                        bind:value={entry.name}
                        oninput={updateChar}
                        class="flex-1 border-b border-white/20 px-4 py-3 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
                    />
                    <input
                        type="text"
                        placeholder={valuePlaceholder}
                        bind:value={entry.value}
                        oninput={updateChar}
                        class="flex-1 border-b border-white/20 px-4 py-3 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
                    />
                    <button
                        type="button"
                        onclick={() => removeChar(index)}
                        class="px-3 py-3 text-tx-secondary hover:text-white"
                    >
                        ✕
                    </button>
                </div>
            {/each}
        </div>
    {:else}
        <p class="font-Manrope font-light text-lg text-tx-secondary italic"
            in:fade={{ duration: 50, delay: 200 }}
        >
            Нет дополнительных свойств
        </p>
    {/if}
</div>