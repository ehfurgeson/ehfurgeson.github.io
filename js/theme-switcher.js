// theme-switcher.js
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    
    // Function to set theme
    function setTheme(theme) {
      if (theme === "dark") {
        document.documentElement.classList.add("dark-theme");
        localStorage.setItem("theme", "dark");
      } else {
        document.documentElement.classList.remove("dark-theme");
        localStorage.setItem("theme", "light");
      }
    }
    
    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem("theme");
    
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Check system preference
      const prefersDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setTheme(prefersDarkMode ? "dark" : "light");
    }
    
    // Toggle theme when button is clicked
    themeToggle.addEventListener("click", () => {
      const isDarkTheme = document.documentElement.classList.contains("dark-theme");
      setTheme(isDarkTheme ? "light" : "dark");
    });
    
    // Listen for system preference changes
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("theme")) {
        setTheme(e.matches ? "dark" : "light");
      }
    });
  });