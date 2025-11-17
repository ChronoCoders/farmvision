/**
 * Chart initialization for detection statistics
 * Extracted from inline scripts for CSP compliance
 */

(function() {
    'use strict';

    /**
     * Initialize the statistics chart
     * Data is passed via data attributes on the canvas element
     */
    function initChart() {
        var ctx = document.getElementById('line-chartjs-chart');
        if (!ctx) return;

        // Get data from data attributes
        var chartDataAttr = ctx.getAttribute('data-chart');
        var chartData = {};

        if (chartDataAttr) {
            try {
                chartData = JSON.parse(chartDataAttr);
            } catch (e) {
                console.error('Failed to parse chart data:', e);
            }
        }

        var labels = chartData.labels || ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024'];
        var values = chartData.values || [28, 28.5, 29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5];
        var label = chartData.label || 'Meyve Üretim Trendi';

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                        'rgba(255, 205, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(201, 203, 207, 0.2)'
                    ],
                    borderColor: [
                        'rgb(255, 99, 132)',
                        'rgb(255, 159, 64)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(54, 162, 235)',
                        'rgb(153, 102, 255)',
                        'rgb(201, 203, 207)'
                    ],
                    borderWidth: 1,
                    data: values
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChart);
    } else {
        initChart();
    }
})();
