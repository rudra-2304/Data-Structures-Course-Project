/**
 * Frequency Histogram Renderer (Matte Orange)
 */

class FrequencyChartVisualizer {
    constructor(svgElementId) {
        this.svg = document.getElementById(svgElementId);
    }

    render(codeTable) {
        if (!this.svg) return;
        this.svg.innerHTML = "";

        if (!codeTable || codeTable.length === 0) return;

        const width = this.svg.clientWidth || 550;
        const height = 240;
        const padding = { top: 20, right: 20, bottom: 40, left: 45 };

        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const displayData = codeTable.slice(0, 20);
        const maxFreq = Math.max(...displayData.map(d => d.freq), 1);
        const barWidth = Math.max(14, Math.floor(chartWidth / displayData.length) - 6);

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("transform", `translate(${padding.left}, ${padding.top})`);
        this.svg.appendChild(g);

        // Y-axis grid
        const ticks = 4;
        for (let i = 0; i <= ticks; i++) {
            const val = Math.round((maxFreq / ticks) * i);
            const y = chartHeight - (val / maxFreq) * chartHeight;

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", 0);
            line.setAttribute("x2", chartWidth);
            line.setAttribute("y1", y);
            line.setAttribute("y2", y);
            line.setAttribute("stroke", "#e7e5e4");
            g.appendChild(line);

            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", -8);
            text.setAttribute("y", y + 4);
            text.setAttribute("text-anchor", "end");
            text.setAttribute("fill", "#78716c");
            text.setAttribute("font-size", "10px");
            text.setAttribute("font-family", "JetBrains Mono");
            text.textContent = val;
            g.appendChild(text);
        }

        // Render bars
        displayData.forEach((item, index) => {
            const barH = (item.freq / maxFreq) * chartHeight;
            const x = index * (barWidth + 6);
            const y = chartHeight - barH;

            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("class", "chart-bar");
            rect.setAttribute("x", x);
            rect.setAttribute("y", y);
            rect.setAttribute("width", barWidth);
            rect.setAttribute("height", Math.max(2, barH));
            rect.setAttribute("rx", "2");

            const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
            title.textContent = `Symbol: ${item.char_display} | Freq: ${item.freq} | P(x): ${item.prob_pct}%`;
            rect.appendChild(title);

            g.appendChild(rect);

            // X label
            const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
            label.setAttribute("x", x + barWidth / 2);
            label.setAttribute("y", chartHeight + 18);
            label.setAttribute("text-anchor", "middle");
            label.setAttribute("fill", "#1c1917");
            label.setAttribute("font-size", "11px");
            label.setAttribute("font-family", "JetBrains Mono");
            label.textContent = item.char_display;
            g.appendChild(label);
        });
    }
}

window.FrequencyChartVisualizer = FrequencyChartVisualizer;
