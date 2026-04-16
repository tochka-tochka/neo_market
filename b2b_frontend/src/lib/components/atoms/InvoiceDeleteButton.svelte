<script lang="ts">
    import { invalidate } from "$app/navigation";
    import { API_URL } from "$lib";
    let { invoiceId } : { invoiceId : string } = $props()

    async function deleteInvoice() {
        try {
            await fetch(`${API_URL}/invoices/${invoiceId}/`, {
                method: "DELETE",
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem("token")}`
                }
            })
            invalidate('invoices:delete')
        } catch (error) {
            console.error('Error accepting invoice:', error);
        }
    }

</script>
<button
    type="button"
    onclick={() => deleteInvoice()}
    class="px-3 py-1 ml-3 border border-red-500/50 text-red-400 cursor-pointer hover:bg-red-500/10"
    style="cursor: pointer;"
>
    <span class="font-Manrope font-light text-md">Удалить</span>
</button>