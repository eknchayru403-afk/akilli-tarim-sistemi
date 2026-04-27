/**
 * ATYS — Main JavaScript
 * Micro-animations and UI interactions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Fade-in animation for cards
    const cards = document.querySelectorAll('.card, .stat-card, .rec-card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.05) + 's';
        card.classList.add('fade-in');
    });

    // Sidebar mobile overlay close
    document.addEventListener('click', function(e) {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        if (sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
});
