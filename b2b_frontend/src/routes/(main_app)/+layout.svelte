<script lang="ts">
import favicon from "$lib/assets/favicon.svg";
import Header from "$lib/components/organisms/Header.svelte";
import Sidebar from "$lib/components/organisms/Sidebar.svelte";
import { sidebarOpen } from "$lib/stores/sidebar";

let { children } = $props();
import "../app.css";
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<Header />
<Sidebar />
<main class="{$sidebarOpen ? 'pl-70' : 'pl-0'}">
    {@render children()}
</main>