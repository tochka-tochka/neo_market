<script lang="ts">
import { goto } from "$app/navigation";
import { API_URL, authorized } from "$lib";
import Characteristics from "$lib/components/atoms/Characteristics.svelte";
import Carousel from "$lib/components/shadcn/carousel/carousel.svelte";
import CarouselContent from "$lib/components/shadcn/carousel/carousel-content.svelte";
import CarouselItem from "$lib/components/shadcn/carousel/carousel-item.svelte";
import CarouselNext from "$lib/components/shadcn/carousel/carousel-next.svelte";
import CarouselPrevious from "$lib/components/shadcn/carousel/carousel-previous.svelte";
import type { ProductType } from "$lib/types";

let {
	product,
}: {
	product: ProductType;
} = $props();

let showDeleteConfirm = $state(false);

console.log(product);
</script>

<div class="p-4">
    <div class="flex flex-row justify-between items-start pb-6">
        <h2 class="font-Manrope font-semibold text-3xl text-white">Информация о товаре</h2>
        <div>
                <button
                    type="button"
                    onclick={() => goto(`/products/${product.id}/edit`)}
                    class="px-6 py-3 bg-white cursor-pointer hover:bg-white/90"
                    style="cursor: pointer;"
                >
                    <span class="font-Manrope font-bold text-xl text-neutral">Редактировать товар</span>
                </button>
                <button
                    type="button"
                    onclick={async () => {
                        await (authorized(fetch))(`${API_URL}/products/${product.id}/`, {
                            method: "DELETE",
                            headers: {
                                'Authorization': `Bearer ${localStorage.getItem('token')}`
                            }
                        })
                        goto("/products")
                    }}
                    class="px-6 py-3 ml-3 border border-red-500/50 text-red-400 cursor-pointer hover:bg-red-500/10"
                    style="cursor: pointer;"
                >
                    <span class="font-Manrope font-light text-lg">Удалить товар</span>
                </button>
        </div>
    </div>

    <div class="flex flex-row items-center justify-start gap-4 pb-8">
        <div class="mx-5 max-w-100">
            <Carousel class="relative w-full">
                    <CarouselContent>
                        {#each product.images as image}
                            <CarouselItem class="content-center">
                                <div class="relative w-100 h-100 flex items-center justify-center">
                                    <img 
                                        src={image.url} 
                                        alt="Preview" 
                                        class="w-100 h-100 object-contain"
                                    />
                                </div>
                            </CarouselItem>
                        {/each}
                    </CarouselContent>
                    <CarouselPrevious class="left-[-4px] top-1/2 -translate-y-1/2 -translate-x-8 text-white hover:text-white/80 z-10" />
                    <CarouselNext class="right-[-4px] top-1/2 -translate-y-1/2 translate-x-8 text-white hover:text-white/80 z-10" />
            </Carousel>
        </div>

        <div class="flex flex-col justify-between gap-6 ml-10">
            <div>
                <h2 class="font-Manrope font-semibold text-3xl text-white">{product.title}</h2>
            </div>

            <div>
                <p class="font-Manrope font-light text-xl text-tx-secondary pb-2">Описание</p>
                <p class="font-Manrope font-light text-xl text-white leading-relaxed">
                    {product.description}
                </p>
            </div>

            <div>
                <p class="font-Manrope font-light text-xl text-tx-secondary pb-2">Категория</p>
                <p class="font-Manrope font-light text-xl text-white">{product.category.value}</p>
            </div>

            <Characteristics chars={product.characteristics} />
        </div>
    </div>
</div>