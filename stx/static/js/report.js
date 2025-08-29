function toggleSection(sectionId){
    const sections = ['productsSection','movementsSection','lowStockSection','suppliersSection'];
    sections.forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function parseJSONSafe(jsonString) {
    try { return JSON.parse(jsonString); } 
    catch(e) { return []; }
}

document.addEventListener("DOMContentLoaded", function() {
    const productStockData = JSON.parse(document.getElementById('productStockChart').dataset.products);
    const movementLabels = JSON.parse(document.getElementById('movementChart').dataset.labels);
    const movementValues = JSON.parse(document.getElementById('movementChart').dataset.values);
    const supplierLabels = JSON.parse(document.getElementById('supplierChart').dataset.labels);
    const supplierValues = JSON.parse(document.getElementById('supplierChart').dataset.values);

    const ctxProducts = document.getElementById('productStockChart');
    if(ctxProducts){
        new Chart(ctxProducts, {
            type: 'bar',
            data: {
                labels: productStockData.map(p => p.name),
                datasets: [{
                    label: 'Quantity',
                    data: productStockData.map(p => p.quantity),
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    }

    const ctxMovements = document.getElementById('movementChart');
    if(ctxMovements){
        new Chart(ctxMovements, {
            type: 'line',
            data: {
                labels: movementLabels,
                datasets: [{
                    label: 'Movements',
                    data: movementValues,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    tension: 0.3
                }]
            },
            options: { responsive: true }
        });
    }

    const ctxSuppliers = document.getElementById('supplierChart');
    if(ctxSuppliers){
        new Chart(ctxSuppliers, {
            type: 'pie',
            data: {
                labels: supplierLabels,
                datasets: [{
                    label: 'Products per Supplier',
                    data: supplierValues,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.6)',
                        'rgba(16, 185, 129, 0.6)',
                        'rgba(234, 179, 8, 0.6)',
                        'rgba(239, 68, 68, 0.6)',
                        'rgba(168, 85, 247, 0.6)',
                    ],
                    borderWidth: 1
                }]
            },
            options: { responsive: true }
        });
    }
});
