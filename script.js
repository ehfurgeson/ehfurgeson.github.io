// Create animated forest particles
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const leafCount = 25;
    const mistCount = 15;
    const dewdropCount = 30;

    // Create leaves
    for (let i = 0; i < leafCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle leaf';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
        particlesContainer.appendChild(particle);
    }

    // Create mist particles
    for (let i = 0; i < mistCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle mist';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 6 + 6) + 's';
        particlesContainer.appendChild(particle);
    }

    // Create dewdrops
    for (let i = 0; i < dewdropCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle dewdrop';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 4 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Intersection Observer for fade-in animations
function setupScrollAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    fadeElements.forEach(element => {
        observer.observe(element);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    createParticles();
    setupScrollAnimations();
});