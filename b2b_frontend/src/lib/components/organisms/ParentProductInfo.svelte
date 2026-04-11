<script lang="ts">
    let {
        product
    }: {
        product: {
            id: number | string;
            title: string;
            description: string;
            category: string;
            image: string;
        };
    } = $props();
</script>

<div class="pt-8">
    <div class="">
        <h2 class="font-Manrope font-semibold text-2xl text-white">Товар</h2>
    </div>

    <div class="pt-6 grid grid-cols-1 gap-2">
        <div>
            <p class="font-Manrope font-light text-xl text-white">{product.title}</p>
        </div>
    </div>
</div>