// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Password confirmation validation
const passwordForm = document.querySelector('form');
if (passwordForm) {
    passwordForm.addEventListener('submit', function (e) {
        const newPassword = document.getElementById('new_password');
        const confirmPassword = document.getElementById('confirm_new_password');

        if (newPassword && confirmPassword) {
            if (newPassword.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
            }
        }
    });
}

// Character counter for post content
const contentTextarea = document.getElementById('content');
if (contentTextarea) {
    contentTextarea.addEventListener('input', function () {
        const maxLength = 1000;
        const remaining = maxLength - this.value.length;

        let counter = this.parentElement.querySelector('.char-counter');
        if (!counter) {
            counter = document.createElement('small');
            counter.className = 'char-counter text-muted';
            this.parentElement.appendChild(counter);
        }

        counter.textContent = `${remaining} characters remaining`;

        if (remaining < 0) {
            counter.style.color = 'red';
        } else {
            counter.style.color = '';
        }
    });
} 