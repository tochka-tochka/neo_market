<script lang="ts">
    import AddInvoiceButton from "$lib/components/atoms/AddInvoiceButton.svelte";
    import InvoiceList from "$lib/components/organisms/InvoiceList.svelte";
    import type { InvoiceType } from "$lib/types";
    let { data } = $props();
    let invoices :  InvoiceType[] = data.invoices;
</script>

<div class="min-h-screen bg-neutral">
    <div class="container mx-auto self-center text-white min-h-screen p-6">
        <div class="grid grid-cols-4 w-full">
            <div class="col-span-3 w-full bg-gradient-to-b from-neutral-900 to-neutral-950 p-6">
                <div class="flex flex-row justify-between items-center border-b-[0.5px] border-tx-secondary/25 pb-6 pt-2">
                    <h1 class="font-Manrope font-semibold text-2xl">Накладные</h1>
                    <AddInvoiceButton />
                </div>
                <InvoiceList invoices={invoices} />
            </div>
        </div>
    </div>
</div>