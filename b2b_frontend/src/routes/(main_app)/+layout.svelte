<script lang="ts">
    import { goto } from '$app/navigation';
	import favicon from '$lib/assets/favicon.svg';
    import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
    import { sidebarOpen } from '$lib/stores/sidebar';

	let { children } = $props();
	import "../app.css"
	// const token = localStorage.getItem('token')
	// if (!token) {
	// 	goto('/auth/login');
	// }
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>
<Header />
<Sidebar />
<main class="{$sidebarOpen ? 'pl-70' : 'pl-0'}">
	{@render children()}
</main>