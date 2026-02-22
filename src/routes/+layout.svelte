<script>
    import "../app.css";
    import { page } from "$app/state";

    let { children } = $props();

    const hindeFooterOn = [
        "/lib/visualization/StarterKitLayout.svelte",
        "/lib/visualization/EmbeddingView.svelte",
    ];
</script>

{@render children()}

{#if !hindeFooterOn.includes(page.url.pathname)}
    <footer class="bg-black text-green-700 p-5 font-mono text-xs text-center">
        <p>©2026 Jennifer Janac and Anton Rabanus</p>
    </footer>
{/if}
