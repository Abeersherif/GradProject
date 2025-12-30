// MedTwin Sign Up - Multi-Step Form Logic

let currentStep = 1;
let selectedRole = '';
let formData = {};

// ========================================
// Step Navigation
// ========================================

function nextStep() {
    // Validate current step
    if (!validateStep(currentStep)) {
        return;
    }

    // Save current step data
    saveStepData(currentStep);

    // Move to next step
    if (currentStep < 3) {
        currentStep++;
        updateStep();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStep();
    }
}

function updateStep() {
    // Update stepper UI
    document.querySelectorAll('.stepper-item').forEach((item, index) => {
        const stepNumber = index + 1;
        item.classList.remove('active', 'completed');

        if (stepNumber < currentStep) {
            item.classList.add('completed');
        } else if (stepNumber === currentStep) {
            item.classList.add('active');
        }
    });

    // Update form steps
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });

    // Show appropriate step based on role
    if (currentStep === 2) {
        const roleStep = document.querySelector(`.form-step[data-step="2"][data-role="${selectedRole}"]`);
        if (roleStep) {
            roleStep.classList.add('active');
        }
    } else {
        const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]:not([data-role])`);
        if (currentStepEl) {
            currentStepEl.classList.add('active');
        }
    }

    // Update review if on step 3
    if (currentStep === 3) {
        updateReview();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ========================================
// Step Validation
// ========================================

function validateStep(step) {
    if (step === 1) {
        // Validate role selection
        const roleInput = document.querySelector('input[name="role"]:checked');
        if (!roleInput) {
            alert('Please select a role to continue');
            return false;
        }
        selectedRole = roleInput.value;
        return true;
    }

    if (step === 2) {
        // Validate form fields
        const activeStep = document.querySelector('.form-step.active');
        const requiredFields = activeStep.querySelectorAll('[required]');

        for (let field of requiredFields) {
            if (!field.value.trim()) {
                field.focus();
                showError(field, 'This field is required');
                return false;
            }

            // Email validation
            if (field.type === 'email' && !validateEmail(field.value)) {
                field.focus();
                showError(field, 'Please enter a valid email address');
                return false;
            }
        }

        // Password match validation
        const password = activeStep.querySelector('[name="password"]');
        const confirmPassword = activeStep.querySelector('[name="confirmPassword"]');

        if (password && confirmPassword) {
            if (password.value !== confirmPassword.value) {
                confirmPassword.focus();
                showError(confirmPassword, 'Passwords do not match');
                return false;
            }

            if (password.value.length < 8) {
                password.focus();
                showError(password, 'Password must be at least 8 characters');
                return false;
            }
        }

        return true;
    }

    if (step === 3) {
        // Validate terms checkbox
        const termsCheckbox = document.querySelector('input[name="terms"]');
        if (!termsCheckbox.checked) {
            alert('Please accept the Terms of Service and Privacy Policy');
            return false;
        }
        return true;
    }

    return true;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(input, message) {
    input.style.borderColor = 'var(--coral)';

    let errorDiv = input.parentElement.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = 'color: var(--coral); font-size: 0.75rem; margin-top: 0.25rem;';
        input.parentElement.appendChild(errorDiv);
    }
    errorDiv.textContent = message;

    // Remove error on input
    input.addEventListener('input', function () {
        this.style.borderColor = '';
        const err = this.parentElement.querySelector('.error-message');
        if (err) err.remove();
    }, { once: true });
}

// ========================================
// Save Step Data
// ========================================

function saveStepData(step) {
    const activeStep = document.querySelector('.form-step.active');
    if (!activeStep) return;

    const inputs = activeStep.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type !== 'radio' && input.type !== 'checkbox') {
            formData[input.name] = input.value;
        } else if (input.type === 'radio' && input.checked) {
            formData[input.name] = input.value;
        } else if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        }
    });

    console.log('Form data saved:', formData);
}

// ========================================
// Update Review
// ========================================

function updateReview() {
    // Update role
    document.getElementById('reviewRole').textContent =
        selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1);

    // Update personal info
    document.getElementById('reviewName').textContent =
        `${formData.firstName || ''} ${formData.lastName || ''}`.trim() || '-';
    document.getElementById('reviewEmail').textContent = formData.email || '-';
    document.getElementById('reviewPhone').textContent = formData.phone || '-';

    // Show/hide role-specific sections
    if (selectedRole === 'patient') {
        document.getElementById('patientReviewSection').style.display = 'block';
        document.getElementById('doctorReviewSection').style.display = 'none';

        document.getElementById('reviewDOB').textContent = formData.dateOfBirth || '-';
        document.getElementById('reviewGender').textContent =
            formData.gender ? formData.gender.charAt(0).toUpperCase() + formData.gender.slice(1) : '-';
        document.getElementById('reviewBloodType').textContent = formData.bloodType || 'Not specified';
    } else {
        document.getElementById('patientReviewSection').style.display = 'none';
        document.getElementById('doctorReviewSection').style.display = 'block';

        document.getElementById('reviewLicense').textContent = formData.licenseNumber || '-';
        document.getElementById('reviewSpecialty').textContent =
            formData.specialty ? formData.specialty.charAt(0).toUpperCase() + formData.specialty.slice(1) : '-';
        document.getElementById('reviewHospital').textContent = formData.hospital || '-';
        document.getElementById('reviewExperience').textContent =
            formData.yearsExperience ? `${formData.yearsExperience} years` : '-';
    }
}

// ========================================
// Role Selection
// ========================================

document.querySelectorAll('.role-card').forEach(card => {
    card.addEventListener('click', function () {
        const radio = this.querySelector('.role-input');
        radio.checked = true;

        // Update visual state
        document.querySelectorAll('.role-card').forEach(c => {
            c.style.borderColor = 'rgba(245, 241, 232, 0.1)';
            c.style.background = 'var(--bg-secondary)';
        });

        this.style.borderColor = 'var(--champagne)';
        this.style.background = 'linear-gradient(135deg, rgba(212, 175, 55, 0.05) 0%, rgba(232, 180, 184, 0.05) 100%)';
    });
});

// ========================================
// Form Submission
// ========================================

const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', function (e) {
        e.preventDefault();

        if (!validateStep(3)) {
            return;
        }

        // Save final step data
        saveStepData(3);

        console.log('Final form data:', formData);

        // Add loading state
        const submitBtn = this.querySelector('.btn-submit');
        const originalHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>Creating Account...</span>';
        submitBtn.disabled = true;

        // Simulate API call
        setTimeout(() => {
            // TODO: Replace with actual API call
            console.log('Account created successfully!');

            // Show success message or redirect
            alert('Account created successfully! Redirecting to login...');
            window.location.href = 'login.html';
        }, 2000);
    });
}

// ========================================
// Auto-fill for Demo (Remove in production)
// ========================================

function fillDemoData() {
    if (selectedRole === 'patient') {
        document.getElementById('firstName').value = 'John';
        document.getElementById('lastName').value = 'Doe';
        document.getElementById('email').value = 'john.doe@example.com';
        document.getElementById('phone').value = '+1 (555) 123-4567';
        document.getElementById('dateOfBirth').value = '1990-01-15';
        document.getElementById('gender').value = 'male';
        document.getElementById('bloodType').value = 'O+';
        document.getElementById('password').value = 'Password123';
        document.getElementById('confirmPassword').value = 'Password123';
    } else {
        document.getElementById('doctorFirstName').value = 'Dr. Sarah';
        document.getElementById('doctorLastName').value = 'Smith';
        document.getElementById('doctorEmail').value = 'dr.smith@hospital.com';
        document.getElementById('licenseNumber').value = 'ML123456';
        document.getElementById('specialty').value = 'cardiology';
        document.getElementById('hospital').value = 'City General Hospital';
        document.getElementById('yearsExperience').value = '15';
        document.getElementById('doctorPhone').value = '+1 (555) 987-6543';
        document.getElementById('doctorPassword').value = 'Password123';
        document.getElementById('doctorConfirmPassword').value = 'Password123';
    }
}

// Add demo button (for testing - remove in production)
window.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        fillDemoData();
        console.log('Demo data filled!');
    }
});

// ========================================
// Smooth Animations
// ========================================

// Animate role cards on load
window.addEventListener('load', () => {
    const roleCards = document.querySelectorAll('.role-card');
    roleCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
});

console.log('%c🏥 MedTwin Sign Up', 'color: #D4AF37; font-size: 16px; font-weight: bold;');
console.log('%cMulti-Step Registration Active', 'color: #E8B4B8; font-size: 12px;');
console.log('%cPress Ctrl+D to fill demo data', 'color: #8B7E74; font-size: 10px;');
