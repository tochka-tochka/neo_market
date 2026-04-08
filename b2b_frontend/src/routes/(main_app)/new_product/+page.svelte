<script lang="ts">
    import NewProductForm from "$lib/components/new_product/organisms/NewProductForm.svelte";

    let { data } = $props();
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen py-6 px-60">
        <div class="bg-neutral-900 p-6">
            <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Добавление товара</h1>
            </div>

            <NewProductForm categoryOptions={data.categories} />
        </div>
    </div>
</div>