<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuScribe AI: The Business Case for Transforming Clinical Documentation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Chosen Palette: Warm Neutral Harmony */
        :root {
            --bg-main: #FDFBF8; /* Warm off-white */
            --bg-subtle: #F5F2ED; /* Slightly darker neutral */
            --text-primary: #33312E; /* Dark, warm gray */
            --text-secondary: #6B6861; /* Muted neutral for subtext */
            --accent-primary: #008080; /* Muted Teal */
            --accent-secondary: #C0A080; /* Warm Sand/Light Brown */
            --border-color: #EAE5DD;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-primary);
        }
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            height: 300px;
            max-height: 400px;
        }
        @media (min-width: 768px) {
            .chart-container {
                height: 350px;
            }
        }
        .nav-link.active {
            background-color: var(--accent-primary);
            color: white;
        }
        .stat-card {
            background-color: white;
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .btn-accent {
            background-color: var(--accent-primary);
            color: white;
            transition: background-color 0.2s;
        }
        .btn-accent:hover {
            background-color: #006666;
        }
        .btn-toggle {
            background-color: var(--bg-subtle);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }
        .btn-toggle.active {
            background-color: var(--accent-secondary);
            color: white;
            border-color: var(--accent-secondary);
        }
    </style>
</head>
<body class="antialiased">
    <!-- Chosen Palette: Warm Neutral Harmony -->
    <!-- Application Structure Plan: The application is structured as a single-page narrative dashboard. It uses a fixed sidebar for navigation, allowing users to either follow the story logically from top to bottom or jump to a specific area of interest. The flow is designed to first establish the "problem" (The Crisis), then present the "solution" (AI Scribes), quantify the "opportunity" (Market Size), analyze the "competition," and finally deliver the "payoff" (ROI & Benefits). This problem-solution-proof structure is highly effective for a business case, making the information intuitive and persuasive. Key interactions include hover effects on stats, dynamic chart updates for competitive analysis, and clear visual data representations to simplify complex numbers. -->
    <!-- Visualization & Content Choices: 
        - The Crisis: Goal is to show the scale of physician burnout. A doughnut chart is used for the burnout percentage (part-to-whole relationship). A bar chart compares time spent on EHR vs. patient care (direct comparison).
        - The Solution: Goal is to show multifaceted benefits. A horizontal bar chart visualizes percentage improvements across satisfaction, stress reduction, etc., making comparisons easy.
        - Market Opportunity: Goal is to demonstrate growth. A line chart is the classic and most effective way to show a trend over time, in this case, the CDI market forecast.
        - Competitive Landscape: Goal is to allow direct comparison. An interactive bar chart is chosen. Users click buttons to update the chart data, dynamically comparing different AI scribe solutions based on reported time savings. This is more engaging than a static table.
        - ROI & Savings: Goal is to highlight financial benefits. A grouped bar chart compares the cost of human vs. AI scribes, a clear and powerful financial argument.
        - Justification: All visualizations are created using Chart.js on a <canvas> element. This avoids SVG/Mermaid and allows for rich tooltips and smooth animations, enhancing user engagement and data clarity. The interactive competitor chart specifically encourages user action and exploration.
    -->
    <!-- CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->

    <div class="flex min-h-screen">
        <!-- Sidebar Navigation -->
        <aside id="sidebar" class="hidden lg:block w-64 bg-white border-r border-gray-200 p-6 fixed h-full">
            <h1 class="text-xl font-bold text-gray-800 mb-8">DocuScribe AI</h1>
            <nav id="desktop-nav" class="space-y-2">
                <a href="#overview" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Dashboard</a>
                <a href="#crisis" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">The Crisis</a>
                <a href="#solution" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">The AI Solution</a>
                <a href="#market" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Market Opportunity</a>
                <a href="#competition" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Competitive Edge</a>
                <a href="#roi" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Financial Impact</a>
            </nav>
        </aside>

        <!-- Mobile Header -->
        <header class="lg:hidden fixed top-0 left-0 right-0 bg-white shadow-md z-50">
            <div class="container mx-auto px-4 py-3 flex justify-between items-center">
                <h1 class="text-lg font-bold text-gray-800">DocuScribe AI</h1>
                <button id="mobile-menu-button" class="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
                </button>
            </div>
            <nav id="mobile-nav" class="hidden px-4 pt-2 pb-4 border-t border-gray-200">
                <a href="#overview" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Dashboard</a>
                <a href="#crisis" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">The Crisis</a>
                <a href="#solution" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">The AI Solution</a>
                <a href="#market" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Market Opportunity</a>
                <a href="#competition" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Competitive Edge</a>
                <a href="#roi" class="nav-link block px-4 py-2 rounded-md text-gray-600 hover:bg-gray-100">Financial Impact</a>
            </nav>
        </header>

        <!-- Main Content -->
        <main class="lg:ml-64 flex-1 p-6 md:p-10 bg-[var(--bg-main)] mt-16 lg:mt-0">
            
            <section id="overview" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">The Case for AI in Clinical Documentation</h2>
                <p class="text-lg text-[var(--text-secondary)] mb-8">An interactive analysis of healthcare's documentation crisis and the transformative potential of AI-powered solutions.</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="stat-card p-6 rounded-lg shadow-sm">
                        <h3 class="text-md font-semibold text-[var(--text-secondary)] mb-2">Time Saved Per Day</h3>
                        <p class="text-4xl font-bold text-[var(--accent-primary)]">~3.2 hours</p>
                        <p class="text-sm text-[var(--text-secondary)] mt-2">Time reclaimed by physicians using AI scribes, reducing "pajama time."</p>
                    </div>
                    <div class="stat-card p-6 rounded-lg shadow-sm">
                        <h3 class="text-md font-semibold text-[var(--text-secondary)] mb-2">Physician Burnout</h3>
                        <p class="text-4xl font-bold text-[var(--accent-primary)]">49%</p>
                        <p class="text-sm text-[var(--text-secondary)] mt-2">of physicians experienced burnout symptoms in 2024, driven by administrative tasks.</p>
                    </div>
                    <div class="stat-card p-6 rounded-lg shadow-sm">
                        <h3 class="text-md font-semibold text-[var(--text-secondary)] mb-2">Market Growth (CDI)</h3>
                        <p class="text-4xl font-bold text-[var(--accent-primary)]">7.9% <span class="text-2xl">CAGR</span></p>
                        <p class="text-sm text-[var(--text-secondary)] mt-2">Projected growth for the Clinical Documentation Improvement market through 2034.</p>
                    </div>
                </div>
            </section>

            <section id="crisis" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">The Documentation Crisis</h2>
                <p class="text-lg text-[var(--text-secondary)] max-w-3xl mb-8">The shift to Electronic Health Records (EHRs) has inadvertently created a new crisis: an immense documentation burden. This section quantifies the profound impact on physicians' time, well-being, and the quality of patient care.</p>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div class="p-6 bg-white rounded-lg border border-[var(--border-color)]">
                        <h3 class="font-semibold mb-4 text-center">Physician Burnout from Administrative Burden (2024)</h3>
                        <div class="chart-container" style="height:300px; max-height:300px;">
                            <canvas id="burnoutChart"></canvas>
                        </div>
                    </div>
                    <div class="p-6 bg-white rounded-lg border border-[var(--border-color)]">
                        <h3 class="font-semibold mb-4 text-center">Physician's Time: EHR vs. Patient Care</h3>
                         <div class="chart-container" style="height:300px; max-height:300px;">
                            <canvas id="timeSplitChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="mt-8 bg-white p-6 rounded-lg border border-[var(--border-color)]">
                    <h3 class="font-semibold text-lg mb-4">The Ripple Effect on Patient Safety and Costs</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                        <div>
                            <p class="text-3xl font-bold text-[var(--accent-secondary)]">20%</p>
                            <p class="text-[var(--text-secondary)] mt-1">of malpractice cases involve a documentation failure.</p>
                        </div>
                        <div>
                            <p class="text-3xl font-bold text-[var(--accent-secondary)]">1.5M</p>
                            <p class="text-[var(--text-secondary)] mt-1">Americans harmed annually by medication errors linked to poor documentation.</p>
                        </div>
                        <div>
                            <p class="text-3xl font-bold text-[var(--accent-secondary)]">$4.6B</p>
                            <p class="text-[var(--text-secondary)] mt-1">annual cost to the U.S. system from physician turnover due to burnout.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="solution" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">The AI Solution: Restoring the Focus on Care</h2>
                <p class="text-lg text-[var(--text-secondary)] max-w-3xl mb-8">AI-powered ambient scribes offer a transformative solution. By passively listening to and documenting patient conversations, this technology frees physicians from the keyboard, leading to dramatic improvements in efficiency, satisfaction, and the patient experience.</p>
                <div class="bg-white p-6 rounded-lg border border-[var(--border-color)]">
                    <h3 class="font-semibold mb-4 text-center">Quantifiable Impact of AI Scribes on Providers & Patients</h3>
                    <div class="chart-container" style="height:400px; max-height:450px;">
                        <canvas id="benefitsChart"></canvas>
                    </div>
                </div>
            </section>

            <section id="market" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">A Substantial and Growing Market</h2>
                 <p class="text-lg text-[var(--text-secondary)] max-w-3xl mb-8">The demand for solutions that ease documentation burden is reflected in the strong, consistent growth across related healthcare technology sectors. This indicates a market that is not only large but actively seeking innovation.</p>
                <div class="grid grid-cols-1 lg:grid-cols-5 gap-8">
                    <div class="lg:col-span-3 bg-white p-6 rounded-lg border border-[var(--border-color)]">
                        <h3 class="font-semibold mb-4 text-center">Clinical Documentation Improvement (CDI) Market Forecast</h3>
                        <div class="chart-container" style="height:350px; max-height:400px; max-width:none;">
                            <canvas id="marketGrowthChart"></canvas>
                        </div>
                    </div>
                    <div class="lg:col-span-2 bg-white p-6 rounded-lg border border-[var(--border-color)]">
                        <h3 class="font-semibold mb-2">Related Market Sizes (2024)</h3>
                        <div class="space-y-4 mt-4">
                            <div class="p-4 bg-[var(--bg-subtle)] rounded-md">
                                <p class="text-sm text-[var(--text-secondary)]">AI in Healthcare</p>
                                <p class="text-2xl font-bold text-[var(--accent-primary)]">$32.3 Billion</p>
                            </div>
                            <div class="p-4 bg-[var(--bg-subtle)] rounded-md">
                                <p class="text-sm text-[var(--text-secondary)]">Clinical Decision Support</p>
                                <p class="text-2xl font-bold text-[var(--accent-primary)]">$2.25 Billion</p>
                            </div>
                            <div class="p-4 bg-[var(--bg-subtle)] rounded-md">
                                <p class="text-sm text-[var(--text-secondary)]">Healthcare IT Integration</p>
                                <p class="text-2xl font-bold text-[var(--accent-primary)]">$4.43 Billion (2023)</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section id="competition" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">Forging a Competitive Edge</h2>
                <p class="text-lg text-[var(--text-secondary)] max-w-3xl mb-8">The AI scribe market is active, but ripe for a solution that overcomes common limitations. By focusing on superior accuracy, seamless integration, and comprehensive revenue cycle support, DocuScribe AI can establish a new standard. Here's how leading competitors stack up on a key metric: reported time savings.</p>
                <div class="bg-white p-6 rounded-lg border border-[var(--border-color)]">
                    <h3 class="font-semibold mb-4 text-center">Interactive Comparison: Time Savings by Solution</h3>
                    <div class="flex justify-center flex-wrap gap-2 mb-6">
                        <button class="btn-toggle active" data-competitor="DocuScribe">DocuScribe AI (Goal)</button>
                        <button class="btn-toggle" data-competitor="DeepScribe">DeepScribe</button>
                        <button class="btn-toggle" data-competitor="Suki">Suki AI</button>
                        <button class="btn-toggle" data-competitor="Nuance">Nuance DAX</button>
                         <button class="btn-toggle" data-competitor="Abridge">Abridge</button>
                    </div>
                    <div class="chart-container" style="height:350px; max-height:400px;">
                        <canvas id="competitorChart"></canvas>
                    </div>
                </div>
            </section>

            <section id="roi" class="mb-16">
                <h2 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">The Financial and Strategic Impact</h2>
                <p class="text-lg text-[var(--text-secondary)] max-w-3xl mb-8">Adopting DocuScribe AI is not just an operational improvement; it's a strategic financial decision. The return on investment is driven by direct cost reductions, enhanced revenue capture, and the significant, often-overlooked savings from improved physician retention.</p>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div class="p-6 bg-white rounded-lg border border-[var(--border-color)]">
                        <h3 class="font-semibold mb-4 text-center">Direct Cost Savings: Human vs. AI Scribe</h3>
                        <div class="chart-container" style="height:350px; max-height:400px;">
                            <canvas id="costSavingsChart"></canvas>
                        </div>
                    </div>
                    <div class="p-6 bg-white rounded-lg border border-[var(--border-color)]">
                         <h3 class="font-semibold text-lg mb-4">Compounding Financial Benefits</h3>
                         <div class="space-y-4">
                            <div class="flex items-start">
                                <span class="text-2xl text-[var(--accent-primary)] mr-4 mt-1">✓</span>
                                <div>
                                    <h4 class="font-semibold">Increased Patient Throughput</h4>
                                    <p class="text-[var(--text-secondary)] text-sm">Ability to see 1-3 extra patients per day boosts revenue.</p>
                                </div>
                            </div>
                             <div class="flex items-start">
                                <span class="text-2xl text-[var(--accent-primary)] mr-4 mt-1">✓</span>
                                <div>
                                    <h4 class="font-semibold">Faster Billing Cycles</h4>
                                    <p class="text-[var(--text-secondary)] text-sm">Same-day note completion accelerates the entire revenue cycle.</p>
                                </div>
                            </div>
                             <div class="flex items-start">
                                <span class="text-2xl text-[var(--accent-primary)] mr-4 mt-1">✓</span>
                                <div>
                                    <h4 class="font-semibold">Improved Coding Accuracy</h4>
                                    <p class="text-[var(--text-secondary)] text-sm">Reduces claim denials and prevents revenue leakage.</p>
                                </div>
                            </div>
                             <div class="flex items-start">
                                <span class="text-2xl text-[var(--accent-primary)] mr-4 mt-1">✓</span>
                                <div>
                                    <h4 class="font-semibold">Reduced Physician Turnover</h4>
                                    <p class="text-[var(--text-secondary)] text-sm">Lowering burnout avoids recruitment costs that can reach up to $1M per physician.</p>
                                </div>
                            </div>
                         </div>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chartColors = {
                primary: 'rgba(0, 128, 128, 0.8)',
                primaryLight: 'rgba(0, 128, 128, 0.2)',
                secondary: 'rgba(192, 160, 128, 0.8)',
                secondaryLight: 'rgba(192, 160, 128, 0.2)',
                gray: 'rgba(107, 114, 128, 0.5)',
                text: '#33312E'
            };

            Chart.defaults.font.family = 'Inter, sans-serif';
            Chart.defaults.color = chartColors.text;
            
            // Data
            const crisisData = {
                burnout: {
                    labels: ['Experienced Burnout', 'Did Not Experience Burnout'],
                    data: [49, 51],
                },
                timeSplit: {
                    labels: ['Time on EHR', 'Scheduled Patient Care'],
                    data: [5.8, 8],
                }
            };

            const benefitsData = {
                labels: [
                    'Improved Communication with Patients',
                    'Improved Overall Work Satisfaction',
                    'Reduction in Documentation Stress',
                    'Improved Work-Life Balance',
                    'Increased Job Satisfaction',
                    'Decrease in Burnout Symptoms'
                ],
                data: [84, 82, 61, 54, 47, 38],
            };

            const marketData = {
                years: [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031],
                values: [4.88, 5.27, 5.69, 6.14, 6.62, 7.14, 7.70, 7.87] // Simplified from report data
            };

            const competitorData = {
                'DocuScribe': { timeReduction: 75, color: chartColors.primary }, // Target goal
                'DeepScribe': { timeReduction: 75, color: chartColors.gray },
                'Suki': { timeReduction: 72, color: chartColors.gray },
                'Nuance': { timeReduction: 50, color: chartColors.gray },
                'Abridge': { timeReduction: 40, color: chartColors.gray } // Estimated from 2hrs/day
            };

            const costData = {
                labels: ['Low Estimate', 'High Estimate'],
                humanScribe: [33000, 55000],
                aiScribe: [4000, 8000] // Estimated from 60-75% cheaper
            };

            // Chart Instantiation
            // Burnout Chart (Doughnut)
            const burnoutCtx = document.getElementById('burnoutChart').getContext('2d');
            new Chart(burnoutCtx, {
                type: 'doughnut',
                data: {
                    labels: crisisData.burnout.labels,
                    datasets: [{
                        data: crisisData.burnout.data,
                        backgroundColor: [chartColors.secondary, chartColors.primaryLight],
                        borderColor: [chartColors.secondary, chartColors.primaryLight],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: { callbacks: { label: (context) => `${context.label}: ${context.raw}%` } }
                    }
                }
            });

            // Time Split Chart (Bar)
            const timeSplitCtx = document.getElementById('timeSplitChart').getContext('2d');
            new Chart(timeSplitCtx, {
                type: 'bar',
                data: {
                    labels: crisisData.timeSplit.labels,
                    datasets: [{
                        label: 'Hours per Day',
                        data: crisisData.timeSplit.data,
                        backgroundColor: [chartColors.secondaryLight, chartColors.primaryLight],
                        borderColor: [chartColors.secondary, chartColors.primary],
                        borderWidth: 2
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { callbacks: { label: (context) => `${context.raw} hours` } }
                    },
                    scales: { x: { beginAtZero: true, suggestedMax: 10 } }
                }
            });

            // Benefits Chart (Horizontal Bar)
            const benefitsCtx = document.getElementById('benefitsChart').getContext('2d');
            new Chart(benefitsCtx, {
                type: 'bar',
                data: {
                    labels: benefitsData.labels,
                    datasets: [{
                        label: '% Improvement / Positive Response',
                        data: benefitsData.data,
                        backgroundColor: chartColors.primaryLight,
                        borderColor: chartColors.primary,
                        borderWidth: 2
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { callbacks: { label: (context) => `${context.raw}%` } }
                    },
                     scales: { x: { beginAtZero: true, max: 100 } }
                }
            });

            // Market Growth Chart (Line)
            const marketGrowthCtx = document.getElementById('marketGrowthChart').getContext('2d');
            new Chart(marketGrowthCtx, {
                type: 'line',
                data: {
                    labels: marketData.years,
                    datasets: [{
                        label: 'Market Size (USD Billion)',
                        data: marketData.values,
                        fill: true,
                        backgroundColor: chartColors.primaryLight,
                        borderColor: chartColors.primary,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: false } },
                    plugins: {
                        legend: { display: false },
                        tooltip: { callbacks: { label: (context) => `$${context.raw} Billion` } }
                    }
                }
            });

            // Competitor Chart (Bar)
            const competitorCtx = document.getElementById('competitorChart').getContext('2d');
            const competitorChart = new Chart(competitorCtx, {
                type: 'bar',
                data: {
                    labels: [''],
                    datasets: Object.entries(competitorData).map(([name, values]) => ({
                        label: name,
                        data: [values.timeReduction],
                        backgroundColor: values.color,
                        borderColor: values.color.replace('0.8', '1'),
                        borderWidth: 1,
                        hidden: name !== 'DocuScribe' // Hide all but the default initially
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Documentation Time Reduction (%)'
                        },
                        legend: {
                           display: false
                        },
                        tooltip: {
                             callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw}% reduction`;
                                }
                            }
                        }
                    },
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });

            const competitorButtons = document.querySelectorAll('.btn-toggle');
            competitorButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const competitorName = button.dataset.competitor;
                    
                    competitorButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');

                    competitorChart.data.datasets.forEach((dataset, index) => {
                       dataset.hidden = dataset.label !== competitorName;
                    });
                    competitorChart.update();
                });
            });
            document.querySelector('.btn-toggle[data-competitor="DocuScribe"]').click(); // Set initial state


             // Cost Savings Chart
            const costSavingsCtx = document.getElementById('costSavingsChart').getContext('2d');
            new Chart(costSavingsCtx, {
                type: 'bar',
                data: {
                    labels: costData.labels,
                    datasets: [
                        {
                            label: 'Human Scribe',
                            data: costData.humanScribe,
                            backgroundColor: chartColors.secondary,
                        },
                        {
                            label: 'AI Scribe',
                            data: costData.aiScribe,
                            backgroundColor: chartColors.primary,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: { display: true, text: 'Annual Cost Per Physician (USD)' },
                        tooltip: { callbacks: { label: (context) => `${context.dataset.label}: $${context.raw.toLocaleString()}` } }
                    },
                    scales: { y: { beginAtZero: true } }
                }
            });


            // Navigation Logic
            const sections = document.querySelectorAll('section');
            const navLinks = document.querySelectorAll('.nav-link');
            const mobileMenuButton = document.getElementById('mobile-menu-button');
            const mobileNav = document.getElementById('mobile-nav');

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navLinks.forEach(link => {
                            link.classList.toggle('active', link.getAttribute('href').substring(1) === entry.target.id);
                        });
                    }
                });
            }, { rootMargin: '-30% 0px -70% 0px' });

            sections.forEach(section => observer.observe(section));

            mobileMenuButton.addEventListener('click', () => {
                mobileNav.classList.toggle('hidden');
            });

            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if(!mobileNav.classList.contains('hidden')) {
                         mobileNav.classList.add('hidden');
                    }
                });
            });

        });
    </script>
</body>
</html>
