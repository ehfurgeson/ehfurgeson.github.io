function adjustLayout() {
    var calc = document.getElementById("calc");
    var map = document.getElementById("map");
    var body = document.getElementById('body');
    var total = document.getElementById('total');

    // Check if the device supports touch events
    if ('ontouchstart' in window) {
        // Load the photoswipe script
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'photoswipe/code.photoswipe-3.0.4.min.js';
        document.body.appendChild(script);
    
        // Adjust the style of some elements
        if (window.innerWidth < window.innerHeight){
            calc.style.width = '100vw';
            calc.style.height = '100vh';
            map.style.width = '100vw';
            map.style.height = '50vh';
            total.style.flexDirection = 'column';
            total.style.overflow = 'auto';
            body.style.overflow = 'auto';
            body.style.height = 'auto';
        }
        else if (window.innerWidth > window.innerHeight){
            calc.style.width = "50vw";
            calc.style.height = "90vh";
            map.style.width = "50vw";
            map.style.height = "90vh";
            body.style.overflow = 'hidden';
            body.style.height = '100vh';
            total.style.flexDirection = "row";
        } 
    }
    else if (window.innerWidth > window.innerHeight){
        calc.style.width = "50vw";
        calc.style.height = "90vh";
        map.style.width = "50vw";
        map.style.height = "90vh";
        body.style.overflow = 'hidden';
        body.style.height = '100vh';
        total.style.flexDirection = "row"; 
    }
    else if (window.innerWidth < window.innerHeight){
        calc.style.width = "100vw";
        calc.style.height = "45vh";
        map.style.width = "100vw";
        map.style.height = "45vh";
        body.style.overflow = 'hidden';
        body.style.height = '100vh';
        total.style.flexDirection = "column";
    }
}

window.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);