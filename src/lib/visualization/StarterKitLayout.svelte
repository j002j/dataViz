<script>
    import { slide } from "svelte/transition";
    import EmbeddingView from "./EmbeddingView.svelte";

    // Panel open states
    let filterOpen = $state(false);
    let statsOpen = $state(false);
    let activeTab = $state("ITEMS"); // ITEMS or KITS
</script>

<!-- Root: full viewport, dark bg, no overflow -->
<div class="starterkit-root">
    <!-- Top bar -->
    <div class="topbar">
        <span class="brand">STARTERKIT</span>
        <div class="tab-group">
            <button
                class="tab-btn"
                class:active={activeTab === "ITEMS"}
                onclick={() => (activeTab = "ITEMS")}>ITEMS</button
            >
            <button
                class="tab-btn"
                class:active={activeTab === "KITS"}
                onclick={() => (activeTab = "KITS")}>KITS</button
            >
        </div>
    </div>

    <!-- Main area: filter | canvas | (future right panel) -->
    <div class="main-area">
        <!-- Left filter panel -->
        {#if filterOpen}
            <div
                class="panel panel-left"
                transition:slide={{ axis: "x", duration: 200 }}
            >
                <!-- empty for now -->
            </div>
        {/if}

        <!-- Filter tab trigger (left edge) -->
        <button
            class="edge-tab edge-tab-left"
            class:open={filterOpen}
            onclick={() => (filterOpen = !filterOpen)}
        >
            <span>filter</span>
            <span class="arrow">{filterOpen ? "◀" : "▶"}</span>
        </button>

        <!-- Pointcloud canvas -->
        <div class="canvas-area">
            <EmbeddingView />
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

    /* ── Top bar ── */
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

    .brand {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #aaa;
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

    /* ── Main area (filter + canvas) ── */
    .main-area {
        flex: 1;
        display: flex;
        min-height: 0;
        position: relative;
        overflow: hidden;
    }

    /* ── Left filter panel ── */
    .panel-left {
        width: 260px;
        flex-shrink: 0;
        background: #252525;
        border-right: 1px solid #333;
        overflow-y: auto;
        z-index: 5;
    }

    /* ── Bottom stats panel ── */
    .panel-bottom {
        height: 200px;
        flex-shrink: 0;
        background: #252525;
        border-top: 1px solid #333;
        overflow-y: auto;
        z-index: 5;
    }

    /* ── Canvas ── */
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
            color 0.15s;
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
        transform: translateY(-50%) rotate(-90deg) translateX(-50%);
        transform-origin: left center;
        padding: 4px 10px;
        border-radius: 0 0 4px 4px;
        writing-mode: horizontal-tb; /* keep text horizontal after rotate */
    }

    /* Bottom edge tab */
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
