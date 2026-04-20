<script lang="ts">
import type { Char } from "$lib/types";

let { chars }: { chars: Char[] } = $props();
</script>

<div class="flex flex-col gap-3">
    {#each chars as char}
        <div class="flex flex-row gap-2">
            <p class="font-Manrope font-light text-xl text-tx-secondary">{char.name}</p>
            <p class="font-Manrope font-light text-xl text-white">{char.value}</p>
        </div>
    {/each}
</div>