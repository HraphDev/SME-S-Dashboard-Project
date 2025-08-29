document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.dropdown-header').forEach(header => {
        header.addEventListener('click', function() {
            const dropdown = this.parentElement;
            dropdown.classList.toggle('open');
        });
    });

    document.querySelectorAll('.dropdown-menu .nav-link.active').forEach(activeLink => {
        const dropdown = activeLink.closest('.dropdown');
        if (dropdown) {
            dropdown.classList.add('open');
        }
    });

    if (document.getElementById('movementsChart')) {
        initializeCharts();
    }
});

function initializeCharts() {
    const ctx = document.getElementById('movementsChart').getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Stock Movements',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: 'rgba(79, 99, 255, 0.2)',
                borderColor: 'rgba(79, 99, 255, 1)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    document.getElementById('movementsChart').classList.add('visible');
}