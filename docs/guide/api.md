<head>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.1/swagger-ui.css" />
    <!-- <link rel="stylesheet" href="/assets/swagger.css" /> -->
</head>

Dark Mode doesn't work because swagger-ui doesn't support it yet.
(If the page doesn't load, try refreshing it.)

<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5.9.1/swagger-ui-bundle.js" crossorigin></script>
<script>
    window.onload = () => {
        window.ui = SwaggerUIBundle({
            url: '/assets/openapi.json',
            dom_id: '#swagger-ui',
            supportedSubmitMethods: [],
        });

        setTimeout(() => {
            document.body.setAttribute('data-md-color-scheme', 'default');
        }, 1000);
    };
</script>