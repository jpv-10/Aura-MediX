// Authentication Pages Scripts

document.addEventListener('DOMContentLoaded', () => {
    initializeAuthForm();
    initializePasswordStrength();
    initializeAuthAnimations();
});

function initializeAuthForm() {
    const form = document.getElementById('register-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = form.password.value;
        const confirmPassword = form.confirm_password.value;
        
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        if (password.length < 8) {
            showError('Password must be at least 8 characters');
            return;
        }
        
        form.submit();
    });
}

function initializePasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    const strengthBar = document.querySelector('.strength-bar::after');
    const strengthText = document.querySelector('.strength-text');
    
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        let strength = 0;
        
        if (password.length >= 8) strength += 25;
        if (password.length >= 12) strength += 25;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
        if (/[0-9]/.test(password) && /[!@#$%^&*]/.test(password)) strength += 25;
        
        let strengthLevel = 'Weak';
        let strengthColor = '#ef4444';
        
        if (strength >= 75) {
            strengthLevel = 'Strong';
            strengthColor = '#10b981';
        } else if (strength >= 50) {
            strengthLevel = 'Medium';
            strengthColor = '#f59e0b';
        }
        
        // Update visual indicator
        const style = document.createElement('style');
        style.textContent = `.strength-bar::after { width: ${strength}%; background: ${strengthColor}; }`;
        document.head.appendChild(style);
        
        if (strengthText) {
            strengthText.textContent = `Strength: ${strengthLevel}`;
            strengthText.style.color = strengthColor;
        }
    });
}

function initializeAuthAnimations() {
    // Auth box entrance
    gsap.from('.auth-box', {
        opacity: 0,
        x: -50,
        duration: 0.8,
        ease: 'power2.out'
    });
    
    // Visual side entrance
    gsap.from('.auth-visual', {
        opacity: 0,
        x: 50,
        duration: 0.8,
        ease: 'power2.out'
    });
    
    // Form elements stagger
    gsap.from('.form-group', {
        opacity: 0,
        y: 20,
        duration: 0.6,
        stagger: 0.1,
        delay: 0.3,
        ease: 'power2.out'
    });
    
    // Button animation
    gsap.from('.btn-primary, .btn-secondary', {
        opacity: 0,
        y: 20,
        duration: 0.6,
        delay: 0.6,
        ease: 'power2.out'
    });
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error animate-fade-in';
    alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    const firstForm = document.querySelector('.form-group');
    if (firstForm) {
        firstForm.parentElement.insertBefore(alert, firstForm);
    }
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Input focus effects
document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function() {
        gsap.to(this, {
            duration: 0.3,
            boxShadow: '0 0 0 3px rgba(0, 212, 255, 0.2)'
        });
    });
    
    input.addEventListener('blur', function() {
        gsap.to(this, {
            duration: 0.3,
            boxShadow: 'none'
        });
    });
});
