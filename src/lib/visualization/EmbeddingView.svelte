<script>
    import { EmbeddingView } from "embedding-atlas/svelte";
    import { onMount } from "svelte";

    let tooltip = $state(null); // This stores the currently hovered point data
    let selectedPoint = $state(null); // To store the point you clicked
    let viewData = $state(null);
    let containerWidth = $state(800);
    let containerHeight = $state(800);
    let containerEl;
    let rawData = [];

    const viewOptions = {
        // [Red, Green, Blue, Alpha]: each 0.0 to 1.0
        clearColor: [0.2, 0.255, 0.333, 1],
        opacity: 1,
        pointSize: 5,
        tolerance: 10,
    };

    function handleCanvasClick() {
        // We use the data currently in 'tooltip' (set by onTooltip)
        if (tooltip) {
            selectedPoint = tooltip;
            console.log("Point Selected:", selectedPoint);
        }
    }

    function handleTooltip(v) {
        console.log("tooltip:", v);
        tooltip = v;
    }

    onMount(async () => {
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                containerWidth = entry.contentRect.width;
                containerHeight = entry.contentRect.height;
            }
        });
        observer.observe(containerEl);

        const response = await fetch("http://localhost:5000/api/items");
        if (!response.ok) return;

        const json = await response.json();
        rawData = json;

        const rawX = json.map((d) => parseFloat(d.x));
        const rawY = json.map((d) => parseFloat(d.y));

        // Re-enable Category Column
        const categoryColumn = new Uint8Array(
            json.map((d) => parseInt(d.category) - 1),
        );

        let minX = Infinity,
            maxX = -Infinity,
            minY = Infinity,
            maxY = -Infinity;
        for (let i = 0; i < rawX.length; i++) {
            if (rawX[i] < minX) minX = rawX[i];
            if (rawX[i] > maxX) maxX = rawX[i];
            if (rawY[i] < minY) minY = rawY[i];
            if (rawY[i] > maxY) maxY = rawY[i];
        }

        // Normalize to -1 to 1 range
        const xNorm = rawX.map((x) => ((x - minX) / (maxX - minX)) * 2 - 1);
        const yNorm = rawY.map((y) => ((y - minY) / (maxY - minY)) * 2 - 1);

        // Store normalized coords back so we can match later
        rawData = json.map((d, i) => ({
            ...d,
            xNorm: xNorm[i],
            yNorm: yNorm[i],
        }));

        const xColumn = new Float32Array(xNorm);
        const yColumn = new Float32Array(yNorm);

        // Include category here so points have colors!
        viewData = { x: xColumn, y: yColumn, category: categoryColumn };

        return () => observer.disconnect();
    });
</script>

<div
    bind:this={containerEl}
    class="flex-grow min-h-0 w-full bg-slate-700"
    style="height: 100%;"
    onclick={handleCanvasClick}
>
    {#if viewData}
        <EmbeddingView
            data={viewData}
            width={containerWidth}
            height={containerHeight}
            config={viewOptions}
            onTooltip={handleTooltip}
            onSelection={(v) => {
                console.log("selection:", v);
            }}
            querySelection={async (x, y, unitDistance) => {
                let nearest = null;
                let minDist = Infinity;
                for (let i = 0; i < rawData.length; i++) {
                    const dx = rawData[i].xNorm - x;
                    const dy = rawData[i].yNorm - y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < minDist) {
                        minDist = dist;
                        nearest = i;
                    }
                }
                if (nearest === null || minDist > unitDistance * 20)
                    return null;
                return {
                    x: rawData[nearest].xNorm,
                    y: rawData[nearest].yNorm,
                    category: parseInt(rawData[nearest].category) - 1,
                };
            }}
        />
    {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
            Loading data...
        </div>
    {/if}
    {#if selectedPoint}
        <div
            class="absolute top-4 right-4 p-4 bg-white rounded shadow-lg text-black max-w-xs"
        >
            <h3 class="font-bold">Metadata</h3>
            <p>ID: {selectedPoint.id}</p>
            <p class="text-xs break-all">Path: {selectedPoint.crop_path}</p>
            <button
                class="mt-2 text-blue-500"
                onclick={() => (selectedPoint = null)}>Close</button
            >
        </div>
    {/if}
</div>

<!--  onTooltip={(v) => {
                console.log("tooltip fired:", v);
                tooltip = v;
            }}
            onSelection={(points) => {
                // console.log("selection:", v);
                if (!points || points.length === 0) return;
                const pt = points[0];
                // find original row by matching x and y
                const match = rawData.find(
                    (d) =>
                        Math.abs(parseFloat(d.x) - pt.x) < 1 &&
                        Math.abs(parseFloat(d.y) - pt.y) < 1,
                );
                console.log("matched row:", match);
            }} -->

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

<!--API response: waht does a single items from local host look like?  
    fetch('http://localhost:5000/api/items')
  .then(r => r.json())
  .then(d => console.log(d[0])) -->

<!-- test clicking 
    document.querySelector('svg').addEventListener('mousemove', (e) => console.log('svg mousemove', e.clientX, e.clientY))
undefined
document.querySelector('svg') -->

<style>
    /* target the canvas inside the EmbeddingView */
    :global(canvas) {
        background: transparent !important;
        /* transparnet greey overlay: */
        /* mix-blend-mode: multiply; */
    }
</style>
