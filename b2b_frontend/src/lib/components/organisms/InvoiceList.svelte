<script lang="ts">
    import type { InvoiceType } from "$lib/types";
    import Invoice from "$lib/components/molecules/Invoice.svelte";
    let { invoices }: { invoices: InvoiceType[] } = $props();
</script>
<div class="space-y-8">
    {#each invoices as invoice}
        <Invoice invoice={invoice} />
    {/each}
</div>