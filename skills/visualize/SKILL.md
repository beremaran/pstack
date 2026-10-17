---
name: visualize
description: Turn verified measurements or structural facts into a chart or diagram for an engineering explanation, progress update, or report. Use when ketchup or another pstack workflow needs a visual.
---

# Visualize

Read [pstack runtime](../pstack-runtime/SKILL.md). This is a portable replacement for the upstream visualization capability.

1. Identify the claim, audience, and actual evidence. Keep units, sample windows, revisions, and baseline/treatment definitions explicit. Do not invent values or render an imagined screen as evidence.
2. Use Mermaid for small relationship or sequence diagrams. For quantitative comparisons, use a bar, line, scatter, or distribution chart that matches the question. Label axes and units and show uncertainty when measured. For actual UI state, capture the real surface with `control-ui` instead of drawing it.
3. Prefer plotting or diagram tooling already installed in the repository or environment. Save a standalone SVG, PNG, or HTML artifact at an agreed output path. If no renderer exists, provide valid Mermaid or the evidence table and state that rendering was unavailable; do not claim an artifact was generated.
4. Render and inspect the result when tools allow. Verify labels, values, scale, legibility, and the claim against source evidence. Link or embed only artifacts that exist and identify the measurements or source paths that support them. Do not publish private data without authorization.
