<script lang="ts">
    import { goto, invalidate } from "$app/navigation";
    import { API_URL } from "$lib";

    let { 
        invoiceId
    } : {
        invoiceId: string;
    } = $props();

    async function acceptInvoice() {
        try {
            const response = await fetch(`${API_URL}/invoices/${invoiceId}/accept/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to accept invoice');
            }
            invalidate('invoices:accept')
        } catch (error) {
            console.error('Error accepting invoice:', error);
        }
    }

</script>
<button 
    type="button"
    onclick={() => acceptInvoice()}
    class="px-3 py-1 bg-white cursor-pointer hover:bg-white/90"
    style="cursor: pointer;"
>
    <span class="font-Manrope font-bold text-md text-neutral">Принять</span>
</button>