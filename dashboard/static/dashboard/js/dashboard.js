document.addEventListener('DOMContentLoaded', function () {
    // Elementos do DOM
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const resetButton = document.getElementById('resetButton');

    // Adiciona os eventos de mudança dos filtros
    const filters = ['accountFilter', 'categoryFilter', 'subcategoryFilter', 'formaPagamentoFilter', 'yearFilter', 'monthFilter'];

    filters.forEach(filterId => {
        document.getElementById(filterId).addEventListener('change', updateAllCharts);
    });

    loadFilterOptions();

    function loadFilterOptions() {
        loadDropdownOptions('/dashboard/api/contas/', 'accountFilter');
        loadDropdownOptions('/dashboard/api/categorias/', 'categoryFilter');
        loadDropdownOptions('/dashboard/api/subcategorias/', 'subcategoryFilter');
        loadDropdownOptions('/dashboard/api/formas-pagamento/', 'formaPagamentoFilter');
    }

    function loadDropdownOptions(apiUrl, elementId) {
        const select = document.getElementById(elementId);
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const option = new Option(item.nome, item.id);  // Supõe que cada item tem 'nome' e 'id'
                    select.add(option);
                });
            })
            .catch(error => {
                console.error('Failed to load data from API:', apiUrl, error);
                select.add(new Option('Failed to load', ''));
            });
    }


    function updateAllCharts() {

        fetchAndRenderDespesasChart();
        fetchAndRenderContaChart();
        fetchAndRenderCategoriaChart();
        fetchAndRenderSubcategoriaChart();
        fetchAndRenderFormaPagamentoChart();
        updateTotalDespesas();
    }


    // Registro do plugin datalabels
    Chart.register(ChartDataLabels);

    // Carregar os gráficos ao carregar a página
    fetchAndRenderDespesasChart();
    fetchAndRenderContaChart();
    fetchAndRenderCategoriaChart();
    fetchAndRenderSubcategoriaChart();
    fetchAndRenderSubcategoriaChart();
    fetchAndRenderFormaPagamentoChart();


    // Reseta a página
    resetButton.addEventListener('click', function () {
        window.location.reload();
    });

    // Função para buscar e renderizar o gráfico de barras
    function fetchAndRenderDespesasChart() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;
        let url = '/dashboard/api/despesas/?';
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        if (account) url += `&account=${account}`;
        if (category) url += `&category=${category}`;
        if (subcategory) url += `&subcategory=${subcategory}`;
        if (formaPagamento) url += `&forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;


        fetch(url)
            .then(handleResponse)
            .then(data => updateChart(data))
            .catch(error => {
                console.error('Error:', error);
                alert('Error fetching data. Please try again.');
            });
    }

    // Função para tratar a resposta da requisição
    function handleResponse(response) {
        if (!response.ok) throw new Error('Failed to fetch');
        return response.json();
    }

    // Função para atualizar o gráfico de barras
    function updateChart(data) {
        const aggregatedData = aggregateData(data);
        renderChart(Object.keys(aggregatedData), Object.values(aggregatedData));
    }

    // Função para agregar os dados
    function aggregateData(data) {
        const aggregated = {};
        data.forEach(d => {
            const date = dayjs(d.data).format('DD/MM/YYYY');
            aggregated[date] = (aggregated[date] || 0) + parseFloat(d.valor);
        });
        return aggregated;
    }

    // Função para renderizar o gráfico de barras de despesas
    function renderChart(labels, values) {
        const ctx = document.getElementById('despesasChart').getContext('2d');
        if (window.despesasChart instanceof Chart) {
            window.despesasChart.destroy();
        }

        window.despesasChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total: ', // Mantenha isso vazio ou remova totalmente a propriedade label
                    data: values,
                    backgroundColor: 'rgba(243,8,8,0.33)',
                    borderColor: 'rgba(170,65,118,0.78)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: false  // Isso remove as linhas de grade do eixo Y
                        }
                    },
                    x: {
                        grid: {
                            display: false  // Isso remove as linhas de grade do eixo X
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false // Não exibir a legenda
                    },
                    datalabels: {
                        color: '#000000',
                        anchor: 'end',
                        align: 'top',
                        formatter: function (value, context) {
                            return new Intl.NumberFormat('pt-BR', {style: 'currency', currency: 'BRL'}).format(value);
                        }
                    },

                },
                tooltips: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (tooltipItem, data) {
                            let label = data.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += `${new Intl.NumberFormat('pt-BR', {
                                style: 'currency',
                                currency: 'BRL'
                            }).format(tooltipItem.yLabel)}`;
                            return label;
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutBounce',
                    onComplete: function () {
                        console.log('Animação completada!');
                    }
                }
            }
        });
    }

    // Função para buscar e renderizar o gráfico de pizza
    function fetchAndRenderContaChart() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;
        let url = '/dashboard/api/despesas-por-conta/?';
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        if (account) url += `&account=${account}`;
        if (category) url += `&category=${category}`;
        if (subcategory) url += `&subcategory=${subcategory}`;
        if (formaPagamento) url += `&forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('despesasPieChart').getContext('2d');
                if (window.pieChart instanceof Chart) {
                    window.pieChart.destroy();
                }
                window.pieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.map(item => item.conta),
                        datasets: [{
                            label: 'Total: ',
                            data: data.map(item => item.total),
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(255, 206, 86, 0.5)',
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(153, 102, 255, 0.5)',
                                'rgba(255, 159, 64, 0.5)'
                            ],
                            borderColor: [
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 206, 86, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: {
                            animateScale: true,
                            animateRotate: true
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            datalabels: {
                                color: '#000000',
                                anchor: 'end',
                                align: 'top',
                                formatter: function (value, context) {
                                    return new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(value);
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching data for pie chart:', error);
            });
    }


    // Função para gerar uma cor aleatória
    function generateRandomColor() {
        let r = Math.floor(Math.random() * 256);
        let g = Math.floor(Math.random() * 256);
        let b = Math.floor(Math.random() * 256);
        return `rgba(${r}, ${g}, ${b}, 0.5)`;
    }

    // Função para gerar um array de cores aleatórias
    function getColorsArray(length) {
        let colors = [];
        for (let i = 0; i < length; i++) {
            colors.push(generateRandomColor());
        }
        return colors;
    }

    // Função para buscar e renderizar o gráfico de pizza por categoria
    function fetchAndRenderCategoriaChart() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;
        let url = '/dashboard/api/despesas-por-categoria/?';
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        if (account) url += `&account=${account}`;
        if (category) url += `&category=${category}`;
        if (subcategory) url += `&subcategory=${subcategory}`;
        if (formaPagamento) url += `&forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('categoriaChart').getContext('2d');
                const colors = getColorsArray(data.length);
                if (window.categoriaChart instanceof Chart) {
                    window.categoriaChart.destroy();
                }
                window.categoriaChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data.map(item => item.categoria),
                        datasets: [{
                            label: 'Total: ',
                            data: data.map(item => item.total),
                            backgroundColor: colors,
                            borderColor: colors.map(color => color.replace('0.5', '1')),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: {
                            animateRotate: true, // Faz com que o gráfico gire levemente ao inicializar
                            animateScale: true  // Faz com que o gráfico escale de dentro para fora
                        },
                        plugins: {
                            legend: {
                                position: 'bottom', // Posição da legenda no lado direito
                            },
                            datalabels: {
                                color: '#000000',
                                anchor: 'end',
                                align: 'top',
                                formatter: function (value, context) {
                                    return new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(value); // Formatação dos valores como moeda
                                }
                            }
                        }
                    }
                });
            })

            .catch(error => {
                console.error('Error fetching data for pie chart:', error);
            });
    }

    // Função para buscar e renderizar o gráfico de barras por subcategoria
    function fetchAndRenderSubcategoriaChart() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;
        let url = '/dashboard/api/despesas-por-subcategoria/?';
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        if (account) url += `&account=${account}`;
        if (category) url += `&category=${category}`;
        if (subcategory) url += `&subcategory=${subcategory}`;
        if (formaPagamento) url += `&forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('subcategoriaChart').getContext('2d');
                const colors = getColorsArray(data.length);
                if (window.subcategoriaChart instanceof Chart) {
                    window.subcategoriaChart.destroy();
                }
                window.subcategoriaChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: data.map(item => item.subcategoria),
                        datasets: [{
                            label: 'Total: ',
                            data: data.map(item => item.total),
                            backgroundColor: colors,
                            borderColor: colors.map(color => color.replace('0.5', '1')),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: {
                            animateRotate: true, // Faz com que o gráfico gire levemente ao inicializar
                            animateScale: true  // Faz com que o gráfico escale de dentro para fora
                        },
                        plugins: {
                            legend: {
                                position: 'right', // Posição da legenda no lado direito
                            },
                            datalabels: {
                                color: '#000000',
                                anchor: 'end',
                                align: 'top',
                                formatter: function (value, context) {
                                    return new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(value); // Formatação dos valores como moeda
                                }
                            }
                        }
                    }
                });

            })
            .catch(error => {
                console.error('Error fetching data for pie chart:', error);
            });
    }

    // Função para buscar e renderizar o gráfico de pizza por forma de pagamento
    function fetchAndRenderFormaPagamentoChart() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;
        let url = '/dashboard/api/despesas-por-forma-pagamento/?';
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        if (account) url += `&account=${account}`;
        if (category) url += `&category=${category}`;
        if (subcategory) url += `&subcategory=${subcategory}`;
        if (formaPagamento) url += `&forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('formaPagamentoChart').getContext('2d');
                if (window.formaPagamentoChart instanceof Chart) {
                    window.formaPagamentoChart.destroy();
                }
                window.formaPagamentoChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.map(item => item.forma_pagamento),
                        datasets: [{
                            label: 'Total: ',
                            data: data.map(item => item.total),
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(255, 206, 86, 0.5)',
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(153, 102, 255, 0.5)',
                                'rgba(255, 159, 64, 0.5)'
                            ],
                            borderColor: [
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 206, 86, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: {
                            animateScale: true,
                            animateRotate: true
                        },
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            datalabels: {
                                color: '#000000',
                                anchor: 'end',
                                align: 'top',
                                formatter: function (value, context) {
                                    return new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(value);
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching data for pie chart:', error);
            });
    }

    // Função para atualizar o total de despesas
    function updateTotalDespesas() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const account = document.getElementById('accountFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const subcategory = document.getElementById('subcategoryFilter').value;
        const formaPagamento = document.getElementById('formaPagamentoFilter').value;
        const year = document.getElementById('yearFilter').value;
        const month = document.getElementById('monthFilter').value;

        let url = `/dashboard/api/atualiza-total/?`;
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}&`;
        if (account) url += `account=${account}&`;
        if (category) url += `category=${category}&`;
        if (subcategory) url += `subcategory=${subcategory}&`;
        if (formaPagamento) url += `forma_pagamento=${formaPagamento}`;
        if (year) url += `&year=${year}`;
        if (month) url += `&month=${month}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalDisplay').textContent = data.total_despesas;
            })
            .catch(error => console.error('Error fetching total:', error));
    }

    // Adiciona os eventos de mudança de data
    startDateInput.addEventListener('change', function () {
        fetchAndRenderDespesasChart();
        fetchAndRenderContaChart();
        fetchAndRenderCategoriaChart();
        fetchAndRenderSubcategoriaChart();
        fetchAndRenderFormaPagamentoChart();
        updateTotalDespesas()

    });

    // Adiciona os eventos de mudança de data
    endDateInput.addEventListener('change', function () {
        fetchAndRenderDespesasChart();
        fetchAndRenderContaChart();
        fetchAndRenderCategoriaChart();
        fetchAndRenderSubcategoriaChart();
        fetchAndRenderFormaPagamentoChart();
        updateTotalDespesas()

    });


});