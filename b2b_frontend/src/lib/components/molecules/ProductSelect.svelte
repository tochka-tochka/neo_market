<script lang="ts">
import type { ProductType } from "$lib/types";

let {
	options,
	value = $bindable(),
}: {
	options: ProductType[];
	value: ProductType;
	placeholder?: string;
} = $props();

let isOpen = $state(false);
let searchText = $state("");
let inputRef: HTMLInputElement;

let filteredOptions = $derived(
	searchText
		? options.filter((opt) =>
				opt.title.toLowerCase().includes(searchText.toLowerCase()),
			)
		: options,
);

function handleSelect(option: ProductType) {
	value = option;
	searchText = option.title;
	isOpen = false;
}

function handleInputFocus() {
	isOpen = true;
	searchText = value?.title || "";
}

function handleInputBlur() {
	setTimeout(() => {
		isOpen = false;
	}, 200);
}

function handleKeydown(e: KeyboardEvent) {
	if (e.key === "Escape") {
		isOpen = false;
		inputRef?.blur();
	}
}

// Initialize search text with current value
$effect(() => {
	if (value?.title) {
		searchText = value.title;
	}
});
</script>

<div class="relative flex flex-col col-span-3 gap-1">
    <label class="font-Manrope font-light text-lg text-tx-secondary" for="category">
        Товар
    </label>
    
    <div class="relative">
        <input
            bind:this={inputRef}
            bind:value={searchText}
            onfocus={handleInputFocus}
            onblur={handleInputBlur}
            onkeydown={handleKeydown}
            autocomplete="off"
            id="category"
            type="text"
            class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
        />
        
        <button
            type="button"
            class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none"
        >
            <svg 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke-width="1.5" 
                stroke="currentColor" 
                class="w-5 h-5 text-tx-secondary transition-transform {isOpen ? 'rotate-180' : ''}"
            >
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
        </button>
    </div>

    {#if isOpen && filteredOptions.length > 0}
        <div 
            class="absolute z-50 w-full mt-1 bg-neutral border border-white/20 rounded-lg shadow-lg overflow-hidden"
            style="top: 100%;"
        >
            <ul class="max-h-60 overflow-y-auto">
                {#each filteredOptions as option}
                    <li>
                        <button
                            type="button"
                            onmousedown={() => handleSelect(option)}
                            class="w-full px-4 py-3 text-left text-white text-lg font-Manrope font-light hover:bg-white/10 transition-colors"
                        >
                            {option.title}
                        </button>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
</div>
