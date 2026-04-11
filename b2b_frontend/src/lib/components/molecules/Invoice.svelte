<script lang="ts">
    import type { InvoiceType } from "$lib/types";
    import InvoiceRow from "$lib/components/atoms/InvoiceRow.svelte";
    import InvoiveAcceptbutton from "$lib/components/atoms/InvoiveAcceptbutton.svelte";
    let { invoice } : { invoice: InvoiceType } = $props();

    let showDetails = $state(false);
</script>
<div class="flex flex-row justify-between items-center mt-4">
    <button
        class="text-left text-lg text-tx-secondary font-Manrope font-regular duration-100 hover:text-tx-secondary/75 transition-colors cursor-pointer"
        onclick={() => showDetails = !showDetails}
    >
        {`Накладная #${invoice.id.slice(0, 8)} от ${new Date(invoice.date).toLocaleDateString()}`}
    </button>
    <InvoiveAcceptbutton invoiceId={invoice.id} />
</div>
<div
    class="overflow-hidden transition-all duration-300 ease-in-out"
    style:max-height={showDetails ? '1000px' : '0'}
    style:opacity={showDetails ? '1' : '0'}
>
    <table class="w-full">
        <thead class="text-lg text-tx-secondary">
            <tr>
                <th>Товар</th>
                <th>SKU</th>
                <th>Количество</th>
                <th>Цена</th>
            </tr>
        </thead>
        <tbody class="font-Manrope font-regular">
            {#each invoice.items as row}
                <InvoiceRow item={row} />
            {/each}
        </tbody>
    </table>
</div>