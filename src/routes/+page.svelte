<script>
    import bg from "$lib/assets/square.gif";
</script>

<div class="page-wrapper">
    <!-- GIF hero: taller than the viewport so the gif bleeds when scrolling down -->
    <div id="hero">
        <div class="gif-bg" style="background-image: url({bg});"></div>
        <div class="hero-content">
            <div class="label-box">
                <span class="box-label">title</span>
                <span class="box">STARTERKIT</span>
            </div>

            <div class="label-box">
                <span class="box-label">text</span>
                <span class="box">fits from around the world</span>
            </div>
        </div>
    </div>

    <!-- Menu: full viewport, three buttons centred -->
    <div id="menu">
        <div class="menu-inner">
            <div class="label-box">
                <span class="box-label">button</span>
                <a href="/globe" class="btn btn-full">EXPLORE 1</a>
            </div>

            <div class="label-box">
                <span class="box-label">button</span>
                <a href="/about" class="btn btn-full">ABOUT</a>
            </div>
        </div>
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";

    .page-wrapper {
        display: flex;
        flex-direction: column;
        width: 100%;
        background: #000;
    }

    /* ── Hero ── */
    #hero {
        position: relative;
        width: 100%;
        /* 120vh = full screen + 20vh bleed so gif is still visible when user starts scrolling */
        height: 120vh;
        overflow: hidden;
    }

    .gif-bg {
        position: absolute;
        inset: 0;
        background-repeat: repeat; /* tile horizontally so it fills any screen width */
        background-size: cover;
        background-position: top center;
    }

    /* Title + text anchored to bottom-left of the hero */
    .hero-content {
        position: absolute;
        bottom: 10vh;
        left: clamp(1rem, 5vw, 3rem);
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: flex-start;
    }

    /* ── Menu ── */
    #menu {
        width: 100%;
        min-height: 100vh;
        background: #111;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .menu-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        width: min(380px, 88vw);
    }

    /* ── label-box wrapper ── */
    .label-box {
        position: relative;
        display: inline-block;
        width: 100%;
    }

    /* smaller body text inside .box */
    .text-body {
        font-size: clamp(0.95rem, 3.5vw, 1.4rem) !important;
    }

    /* buttons stretch to fill the column */
    .btn-full {
        display: block;
        width: 100%;
        text-align: center;
    }
</style>
