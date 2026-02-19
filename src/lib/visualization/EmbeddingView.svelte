<script>
    import { EmbeddingView } from "embedding-atlas/svelte";
    import { onMount } from "svelte";

    let tooltip = $state(null);
    let viewData = $state(null);
    let containerWidth = $state(800);
    let containerHeight = $state(800);
    let containerEl;

    const viewOptions = {
        // [Red, Green, Blue, Alpha]: each 0.0 to 1.0
        // backgroundColor: "#334155", // This is Tailwind's slate-700 hex code
        clearColor: [0.2, 0.255, 0.333, 1],
        opacity: 1,
    };

    onMount(async () => {
        // Watch container size and feed real pixel dimensions to EmbeddingView
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                containerWidth = entry.contentRect.width;
                containerHeight = entry.contentRect.height;
            }
        });
        observer.observe(containerEl);

        // Fetch data
        const response = await fetch("http://localhost:5000/api/items");
        if (!response.ok) {
            console.error("Server error:", response.status);
            return;
        }
        const json = await response.json();

        const xColumn = new Float32Array(json.map((d) => parseFloat(d.x)));
        const yColumn = new Float32Array(json.map((d) => parseFloat(d.y)));
        const categoryColumn = new Uint8Array(
            json.map((d) => parseInt(d.category) - 1),
        );

        viewData = { x: xColumn, y: yColumn, category: categoryColumn };

        // Cleanup observer when component is destroyed
        return () => observer.disconnect();
    });
</script>

<div
    bind:this={containerEl}
    class="flex-grow min-h-0 w-full bg-slate-700"
    style="height: 100%;"
>
    {#if viewData}
        <EmbeddingView
            data={viewData}
            width={containerWidth}
            height={containerHeight}
            options={viewOptions}
            {tooltip}
            onTooltip={(v) => (tooltip = v)}
        />
    {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
            Loading data...
        </div>
    {/if}
</div>

<!-- <script>
    import { EmbeddingView } from "embedding-atlas/svelte";
    import { onMount } from "svelte";

    //let data = [];

    // onMount(async () => {
    //     const response = await fetch("http://localhost:5000/api/items");
    //     if (!response.ok) {
    //         throw new Error("Server reposnds with : ${response.status}");
    //     } else {
    //         console.log("Server reposnds with : ${response.status}");
    //     }

    //     data = await response.json();
    //     console.log("Data loaded sucsessfully:", data);

    //     if (data.length === 0) {
    //         console.log("Data is 0");
    //     } else {
    //         console.log("count loaded data:", data.length);
    //     }

    //     if (!containerElement) {
    //         console.error("Container missing!");
    //         return;
    //     }
    // });

    let tooltip = $state(null);
    let viewData = $state(null); // null until ready

    onMount(async () => {
        const response = await fetch("http://localhost:5000/api/items");
        if (!response.ok) {
            console.error("Server error:", response.status);
            return;
        }

        const json = await response.json();
        console.log("Loaded rows:", json.length);

        // EmbeddingView requires typed arrays, not plain JSON
        const xColumn = new Float32Array(json.map((d) => parseFloat(d.x)));
        const yColumn = new Float32Array(json.map((d) => parseFloat(d.y)));
        // category must be 0-indexed integers as Uint8Array
        const categoryColumn = new Uint8Array(
            json.map((d) => parseInt(d.category) - 1),
        );

        viewData = { x: xColumn, y: yColumn, category: categoryColumn };
    });
</script>

<div class="flex-grow flex flex-col min-h-0 w-full">
    {#if viewData}
        <div class="flex-grow min-h-0 w-full">
            <EmbeddingView
                data={viewData}
                {tooltip}
                onTooltip={(v) => (tooltip = v)}
            />
        </div>
    {:else}
        <div class="flex items-center justify-center flex-grow text-gray-500">
            Loading data...
        </div>
    {/if}
</div> -->

<!-- check if no data on first render -->
<!-- {#if data.length > 0}
    <EmbeddingView {data} x="x" y="y" colorBy="category" />
    <div style="height: 600px; width: 100%;">
        <EmbeddingView {data} x="x" y="y" colorBy="category" />
    </div>
{:else}
    <p>Loading data...</p>
{/if} -->

<style>
    /* target the canvas inside the EmbeddingView */
    :global(canvas) {
        background: transparent !important;
        /* transparnet greey overlay: */
        /* mix-blend-mode: multiply; */
    }
</style>
