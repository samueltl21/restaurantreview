// JavaScript for the login page
document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('Please fill in both email and password.');
        return;
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
document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
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
            
            // If everything filled, submit the form normally
            this.submit();
        });
    }
    
    // Profile page animations and functionality
    // Check if profile page elements exist before attaching behaviors
    if (document.querySelector('.table-row-animate')) {
        // Animation trigger for table rows
        const tableRows = document.querySelectorAll(".table-row-animate");
        setTimeout(() => {
            tableRows.forEach((row) => {
                row.style.opacity = 1;
            });
        }, 300);
        
        // Simple pagination functionality
        const rowsPerPage = 5;
        const table = document.getElementById('reviewTable');
        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            const pageCount = Math.ceil(rows.length / rowsPerPage);
            const pagination = document.querySelector('.pagination');
            
            // Create pagination links if more than one page
            if (pageCount > 1) {
                // Function to show page
                function showPage(pageNum) {
                    // Hide all rows
                    rows.forEach(row => {
                        row.style.display = 'none';
                    });
                    
                    // Show rows for current page
                    const start = (pageNum - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    
                    for (let i = start; i < end && i < rows.length; i++) {
                        rows[i].style.display = '';
                    }
                    
                    // Update active page
                    document.querySelectorAll('.page-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    
                    document.querySelector(`.page-item:nth-child(${pageNum + 1})`).classList.add('active');
                    
                    // Update disabled state for Previous/Next buttons
                    document.querySelector('.page-item:first-child').classList.toggle('disabled', pageNum === 1);
                    document.querySelector('.page-item:last-child').classList.toggle('disabled', pageNum === pageCount);
                }
                
                // Add click handlers to pagination
                const pageLinks = document.querySelectorAll('.pagination .page-link');
                pageLinks.forEach((link, index) => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        
                        if (index === 0) { // Previous
                            const activePage = parseInt(document.querySelector('.page-item.active .page-link').textContent);
                            if (activePage > 1) {
                                showPage(activePage - 1);
                            }
                        } else if (index === pageLinks.length - 1) { // Next
                            const activePage = parseInt(document.querySelector('.page-item.active .page-link').textContent);
                            if (activePage < pageCount) {
                                showPage(activePage + 1);
                            }
                        } else { // Number
                            showPage(index);
                        }
                    });
                });
                
                // Show first page initially
                showPage(1);
            }
        }
    }
});
