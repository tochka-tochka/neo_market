<script>
    import { goto } from "$app/navigation";

</script>
<button 
    type="button"
    onclick={() => goto("/new_product")}
    class="px-4 py-3 bg-white cursor-pointer hover:bg-white/90"
    style="cursor: pointer;"
>
    <span class="font-Manrope font-bold text-lg text-neutral">Добавить товар</span>
</button>