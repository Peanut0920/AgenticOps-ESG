/**
 * AgenticOps-ESG Frontend Script – Dark Theme & Structured Reports
 */

const API_BASE = 'http://localhost:8000';
let telemetryChart = null;
let refreshInterval = null;

// ============================================================
// DOM Ready
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('current-date').innerText =
        new Date().toLocaleString('en-MY', { timeZone: 'Asia/Kuala_Lumpur' });

    // Tab switching
    document.querySelectorAll('.tab-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = link.dataset.tab;
            document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active-tab'));
            link.classList.add('active-tab');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
            const target = document.getElementById(`tab-${tab}`);
            if (target) target.classList.remove('hidden');
            document.getElementById('page-title').innerText =
                tab.charAt(0).toUpperCase() + tab.slice(1);
            if (tab === 'telemetry' && !telemetryChart) initChart();
            if (tab === 'compliance') renderStructuredReport();
        });
    });

    refreshData();
    refreshInterval = setInterval(refreshData, 15000);
});

// ============================================================
// Data Fetch & Rendering
// ============================================================
async function refreshData() {
    try {
        // 1. Stats
        const stats = await (await fetch(`${API_BASE}/api/dashboard/stats`)).json();
        document.getElementById('kpi-carbon').innerText = stats.total_carbon_kg || '0';
        document.getElementById('kpi-pending').innerText = stats.pending_actions || '0';
        document.getElementById('kpi-pue').innerText = stats.current_pue || '--';
        document.getElementById('kpi-violations').innerText = stats.compliance_violations || '0';
        document.getElementById('pending-badge').innerText = stats.pending_actions || '0';

        // 2. Telemetry
        const tele = await (await fetch(`${API_BASE}/api/telemetry/latest`)).json();
        if (telemetryChart) {
            telemetryChart.data.labels = tele.timestamps || [];
            telemetryChart.data.datasets[0].data = tele.power_watts || [];
            telemetryChart.data.datasets[1].data = tele.cpu_pct || [];
            telemetryChart.update();
        }

        // 3. Actions
        const actions = await (await fetch(`${API_BASE}/api/actions/pending`)).json();
        renderActions(actions);

        // 4. Audit
        const audit = await (await fetch(`${API_BASE}/api/audit/log?limit=20`)).json();
        renderAudit(audit);

        // 5. Structured Report (only if compliance tab is visible)
        if (!document.getElementById('tab-compliance').classList.contains('hidden')) {
            renderStructuredReport();
        }

        document.getElementById('dashboard-message').innerHTML = `
            <i class="fas fa-check-circle text-green-400 mr-2"></i>
            Updated: ${new Date().toLocaleTimeString()}. ${actions.length} action(s) pending.
        `;
    } catch (err) {
        console.error(err);
        document.getElementById('dashboard-message').innerHTML = `
            <i class="fas fa-exclamation-triangle text-red-400 mr-2"></i>
            Error connecting to backend.
        `;
    }
}

// ============================================================
// Actions Rendering (dark theme)
// ============================================================
function renderActions(actions) {
    const container = document.getElementById('action-list');
    if (!actions || actions.length === 0) {
        container.innerHTML = `<div class="text-gray-400 text-sm p-4 border border-dashed border-gray-700 rounded-lg text-center">✅ All clear. No pending actions.</div>`;
        return;
    }
    let html = '';
    actions.forEach(a => {
        let desc = '';
        if (a.action === 'resize') desc = `Resize ${a.vm_id} to ${a.new_cpu_limits} CPU / ${a.new_ram_gb} RAM`;
        else if (a.action === 'full_refresh') desc = `🔄 Full refresh ${a.host_id} (crossover: ${a.crossover_quarter})`;
        else if (a.action === 'partial_repair') desc = `🔧 Partial repair ${a.host_id} – ${a.recommendation || ''}`;
        else desc = `${a.action} on ${a.vm_id || a.host_id || 'unknown'}`;

        const carbon = a.carbon_saving_kg ? `${a.carbon_saving_kg} kg CO2e` : '';
        const utility = a.utility_score ? `Utility: ${a.utility_score}` : '';

        html += `
            <div class="action-item flex flex-wrap items-center justify-between gap-3">
                <div class="flex-1 min-w-[200px]">
                    <span class="status-badge status-pending">PENDING</span>
                    <span class="font-medium text-sm text-white ml-2">${desc}</span>
                    <div class="text-xs text-gray-400 mt-1">
                        ${carbon} ${utility ? '| ' + utility : ''}
                        ${a.risk_score ? `| Risk: ${a.risk_score}%` : ''}
                    </div>
                </div>
                <div class="flex gap-2">
                    <button onclick="handleApproval(${a.index}, true)" class="btn-approve"><i class="fas fa-check"></i> Approve</button>
                    <button onclick="handleApproval(${a.index}, false)" class="btn-reject"><i class="fas fa-times"></i> Reject</button>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// ============================================================
// Structured Report Rendering
// ============================================================
async function renderStructuredReport() {
    const container = document.getElementById('structured-report');
    try {
        const resp = await fetch(`${API_BASE}/api/report/structured`);
        const data = await resp.json();
        if (!data.sections || data.sections.length === 0) {
            container.innerHTML = `<div class="text-gray-400 text-center py-8">No report data available yet. Run a workflow cycle.</div>`;
            return;
        }

        let html = '';
        data.sections.forEach(section => {
            const iconColor = section.color === 'yellow' ? 'icon-yellow' :
                              section.color === 'red' ? 'icon-red' : 'icon-white';
            html += `
                <div class="report-section slide-up">
                    <div class="report-section-header">
                        <i class="fas ${section.icon} ${iconColor} text-xl"></i>
                        <h3>${section.title}</h3>
                    </div>
                    <div class="report-fields">
                        ${section.fields.map(f => {
                            const valueClass = f.value?.toString().toLowerCase().includes('risk') ? 'highlight-red' :
                                               f.value?.toString().toLowerCase().includes('gold') ? 'highlight-yellow' : '';
                            return `
                                <div class="report-field">
                                    <span class="report-field-label">${f.label}</span>
                                    <span class="report-field-value ${valueClass}">${f.value ?? 'N/A'}</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        });

        // Audit provenance at bottom
        if (data.audit_provenance && data.audit_provenance.length > 0) {
            html += `
                <div class="report-section">
                    <div class="report-section-header">
                        <i class="fas fa-fingerprint icon-white text-xl"></i>
                        <h3>Audit Provenance (Last 5 events)</h3>
                    </div>
                    <div class="text-xs text-gray-400 space-y-1">
                        ${data.audit_provenance.slice(-5).map(e => `<div>• ${e}</div>`).join('')}
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    } catch (err) {
        console.error('Report render error:', err);
        container.innerHTML = `<div class="text-red-400 text-center py-8">⚠️ Failed to load structured report.</div>`;
    }
}

// ============================================================
// Audit Rendering (dark)
// ============================================================
function renderAudit(logs) {
    const container = document.getElementById('audit-log');
    if (!logs || logs.length === 0) {
        container.innerHTML = '<div class="text-gray-400">No audit entries yet.</div>';
        return;
    }
    container.innerHTML = logs.map(entry => {
        // try to parse timestamp and agent from log
        const parts = entry.match(/\[(.*?)\]\s+\[(.*?)\]\s+(.*)/);
        if (parts) {
            return `<div class="audit-entry"><span class="time">${parts[1]}</span> <span class="agent">[${parts[2]}]</span> <span class="message">${parts[3]}</span></div>`;
        }
        return `<div class="audit-entry">${entry}</div>`;
    }).join('');
}

// ============================================================
// Approval handler
// ============================================================
async function handleApproval(index, approved) {
    try {
        const resp = await fetch(`${API_BASE}/api/actions/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action_index: index, approved })
        });
        const result = await resp.json();
        alert(`✅ Action ${approved ? 'APPROVED' : 'REJECTED'} – ${result.status}`);
        refreshData();
    } catch (err) {
        alert('❌ Failed to process approval.');
    }
}

// ============================================================
// Workflow triggers
// ============================================================
async function triggerWorkflow() {
    if (!confirm('Run full autonomous cycle?')) return;
    try {
        const resp = await fetch(`${API_BASE}/api/workflow/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: 'Optimize infrastructure for lowest carbon intensity' })
        });
        const data = await resp.json();
        alert(`✅ Workflow triggered. Session: ${data.session_id}\nActions generated: ${data.actions_generated}`);
        setTimeout(refreshData, 3000);
    } catch (err) {
        alert('❌ Failed to trigger workflow.');
    }
}

async function resetState() {
    if (!confirm('Reset state and run fresh discovery?')) return;
    try {
        const resp = await fetch(`${API_BASE}/api/workflow/reset`, { method: 'POST' });
        const data = await resp.json();
        alert(`✅ State reset. New session: ${data.session_id}`);
        refreshData();
    } catch (err) {
        alert('❌ Failed to reset state.');
    }
}

// ============================================================
// Chart
// ============================================================
function initChart() {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    telemetryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Power (Watts)',
                    data: [],
                    backgroundColor: 'rgba(255, 215, 0, 0.5)',
                    borderColor: '#ffd700',
                    borderWidth: 1
                },
                {
                    label: 'CPU Utilization (%)',
                    data: [],
                    backgroundColor: 'rgba(255, 68, 68, 0.4)',
                    borderColor: '#ff4444',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#ffffff' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#aaaaaa' }
                },
                x: {
                    ticks: { color: '#aaaaaa' }
                }
            }
        }
    });
    refreshData();
}