<script>
    import "../app.css";
    import { page } from "$app/state";

    let { children } = $props();

    //links as shown in browser
    const hindeFooterOnPointcloud = ["/globe"];
    const hideHeader = ["/starerkit", "/globe", "/"];
</script>

{@render children()}
{#if !hideHeader.includes(page.url.pathname)}
    <header class="bg-black text-green-700 p-5 font-mono text-xs text-center">
        <a
            href="/"
            class="title absolute top-6 left-7 z-10 font-mono text-[#2fff3e] text-base font-bold tracking-widest"
        >
            STARTERKIT
        </a>
    </header>
{/if}
{#if !hindeFooterOnPointcloud.includes(page.url.pathname)}
    <footer class="bg-black text-neutral-500 p-5 font-mono text-xs text-center">
        <p>©2026 Jennifer Janac & Anton Rabanus</p>
    </footer>
{/if}
