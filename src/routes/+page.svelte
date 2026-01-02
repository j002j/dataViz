<!-- <div class="main-container">
    <div id="squares-background">
        <div
            class="text-bold flex flex-col items-center justify-center pt-12 pl-12"
            id="title"
        >
            <div class="relative inline-block" id="title">
                <span class="box-label">title</span>
                <span class="box">STARTERKITS</span>
            </div>
        </div>

        <div
            class="text-bold flex flex-col items-center justify-center pt-12 pl-12"
            id="title"
        >
            <div class="relative inline-block" id="title">
                <span class="box-label">text</span>
                <span class="box">STARTERKITS from Around the WORLD</span>
            </div>
        </div>
    </div>

    <div
        id="menue-landingpage"
        class="text-bold flex flex-col items-center justify-center"
    >
        <div class="relative inline-block">
            <span class="box-label">button</span>
            <a href="/globe" class="btn">ENTER</a>
        </div>
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";

    :global(html) {
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }

    #squares-background {
        background-image: url("/square.gif");
        background-repeat: no-repeat;
        background-size: cover;
        display: flex;
        felx-direction: column;
        height: 100vh;
    }

    #menue-landingpage {
        background-color: black;
        height: 100vh;
    }
    #title {
        float: right;
    }
</style> -->

<div class="flex flex-col w-full">
    <div
        id="squares-background"
        class="flex flex-col items-center justify-center h-screen w-full relative"
    >
        <div class="relative inline-block mb-8">
            <span class="box-label text-xs uppercase absolute -top-4 left-0"
                >title</span
            >
            <span class="box text-4xl font-black bg-white text-black p-2"
                >STARTERKITS</span
            >
        </div>

        <div class="relative inline-block">
            <span class="box-label text-xs uppercase absolute -top-4 left-0"
                >text</span
            >
            <span
                class="box text-xl font-bold bg-white text-black p-2 uppercase"
                >Starterkits from Around the WORLD</span
            >
        </div>
    </div>

    <div
        id="menue-landingpage"
        class="flex items-center justify-center h-screen w-full bg-black"
    >
        <div class="relative inline-block">
            <span
                class="box-label text-xs uppercase absolute -top-4 left-0 text-white"
                >button</span
            >
            <a
                href="/globe"
                class="btn text-white border border-white px-8 py-4 hover:bg-white hover:text-black transition-all font-bold"
            >
                ENTER
            </a>
        </div>
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";

    #squares-background {
        background-image: url("/square.gif");
        background-repeat: no-repeat;
        background-size: cover;
    }

    /* Helper for the box labels if you want them styled specifically */
    .box-label {
        font-family: monospace;
    }
</style>
