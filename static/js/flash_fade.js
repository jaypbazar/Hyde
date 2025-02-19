document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        // Add fade-out animation class
        message.classList.add('fade-out');
        // Remove the message after 5 seconds
        setTimeout(function() {
            message.style.display = 'none';
        }, 5000);
    });
});