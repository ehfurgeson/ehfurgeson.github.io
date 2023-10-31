function adjustLayout() {
    var calc = document.getElementById("calc");
    var map = document.getElementById("map");

    if (window.innerWidth > window.innerHeight){
        calc.style.width = "50vw";
        calc.style.height = "90vh";
        map.style.width = "50vw";
        map.style.height = "90vh";
        document.getElementById("total").style.flexDirection = "row";
    }
    else if (window.innerWidth < window.innerHeight){
        calc.style.width = "100vw";
        calc.style.height = "65vh";
        map.style.width = "100vw";
        map.style.height = "30vh";
        document.getElementById("total").style.flexDirection = "column";
    }
}

window.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);