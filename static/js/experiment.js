/**
 * Multi-Dataset Benchmark Matrix Module
 */

class ExperimentBench {
    constructor(tableBodyId) {
        this.tableBody = document.getElementById(tableBodyId);
    }

    async runBenchmark() {
        if (!this.tableBody) return;
        this.tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">⏳ Running multi-dataset benchmark matrix...</td></tr>`;

        try {
            const resp = await API.runBenchmark();
            if (resp.success && resp.benchmark_results) {
                this.renderResults(resp.benchmark_results);
            } else {
                this.tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Benchmark error: ${resp.error || 'Unknown'}</td></tr>`;
            }
        } catch (err) {
            this.tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Error: ${err.message}</td></tr>`;
        }
    }

    renderResults(results) {
        this.tableBody.innerHTML = "";

        if (!results || results.length === 0) {
            this.tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">No benchmark datasets found.</td></tr>`;
            return;
        }

        results.forEach((row) => {
            const tr = document.createElement("tr");
            const savedColor = row.space_saved > 0 ? "text-orange" : "text-muted";

            tr.innerHTML = `
                <td><strong>${escapeHtml(row.filename)}</strong></td>
                <td><span style="background:var(--orange-light); color:#9a3412; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">${escapeHtml(row.file_type || 'Data')}</span></td>
                <td>${formatBytes(row.original_size)}</td>
                <td>${formatBytes(row.compressed_size)}</td>
                <td>${row.compression_ratio.toFixed(2)}</td>
                <td class="${savedColor}"><strong>${row.space_saved.toFixed(1)}%</strong></td>
                <td>${row.entropy.toFixed(2)}</td>
                <td>${row.avg_code_length.toFixed(2)}</td>
                <td>${row.efficiency.toFixed(1)}%</td>
            `;
            this.tableBody.appendChild(tr);
        });
    }
}

window.ExperimentBench = ExperimentBench;
