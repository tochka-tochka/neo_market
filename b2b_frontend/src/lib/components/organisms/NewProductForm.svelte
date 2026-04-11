<script lang="ts">
    import CreateProductFields from "../molecules/CreateProductFields.svelte";
    import KeyValueEditor from "$lib/components/molecules/KeyValueEditor.svelte";
    import CategorySelect from "../molecules/CategorySelect.svelte";
    import Carousel from "$lib/components/shadcn/carousel/carousel.svelte";
    import CarouselContent from "$lib/components/shadcn/carousel/carousel-content.svelte";
    import CarouselItem from "$lib/components/shadcn/carousel/carousel-item.svelte";
    import CarouselPrevious from "$lib/components/shadcn/carousel/carousel-previous.svelte";
    import CarouselNext from "$lib/components/shadcn/carousel/carousel-next.svelte";
    import { API_URL } from '$lib';
    import type { Char, Category } from "$lib/types";
    import { goto } from "$app/navigation";

    let { categoryOptions } : { categoryOptions: Category[] } = $props();

    let title : string = $state("");
    let description : string = $state("");
    let category : Category = $state({
        id: "",
        value: ""
    });
    let images : File[] = $state([]);
    let imagePreviews : string[] = $state([]);
    let characteristics : Char[] = $state([]);
    let fileInput : HTMLInputElement | null = $state(null);
    
    function handleImageChange(e: Event) {
        const target = e.target as HTMLInputElement;
        const files = target.files;
        if (files && files.length > 0) {
            const newImages = Array.from(files);
            images = [...images, ...newImages];
            
            const newPreviews = newImages.map(file => URL.createObjectURL(file));
            imagePreviews = [...imagePreviews, ...newPreviews];
        }
        // Reset input to allow selecting same files again
        target.value = '';
    }

    function openFilePicker() {
        fileInput?.click();
    }

    function removeImage(index: number, e: Event) {
        e.stopPropagation();
        images = images.filter((_, i) => i !== index);
        imagePreviews = imagePreviews.filter((_, i) => i !== index);
    }

    async function submitForm(e: SubmitEvent) {
        e.preventDefault();

        const formData = new FormData();
        
        formData.append("title", title);
        formData.append("description", description);
        formData.append("category", category.id);
        images.forEach((image) => {
            formData.append("images", image);
        });
        formData.append("characteristics", JSON.stringify(characteristics));

        console.log([...formData.entries()]);

        await fetch(`${API_URL}/products/`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem("token")}`
        }});

        goto('/products')
    }
</script>

<div class="pt-8">
    <form onsubmit={submitForm}>
        <div class="grid grid-cols-3 gap-6 p-3">
        <div class="flex flex-col col-span-3 gap-1">
            <input
                bind:value={title}
                id="title"
                placeholder="Название"
                type="text"
                class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
            />
        </div>

        <div class="flex flex-col col-span-3 gap-1">
            <textarea
                bind:value={description}
                placeholder="Описание"
                id="description"
                rows="3"
                class="w-full border-b border-white/20 px-4 py-4 text-white text-lg font-Manrope font-light outline-none placeholder:text-tx-secondary"
            ></textarea>
        </div>

        <CategorySelect 
            bind:value={category} 
            options={categoryOptions} 
        />

        <div class="flex flex-col col-span-1 gap-1">
            <label class="font-Manrope font-light text-lg text-tx-secondar mb-2" for="image">
                Изображения
            </label>
            <div class="relative w-48 h-48">
                <input
                    bind:this={fileInput}
                    id="image"
                    type="file"
                    accept="image/*"
                    multiple
                    class="hidden"
                    onchange={handleImageChange}
                />
                <Carousel class="w-full h-full">
                    <CarouselContent>
                        {#each imagePreviews as preview, index}
                            <CarouselItem>
                                <div class="relative w-full h-48">
                                    <img 
                                        src={preview} 
                                        alt="Preview" 
                                        class="w-full h-full object-cover rounded-lg"
                                    />
                                    <button
                                        type="button"
                                        onclick={(e) => removeImage(index, e)}
                                        class="absolute top-1 right-1 w-6 h-6 text-black rounded-full flex items-center justify-center hover:opacity-70"
                                    >
                                        X
                                    </button>
                                </div>
                            </CarouselItem>
                        {/each}
                        {#if images.length === 0}
                            <CarouselItem>
                                <button
                                    type="button"
                                    onclick={openFilePicker}
                                    class="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-white/20 rounded-lg cursor-pointer hover:border-white/40 transition-colors"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-tx-secondary mb-2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                                    </svg>
                                    <span class="text-tx-secondary text-sm">Добавить</span>
                                </button>
                            </CarouselItem>
                        {/if}
                    </CarouselContent>
                    <CarouselPrevious class="left-[-4px] top-1/2 -translate-y-1/2 -translate-x-8 text-white hover:text-white/80 z-10" />
                    <CarouselNext class="right-[-4px] top-1/2 -translate-y-1/2 translate-x-8 text-white hover:text-white/80 z-10" />
                </Carousel>
                <button
                    type="button"
                    onclick={openFilePicker}
                    class="mt-3 text-sm text-tx-secondary hover:text-white transition-colors"
                >
                    + Добавить изображение
                </button>
            </div>
        </div>

        <div>
            <label class="font-Manrope font-light text-lg text-tx-secondar mb-2" for="image">
                Свойства
            </label>
            <KeyValueEditor bind:chars={characteristics} keyPlaceholder="Бренд" valuePlaceholder="Apple" />
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