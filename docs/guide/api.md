<swagger-ui src="/assets/openapi.json" />

<script>
    function setIframesScheme(scheme) {
        document.querySelectorAll(".swagger-ui-iframe").forEach(iframe => {
            iframe.contentWindow.document.body.setAttribute("data-md-color-scheme", scheme);
        });
    }

    const observer = new MutationObserver(() => {
        const scheme = document.body.getAttribute("data-md-color-scheme");
        setIframesScheme(scheme);
    });

    observer.observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });

    document.querySelectorAll(".swagger-ui-iframe").forEach(iframe => {
        iframe.addEventListener("load", () => {
            const scheme = document.body.getAttribute("data-md-color-scheme");
            iframe.contentWindow.document.body.setAttribute("data-md-color-scheme", scheme);
        });
    });
</script>