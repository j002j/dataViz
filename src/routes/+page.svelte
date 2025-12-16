<div class="main-container">
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
</style>
