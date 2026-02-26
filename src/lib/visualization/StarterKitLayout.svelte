<script>
    import { slide } from "svelte/transition";
    import EmbeddingView from "./EmbeddingView.svelte";

    // Panel open states
    let filterOpen = $state(false);
    let statsOpen = $state(false);
    let activeTab = $state("ITEMS"); // ITEMS or KITS
    let yearValue = $state(2020);
    const CATEGORIES = [
        { id: 1, name: "Short Sleeve Top" },
        { id: 2, name: "Long Sleeve Top" },
        { id: 3, name: "Short Sleeve Outerwear" },
        { id: 4, name: "Long Sleeve Outerwear" },
        { id: 5, name: "Vest" },
        { id: 6, name: "Sling" },
        { id: 7, name: "Shorts" },
        { id: 8, name: "Trousers" },
        { id: 9, name: "Skirt" },
        { id: 10, name: "Short Sleeve Dress" },
        { id: 11, name: "Long Sleeve Dress" },
        { id: 12, name: "Vest Dress" },
        { id: 13, name: "Sling Dress" },
    ];

    let activeCategories = $state(new Set()); // empty = show all
    $effect(() => {
        console.log(
            "StarterKitLayout: layout activeCategories size:",
            activeCategories.size,
        );
    });
</script>

<!-- Root: full viewport, dark bg, no overflow -->
<div class="starterkit-root">
    <!-- Top bar -->
    <div class="topbar">
        <a
            href="/"
            class="test-[0.75rem] font-bold tracking-widest text-neutral-400"
            >STARTERKIT</a
        >
        <div class="tab-group">
            <a href="/" class="tab-btn">HOME</a>
            <button
                class="tab-btn"
                class:active={activeTab === "ITEMS"}
                onclick={() => {
                    activeTab = "ITEMS";
                    activeCategories = new Set();
                }}>ITEMS</button
            >
            <button
                class="tab-btn"
                class:active={activeTab === "OUTFITS"}
                onclick={() => {
                    activeTab = "OUTFITS";
                    activeCategories = new Set();
                }}>OUTFITS</button
            >
        </div>
    </div>

    <!-- Main area: filter | canvas | (future right panel) -->
    <div class="main-area">
        <!-- Left filter panel -->
        {#if filterOpen}
            <div
                class="panel panel-left outline-1 md:outline-neutral-600/50"
                transition:slide={{ axis: "x", duration: 200 }}
            >
                <!-- empty for now -->
                <div class="p-5 font-mono">
                    <h2
                        class="text-[0.65rem] uppercase tracking-[0.2em] text-[#2fff3d] mb-8 pb-2"
                    >
                        Filter Parameters
                    </h2>

                    <div class="space-y-8">
                        <div class="flex flex-col gap-3">
                            <label
                                class="text-[0.6rem] uppercase text-neutral-400 tracking-widest"
                                >Item Category</label
                            >
                            {#each CATEGORIES as cat}
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                        checked={activeCategories.has(cat.id)}
                                        onchange={() => {
                                            console.log(
                                                "checkbox clicked, cat.id:",
                                                cat.id,
                                            );
                                            const next = new Set(
                                                activeCategories,
                                            );
                                            if (next.has(cat.id))
                                                next.delete(cat.id);
                                            else next.add(cat.id);
                                            activeCategories = next;
                                            console.log(
                                                "new size:",
                                                activeCategories.size,
                                            );
                                        }}
                                    />
                                    <span>{cat.name}</span>
                                </div>
                            {/each}
                            <!-- <div class="flex flex-col gap-1 text-neutral-400">
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>short sleeve top</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>long sleeve top</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>short sleeve outerwear</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>long sleeve outerwear</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>vest</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>sling</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>shorts</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>trousers</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>skirt</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>short sleeve dress</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>long sleeve dress</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>vest dress</span>
                                </div>
                                <div
                                    class="flex items-center gap-2 text-[0.7rem]"
                                >
                                    <input
                                        type="checkbox"
                                        class="accent-[#2fff3d]"
                                    /> <span>sling dress</span>
                                </div>
                            </div> -->
                        </div>

                        <div class="flex flex-col gap-3">
                            <label
                                class="text-[0.6rem] uppercase text-neutral-500 tracking-widest"
                                >Capture Year: <span class="text-[#2fff3d]"
                                    >{yearValue}</span
                                >
                            </label>
                            <input
                                type="range"
                                min="2016"
                                max="2026"
                                bind:value={yearValue}
                                class="w-full accent-[#2fff3d] bg-neutral-500 appearance-none h-1 rounded"
                            />
                            <div
                                class="flex justify-between text-[0.6rem] text-neutral-500"
                            >
                                <span>2016</span>
                                <span>2026</span>
                            </div>
                        </div>

                        <div class="flex flex-col gap-3">
                            <label
                                class="text-[0.6rem] uppercase text-neutral-500 tracking-widest"
                                >Federal State</label
                            >
                            <select
                                class="border border-neutral-700 text-neutral-300 text-[0.7rem] p-1 outline-none focus:border-[#2fff3d]"
                            >
                                <option>ALL STATES</option>
                                <option>NORDRHEIN-WESTFALEN</option>
                                <option>BERLIN</option>
                                <option>BAYERN</option>
                            </select>
                        </div>

                        <div class="flex flex-col gap-3">
                            <label
                                class="text-[0.6rem] uppercase text-neutral-500 tracking-widest"
                                >Colour Palette</label
                            >
                            <div class="flex gap-2">
                                <button
                                    class="w-4 h-4 rounded-full bg-white border border-neutral-600"
                                ></button>
                                <button
                                    class="w-4 h-4 rounded-full bg-black border border-[#2fff3d]"
                                ></button>
                                <button
                                    class="w-4 h-4 rounded-full bg-blue-600 border border-neutral-600"
                                ></button>
                                <button
                                    class="w-4 h-4 rounded-full bg-red-600 border border-neutral-600"
                                ></button>
                                <button
                                    class="w-4 h-4 rounded-full bg-yellow-500 border border-neutral-600"
                                ></button>
                                <button
                                    class="w-4 h-4 rounded-full bg-green-500 border border-neutral-600"
                                ></button>
                            </div>
                        </div>
                    </div>

                    <button
                        class="mt-12 w-full text-[0.6rem] uppercase tracking-[0.2em] py-2 border border-neutral-700 text-neutral-500 hover:text-[#2fff3d] hover:border-[#2fff3d] transition-all"
                        onclick={() => {
                            activeCategories = new Set();
                            yearValue = 2020;
                        }}
                    >
                        reset filters
                    </button>
                </div>
            </div>
        {/if}

        <!-- Filter tab trigger (left edge) -->
        <button
            class="edge-tab edge-tab-left"
            class:open={filterOpen}
            onclick={() => (filterOpen = !filterOpen)}
            style="left: {filterOpen ? '260px' : '0px'};"
        >
            <span>filter</span>
            <span class="arrow">{filterOpen ? "▲" : "▼"}</span>
            <!-- "◀" : "▶" -->
        </button>

        <!-- Pointcloud canvas -->
        <div class="canvas-area">
            <EmbeddingView
                type={activeTab}
                selectedCategories={activeCategories}
            />
        </div>

        <!-- Stats tab trigger (right edge of canvas, actually bottom) -->
    </div>

    <!-- Stats bottom panel -->
    {#if statsOpen}
        <div
            class="panel panel-bottom"
            transition:slide={{ axis: "y", duration: 250 }}
        >
            <!-- empty for now -->
        </div>
    {/if}

    <!-- Stats tab trigger (bottom edge) -->
    <button
        class="edge-tab edge-tab-bottom"
        class:open={statsOpen}
        onclick={() => (statsOpen = !statsOpen)}
    >
        <span>stats</span>
        <span class="arrow">{statsOpen ? "▼" : "▲"}</span>
    </button>
</div>

<style>
    .starterkit-root {
        position: fixed;
        inset: 0;
        background: #1a1a1a;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: monospace;
        color: #ccc;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 12px;
        background: #222;
        border-bottom: 1px solid #333;
        flex-shrink: 0;
        z-index: 10;
    }

    .tab-group {
        display: flex;
        gap: 2px;
    }

    .tab-btn {
        padding: 4px 14px;
        font-size: 0.7rem;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 0.08em;
        background: #333;
        color: #999;
        border: 1px solid #444;
        cursor: pointer;
        transition:
            background 0.15s,
            color 0.15s;
    }

    .tab-btn:hover {
        background: #444;
        color: #ddd;
    }

    .tab-btn.active {
        background: #555;
        color: #fff;
        border-color: #666;
    }

    /* filter + canvas */
    .main-area {
        flex: 1;
        display: flex;
        min-height: 0;
        position: relative;
        overflow: hidden;
    }

    .panel-left {
        width: 260px;
        flex-shrink: 0;
        background: #252525;
        border-right: 1px solid #333;
        overflow-y: auto;
        z-index: 5;
    }

    /* stats panel  */
    .panel-bottom {
        height: 200px;
        flex-shrink: 0;
        background: #252525;
        border-top: 1px solid #333;
        overflow-y: auto;
        z-index: 5;
    }

    .canvas-area {
        flex: 1;
        min-width: 0;
        min-height: 0;
        display: flex;
        flex-direction: column;
    }

    /* ── Edge tab triggers ── */
    .edge-tab {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.65rem;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: lowercase;
        background: #2a2a2a;
        color: #888;
        border: 1px solid #3a3a3a;
        cursor: pointer;
        transition:
            background 0.15s,
            color 0.15s,
            left 0.2s ease-in-out;
        z-index: 20;
    }

    .edge-tab:hover,
    .edge-tab.open {
        background: #333;
        color: #ccc;
    }

    /* Left edge tab — vertical, anchored left side */
    .edge-tab-left {
        left: 0;
        top: 50%;
        transform: rotate(-90deg) translateX(-50%);
        transform-origin: top left;
        padding: 4px 10px;
        border-radius: 0 0 4px 4px;
        writing-mode: horizontal-tb; /* keep text horizontal after rotate */
    }

    .edge-tab-bottom {
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        padding: 4px 14px;
        border-radius: 4px 4px 0 0;
        border-bottom: none;
    }

    .arrow {
        font-size: 0.6rem;
    }
</style>
