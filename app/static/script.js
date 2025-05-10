// JavaScript for the login page
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            // No event.preventDefault() because we WANT to submit the form normally to the server
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {
                event.preventDefault(); // Block submission if missing fields
                alert('Please fill in both email and password.');
                return;
            }
            // If both email and password are filled, let the form submit
        });
    }

    // This is the JavaScript for the registration page
    // Add an event listener to the sign-up form to handle form submission
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
            // No preventDefault() immediately, only if passwords don't match
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            // Check if the passwords match
            if (password !== confirmPassword) {
                event.preventDefault(); // Block the submission
                alert('Passwords do not match!');
                return;
            }

            // If passwords match, allow the form to submit normally
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

                const pageLinks = document.querySelectorAll('.pagination .page-link');
                pageLinks.forEach((link, index) => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const activePage = parseInt(document.querySelector('.page-item.active .page-link').textContent);
                        if (index === 0 && activePage > 1) { // Previous
                            showPage(activePage - 1);
                        } else if (index === pageLinks.length - 1 && activePage < pageCount) { // Next
                            showPage(activePage + 1);
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

document.addEventListener('DOMContentLoaded', function () {
    const chartCanvas = document.getElementById('reviewChart');
    if (chartCanvas && typeof chartLabels !== "undefined" && typeof chartValues !== "undefined") {
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Number of Reviews',
                    data: chartValues,
                    borderWidth: 1,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    barThickness: 30 // 👈 This makes bars thinner
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Reviews per Top Restaurant'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1 // 👈 Show every integer
                        }
                    }
                }
            }
        });

        chartCanvas.style.backgroundColor = 'white';
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const shareBtn = document.getElementById("shareButton");
    shareBtn.addEventListener("click", () => {
      const selected = [];
      document.querySelectorAll(".share-checkbox:checked").forEach((checkbox) => {
        selected.push(checkbox.value);
      });
  
      if (selected.length === 0) {
        alert("Please select at least one review to share.");
        return;
      }
  
      // Send selected review IDs to backend to generate share link
      fetch("/generate_share_link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review_ids: selected })
      })
      .then(res => res.json())
      .then(data => {
        const shareLink = window.location.origin + "/shared/" + data.token;
        navigator.clipboard.writeText(shareLink); // Copy to clipboard
        alert("Share link copied to clipboard:\n" + shareLink);
      });
    });
  });
  
document.addEventListener('DOMContentLoaded', function() {
  // Analytics page charts
  // Check if we're on the analytics page by looking for required elements
  if (document.getElementById('cuisineChart') && document.getElementById('spendChart')) {
    // Create random colors for the pie chart
    function generateColors(count) {
      const colors = [];
      for (let i = 0; i < count; i++) {
        const r = Math.floor(Math.random() * 200);
        const g = Math.floor(Math.random() * 200);
        const b = Math.floor(Math.random() * 200);
        colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
      }
      return colors;
    }

    if (cuisineLabels && cuisineLabels.length > 0) {
      // Cuisine Preference Pie Chart
      const cuisineCtx = document.getElementById('cuisineChart').getContext('2d');
      const pieColors = generateColors(cuisineLabels.length);
      
      new Chart(cuisineCtx, {
        type: 'pie',
        data: {
          labels: cuisineLabels,
          datasets: [{
            data: cuisineValues,
            backgroundColor: pieColors,
            borderColor: pieColors.map(color => color.replace('0.7', '1')),
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        }
      });
      
      // Average Spend per Cuisine Bar Chart
      const spendCtx = document.getElementById('spendChart').getContext('2d');
      
      new Chart(spendCtx, {
        type: 'bar',
        data: {
          labels: spendLabels,
          datasets: [{
            label: 'Average Spend ($)',
            data: spendValues,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value;
                }
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          }
        }
      });
    }
  }
});
  