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
    let mouseX = $state(0);
    let mouseY = $state(0);
    let containerEl;
    let currentController = null;

    let rawObjects = $state.raw([]);

    let colDates;
    let colTimes;
    let colR, colG, colB;
    let colX, colY;

    let bitsetWords = 0;
    let indexCity = new Map();
    let indexCategory = new Map();

    function createBitset(size) { return new Uint32Array(Math.ceil(size / 32)); }
    function setBit(bitset, index) { bitset[index >> 5] |= (1 << (index & 31)); }
    function testBit(bitset, index) { return (bitset[index >> 5] & (1 << (index & 31))) !== 0; }
    function intersectBitsets(a, b) {
        const res = new Uint32Array(a.length);
        for (let i = 0; i < a.length; i++) res[i] = a[i] & b[i];
        return res;
    }
    function unionBitsets(a, b) {
        const res = new Uint32Array(a.length);
        for (let i = 0; i < a.length; i++) res[i] = a[i] | b[i];
        return res;
    }
    let viewData = $derived.by(() => {
        if (!rawObjects || rawObjects.length === 0) return null;
        
        const N = rawObjects.length;
        let activeMask = new Uint32Array(bitsetWords);
        activeMask.fill(0xFFFFFFFF);
        
        if (activeCity !== "ALL") {
            const cityMask = indexCity.get(activeCity.toLowerCase());
            if (cityMask) activeMask = intersectBitsets(activeMask, cityMask);
            else return null;
        }
    
        if (selectedCategories.size > 0) {
            let catMask = new Uint32Array(bitsetWords);
            if (type === "OUTFITS") catMask.fill(0xFFFFFFFF);
            
            let validMatch = false;
            for (const catId of selectedCategories) {
                const m = indexCategory.get(catId);
                if (type === "OUTFITS") {
                    if (m) {
                        catMask = intersectBitsets(catMask, m);
                        validMatch = true;
                    } else {
                        catMask.fill(0);
                    }
                } else {
                    if (m) {
                        catMask = unionBitsets(catMask, m);
                        validMatch = true;
                    }
                }
            }
            if (!validMatch) catMask.fill(0);
            activeMask = intersectBitsets(activeMask, catMask);
        }
    
        let targetRgb, tolSq;
        if (colorFilterActive) {
            targetRgb = hexToRgb(targetColor);
            tolSq = colorTolerance * colorTolerance;
        }
    
        const outX = [];
        const outY = [];
        const outCat = [];
        const outOriginalIndex = [];
    
        for (let i = 0; i < N; i++) {
            if (testBit(activeMask, i)) {
                if (colDates[i] < dateValues[0] || colDates[i] > dateValues[1]) continue;
                if (colTimes[i] < timeValues[0] || colTimes[i] > timeValues[1]) continue;
            
                if (colorFilterActive) {
                    const dr = colR[i] - targetRgb[0];
                    const dg = colG[i] - targetRgb[1];
                    const db = colB[i] - targetRgb[2];
                    if ((dr * dr + dg * dg + db * db) > tolSq) continue;
                }
            
                outX.push(colX[i]);
                outY.push(colY[i]);
                outCat.push(rawObjects[i].category);
                outOriginalIndex.push(i);
            }
        }
    
        if (outX.length === 0) return null;
    
        return {
            x: new Float32Array(outX),
            y: new Float32Array(outY),
            category: new Uint8Array(outCat),
            originalIndices: new Int32Array(outOriginalIndex)
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
        tooltip: false
    };

    // 2. Create a reactive URL based on the tab
    const apiUrl = $derived(`http://localhost:5000/api/${type.toLowerCase()}`);

    // 3. Use an effect to re-fetch whenever the URL changes
    $effect(() => {
        if (apiUrl) {
            loadData(apiUrl);
        }
    });

    $effect(() => {
        console.log("[State Layer] Tooltip payload:", tooltip);
        console.log("[State Layer] Selected point payload:", selectedPoint);
    });

    async function loadData(url) {
        // Cancel any in-flight fetch
        if (currentController) currentController.abort();
        currentController = new AbortController();

        viewData = null;
        rawObjects = [];
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
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        
        for (let i = 0; i < rawX.length; i++) {
            if (rawX[i] < minX) minX = rawX[i];
            if (rawX[i] > maxX) maxX = rawX[i];
            if (rawY[i] < minY) minY = rawY[i];
            if (rawY[i] > maxY) maxY = rawY[i];
        }
    
        const xNorm = rawX.map((x) => (x - minX) / (maxX - minX));
        const yNorm = rawY.map((y) => (y - minY) / (maxY - minY));
    
        const N = json.length;
        bitsetWords = Math.ceil(N / 32);
    
        colDates = new Float64Array(N);
        colTimes = new Int8Array(N);
        colR = new Uint8Array(N);
        colG = new Uint8Array(N);
        colB = new Uint8Array(N);
        colX = new Float32Array(N);
        colY = new Float32Array(N);
    
        indexCity.clear();
        indexCategory.clear();
    
        const objects = new Array(N);
    
        for (let i = 0; i < N; i++) {
            const d = json[i];
            const rgb = hexToRgb(d.color);
        
            colDates[i] = new Date(d.date).getTime();
            colTimes[i] = parseInt(d.time) || 0;
            colR[i] = rgb[0];
            colG[i] = rgb[1];
            colB[i] = rgb[2];
            colX[i] = xNorm[i];
            colY[i] = yNorm[i];
        
            let cat = 0;
            if (type === "OUTFITS") {
                const cats = String(d.category_list).split("|").map(Number);
                cat = cats[0] || 0;
                cats.forEach(c => {
                    if (!indexCategory.has(c)) indexCategory.set(c, createBitset(N));
                    setBit(indexCategory.get(c), i);
                });
            } else {
                cat = parseInt(String(d.category_list).split('|')[0]) || 0;
                if (!indexCategory.has(cat)) indexCategory.set(cat, createBitset(N));
                setBit(indexCategory.get(cat), i);
            }
        
            const city = String(d.city).toLowerCase();
            if (!indexCity.has(city)) indexCity.set(city, createBitset(N));
            setBit(indexCity.get(city), i);
        
            objects[i] = { ...d, rgb, category: cat - 1 };
        }
    
        rawObjects = objects;
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
    class="flex-grow min-h-0 w-full bg-neutral-800 relative"
    style="height: 100%;"
    onclick={(e) => {
        console.log("[DOM Layer] Click detected at CSS:", e.clientX, e.clientY);
        handleCanvasClick();
    }}
    onmousemove={(e) => { 
        mouseX = e.clientX; 
        mouseY = e.clientY; 
        if (e.clientX % 50 === 0) console.log("[DOM Layer] Mouse tracking active:", mouseX, mouseY);
    }}
>
    {#if viewData}
        <EmbeddingView
            data={viewData}
            width={containerWidth}
            height={containerHeight}
            config={viewOptions}
            {categoryColors}
            onHover={(v) => {
                console.log("[WebGL Layer] Engine emitted hover event:", v);
                tooltip = v;
            }}
            onSelection={(v) => {
                console.log("[WebGL Layer] Engine emitted selection event:", v);
            }}
            querySelection={async (x, y, unitDistance) => {
                let nearest = null;
                let minDist = Infinity;
                for (let i = 0; i < viewData.x.length; i++) {
                    const dx = viewData.x[i] - x;
                    const dy = viewData.y[i] - y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < minDist) {
                        minDist = dist;
                        nearest = i;
                    }
                }
                
                if (nearest === null || minDist > unitDistance * 20) {
                    tooltip = null;
                    return null;
                }
                
                const originalIdx = viewData.originalIndices[nearest];
                const hitNode = rawObjects[originalIdx];
                
                // 1. Intercept payload for custom HTML overlay
                tooltip = hitNode; 
                
                // 2. Transmit null to engine to kill native JSON tooltip render cycle
                return null; 
            }}
        />
    {:else}
        <div class="flex items-center justify-center h-full text-green-400">
            Loading data...
        </div>
    {/if}
    {#if tooltip && !selectedPoint}
        <div
            class="fixed pointer-events-none p-3 bg-neutral-900 border border-neutral-700 rounded shadow-2xl text-white w-48 z-40 flex flex-col gap-2"
            style="left: {mouseX + 15}px; top: {mouseY + 15}px;"
        >
            <img 
                src={`http://localhost:5000/image/${tooltip.crop_path}`} 
                alt="Thumbnail" 
                class="w-full h-auto rounded bg-black"
            />
            <div class="text-[0.65rem] uppercase tracking-widest text-neutral-400 font-mono space-y-1">
                <p><span class="text-neutral-500">City:</span> {tooltip.city}</p>
                <p><span class="text-neutral-500">Date:</span> {tooltip.date}</p>
                <p><span class="text-neutral-500">Time:</span> {tooltip.time}h</p>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-neutral-500">Color:</span> 
                    <div class="w-4 h-4 rounded border border-neutral-500" style="background-color: {tooltip.color};"></div>
                </div>
            </div>
        </div>
    {/if}

    {#if selectedPoint}
        <div class="absolute top-4 right-4 p-4 bg-neutral-900 border border-neutral-700 rounded shadow-2xl text-white max-w-xs z-50 flex flex-col gap-2 font-mono">
            <h3 class="font-bold text-xs uppercase tracking-[0.2em] text-[#2fff3d] mb-2">Node Metadata</h3>
            <div class="text-[0.7rem] uppercase tracking-widest text-neutral-400 space-y-1">
                <p><span class="text-neutral-500">ID:</span> {selectedPoint.id}</p>
                <p><span class="text-neutral-500">City:</span> {selectedPoint.city}</p>
                <p><span class="text-neutral-500">Date:</span> {selectedPoint.date}</p>
                <p><span class="text-neutral-500">Time:</span> {selectedPoint.time}h</p>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-neutral-500">Color:</span> 
                    <div class="w-4 h-4 rounded border border-neutral-500" style="background-color: {selectedPoint.color};"></div>
                </div>
            </div>
            <img 
                src={`http://localhost:5000/image/${selectedPoint.crop_path}`} 
                alt="Cropped entity" 
                class="w-full h-auto mt-2 rounded border border-neutral-700"
            />
            <button class="mt-3 text-neutral-900 bg-[#2fff3d] hover:bg-[#25cc30] py-2 w-full text-[0.65rem] font-bold uppercase tracking-widest transition-colors cursor-pointer" onclick={() => (selectedPoint = null)}>Close</button>
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
