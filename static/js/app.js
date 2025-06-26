// Additional JavaScript functionality for the CV Parser app

document.addEventListener('DOMContentLoaded', function() {
    console.log('CV Parser App loaded');
    
    // Add any additional interactive features here
    
    // Example: Add tooltips or additional animations
    const skillTags = document.querySelectorAll('.skill-tag');
    skillTags.forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        tag.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});