// JavaScript for the login page
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {
                event.preventDefault();
                alert('Please fill in both email and password.');
                return;
            }
        });
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                event.preventDefault();
                alert('Passwords do not match!');
                return;
            }
        });
    }

    if (document.querySelector('.table-row-animate')) {
        const tableRows = document.querySelectorAll(".table-row-animate");
        setTimeout(() => {
            tableRows.forEach((row) => {
                row.style.opacity = 1;
            });
        }, 300);

        const rowsPerPage = 5;
        const table = document.getElementById('reviewTable');
        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            const pageCount = Math.ceil(rows.length / rowsPerPage);
            const pagination = document.querySelector('.pagination');

            if (pageCount > 1) {
                function showPage(pageNum) {
                    rows.forEach(row => {
                        row.style.display = 'none';
                    });

                    const start = (pageNum - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    for (let i = start; i < end && i < rows.length; i++) {
                        rows[i].style.display = '';
                    }

                    document.querySelectorAll('.page-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    document.querySelector(`.page-item:nth-child(${pageNum + 1})`).classList.add('active');

                    document.querySelector('.page-item:first-child').classList.toggle('disabled', pageNum === 1);
                    document.querySelector('.page-item:last-child').classList.toggle('disabled', pageNum === pageCount);
                }

                const pageLinks = document.querySelectorAll('.pagination .page-link');
                pageLinks.forEach((link, index) => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const activePage = parseInt(document.querySelector('.page-item.active .page-link').textContent);
                        if (index === 0 && activePage > 1) {
                            showPage(activePage - 1);
                        } else if (index === pageLinks.length - 1 && activePage < pageCount) {
                            showPage(activePage + 1);
                        } else {
                            showPage(index);
                        }
                    });
                });

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
                    barThickness: 30
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
                            stepSize: 1
                        }
                    }
                }
            }
        });

        chartCanvas.style.backgroundColor = 'white';
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const $restaurantInput = $('#restaurant-name');
    const $suggestions = $('#restaurant-suggestions');
    const $checkResult = $('#restaurant-check-result');
    const $infoSection = $('#restaurant-info-section');
    const $reviewSection = $('#review-fields-section');

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

    $suggestions.on('click', 'button', function () {
        const selected = $(this).text();
        $restaurantInput.val(selected);
        $suggestions.empty();
        $restaurantInput.trigger('blur');
    });

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

    $restaurantInput.on('focus', function () {
        $suggestions.empty();
        $checkResult.text('');
        $reviewSection.hide();
        $infoSection.hide();
    });

    $restaurantInput.on('blur', function () {
        setTimeout(() => $suggestions.empty(), 150);
    });
});

function showUploadForm() {
    document.getElementById("upload-prompt").style.display = "none";
    document.getElementById("upload-form").style.display = "block";
}

// ✅ ADDITION — Share Selected Reviews (ADD AT THE VERY END ONLY)

function showCopiedFeedback(link) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(link).then(() => {
            alert("Share link copied to clipboard:\n" + link);
        }).catch(() => {
            prompt("Copy the link manually:", link);
        });
    } else {
        prompt("Copy the link manually:", link);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const shareBtn = document.getElementById("shareButton");
    if (shareBtn) {
        shareBtn.addEventListener("click", () => {
            const selected = [];
            document.querySelectorAll(".share-checkbox:checked").forEach(cb => {
                selected.push(cb.value);
            });

            const recipientId = document.getElementById("recipientUser").value;

            if (selected.length === 0) {
                alert("Please select at least one review.");
                return;
            }
            if (!recipientId) {
                alert("Please select a user to share with.");
                return;
            }

            fetch("/share_reviews", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ review_ids: selected, recipient_id: recipientId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.url;
                } else {
                    alert("Failed to share: " + data.message);
                }
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // Cuisine Preference Pie Chart
    if (document.getElementById("cuisineChart")) {
      const ctx1 = document.getElementById("cuisineChart").getContext("2d");
      new Chart(ctx1, {
        type: "pie",
        data: {
          labels: cuisineLabels,
          datasets: [{
            data: cuisineValues,
            backgroundColor: [
              "#f94144", "#f3722c", "#f8961e", "#f9c74f",
              "#90be6d", "#43aa8b", "#577590", "#6a4c93"
            ]
          }]
        },
        options: {
          plugins: {
            title: {
              display: true,
              text: "Your Cuisine Preferences"
            },
            legend: {
              position: "bottom"
            }
          }
        }
      });
    }
  
    // Average Spend per Cuisine Bar Chart
    if (document.getElementById("spendChart")) {
      const ctx2 = document.getElementById("spendChart").getContext("2d");
      new Chart(ctx2, {
        type: "bar",
        data: {
          labels: spendLabels,
          datasets: [{
            label: "Average Spend ($)",
            data: spendValues,
            backgroundColor: "rgba(75, 192, 192, 0.6)",
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: "Average Spend by Cuisine"
            },
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  });
  