

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initNotifications();
    initGlassEffects();
});


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

    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}


function initNotifications() {
    // Alert removed as notifications are natively routed via the HTML anchor tag
}


function initGlassEffects() {
}
