<!-- workflow: 
1. querySelection finds the nearest point when you click
2. library calls onSelection with that point (ignored just now) .. for debugging 
3. Meanwhile your onclick={handleCanvasClick} on the outer div fires too
4. handleCanvasClick reads whatever is in tooltip and sets selectedPoint
-->

<script>
    import { EmbeddingView } from "embedding-atlas/svelte";
    import { onMount } from "svelte";

    // 1. Accept the type prop (ITEMS or OUTFIT)
    let { 
        type = "ITEMS", 
        selectedCategories = new Set(),
        dateValues = [new Date("2016-01-01").getTime(), new Date("2026-12-31").getTime()],
        timeValues = [0, 23],
        targetColor = "#ffffff",
        colorTolerance = 50,
        colorFilterActive = false,
        activeCity = "ALL"
    } = $props();
    
let tooltip = $state(null);
    let selectedPoint = $state(null);
    let containerWidth = $state(800);
    let containerHeight = $state(800);
    let containerEl;
    let currentController = null;

    let rawData = $state([]);

    let filteredData = $derived.by(() => {
        if (rawData.length === 0) return [];
        
        let targetRgb;
        let tolSq;
        if (colorFilterActive) {
            targetRgb = hexToRgb(targetColor);
            tolSq = colorTolerance * colorTolerance;
        }

        return rawData.filter((d) => {
            const dDate = new Date(d.date).getTime();
            if (dDate < dateValues[0] || dDate > dateValues[1]) return false;

            const dTime = parseInt(d.time);
            if (isNaN(dTime) || dTime < timeValues[0] || dTime > timeValues[1]) return false;

            if (selectedCategories.size > 0) {
                if (type === "OUTFITS") {
                    const cats = String(d.category_list).split("|").map(Number);
                    if (![...selectedCategories].every((c) => cats.includes(c))) return false;
                } else {
                    if (!selectedCategories.has(parseInt(String(d.category_list).split('|')[0]))) return false;
                }
            }

            if (colorFilterActive) {
                const dr = d.rgb[0] - targetRgb[0];
                const dg = d.rgb[1] - targetRgb[1];
                const db = d.rgb[2] - targetRgb[2];
                if ((dr * dr + dg * dg + db * db) > tolSq) return false;
            }

            if (activeCity !== "ALL" && String(d.city).toLowerCase() !== activeCity.toLowerCase()) return false;

            return true;
        });
    });

        let viewData = $derived.by(() => {
            if (filteredData.length === 0) return null;
            return {
                x: new Float32Array(filteredData.map((d) => d.xNorm)),
                y: new Float32Array(filteredData.map((d) => d.yNorm)),
                category: new Uint8Array(
                    filteredData.map((d) => parseInt(String(d.category_list).split('|')[0]) - 1),
                ),
            };
        });

    const categoryColors = [
        "#FA8072", // 1 Short Sleeve Top: salmon
        "#FF924C", // 2 Long Sleeve Top: orange
        "#FFCA3A", // 3 Short Sleeve Outerwear: Yellow
        "#C5CA30", // 4 Long Sleeve Outerwear: lime
        "#8AC926", // 5 Vest: bright green
        "#36949D", // 6 Sling: light blue
        "#FFFFFF", // 7 Shorts: blue
        "#4267AC", // 8 Trousers: medium blue
        "#565AA0", // 9 Skirt: purple
        "#6A4C93", // 10 Short Sleeve Dress: light purple
        "#808080", // 11 Long Sleeve Dress: gray
        "#00FF00", // 12 Vest Dress: neon green
        "#8B0000", // 13 Sling Dress: red
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

    async function loadData(url) {
        // Cancel any in-flight fetch
        if (currentController) currentController.abort();
        currentController = new AbortController();

        viewData = null;
        rawData = [];
        filteredData = [];
        selectedPoint = null;

        try {
            const response = await fetch(url, {
                signal: currentController.signal,
            });
            if (!response.ok) throw new Error("Fetch failed");
            const json = await response.json();

            processData(json);
        } catch (err) {
            if (err.name === "AbortError") return; // expected, ignore
            console.error("Error loading data:", err);
        }
    }

    function processData(json) {
        const rawX = json.map((d) => parseFloat(d.x));
        const rawY = json.map((d) => parseFloat(d.y));
        const categoryColumn = new Uint8Array(
            json.map((d) => (d.category_list ? parseInt(String(d.category_list).split('|')[0]) - 1 : 0)),
        );
        // const categoryColumn = new Uint8Array(
        //     json.map((d) => parseInt(d.category) - 1),
        // );

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
            rgb: hexToRgb(d.color)
        }));
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

    function hexToRgb(hex) {
        if (!hex) return [0, 0, 0];
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16)
        ] : [0, 0, 0];
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
                for (let i = 0; i < filteredData.length; i++) {
                    const dx = filteredData[i].xNorm - x;
                    const dy = filteredData[i].yNorm - y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < minDist) {
                        minDist = dist;
                        nearest = i;
                    }
                }
                if (nearest === null || minDist > unitDistance * 20)
                    return null;
                return {
                    ...filteredData[nearest],
                    category: parseInt(String(filteredData[nearest].category_list).split('|')[0]) - 1,
                };
            }}
        />
    {:else}
        <div class="flex items-center justify-center h-full text-green-400">
            Loading data...
        </div>
    {/if}
    {#if selectedPoint}
        <div class="absolute top-4 right-4 p-4 bg-white rounded shadow-lg text-black max-w-xs z-50">
            <h3 class="font-bold text-lg mb-2">Metadata</h3>
            <p>ID: {selectedPoint.id}</p>
            <p>Date: {selectedPoint.date}</p>
            <p class="text-xs break-all mb-1">Path: {selectedPoint.crop_path}</p>
            <img 
                src={`http://localhost:5000/image/${selectedPoint.crop_path}`} 
                alt="Cropped entity" 
                class="w-full h-auto mt-2 rounded border border-neutral-300"
            />
            <button class="mt-2 text-blue-500 text-base font-bold uppercase" onclick={() => (selectedPoint = null)}>Close</button>
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
