// JavaScript for the personal site

// Category filter functionality for recipes page
function setupRecipeFilters() {
    if (!document.getElementById('category-filters')) return;
    
    const filters = document.querySelectorAll('#category-filters .category-filter');
    const recipeCards = document.querySelectorAll('#recipe-grid .recipe-card');
    const noResults = document.getElementById('no-results');
    
    filters.forEach(filter => {
      filter.addEventListener('click', function() {
        // Update active filter
        filters.forEach(f => f.classList.remove('active'));
        this.classList.add('active');
        
        // Get selected category
        const category = this.getAttribute('data-category');
        
        // Show/hide recipes based on category
        let visibleCount = 0;
        
        recipeCards.forEach(card => {
          const cardCategories = card.getAttribute('data-categories') || '';
          
          if (category === 'all' || cardCategories.includes(category)) {
            card.style.display = 'block';
            visibleCount++;
          } else {
            card.style.display = 'none';
          }
        });
        
        // Show/hide no results message
        if (visibleCount === 0) {
          noResults.classList.remove('hidden');
        } else {
          noResults.classList.add('hidden');
        }
      });
    });
  }
  
  // Back to top button functionality
  function setupBackToTopButton() {
    const backToTopButton = document.querySelector('.back-to-top');
    if (!backToTopButton) return;
    
    // Initially hide the button
    backToTopButton.style.display = 'none';
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
      if (window.pageYOffset > 300) {
        backToTopButton.style.display = 'flex';
      } else {
        backToTopButton.style.display = 'none';
      }
    });
    
    // Scroll to top when clicked
    backToTopButton.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
  
  // Initialize all functionality when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    setupRecipeFilters();
    setupBackToTopButton();
    
    // Add any additional initialization here
  });