/**
 * TubeTale Analytics - Main JavaScript
 * Handles form submissions, API calls, and UI updates
 */

// Mode switching
function showMode(formId) {
    // Hide all forms
    document.querySelectorAll('.form-section').forEach(form => {
        form.classList.add('hidden');
    });

    // Show selected form
    document.getElementById(formId).classList.remove('hidden');

    // Scroll to form
    document.getElementById(formId).scrollIntoView({ behavior: 'smooth' });
}

// Battle input management
function addBattleInput() {
    const container = document.getElementById('battleInputs');
    const inputs = container.querySelectorAll('.battle-input');

    if (inputs.length >= 5) {
        alert('Maximum 5 channels allowed');
        return;
    }

    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.className = 'battle-input w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 mb-3 focus:outline-none focus:border-secondary transition';
    newInput.placeholder = `Channel ${inputs.length + 1}`;
    newInput.required = true;

    container.appendChild(newInput);
}

function removeBattleInput() {
    const container = document.getElementById('battleInputs');
    const inputs = container.querySelectorAll('.battle-input');

    if (inputs.length <= 2) {
        alert('Minimum 2 channels required');
        return;
    }

    container.removeChild(inputs[inputs.length - 1]);
}

// Show/hide loading
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Show error
function showError(message) {
    hideLoading();
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('error').classList.remove('hidden');
    document.getElementById('error').scrollIntoView({ behavior: 'smooth' });
}

// Reset analysis
function resetAnalysis() {
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    document.querySelectorAll('.form-section').forEach(form => {
        form.classList.add('hidden');
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Solo Analysis
async function analyzeSolo(event) {
    event.preventDefault();

    const channelName = document.getElementById('channelName').value.trim();

    if (!channelName) {
        showError('Please enter a channel name');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/analyze-channel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ channelName }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }

        const data = await response.json();
        displaySoloResults(data);
    } catch (error) {
        console.error('Solo Analysis Error:', error);
        showError(error.message);
    }
}

// Battle Analysis
async function analyzeBattle(event) {
    event.preventDefault();

    const inputs = document.querySelectorAll('.battle-input');
    const channelNames = Array.from(inputs)
        .map(input => input.value.trim())
        .filter(name => name);

    if (channelNames.length < 2) {
        showError('Please enter at least 2 channel names');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/run-battle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ channels: channelNames }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Battle failed');
        }

        const data = await response.json();
        displayBattleResults(data);
    } catch (error) {
        console.error('Battle Error:', error);
        showError(error.message);
    }
}

// Truth Analysis
async function analyzeTruth(event) {
    event.preventDefault();

    const videoUrl = document.getElementById('videoUrl').value.trim();

    if (!videoUrl) {
        showError('Please enter a video URL');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/analyze-truth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ videoInput: videoUrl }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }

        const data = await response.json();
        displayTruthResults(data);
    } catch (error) {
        console.error('Truth Analysis Error:', error);
        showError(error.message);
    }
}

// Display Solo Results
function displaySoloResults(data) {
    hideLoading();

    const resultsContent = document.getElementById('resultsContent');

    resultsContent.innerHTML = `
        <div class="space-y-8">
            <!-- Channel Header -->
            <div class="text-center pb-6 border-b border-white/10">
                <h3 class="text-4xl font-bold mb-2">${data.channelName}</h3>
                <p class="text-gray-400">${data.stats.country}</p>
            </div>
            
            <!-- Stats Grid -->
            <div class="grid md:grid-cols-3 gap-6">
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Subscribers</p>
                    <p class="text-3xl font-bold text-primary">${data.stats.subscribers}</p>
                </div>
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Total Videos</p>
                    <p class="text-3xl font-bold text-secondary">${data.stats.totalVideos}</p>
                </div>
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Shorts</p>
                    <p class="text-3xl font-bold text-purple-400">${data.stats.shortsCount}</p>
                </div>
            </div>
            
            <!-- Growth Chart -->
            <div class="bg-white/5 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-4">Growth Timeline</h4>
                <canvas id="growthChart"></canvas>
            </div>
            
            <!-- Topic Distribution -->
            <div class="bg-white/5 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-4">Topic Distribution</h4>
                <canvas id="topicChart"></canvas>
            </div>
            
            <!-- Biography -->
            <div class="bg-white/5 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-4">Channel Biography</h4>
                <div class="space-y-3 text-gray-300">
                    <p><strong>Summary:</strong> ${data.biography.summary}</p>
                    <p><strong>Origin:</strong> ${data.biography.origin}</p>
                    <p><strong>Evolution:</strong> ${data.biography.evolution}</p>
                </div>
            </div>
            
            <!-- Recommendation -->
            <div class="bg-gradient-to-r from-primary/20 to-secondary/20 rounded-lg p-6 border-2 border-primary/50">
                <h4 class="text-xl font-bold mb-3">Recommendation: ${data.recommendation.status}</h4>
                <p class="text-gray-300">${data.recommendation.reason}</p>
            </div>
            
            <!-- Sources -->
            ${data.sources && data.sources.length > 0 ? `
                <div class="bg-white/5 rounded-lg p-6">
                    <h4 class="text-xl font-bold mb-4">Sources</h4>
                    <div class="space-y-2">
                        ${data.sources.map(source => `
                            <a href="${source.uri}" target="_blank" class="block text-primary hover:text-secondary transition">
                                ${source.title}
                            </a>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    document.getElementById('results').classList.remove('hidden');
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    // Render charts
    renderGrowthChart(data.growthTimeline);
    renderTopicChart(data.topicAnalysis.topicDistribution);
}

// Display Battle Results
function displayBattleResults(data) {
    hideLoading();

    const resultsContent = document.getElementById('resultsContent');

    resultsContent.innerHTML = `
        <div class="space-y-8">
            <!-- Winner -->
            <div class="text-center pb-6 border-b border-white/10">
                <h3 class="text-4xl font-bold mb-4 text-yellow-400">🏆 Winner: ${data.verdict.winner}</h3>
                <p class="text-xl text-gray-300">${data.verdict.reasoning}</p>
            </div>
            
            <!-- Scores Comparison -->
            <div class="bg-white/5 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-4">Battle Scores</h4>
                <canvas id="battleChart"></canvas>
            </div>
            
            <!-- Detailed Scores -->
            <div class="grid md:grid-cols-${data.scores.length} gap-6">
                ${data.scores.map(score => `
                    <div class="bg-white/5 rounded-lg p-6 ${score.channelName === data.verdict.winner ? 'border-2 border-yellow-400' : ''}">
                        <h5 class="text-xl font-bold mb-4">${score.channelName}</h5>
                        <div class="space-y-2">
                            <div class="flex justify-between">
                                <span>Quality:</span>
                                <span class="font-bold">${score.quality}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Consistency:</span>
                                <span class="font-bold">${score.consistency}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Trust:</span>
                                <span class="font-bold">${score.trust}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Variety:</span>
                                <span class="font-bold">${score.variety}</span>
                            </div>
                            <div class="flex justify-between text-xl text-primary">
                                <span>Overall:</span>
                                <span class="font-bold">${score.overall}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Narrative -->
            <div class="bg-gradient-to-r from-primary/20 to-secondary/20 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-3">Battle Narrative</h4>
                <p class="text-gray-300">${data.verdict.narrative}</p>
            </div>
        </div>
    `;

    document.getElementById('results').classList.remove('hidden');
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    // Render battle chart
    renderBattleChart(data.scores);
}

// Display Truth Results
function displayTruthResults(data) {
    hideLoading();

    const resultsContent = document.getElementById('resultsContent');

    const scoreColor = data.truthScore >= 70 ? 'text-green-400' : data.truthScore >= 40 ? 'text-yellow-400' : 'text-red-400';

    resultsContent.innerHTML = `
        <div class="space-y-8">
            <!-- Video Header -->
            <div class="text-center pb-6 border-b border-white/10">
                <h3 class="text-3xl font-bold mb-2">${data.videoTitle}</h3>
                <p class="text-gray-400">by ${data.creatorName}</p>
            </div>
            
            <!-- Truth Score -->
            <div class="text-center">
                <div class="inline-block bg-white/5 rounded-full p-8">
                    <p class="text-gray-400 mb-2">Truth Score</p>
                    <p class="text-6xl font-bold ${scoreColor}">${data.truthScore}/100</p>
                </div>
            </div>
            
            <!-- Verdict -->
            <div class="bg-white/5 rounded-lg p-6">
                <h4 class="text-xl font-bold mb-3">Verdict</h4>
                <p class="text-gray-300">${data.summaryVerdict}</p>
            </div>
            
            <!-- Meta Info -->
            <div class="grid md:grid-cols-3 gap-6">
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Tone</p>
                    <p class="text-xl font-bold">${data.toneAnalysis}</p>
                </div>
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Faking Facts?</p>
                    <p class="text-xl font-bold ${data.isFakingFacts ? 'text-red-400' : 'text-green-400'}">
                        ${data.isFakingFacts ? 'Yes' : 'No'}
                    </p>
                </div>
                <div class="bg-white/5 rounded-lg p-6">
                    <p class="text-gray-400 mb-2">Language</p>
                    <p class="text-xl font-bold">${data.language}</p>
                </div>
            </div>
            
            <!-- Claims -->
            ${data.claims && data.claims.length > 0 ? `
                <div class="bg-white/5 rounded-lg p-6">
                    <h4 class="text-xl font-bold mb-4">Claims Analysis</h4>
                    <div class="space-y-4">
                        ${data.claims.map(claim => `
                            <div class="border-l-4 ${claim.status === 'Verified' ? 'border-green-400' :
            claim.status === 'False' ? 'border-red-400' :
                claim.status === 'Misleading' ? 'border-yellow-400' :
                    'border-gray-400'
        } pl-4">
                                <p class="font-bold mb-1">${claim.statement}</p>
                                <p class="text-sm text-gray-400 mb-1">Status: <span class="font-semibold">${claim.status}</span></p>
                                <p class="text-sm text-gray-300">${claim.evidence}</p>
                                ${claim.sourceUrl ? `
                                    <a href="${claim.sourceUrl}" target="_blank" class="text-sm text-primary hover:text-secondary">
                                        View Source →
                                    </a>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- References -->
            ${data.references && data.references.length > 0 ? `
                <div class="bg-white/5 rounded-lg p-6">
                    <h4 class="text-xl font-bold mb-4">References</h4>
                    <div class="space-y-2">
                        ${data.references.map(ref => `
                            <a href="${ref.uri}" target="_blank" class="block text-primary hover:text-secondary transition">
                                ${ref.title}
                            </a>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    document.getElementById('results').classList.remove('hidden');
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}
