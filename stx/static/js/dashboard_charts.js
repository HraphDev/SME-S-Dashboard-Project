document.addEventListener('DOMContentLoaded', function () {
    const dataDiv = document.getElementById('dashboard-data');

    const movementLabels = JSON.parse(dataDiv.dataset.movementLabels);
    const movementValues = JSON.parse(dataDiv.dataset.movementValues);
    const stockLabels = JSON.parse(dataDiv.dataset.stockLabels);
    const stockValues = JSON.parse(dataDiv.dataset.stockValues);

    const movementCtx = document.getElementById('movementChart').getContext('2d');
    new Chart(movementCtx, {
        type: 'bar',
        data: {
            labels: movementLabels,
            datasets: [{
                label: 'Mouvements',
                data: movementValues,
                backgroundColor: '#f43f5e'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    const stockCtx = document.getElementById('stockChart').getContext('2d');
    new Chart(stockCtx, {
        type: 'doughnut',
        data: {
            labels: stockLabels,
            datasets: [{
                label: 'Stock',
                data: stockValues,
                backgroundColor: ['#22d3ee', '#f97316', '#a78bfa', '#4ade80', '#facc15']
            }]
        },
        options: {
            responsive: true
        }
    });
});
