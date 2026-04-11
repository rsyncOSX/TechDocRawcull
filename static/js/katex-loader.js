// Load KaTeX for math rendering - optimized for all browsers including Safari
(function() {
    var katexLoaded = false;
    var autoRenderLoaded = false;
    
    function attemptRender() {
        if (katexLoaded && autoRenderLoaded && window.renderMathInElement) {
            try {
                renderMathInElement(document.body, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false}
                    ],
                    strict: false
                });
                console.log('✓ KaTeX rendering complete');
            } catch(e) {
                console.warn('KaTeX rendering error:', e.message);
            }
        }
    }
    
    // Load KaTeX CSS
    var katexCSS = document.createElement('link');
    katexCSS.rel = 'stylesheet';
    katexCSS.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.min.css';
    document.head.appendChild(katexCSS);

    // Load KaTeX JS
    var katexJS = document.createElement('script');
    katexJS.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.min.js';
    katexJS.onload = function() {
        katexLoaded = true;
        console.log('✓ KaTeX loaded');
        attemptRender();
    };
    katexJS.onerror = function() {
        console.error('✗ Failed to load KaTeX');
    };
    document.head.appendChild(katexJS);

    // Load auto-render extension
    var autoRenderJS = document.createElement('script');
    autoRenderJS.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/contrib/auto-render.min.js';
    autoRenderJS.onload = function() {
        autoRenderLoaded = true;
        console.log('✓ KaTeX auto-render loaded');
        attemptRender();
    };
    autoRenderJS.onerror = function() {
        console.error('✗ Failed to load KaTeX auto-render');
    };
    document.head.appendChild(autoRenderJS);
    
    // Fallback: try rendering after 2 seconds
    setTimeout(attemptRender, 2000);
})();
