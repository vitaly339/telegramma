// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh functionality for real-time updates
    let refreshInterval;
    
    // Check if we're on dashboard page
    if (document.querySelector('#weeklyChart')) {
        // Start auto-refresh every 30 seconds for dashboard
        refreshInterval = setInterval(function() {
            // Only refresh if document is visible to avoid unnecessary requests
            if (!document.hidden) {
                refreshUnreadMessages();
            }
        }, 30000);
    }
    
    // Stop refresh when leaving page
    window.addEventListener('beforeunload', function() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    });
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Real-time notifications for new messages
    function refreshUnreadMessages() {
        // This would typically connect to a WebSocket or make periodic AJAX calls
        // For now, we'll just update the page title if there are unread messages
        const unreadBadge = document.querySelector('.navbar .badge');
        if (unreadBadge && parseInt(unreadBadge.textContent) > 0) {
            updatePageTitle('⚠️ Новые сообщения - Батутный парк');
        }
    }
    
    function updatePageTitle(title) {
        if (document.title !== title) {
            document.title = title;
        }
    }
    
    // Focus management for message forms
    const messageInput = document.querySelector('input[name="message"]');
    if (messageInput) {
        messageInput.focus();
        
        // Auto-resize based on content (if needed)
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Submit on Enter (but not Shift+Enter)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.form.submit();
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Confirm dialogs for destructive actions
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Loading states for forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Загрузка...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds to prevent permanent lock
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
    
    // Charts color scheme for dark theme
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = '#dee2e6';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
    
    // Mobile menu handling
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick search (if search input exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            const searchInput = document.querySelector('input[type="text"][placeholder*="Поиск"]');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        }
        
        // ESC to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const bsModal = bootstrap.Modal.getInstance(openModal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }
    });
    
    // Table row highlighting
    document.querySelectorAll('table tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bs-gray-800)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Status update confirmations
    document.querySelectorAll('select[name="status"]').forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                const statusText = this.options[this.selectedIndex].text;
                if (confirm(`Изменить статус на "${statusText}"?`)) {
                    // Status change will be handled by form submission
                } else {
                    // Reset to original value
                    this.selectedIndex = 0;
                }
            }
        });
    });
    
    console.log('Dashboard initialized successfully');
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showToast(message, type = 'success') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 4000);
}
