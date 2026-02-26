<script>
    import bg from "$lib/assets/ppl_square.gif";
</script>

<div class="page-wrapper">
    <div id="hero">
        <div class="gif-bg" style="background-image: url({bg});"></div>
        <div class="hero-content">
            <div id="title-box" class="label-box">
                <span class="box-label">title</span>
                <span class="box">STARTERKIT</span>
            </div>
            <div id="subtitle-box" class="label-box">
                <span class="box-label">text</span>
                <span class="box">FITS FROM GERMANY</span>
            </div>
        </div>
    </div>
    <div id="menu">
        <div class="menu-inner">
            <div class="label-box">
                <span class="box-label">button</span>
                <a href="/globe" class="btn btn-full">EXPLORE</a>
            </div>
            <div class="label-box">
                <span class="box-label">button</span>
                <a href="/about" class="btn btn-full">ABOUT</a>
            </div>
            <div class="label-box">
                <span class="box-label">button</span>
                <a href="/credits" class="btn btn-full">CREDITS</a>
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
    #hero {
        position: relative;
        width: 100%;
        height: 120vh;
        overflow: hidden;
    }
    .gif-bg {
        position: absolute;
        inset: 0;
        background-repeat: repeat;
        background-size: cover;
        background-position: top center;
    }
    .hero-content {
        position: absolute;
        bottom: 40vh;
        left: clamp(1rem, 5vw, 3rem);
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: flex-start;
    }
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
    .label-box {
        position: relative;
        display: inline-block;
        width: 100%;
    }
    .text-body {
        font-size: clamp(0.95rem, 3.5vw, 1.4rem) !important;
    }
    .btn-full {
        display: block;
        width: 100%;
        text-align: center;
    }
</style>
