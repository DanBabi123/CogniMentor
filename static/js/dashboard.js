/* =========================================
   CogniMentor Dashboard Interactions
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initNotifications();
    initGlassEffects();
});

/* --- Sidebar Handling --- */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.menu-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (!sidebar || !toggleBtn) return;

    function toggleMenu() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    }

    toggleBtn.addEventListener('click', toggleMenu);

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // Active Link Highlighting (if not handled by backend)
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/* --- Notifications --- */
function initNotifications() {
    const notifBtn = document.querySelector('.header-actions .material-icons');
    if (notifBtn) {
        notifBtn.parentElement.addEventListener('click', () => {
            // Future: Show notification dropdown
            alert('Notifications coming soon!');
        });
    }
}

/* --- Glassmorphism Polish --- */
function initGlassEffects() {
    // Add tilt effect to cards ? (Optional Polish)
    // const cards = document.querySelectorAll('.card');
    // ...
}
