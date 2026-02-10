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
        //background-image: url("/square.gif");
        background-repeat: no-repeat;
        background-size: cover;
    }

    /* Helper for the box labels if you want them styled specifically */
    .box-label {
        font-family: monospace;
    }
</style>
