// MedTwin Authentication JavaScript

// ========================================
// Login Page
// ========================================

// Password Toggle
const togglePassword = document.getElementById('togglePassword');
if (togglePassword) {
    togglePassword.addEventListener('click', function () {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);

        // Toggle icon (optional - you can add different SVG for show/hide)
        this.classList.toggle('active');
    });
}

// Login Form Submission
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const remember = document.querySelector('input[name="remember"]').checked;

        console.log('Login attempt:', { email, remember });

        // Add loading state
        const submitBtn = this.querySelector('.btn-submit');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>Signing in...</span>';
        submitBtn.disabled = true;

        // Simulate API call
        setTimeout(() => {
            // TODO: Replace with actual API call
            console.log('Login successful!');

            // Redirect based on role (you'll get this from API)
            // For demo, redirect to a dashboard
            window.location.href = 'patient-dashboard.html'; // or 'doctor-dashboard.html'
        }, 1500);
    });
}

// ========================================
// Input Focus Effects
// ========================================

document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function () {
        this.parentElement.classList.add('focused');
    });

    input.addEventListener('blur', function () {
        this.parentElement.classList.remove('focused');
    });
});

// ========================================
// Social Login Buttons
// ========================================

document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const provider = this.textContent.trim();
        console.log(`Social login with ${provider}`);
        // TODO: Implement OAuth flow
    });
});

// ========================================
// Form Validation
// ========================================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return re.test(password);
}

// Real-time validation
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function () {
        if (this.value && !validateEmail(this.value)) {
            this.style.borderColor = 'var(--coral)';
            showError(this, 'Please enter a valid email address');
        } else {
            this.style.borderColor = '';
            hideError(this);
        }
    });
});

document.querySelectorAll('input[type="password"]').forEach(input => {
    input.addEventListener('input', function () {
        if (this.id === 'password' || this.id === 'doctorPassword') {
            const strength = getPasswordStrength(this.value);
            updatePasswordStrength(this, strength);
        }
    });
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    return strength;
}

function updatePasswordStrength(input, strength) {
    // You can add a visual indicator here
    const colors = ['#FF6B9D', '#FF8E53', '#F4A89F', '#A8B5A0', '#10B981'];
    const labels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];

    // Optional: Add strength indicator UI
    console.log(`Password strength: ${labels[strength - 1] || 'Too short'}`);
}

function showError(input, message) {
    let errorDiv = input.parentElement.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = 'color: var(--coral); font-size: 0.75rem; margin-top: 0.25rem;';
        input.parentElement.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function hideError(input) {
    const errorDiv = input.parentElement.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// ========================================
// Smooth Animations
// ========================================

// Animate form elements on page load
window.addEventListener('load', () => {
    const formElements = document.querySelectorAll('.form-group, .social-btn, .auth-footer');
    formElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';

        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});

// Add ripple effect to buttons
document.querySelectorAll('.btn-submit, .social-btn').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

console.log('%c🏥 MedTwin Authentication', 'color: #D4AF37; font-size: 16px; font-weight: bold;');
console.log('%cSecure Login System Active', 'color: #E8B4B8; font-size: 12px;');
