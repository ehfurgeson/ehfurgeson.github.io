window.smoothScroll = function(target) {
    var scrollContainer = target;
    do {
        scrollContainer = scrollContainer.parentNode;
        if (!scrollContainer) return;
    } while (scrollContainer.scrollTop === 0 && scrollContainer !== document.documentElement);

    var targetY = 0;
    do {
        if (target == scrollContainer) break;
        targetY += target.offsetTop;
    } while (target = target.offsetParent);

    var scroll = function(c, a, b, i) {
        i++;
        if (i > 30) return;
        c.scrollTop = a + (b - a) / 30 * i;
        setTimeout(function() {
            scroll(c, a, b, i);
        }, 20);
    }

    scroll(scrollContainer, scrollContainer.scrollTop, targetY, 0);
}
// created with help from nico on stack overflow
// source https://stackoverflow.com/questions/18071046/smooth-scroll-to-specific-div-on-click
// and with tweaking by myself because the original code had an issue where if you were scrolled all the way up it wouldn't properly scroll to the div you wanted, so I tweaked it slightly to fix that

/* When the user scrolls down, hide the navbar. When the user scrolls up, show the navbar */
var prevScrollpos = window.scrollY;
window.onscroll = function() {
  var currentScrollPos = window.scrollY;
  if (prevScrollpos > currentScrollPos) {
    document.getElementById("fade").style.height = "15vh";
  } else {
    document.getElementById("fade").style.height = "5vh";
  }
  prevScrollpos = currentScrollPos;
}