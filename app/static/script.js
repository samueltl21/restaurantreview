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
  
  document.addEventListener('DOMContentLoaded', function () {
    const $restaurantInput = $('#restaurant-name');
    const $suggestions = $('#restaurant-suggestions');
    const $checkResult = $('#restaurant-check-result');
    const $infoSection = $('#restaurant-info-section'); // location + cuisine
    const $reviewSection = $('#review-fields-section'); // date, rating, spend
  
    // Autocomplete suggestions
    $restaurantInput.on('input', function () {
      const query = $(this).val().trim();
      if (query.length < 2) {
        $suggestions.empty();
        return;
      }
  
      $.get('/search_restaurants', { q: query }, function (data) {
        $suggestions.empty();
        data.forEach(name => {
          $suggestions.append(`<button type="button" class="list-group-item list-group-item-action">${name}</button>`);
        });
      });
    });
  
    // Click on suggestion
    $suggestions.on('click', 'button', function () {
      const selected = $(this).text();
      $restaurantInput.val(selected);
      $suggestions.empty();
      $restaurantInput.trigger('blur');
    });
  
    // Blur triggers check
    $restaurantInput.on('blur', function () {
      const name = $restaurantInput.val().trim();
      if (!name) return;
  
      $.post('/check_restaurant', { restaurant_name: name }, function (data) {
        if (data.status === 'exists') {
          $('#location').val(data.location);
          $('#cuisine').val(data.cuisine);
  
          $checkResult.text(data.message).css('color', 'green');
          $infoSection.hide();
          $reviewSection.show();
        } else {
          $('#location').val('');
          $('#cuisine').val('');
  
          $checkResult.text("Restaurant not found. Please provide details.")
                      .css('color', 'red');
  
          $infoSection.show();
          $reviewSection.show();
        }
      }).fail(function () {
        $checkResult.text("Error checking restaurant.").css('color', 'orange');
      });
    });
  
    // Clear state on focus
    $restaurantInput.on('focus', function () {
      $suggestions.empty();
      $checkResult.text('');
      $reviewSection.hide();
      $infoSection.hide();
    });
  
    // Clean up suggestions if clicked outside
    $restaurantInput.on('blur', function () {
      setTimeout(() => $suggestions.empty(), 150);
    });
  });

  function showUploadForm() {
    document.getElementById("upload-prompt").style.display = "none";
    document.getElementById("upload-form").style.display = "block";
  }

document.addEventListener('DOMContentLoaded', function () {
    const imgInput = document.getElementById('review_image');
    if (imgInput) {
        imgInput.addEventListener('change', function () {
            const file = this.files && this.files[0];
            if (!file) return;
            
            let preview = document.getElementById('image-preview');
            if (!preview) {
                preview = document.createElement('img');
                preview.id = 'image-preview';
                preview.style.maxWidth = '200px';
                preview.style.marginTop = '10px';
              
                this.parentNode.appendChild(preview);
            }
            
            preview.src = URL.createObjectURL(file);
        });
    }
});
