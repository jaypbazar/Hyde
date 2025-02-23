// Get all eye icons
const eyeIcons = document.querySelectorAll('.eye-icon');

eyeIcons.forEach(icon => {
    icon.addEventListener('click', function() {
        // Get the password input that comes before the icon's parent <a> tag
        const passwordInput = this.parentElement.previousElementSibling;
        
        // Toggle password visibility
        if (passwordInput && passwordInput.type === 'password') {
            passwordInput.type = 'text';
            this.src = this.dataset.eyeOpen;
        } else if (passwordInput) {
            passwordInput.type = 'password';
            this.src = this.dataset.eyeClosed;
        }
    });
});