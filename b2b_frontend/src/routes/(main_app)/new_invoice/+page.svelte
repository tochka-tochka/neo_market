<script lang="ts">
    import NewInvoiceForm from "$lib/components/organisms/NewInvoiceForm.svelte";

    let { data } = $props();

    let products = data?.products;
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen py-6 px-60">
        <div class="bg-gradient-to-b from-neutral-900 to-neutral-950 p-6">
            <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary pb-6 pt-2">
                <h1 class="font-Manrope font-semibold text-4xl">Создание накладной</h1>
            </div>

            <NewInvoiceForm products={products} />
        </div>
    </div>
</div>