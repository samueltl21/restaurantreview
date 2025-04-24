// This is the JavaScript for the login page
// Get the login form element
document.getElementById('login-form').addEventListener('submit', function (event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the values from the email and password fields
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Ensure both fields are filled
    if (!email || !password) {
        alert('Please fill in both email and password.');
        return; // Stop further execution
    }

    // Example: Add login logic here (e.g., send data to the server)
    /*
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    })
    .then((response) => {
        if (response.ok) {
            alert('Login successful!');
            // Redirect to another page or handle success
        } else {
            alert('Invalid email or password.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred during login.');
    });
    */

    // Temporary placeholder for success message
    alert('Login successful!');
});

// This is the JavaScript for the registration page
// Add an event listener to the sign-up form to handle form submission
document.getElementById('signup-form').addEventListener('submit', function(event) {
    // Prevent the form's default submission behavior (e.g., page reload)
    event.preventDefault();

    // Get the values of the password and confirm password fields
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Check if the passwords match
    if (password !== confirmPassword) {
        // Display an alert if the passwords do not match
        alert('Passwords do not match!');
        return; // Stop the execution of the form submission
    }

    // Display a success message if passwords match
    alert('Sign up successful!');
});
