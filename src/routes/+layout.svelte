<script>
    import "../app.css";
    let { children } = $props();
</script>

{@render children()}

<!-- 
<div class="flex flex-col min-h-screen bg-gray-100">
    <main class="flex-grow flex flex-col min-h-0">
        {@render children()}
    </main>
</div> -->
