/**
 * Huffman Tree Visualiser App Controller
 * Handles UI interactions, API calls, and rendering for /visualiser page.
 */

const treeContainer = document.getElementById("tree-svg-container");
const metricsBar    = document.getElementById("metrics-bar");
const infoGrid      = document.getElementById("vis-info-grid");
const inputEl       = document.getElementById("vis-input");
const btnBuild      = document.getElementById("btn-build");
const btnReset      = document.getElementById("btn-reset");

/* -- Helpers --------------------------------------------------- */
function escHtml(str) {
    const d = document.createElement("div");
    d.textContent = String(str);
    return d.innerHTML;
}

/* -- Build ----------------------------------------------------- */
async function buildTree() {
    const text = inputEl.value.trim();
    if (!text) { alert("Please enter some text first."); return; }

    btnBuild.textContent = "Building...";
    btnBuild.disabled = true;

    try {
        const resp = await fetch("/api/visualiser", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await resp.json();

        if (!data.success) {
            alert("Error: " + (data.error || "Unknown"));
            return;
        }

        // Metrics
        document.getElementById("m-total").textContent   = data.total_chars;
        document.getElementById("m-symbols").textContent = data.unique_symbols;
        document.getElementById("m-entropy").textContent = data.entropy.toFixed(4) + " bits";
        document.getElementById("m-avglen").textContent  = data.avg_code_length.toFixed(4) + " bits";
        metricsBar.style.display = "flex";
        infoGrid.style.display   = "grid";

        renderPQ(data.pq_steps[0].queue);
        renderSteps(data.pq_steps);
        renderCodes(data.codes);
        renderTree(data.tree);

    } catch (e) {
        alert("Network error: " + e.message);
    } finally {
        btnBuild.textContent = "Build Tree";
        btnBuild.disabled = false;
    }
}

/* -- Panels ---------------------------------------------------- */
function renderPQ(queue) {
    const el = document.getElementById("pq-list");
    el.innerHTML = "";
    queue.forEach(item => {
        const div = document.createElement("div");
        div.className = "pq-item";
        div.innerHTML = `<span class="pq-sym">${escHtml(item.symbol)}</span><span class="pq-freq">freq: ${item.freq}</span>`;
        el.appendChild(div);
    });
}

function renderSteps(steps) {
    const log   = document.getElementById("steps-log");
    const badge = document.getElementById("steps-count");
    log.innerHTML = "";

    const mergeSteps = steps.filter(s => s.type === "merge");
    badge.textContent = mergeSteps.length + " merge" + (mergeSteps.length !== 1 ? "s" : "");

    const initDiv = document.createElement("div");
    initDiv.className = "step-entry";
    initDiv.innerHTML = `<span class="step-index">0</span><strong>Initialize</strong> &mdash; Count frequencies, insert all into min-priority queue.`;
    log.appendChild(initDiv);

    mergeSteps.forEach((s, i) => {
        const div = document.createElement("div");
        div.className = "step-entry";
        div.innerHTML =
            `<span class="step-index">${i + 1}</span>` +
            `<strong>Merge</strong> ` +
            `<code style="background:#f5f5f4;padding:1px 5px;border-radius:3px;">${escHtml(s.a.symbol)}(${s.a.freq})</code> + ` +
            `<code style="background:#f5f5f4;padding:1px 5px;border-radius:3px;">${escHtml(s.b.symbol)}(${s.b.freq})</code> ` +
            `&rarr; <strong style="color:var(--orange-main)">(${s.merged_freq})</strong><br>` +
            `<span style="color:var(--text-muted);font-size:0.72rem;">Queue: ${s.queue.map(x => escHtml(x.symbol) + "(" + x.freq + ")").join(", ")}</span>`;
        log.appendChild(div);
    });
}

function renderCodes(codes) {
    const tbody = document.getElementById("codes-body");
    tbody.innerHTML = "";
    codes.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML =
            `<td><strong>${escHtml(row.symbol)}</strong></td>` +
            `<td>${row.freq}</td>` +
            `<td>${row.prob_pct}%</td>` +
            `<td><span class="code-chip">${row.code}</span></td>` +
            `<td>${row.code_length}</td>`;
        tbody.appendChild(tr);
    });
}

function renderTree(treeJson) {
    treeContainer.innerHTML = "";
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.id = "vis-tree-svg";
    treeContainer.appendChild(svg);
    const vis = new HuffmanTreeVisualiser("vis-tree-svg");
    vis.render(treeJson);
}

/* -- Reset ----------------------------------------------------- */
function resetAll() {
    inputEl.value = "";
    treeContainer.innerHTML = `<div class="vis-empty vis-empty-large">Enter text above and click Build Tree to visualise the Huffman tree.</div>`;
    document.getElementById("pq-list").innerHTML   = `<div class="vis-empty">No data</div>`;
    document.getElementById("steps-log").innerHTML = `<div class="vis-empty">No data</div>`;
    document.getElementById("codes-body").innerHTML = `<tr><td colspan="5" class="text-center text-muted" style="padding:1rem;">No data</td></tr>`;
    metricsBar.style.display = "none";
    infoGrid.style.display   = "none";
}

/* -- Events ---------------------------------------------------- */
btnBuild.addEventListener("click", buildTree);
btnReset.addEventListener("click", resetAll);
inputEl.addEventListener("keydown", e => { if (e.ctrlKey && e.key === "Enter") buildTree(); });

// Auto-build on load
buildTree();
