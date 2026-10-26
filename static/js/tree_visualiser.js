/**
 * Huffman Tree Visualiser — Matte White & Orange Edition
 * Renders interactive animated SVG tree from backend tree JSON.
 * Uses the project's existing design system (style.css tokens).
 */

class HuffmanTreeVisualiser {
    constructor(svgId) {
        this.svg = document.getElementById(svgId);
        this.positions = new Map();
    }

    /* ─── Layout ─────────────────────────────────────────────── */

    _assignPositions(node, depth, xCounter) {
        if (!node) return xCounter;
        const GAP_X = 80;
        const GAP_Y = 100;

        xCounter = this._assignPositions(node.left, depth + 1, xCounter);

        xCounter++;
        this.positions.set(node.id, {
            x: xCounter * GAP_X,
            y: depth * GAP_Y + 60,
            node
        });

        xCounter = this._assignPositions(node.right, depth + 1, xCounter);
        return xCounter;
    }

    /* ─── SVG Helpers ─────────────────────────────────────────── */

    _ns(tag) {
        return document.createElementNS("http://www.w3.org/2000/svg", tag);
    }

    _drawEdge(parent, child, label) {
        const p = this.positions.get(parent.id);
        const c = this.positions.get(child.id);
        if (!p || !c) return;

        const line = this._ns("line");
        line.setAttribute("x1", p.x);
        line.setAttribute("y1", p.y);
        line.setAttribute("x2", c.x);
        line.setAttribute("y2", c.y);
        line.setAttribute("stroke", "#d6d3d1");
        line.setAttribute("stroke-width", "2");
        this.svg.insertBefore(line, this.svg.firstChild);

        // Edge label (0 / 1)
        const mx = (p.x + c.x) / 2;
        const my = (p.y + c.y) / 2;
        const bg = this._ns("rect");
        const padding = 5;
        bg.setAttribute("x", mx - padding - 1);
        bg.setAttribute("y", my - 10);
        bg.setAttribute("width", padding * 2 + 12);
        bg.setAttribute("height", 16);
        bg.setAttribute("rx", "4");
        bg.setAttribute("fill", label === "0" ? "#ffffff" : "#ffedd5");
        bg.setAttribute("stroke", label === "0" ? "#e7e5e4" : "#fed7aa");
        bg.setAttribute("stroke-width", "1");
        this.svg.appendChild(bg);

        const txt = this._ns("text");
        txt.setAttribute("x", mx + 5);
        txt.setAttribute("y", my + 3);
        txt.setAttribute("text-anchor", "middle");
        txt.setAttribute("font-size", "11");
        txt.setAttribute("font-weight", "700");
        txt.setAttribute("font-family", "JetBrains Mono, monospace");
        txt.setAttribute("fill", label === "0" ? "#78716c" : "#ea580c");
        txt.textContent = label;
        this.svg.appendChild(txt);
    }

    _drawNode(pos) {
        const { x, y, node } = pos;
        const isLeaf = node.is_leaf;
        const RADIUS = 26;

        const g = this._ns("g");
        g.setAttribute("transform", `translate(${x},${y})`);
        g.style.opacity = "0";
        g.style.transition = "opacity 0.4s ease";

        // Tooltip
        const title = this._ns("title");
        const tipLines = isLeaf
            ? `Symbol: ${node.label}\nFreq: ${node.freq}\nP(x): ${(node.prob * 100).toFixed(1)}%\nCode: ${node.code}`
            : `Internal Node\nFreq: ${node.freq}\nP(x): ${(node.prob * 100).toFixed(1)}%`;
        title.textContent = tipLines;
        g.appendChild(title);

        // Circle
        const circle = this._ns("circle");
        circle.setAttribute("r", RADIUS);
        circle.setAttribute("fill", isLeaf ? "#ea580c" : "#ffffff");
        circle.setAttribute("stroke", isLeaf ? "#c2410c" : "#d6d3d1");
        circle.setAttribute("stroke-width", "2");
        circle.setAttribute("filter", "drop-shadow(0 2px 6px rgba(0,0,0,0.08))");
        g.appendChild(circle);

        // Frequency text
        const freqTxt = this._ns("text");
        freqTxt.setAttribute("text-anchor", "middle");
        freqTxt.setAttribute("y", isLeaf ? "6" : "5");
        freqTxt.setAttribute("font-size", "13");
        freqTxt.setAttribute("font-weight", "700");
        freqTxt.setAttribute("font-family", "JetBrains Mono, monospace");
        freqTxt.setAttribute("fill", isLeaf ? "#ffffff" : "#1c1917");
        freqTxt.textContent = node.freq;
        g.appendChild(freqTxt);

        // Symbol label above node (leaf only)
        if (isLeaf) {
            const symBg = this._ns("rect");
            symBg.setAttribute("x", -18);
            symBg.setAttribute("y", -RADIUS - 26);
            symBg.setAttribute("width", "36");
            symBg.setAttribute("height", "20");
            symBg.setAttribute("rx", "4");
            symBg.setAttribute("fill", "#fff7ed");
            symBg.setAttribute("stroke", "#fed7aa");
            symBg.setAttribute("stroke-width", "1");
            g.appendChild(symBg);

            const symTxt = this._ns("text");
            symTxt.setAttribute("text-anchor", "middle");
            symTxt.setAttribute("y", -RADIUS - 11);
            symTxt.setAttribute("font-size", "12");
            symTxt.setAttribute("font-weight", "700");
            symTxt.setAttribute("font-family", "JetBrains Mono, monospace");
            symTxt.setAttribute("fill", "#ea580c");
            symTxt.textContent = node.label;
            g.appendChild(symTxt);

            // Code badge below node
            const codeW = Math.max(36, node.code.length * 9 + 12);
            const codeBg = this._ns("rect");
            codeBg.setAttribute("x", -codeW / 2);
            codeBg.setAttribute("y", RADIUS + 4);
            codeBg.setAttribute("width", codeW);
            codeBg.setAttribute("height", "18");
            codeBg.setAttribute("rx", "4");
            codeBg.setAttribute("fill", "#1c1917");
            g.appendChild(codeBg);

            const codeTxt = this._ns("text");
            codeTxt.setAttribute("text-anchor", "middle");
            codeTxt.setAttribute("y", RADIUS + 17);
            codeTxt.setAttribute("font-size", "10");
            codeTxt.setAttribute("font-family", "JetBrains Mono, monospace");
            codeTxt.setAttribute("fill", "#ffffff");
            codeTxt.textContent = node.code;
            g.appendChild(codeTxt);
        }

        this.svg.appendChild(g);
        return g;
    }

    /* ─── Public: render ──────────────────────────────────────── */

    render(treeJson) {
        if (!this.svg || !treeJson) return;
        this.svg.innerHTML = "";
        this.positions.clear();

        this._assignPositions(treeJson, 0, 0);

        const allPositions = [...this.positions.values()];
        const maxX = Math.max(...allPositions.map(p => p.x));
        const maxY = Math.max(...allPositions.map(p => p.y));

        const svgW = maxX + 120;
        const svgH = maxY + 100;
        this.svg.setAttribute("viewBox", `0 0 ${svgW} ${svgH}`);
        this.svg.setAttribute("width", svgW);
        this.svg.setAttribute("height", svgH);
        this.svg.style.minWidth = `${svgW}px`;

        // Draw edges first
        this.positions.forEach(pos => {
            const { node } = pos;
            if (node.left)  this._drawEdge(node, node.left, "0");
            if (node.right) this._drawEdge(node, node.right, "1");
        });

        // Draw nodes with staggered animation (depth-order from positions map)
        const nodeEls = [];
        this.positions.forEach(pos => {
            const el = this._drawNode(pos);
            nodeEls.push(el);
        });

        // Sort by y (depth) so animation goes top-down
        nodeEls.sort((a, b) => {
            const ya = parseFloat(a.getAttribute("transform").match(/translate\([\d.]+,([\d.]+)\)/)?.[1] || 0);
            const yb = parseFloat(b.getAttribute("transform").match(/translate\([\d.]+,([\d.]+)\)/)?.[1] || 0);
            return ya - yb;
        });

        nodeEls.forEach((el, i) => {
            setTimeout(() => { el.style.opacity = "1"; }, i * 70);
        });
    }
}

window.HuffmanTreeVisualiser = HuffmanTreeVisualiser;
