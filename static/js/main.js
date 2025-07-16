// Tokyo Night CTF Platform - JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle) {
        navToggle.addEventListener('click', function () {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add typing effect to code elements
    const codeElements = document.querySelectorAll('code, .code-text');
    codeElements.forEach(function (element) {
        element.classList.add('typing-effect');
    });

    // Particle effect for background
    createParticleEffect();

    // Stats counter animation
    animateStats();

    // Add neon glow effect to important elements
    addNeonEffects();

    // Form validation
    setupFormValidation();

    // Challenge timer
    setupChallengeTimer();
});

// Particle Effect
function createParticleEffect() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.3';

    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            color: getRandomColor(),
            opacity: Math.random() * 0.5 + 0.3
        };
    }

    function getRandomColor() {
        const colors = ['#7aa2f7', '#bb9af7', '#7dcfff', '#f7768e', '#9ece6a', '#e0af68'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    function initParticles() {
        for (let i = 0; i < 50; i++) {
            particles.push(createParticle());
        }
    }

    function updateParticles() {
        for (let i = 0; i < particles.length; i++) {
            const particle = particles[i];

            particle.x += particle.speedX;
            particle.y += particle.speedY;

            if (particle.x < 0 || particle.x > canvas.width) {
                particle.speedX = -particle.speedX;
            }
            if (particle.y < 0 || particle.y > canvas.height) {
                particle.speedY = -particle.speedY;
            }
        }
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < particles.length; i++) {
            const particle = particles[i];

            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = particle.color;
            ctx.globalAlpha = particle.opacity;
            ctx.fill();

            // Draw connections
            for (let j = i + 1; j < particles.length; j++) {
                const otherParticle = particles[j];
                const distance = Math.sqrt(
                    Math.pow(particle.x - otherParticle.x, 2) +
                    Math.pow(particle.y - otherParticle.y, 2)
                );

                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = particle.color;
                    ctx.globalAlpha = (100 - distance) / 100 * 0.2;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }

        ctx.globalAlpha = 1;
    }

    function animate() {
        updateParticles();
        drawParticles();
        requestAnimationFrame(animate);
    }

    resizeCanvas();
    initParticles();
    animate();

    window.addEventListener('resize', resizeCanvas);
}

// Stats Animation
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');

    statNumbers.forEach(function (stat) {
        const targetValue = parseInt(stat.textContent);
        let currentValue = 0;
        const increment = targetValue / 50;

        const timer = setInterval(function () {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            stat.textContent = Math.floor(currentValue);
        }, 40);
    });
}

// Neon Effects
function addNeonEffects() {
    const neonElements = document.querySelectorAll('.neon-text, .brand-text .neon-accent');

    neonElements.forEach(function (element) {
        element.addEventListener('mouseenter', function () {
            this.style.textShadow = '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor';
        });

        element.addEventListener('mouseleave', function () {
            this.style.textShadow = '0 0 10px currentColor';
        });
    });
}

// Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function (field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    showFieldError(field, '此字段为必填项');
                } else {
                    field.classList.remove('error');
                    hideFieldError(field);
                }
            });

            // Email validation
            const emailFields = form.querySelectorAll('[type="email"]');
            emailFields.forEach(function (field) {
                if (field.value && !isValidEmail(field.value)) {
                    isValid = false;
                    field.classList.add('error');
                    showFieldError(field, '请输入有效的邮箱地址');
                }
            });

            // Password confirmation
            const passwordField = form.querySelector('[name="password"]');
            const confirmField = form.querySelector('[name="confirm_password"]');

            if (passwordField && confirmField && passwordField.value !== confirmField.value) {
                isValid = false;
                confirmField.classList.add('error');
                showFieldError(confirmField, '密码确认不匹配');
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(field, message) {
    hideFieldError(field);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#f7768e';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';

    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

function hideFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Challenge Timer
function setupChallengeTimer() {
    const timerElements = document.querySelectorAll('.challenge-timer');

    timerElements.forEach(function (timer) {
        const endTime = new Date(timer.dataset.endTime).getTime();

        function updateTimer() {
            const now = new Date().getTime();
            const timeLeft = endTime - now;

            if (timeLeft > 0) {
                const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

                timer.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            } else {
                timer.textContent = '已结束';
                timer.classList.add('expired');
            }
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    });
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <span class="flash-text">${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    const container = document.querySelector('.flash-container') || createFlashContainer();
    container.appendChild(notification);

    setTimeout(function () {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(function () {
            notification.remove();
        }, 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
    return container;
}

// Loading states
function showLoading(element) {
    const loader = document.createElement('span');
    loader.className = 'loading';
    element.appendChild(loader);
    element.disabled = true;
}

function hideLoading(element) {
    const loader = element.querySelector('.loading');
    if (loader) {
        loader.remove();
    }
    element.disabled = false;
}

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl + / for help
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        showHelpModal();
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        closeModals();
    }
});

function showHelpModal() {
    // Implementation for help modal
    console.log('Help modal would be shown here');
}

function closeModals() {
    const modals = document.querySelectorAll('.modal.active');
    modals.forEach(function (modal) {
        modal.classList.remove('active');
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () {
            showNotification('已复制到剪贴板', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('已复制到剪贴板', 'success');
        } catch (err) {
            showNotification('复制失败', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Add copy buttons to code blocks
document.querySelectorAll('pre code').forEach(function (codeBlock) {
    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.innerHTML = '<i class="fas fa-copy"></i>';
    button.title = '复制代码';

    button.addEventListener('click', function () {
        copyToClipboard(codeBlock.textContent);
    });

    const pre = codeBlock.parentNode;
    pre.style.position = 'relative';
    pre.appendChild(button);
});

// Theme switcher (if needed)
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
}

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
}

// Export functions for global use
window.CTF = {
    showNotification,
    showLoading,
    hideLoading,
    copyToClipboard,
    toggleTheme
};
