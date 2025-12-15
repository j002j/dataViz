<!-- <h1 class="text-3xl font-bold underline text-white">Hello world!</h1>
<p>TODO...</p>
<a href="/globe">to the globe</a> -->

<div class="main-container">
    <div id="squares-background" class="text-green-500 font-bold">
        <h1>Starterkist</h1>
    </div>
    <div
        id="menue-landingpage"
        class="text-bold flex flex-col items-center justify-center"
    >
        <!-- <h1>globe</h1>-->
        <a href="/globe" class="btn">ENTER</a>
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
        display: flex;
        felx-direction: column;
        height: 100vh;
    }

    #menue-landingpage {
        background-color: black;
        height: 100vh;
    }

    .btn {
        background-image: url("/button-background.jpg");
        background-repeat: no-repeat;
        background-size: cover;
        //font-color: rgb(47, 255, 61);
        @apply font-bold py-4 px-8 text-2xl text-green-500;
        text-decoration: none;
        outline: solid;
        outline-color: rgb(47, 255, 61);
    }
</style>
