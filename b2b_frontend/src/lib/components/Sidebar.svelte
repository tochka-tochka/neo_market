<script lang="ts">
    import { sidebarOpen } from '$lib/stores/sidebar';
</script>
<button
    onclick={() => $sidebarOpen = !$sidebarOpen}
    class="fixed top-8 left-6 z-50 p-2 rounded-md text-white hover:bg-primary/20"
>
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
</button>

<aside
    class="fixed left-0 top-0 h-full bg-neutral z-40 flex flex-col"
    class:w-70={$sidebarOpen}
    class:w-0={!$sidebarOpen}
    class:overflow-hidden={!$sidebarOpen}
>
    <div class="p-4">
        <h1 class="font-Manrope font-semibold text-2xl text-white bg-primary/50 px-3 py-2  mt-22">
            Neo_Market_Seller
        </h1>
    </div>
    <nav class="mt-4 flex flex-col">
        <a 
            href="/my_products" 
            class="font-Manrope font-light text-xl text-white px-4 py-3 hover:bg-neutral-highlight"
        >
            Мои товары
        </a>
    </nav>
</aside>
