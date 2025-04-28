// JavaScript for the login page
document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('Please fill in both email and password.');
        return;
    }

    // If everything filled, submit the form normally
    this.submit();
});
