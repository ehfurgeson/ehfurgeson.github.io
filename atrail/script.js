function adjustLayout() {
    var calc = document.getElementById("calc");
    var map = document.getElementById("map");

    if (/Android|webOS|iPhone|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(navigator.userAgent)) {
    // Take the user to a different screen here.
        calc.style.width = "100vw";
        calc.style.height = "70vh";
        map.style.width = "100vw";
        map.style.height = "20vh";
        document.getElementById("total").style.flexDirection = "column";
    }
    else if (window.innerWidth > window.innerHeight){
        calc.style.width = "50vw";
        calc.style.height = "90vh";
        map.style.width = "50vw";
        map.style.height = "90vh";
        document.getElementById("total").style.flexDirection = "row";
    }
    else if (window.innerWidth < window.innerHeight){
        calc.style.width = "100vw";
        calc.style.height = "45vh";
        map.style.width = "100vw";
        map.style.height = "45vh";
        document.getElementById("total").style.flexDirection = "column";
    }
}

window.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);