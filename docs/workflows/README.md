# Workflow diagram sources

The root [README](../../README.md#workflow-diagrams) embeds the rendered SVGs. Each `.mmd` file is the editable Mermaid source for its adjacent `.svg`. The maps summarize the pinned local workflows; update both when changing the relevant skill or playbook. Capability branches are alternatives; they do not impose an ordered pipeline.

Rendered and checked with Mermaid CLI 12.0.0 and Chrome. To regenerate, install Node.js and a compatible browser, then install the renderer in a temporary tools directory:

```sh
npm install --prefix /tmp/skill-diagram-tools @mermaid-js/mermaid-cli@12.0.0
```

From the repository root, render an updated source:

```sh
/tmp/skill-diagram-tools/node_modules/.bin/mmdc \
  -i docs/workflows/matt-main.mmd \
  -o docs/workflows/matt-main.svg \
  -c docs/workflows/mermaid-config.json \
  --no-font-embed -b white
```

Use Mermaid CLI's `-p` option with a local Puppeteer configuration if the browser needs an explicit executable path. Keep machine-specific browser configuration outside the repository. The shared rendering config uses SVG text rather than HTML labels, so the exported diagrams do not depend on embedded HTML support. No renderer or browser is required to view the committed images.

Check every changed diagram renders, inspect its labels and branches, and verify README image/source links. Compare the maps against `skills/poteto-mode/SKILL.md`, its 23 playbooks, `skills/poteto-help/SKILL.md`, all `skills/mattpocock-*/SKILL.md` files, and the phase-boundary reference. This is diagram validation, not runtime verification of those workflows on any agent.
