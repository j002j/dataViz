<script>
    import CosmosCanvas from "$lib/visualization/CosmosCanvas.svelte";
    // import EmbeddingView from "../../lib/visualization/EmbeddingView.svelte";
    import EmbeddingView from "$lib/visualization/EmbeddingView.svelte";
</script>

<!-- <CosmosCanvas /> -->
<!-- min-h-0 for allowing the child to shring belog ist content size  -->
<div class="flex-grow flex flex-col min-h-0">
    <EmbeddingView />
</div>
