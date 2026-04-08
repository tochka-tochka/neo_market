<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
    import { sidebarOpen } from '$lib/stores/sidebar';

	let { children } = $props();
	import '../app.css'
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>
<main class="bg-neutral min-h-screen flex justify-center items-center">
	{@render children()}
</main>