<script lang="ts">
let { id, title, image } = $props();
</script>
<div class="flex flex-row items-center">
    <img class="size-20 mr-8" src={image} alt={title} />
    <a href={`products/${id}`} class="font-Manrope font-semibold text-2xl duration-100 hover:opacity-80">{title}</a>
</div>