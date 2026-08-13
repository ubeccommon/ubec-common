/*
UBEC Protocol Website - Main JavaScript
========================================

Provides client-side interactivity, data visualization, and Ubuntu-inspired
animations for the web interface.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 2.0.0
Date: November 5, 2025
*/

/* ========================================================================
   UBEC Global Object - Ubuntu Philosophy Utilities
   ======================================================================== */

window.UBEC = window.UBEC || {};

/**
 * UBEC Configuration and Constants
 */
UBEC.config = {
    // Four Elements
    elements: {
        air: {
            symbol: '🌬️',
            color: '#B8D4E8',
            principle: 'Diversity',
            token: 'UBEC'
        },
        water: {
            symbol: '💧',
            color: '#7FC7C4',
            principle: 'Reciprocity',
            token: 'UBECrc'
        },
        earth: {
            symbol: '🌍',
            color: '#8AA67E',
            principle: 'Mutualism',
            token: 'UBECgpi'
        },
        fire: {
            symbol: '🔥',
            color: '#F4A896',
            principle: 'Regeneration',
            token: 'UBECtt'
        }
    },
    
    // Holonic Categories
    holonicCategories: {
        exemplar: { color: '#B08BBB', label: 'Exemplar' },
        integrator: { color: '#8FBC8F', label: 'Integrator' },
        contributor: { color: '#87CEEB', label: 'Contributor' },
        participant: { color: '#E8A87C', label: 'Participant' },
        observer: { color: '#9CB4CC', label: 'Observer' }
    },
    
    // API Configuration
    api: {
        baseUrl: '/api/v1',
        refreshInterval: 30000 // 30 seconds
    },
    
    // Feature Flags
    features: {
        autoRefresh: true,
        animations: true,
        darkMode: false
    }
};

/**
 * UBEC Utility Functions
 */
UBEC.utils = {
    /**
     * Format large numbers with commas
     */
    formatNumber: function(num) {
        if (!num && num !== 0) return '0';
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    /**
     * Format currency values
     */
    formatCurrency: function(value, decimals = 2) {
        if (!value && value !== 0) return '$0.00';
        return '$' + parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    /**
     * Format percentages
     */
    formatPercent: function(value, decimals = 1) {
        if (!value && value !== 0) return '0%';
        return (parseFloat(value) * 100).toFixed(decimals) + '%';
    },
    
    /**
     * Format dates
     */
    formatDate: function(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * Get element by token code
     */
    getElementByToken: function(tokenCode) {
        const elements = UBEC.config.elements;
        for (let key in elements) {
            if (elements[key].token === tokenCode) {
                return elements[key];
            }
        }
        return null;
    },
    
    /**
     * Truncate address for display
     */
    truncateAddress: function(address, length = 8) {
        if (!address) return '';
        if (address.length <= length * 2) return address;
        return address.substring(0, length) + '...' + address.substring(address.length - length);
    },
    
    /**
     * Debounce function
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Throttle function
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

/**
 * UBEC Animation Utilities
 */
UBEC.animate = {
    /**
     * Fade in element
     */
    fadeIn: function(element, duration = 600) {
        if (!UBEC.config.features.animations) return;
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    },
    
    /**
     * Slide in element
     */
    slideIn: function(element, direction = 'up', duration = 600) {
        if (!UBEC.config.features.animations) return;
        const transforms = {
            up: 'translateY(20px)',
            down: 'translateY(-20px)',
            left: 'translateX(20px)',
            right: 'translateX(-20px)'
        };
        
        element.style.opacity = '0';
        element.style.transform = transforms[direction];
        element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`;
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translate(0, 0)';
        }, 10);
    },
    
    /**
     * Pulse element
     */
    pulse: function(element, iterations = 1) {
        if (!UBEC.config.features.animations) return;
        let count = 0;
        const interval = setInterval(() => {
            element.style.transform = 'scale(1.05)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 150);
            count++;
            if (count >= iterations) {
                clearInterval(interval);
            }
        }, 300);
    },
    
    /**
     * Count up animation for numbers
     */
    countUp: function(element, start, end, duration = 1000) {
        if (!UBEC.config.features.animations) {
            element.textContent = UBEC.utils.formatNumber(end);
            return;
        }
        
        const range = end - start;
        const increment = range / (duration / 16); // 60fps
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = UBEC.utils.formatNumber(Math.floor(current));
        }, 16);
    }
};

/**
 * UBEC API Client
 */
UBEC.api = {
    /**
     * Fetch data from API
     */
    fetch: async function(endpoint) {
        try {
            const response = await fetch(`${UBEC.config.api.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('UBEC API Error:', error);
            throw error;
        }
    },
    
    /**
     * Get all tokens
     */
    getTokens: function() {
        return this.fetch('/tokens');
    },
    
    /**
     * Get network status
     */
    getNetworkStatus: function() {
        return this.fetch('/network/status');
    },
    
    /**
     * Get holonic scores
     */
    getHolonicScores: function() {
        return this.fetch('/holonic/scores');
    },
    
    /**
     * Get recent transactions
     */
    getRecentTransactions: function(limit = 20) {
        return this.fetch(`/transactions/recent?limit=${limit}`);
    }
};

/* ========================================================================
   DOM Ready Initialization
   ======================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌍 UBEC Protocol Website Loaded');
    console.log('Ubuntu: "I am because we are"');
    
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    // Initialize animations
    initAnimations();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize auto-refresh if enabled
    if (UBEC.config.features.autoRefresh) {
        initAutoRefresh();
    }
    
    // Initialize element cards
    initElementCards();
    
    // Log configuration
    console.log('UBEC Configuration:', UBEC.config);
});

/* ========================================================================
   Feature Initialization Functions
   ======================================================================== */

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Initialize scroll-triggered animations
 */
function initAnimations() {
    if (!UBEC.config.features.animations) return;
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards and sections
    document.querySelectorAll('.element-card, .card, .stat').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

/**
 * Initialize auto-refresh for dashboard
 */
function initAutoRefresh() {
    // Only auto-refresh on dashboard page
    if (!window.location.pathname.includes('/dashboard')) return;
    
    const refreshInterval = UBEC.config.api.refreshInterval;
    console.log(`Auto-refresh enabled: every ${refreshInterval / 1000} seconds`);
    
    setInterval(() => {
        // Reload page to fetch fresh data
        location.reload();
    }, refreshInterval);
    
    // Update last update time
    updateLastUpdateTime();
}

/**
 * Update "last updated" timestamp
 */
function updateLastUpdateTime() {
    const timeElement = document.getElementById('last-update-time');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString();
    }
}

/**
 * Initialize element card interactions
 */
function initElementCards() {
    const elementCards = document.querySelectorAll('.element-card');
    
    elementCards.forEach(card => {
        // Add hover effect with element color
        card.addEventListener('mouseenter', function() {
            const element = this.classList.contains('element-air') ? 'air' :
                          this.classList.contains('element-water') ? 'water' :
                          this.classList.contains('element-earth') ? 'earth' :
                          this.classList.contains('element-fire') ? 'fire' : null;
            
            if (element) {
                const color = UBEC.config.elements[element].color;
                this.style.borderTopColor = color;
            }
        });
        
        // Pulse animation on click
        card.addEventListener('click', function() {
            UBEC.animate.pulse(this, 1);
        });
    });
}

/* ========================================================================
   Data Visualization Utilities
   ======================================================================== */

/**
 * Update network statistics with animation
 */
UBEC.updateNetworkStats = function(stats) {
    // Update participant count
    const participantElement = document.querySelector('[data-stat="participants"]');
    if (participantElement && stats.active_participants) {
        UBEC.animate.countUp(participantElement, 0, stats.active_participants, 1000);
    }
    
    // Update transaction count
    const txElement = document.querySelector('[data-stat="transactions"]');
    if (txElement && stats.total_transactions_24h) {
        UBEC.animate.countUp(txElement, 0, stats.total_transactions_24h, 1000);
    }
    
    // Update Ubuntu score
    const scoreElement = document.querySelector('[data-stat="ubuntu-score"]');
    if (scoreElement && stats.average_ubuntu_score) {
        const percentage = Math.round(stats.average_ubuntu_score * 100);
        UBEC.animate.countUp(scoreElement, 0, percentage, 1000);
    }
    
    // Update bioregions count
    const bioregionElement = document.querySelector('[data-stat="bioregions"]');
    if (bioregionElement && stats.bioregions_count) {
        UBEC.animate.countUp(bioregionElement, 0, stats.bioregions_count, 1000);
    }
};

/**
 * Update holonic score bars
 */
UBEC.updateHolonicScores = function(scores) {
    const scoreMap = {
        'autonomy-integration': scores.autonomy_integration,
        'ubuntu-alignment': scores.ubuntu_alignment,
        'reciprocity-health': scores.reciprocity_health,
        'mutualism-capacity': scores.mutualism_capacity,
        'regeneration-impact': scores.regeneration_impact
    };
    
    for (let key in scoreMap) {
        const bar = document.querySelector(`[data-score="${key}"] .score-fill`);
        if (bar && scoreMap[key]) {
            const percentage = scoreMap[key] * 100;
            setTimeout(() => {
                bar.style.width = `${percentage}%`;
            }, 100);
        }
    }
};

/* ========================================================================
   Error Handling
   ======================================================================== */

/**
 * Global error handler
 */
window.addEventListener('error', function(event) {
    console.error('UBEC Error:', event.error);
    // In production, you might want to send this to an error tracking service
});

/**
 * Unhandled promise rejection handler
 */
window.addEventListener('unhandledrejection', function(event) {
    console.error('UBEC Unhandled Promise Rejection:', event.reason);
    // In production, you might want to send this to an error tracking service
});

/* ========================================================================
   Export UBEC Object (for modules if needed)
   ======================================================================== */

if (typeof module !== 'undefined' && module.exports) {
    module.exports = UBEC;
}

console.log('✅ UBEC JavaScript Loaded Successfully');
