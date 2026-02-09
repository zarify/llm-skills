# SKILL: Moodle “Widget” (embeddable HTML/CSS/JS)

This guide is for building a **self-contained interactive widget** that can be pasted into a **Moodle Page resource** (not an iframe).

> Important: many Moodle sites **strip or disable `<script>`** for non-admin users (via HTML sanitising / “trusted content”). If scripts don’t run, your widget can’t be interactive—ask your admin about enabling the appropriate filter/role capability.

## Goals

- Paste into Moodle Page (HTML editor) and it still works
- No external dependencies (no CDN, no imports)
- Styling does not leak into the rest of the Moodle page
- Script does not depend on being in `<head>` and does not require `onload=` attributes

## Key constraints in Moodle Page content

- Your HTML is often inserted *inside the body of Moodle’s page*.
- `<style>` tags may be stripped or ignored by the editor/sanitiser.
- `<head>`, `<html>`, `<body>` wrappers are not appropriate.
- IDs/classes can collide with other content (including other copies of your widget).

## Recommended structure

### 1) Use a single root container

Wrap everything in a root element with:

- a **unique class** (namespaced), e.g. `.mw-binary-demo`
- an **optional unique instance id**, generated at runtime

Example:

```html
<div class="mw-widget mw-binary-demo" data-mw-widget="binary-demo">
  <!-- widget content here -->
</div>
```

### 2) Scope all CSS to the container

Never write global selectors like `body`, `button`, `table`.

Do:

- `.mw-binary-demo button { ... }`
- `.mw-binary-demo .grid { ... }`

### 3) Inject CSS via JavaScript (instead of `<style>`)

Because Moodle may not allow `<style>` in Page content, inject a `<style>` element into `document.head` from JavaScript.

Rules:

- Use a **stable style element id** so you inject once:
  - `id="mw-binary-demo-styles"`
- Keep CSS **minimal** and **scoped**.

### 4) Avoid global variables and avoid relying on global IDs

If you use `document.getElementById('something')`, it will break if:

- the widget is duplicated on the page
- the same ID exists elsewhere

Instead:

- select elements *within the widget container* (recommended)
- use `container.querySelector(...)` rather than `document.querySelector(...)`

### 5) Support multiple instances (copy/paste multiple times)

Write the script so it can initialise **every** matching widget on the page:

- `document.querySelectorAll('[data-mw-widget="binary-demo"]')`
- loop and initialise each container independently

## Copy/paste checklist

- [ ] No `<html>`, `<head>`, `<body>`, `<title>` wrappers
- [ ] No external scripts/styles/fonts/images (unless you control site policy)
- [ ] No global CSS selectors (`body`, `button`, `table`, `*`, etc.)
- [ ] CSS is injected from JS and scoped to the widget class
- [ ] JS initialises per-widget container (supports multiple copies)
- [ ] All DOM lookups are relative to the container
- [ ] Accessible labels (`aria-live`, descriptive button text)
- [ ] Works if pasted into a larger page with other content

## Template: Moodle widget skeleton

Paste and then customise.

```html
<div class="mw-widget mw-REPLACE" data-mw-widget="REPLACE">
  <div class="mw-REPLACE__controls">
    <button type="button" data-action="random">Random</button>
    <span class="mw-REPLACE__output" data-role="output">…</span>
  </div>
  <div class="mw-REPLACE__work" data-role="work">…</div>
  <noscript><p>This activity needs JavaScript enabled.</p></noscript>
</div>

<script>
(function () {
  'use strict';

  var WIDGET = 'REPLACE';
  var ROOT_SELECTOR = '[data-mw-widget="' + WIDGET + '"]';
  var STYLE_ID = 'mw-' + WIDGET + '-styles';

  function injectStylesOnce() {
    if (document.getElementById(STYLE_ID)) return;

    var css = [
      '.mw-' + WIDGET + '{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.35;}',
      '.mw-' + WIDGET + ' .mw-' + WIDGET + '__controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;}',
      '.mw-' + WIDGET + ' button{border:1px solid #d6d9de;background:#fff;border-radius:10px;padding:10px 12px;cursor:pointer;font-weight:600;}'
    ].join('\n');

    var style = document.createElement('style');
    style.id = STYLE_ID;
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
    (document.head || document.documentElement).appendChild(style);
  }

  function initWidget(container) {
    var btn = container.querySelector('[data-action="random"]');
    var output = container.querySelector('[data-role="output"]');
    var work = container.querySelector('[data-role="work"]');

    function render() {
      // TODO: update output/work
      if (output) output.textContent = '…';
      if (work) work.textContent = '…';
    }

    if (btn) btn.addEventListener('click', render);
    render();
  }

  injectStylesOnce();
  var widgets = document.querySelectorAll(ROOT_SELECTOR);
  for (var i = 0; i < widgets.length; i++) initWidget(widgets[i]);
})();
</script>
```

## Notes / gotchas

- If Moodle strips your `<script>`, you’ll see the static HTML only. That’s a site policy/role capability issue, not a code issue.
- If you *must* use IDs, generate them per instance and apply them inside `initWidget(container)`.
- Prefer `textContent` over `innerHTML` unless you’re deliberately rendering HTML.
