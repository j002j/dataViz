<!-- workflow: 
1. querySelection finds the nearest point when you click
2. library calls onSelection with that point (which you're ignoring now) .. for debugging 
3. Meanwhile your onclick={handleCanvasClick} on the outer div fires too
4. handleCanvasClick reads whatever is in tooltip and sets selectedPoint
-->

<script>
    import { EmbeddingView } from "embedding-atlas/svelte";
    import { onMount } from "svelte";

    // 1. Accept the type prop (ITEMS or OUTFIT)
    let { type = "ITEMS", selectedCategories = new Set() } = $props();

    let tooltip = $state(null);
    let selectedPoint = $state(null);
    let viewData = $state(null);
    let containerWidth = $state(800);
    let containerHeight = $state(800);
    let containerEl;
    let rawData = [];

    const categoryColors = [
        "#FF595E", // 1 Short Sleeve Top
        "#FF924C", // 2 Long Sleeve Top
        "#FFCA3A", // 3 Short Sleeve Outerwear
        "#C5CA30", // 4 Long Sleeve Outerwear
        "#8AC926", // 5 Vest
        "#36949D", // 6 Sling
        "#1982C4", // 7 Shorts
        "#4267AC", // 8 Trousers
        "#565AA0", // 9 Skirt
        "#6A4C93", // 10 Short Sleeve Dress
        "#FF595E", // 11 Long Sleeve Dress (reusing, only 10 colors in palette)
        "#FF924C", // 12 Vest Dress
        "#FFCA3A", // 13 Sling Dress
    ];

    const viewOptions = {
        colorScheme: "dark",
        opacity: 1,
        pointSize: 2,
    };

    // 2. Create a reactive URL based on the tab
    const apiUrl = $derived(`http://localhost:5000/api/${type.toLowerCase()}`);

    // 3. Use an effect to re-fetch whenever the URL changes
    $effect(() => {
        if (apiUrl) {
            loadData(apiUrl);
        }
    });

    // effect to rebuild viewData when selectedCategories changes (and rawData is available)
    $effect(() => {
        console.log(
            "EmbeddingView: categories effect ran, size:",
            selectedCategories.size,
        );
        if (rawData.length > 0) {
            selectedCategories; // declare dependency
            rebuildViewData();
        }
    });

    async function loadData(url) {
        viewData = null; // Clear view to show loading state
        selectedPoint = null; // Clear selection on switch

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Fetch failed");
            const json = await response.json();

            processData(json);
        } catch (err) {
            console.error("Error loading data:", err);
        }
    }

    function processData(json) {
        const rawX = json.map((d) => parseFloat(d.x));
        const rawY = json.map((d) => parseFloat(d.y));
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

        const xNorm = rawX.map((x) => ((x - minX) / (maxX - minX)) * 2 - 1);
        const yNorm = rawY.map((y) => ((y - minY) / (maxY - minY)) * 2 - 1);

        // rawData = json.map((d, i) => ({
        //     ...d,
        //     xNorm: xNorm[i],
        //     yNorm: yNorm[i],
        // }));

        // viewData = {
        //     x: new Float32Array(xNorm),
        //     y: new Float32Array(yNorm),
        //     category: categoryColumn,
        //     // category_list: , // adapt accoring to which categories I have per point cloud
        // };

        rawData = json.map((d, i) => ({
            ...d,
            xNorm: xNorm[i],
            yNorm: yNorm[i],
        }));

        rebuildViewData();
    }

    onMount(() => {
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                containerWidth = entry.contentRect.width;
                containerHeight = entry.contentRect.height;
            }
        });
        observer.observe(containerEl);
        return () => observer.disconnect();
    });

    function handleCanvasClick() {
        if (tooltip) {
            selectedPoint = tooltip;
        }
    }

    function applyFilter(data) {
        console.log(
            "applyFilter called, selectedCategories.size:",
            selectedCategories.size,
        );
        if (selectedCategories.size === 0) return data; // empty = show all
        return data.filter((d) => selectedCategories.has(parseInt(d.category)));
    }

    function rebuildViewData() {
        const filtered = applyFilter(rawData);
        viewData = {
            x: new Float32Array(filtered.map((d) => d.xNorm)),
            y: new Float32Array(filtered.map((d) => d.yNorm)),
            category: new Uint8Array(
                filtered.map((d) => parseInt(d.category) - 1),
            ),
        };
    }
</script>

<div
    bind:this={containerEl}
    class="flex-grow min-h-0 w-full bg-neutral-800"
    style="height: 100%;"
    onclick={handleCanvasClick}
>
    {#if viewData}
        <EmbeddingView
            data={viewData}
            width={containerWidth}
            height={containerHeight}
            config={viewOptions}
            {categoryColors}
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
        <div class="flex items-center justify-center h-full text-green-400">
            Loading data...
        </div>
    {/if}
    {#if selectedPoint}
        <div
            class="absolute top-4 right-4 p-4 bg-white rounded shadow-lg text-black max-w-xs"
        >
            <h3 class="font-bold text-lg mb-2">Metadata</h3>
            <p>ID: {selectedPoint.id}</p>
            <p class="text-xs break-all mb-1">
                Path: {selectedPoint.crop_path}
            </p>
            <button
                class="mt-2 text-blue-500 text-base"
                onclick={() => (selectedPoint = null)}>Close</button
            >
        </div>
    {/if}
</div>

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
