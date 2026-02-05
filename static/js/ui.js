/* ==========================================================================
   CogniMentor Global UI Interaction Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initAnimations();
    initToasts();
});

/* --- Sidebar Toggle for Mobile --- */
function initSidebar() {
    const toggleBtn = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        });
        
        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }
}

/* --- Smooth Entry Animations --- */
function initAnimations() {
    const elements = document.querySelectorAll('.animate-fade-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}

/* --- Toast Notification Handler --- */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="material-icons">${type === 'success' ? 'check_circle' : 'info'}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    
    // Animation
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function initToasts() {
    // Check for flask flash messages injected in DOM
    const flashMessages = document.querySelectorAll('.flash-data');
    flashMessages.forEach(msg => {
        showToast(msg.dataset.message, msg.dataset.category);
    });
}
