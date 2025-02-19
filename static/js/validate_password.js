document.addEventListener('DOMContentLoaded', function() {
    const password = document.getElementById('password');
    const password2 = document.getElementById('password2');
    const form = document.querySelector('.login-form');

    // Create password requirements container
    const requirementsDiv = document.createElement('div');
    requirementsDiv.className = 'password-requirements';
    requirementsDiv.innerHTML = `
        <div class="requirement" id="length">At least 8 characters long</div>
        <div class="requirement" id="uppercase">Contains uppercase letter</div>
        <div class="requirement" id="lowercase">Contains lowercase letter</div>
        <div class="requirement" id="number">Contains number</div>
        <div class="requirement" id="special">Contains special character</div>
    `;
    password.parentNode.insertBefore(requirementsDiv, password.nextSibling);

    // Show requirements when password field is focused
    password.addEventListener('focus', function() {
        requirementsDiv.style.display = 'block';
    });

    // Hide requirements when clicking outside
    document.addEventListener('click', function(e) {
        if (!password.contains(e.target) && !requirementsDiv.contains(e.target)) {
            requirementsDiv.style.display = 'none';
        }
    });

    // Check password strength in real-time
    password.addEventListener('input', checkPasswordStrength);
    password2.addEventListener('input', checkPasswordsMatch);

    function checkPasswordStrength() {
        const value = password.value;
        
        // Define requirements
        const requirements = {
            length: value.length >= 8,
            uppercase: /[A-Z]/.test(value),
            lowercase: /[a-z]/.test(value),
            number: /[0-9]/.test(value),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(value)
        };

        // Update requirement visual indicators
        for (const [req, met] of Object.entries(requirements)) {
            const element = document.getElementById(req);
            if (met) {
                element.classList.add('met');
            } else {
                element.classList.remove('met');
            }
        }

        // Check if all requirements are met
        const allRequirementsMet = Object.values(requirements).every(Boolean);
        password.setCustomValidity(allRequirementsMet ? '' : 'Password does not meet requirements');
        
        // Update matching check if confirmation field has value
        if (password2.value) {
            checkPasswordsMatch();
        }
    }

    function checkPasswordsMatch() {
        if (password.value !== password2.value) {
            password2.setCustomValidity('Passwords do not match');
            password2.classList.add('input-error');
        } else {
            password2.setCustomValidity('');
            password2.classList.remove('input-error');
        }
    }

    // Form submission handler
    form.addEventListener('submit', function(e) {
        checkPasswordStrength();
        checkPasswordsMatch();
        
        if (!password.checkValidity() || !password2.checkValidity()) {
            e.preventDefault();
            if (!password.checkValidity()) {
                requirementsDiv.style.display = 'block';
            }
        }
    });
});