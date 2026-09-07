/** Injeta o tema Tailwind do PsycoManager (demo estática). */
(function () {
  const style = document.createElement("style");
  style.type = "text/tailwindcss";
  style.textContent = `
    @theme {
      --font-sans: "DM Sans", ui-sans-serif, system-ui, sans-serif;
      --font-display: "Fraunces", ui-serif, Georgia, serif;
      --color-brand-50: #eef8f6;
      --color-brand-100: #d5efe9;
      --color-brand-200: #aadcd2;
      --color-brand-500: #2a9d8f;
      --color-brand-600: #1f7a6f;
      --color-brand-700: #186258;
      --color-ink: #14201f;
      --color-muted: #5a6b69;
      --color-surface: #f3f6f5;
      --color-line: #e2ebe8;
    }

    body {
      font-family: var(--font-sans);
      color: var(--color-ink);
      background-color: var(--color-surface);
      min-height: 100vh;
    }

    .font-display { font-family: var(--font-display); }

    .input-field {
      @apply block w-full rounded-lg border-0 bg-white px-3.5 py-2.5 text-sm text-ink shadow-sm ring-1 ring-inset ring-line placeholder:text-muted/50 focus:ring-2 focus:ring-inset focus:ring-brand-500;
    }
    .input-field.with-icon-left { padding-left: 2.5rem; }

    .btn-primary {
      @apply inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 disabled:opacity-50;
    }
    .btn-secondary {
      @apply inline-flex items-center justify-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-ink ring-1 ring-inset ring-line transition hover:bg-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600;
    }
    .btn-ghost {
      @apply inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted transition hover:bg-white hover:text-ink;
    }
    .badge { @apply inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium; }
    .file-field {
      @apply block w-full text-sm text-muted file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-brand-700 hover:file:bg-brand-100;
    }

    .checkbox-field {
      -webkit-appearance: none;
      appearance: none;
      @apply relative mt-0.5 size-4 shrink-0 cursor-pointer rounded-[0.3rem] border border-line bg-white shadow-sm transition;
      background-position: center;
      background-repeat: no-repeat;
      background-size: 0.65rem;
    }
    .checkbox-field:hover { @apply border-brand-500; }
    .checkbox-field:checked {
      @apply border-brand-600 bg-brand-600;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Cpath d='M3.5 8.5L6.5 11.5L12.5 4.5' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    }
    .checkbox-field:focus-visible { @apply outline-none ring-2 ring-brand-500/35 ring-offset-2 ring-offset-white; }
    .checkbox-row { @apply flex cursor-pointer items-start gap-3 rounded-md px-2 py-2 transition hover:bg-surface; }
    .checkbox-row:has(.checkbox-field:checked) { @apply bg-brand-50; }

    .select-root { @apply relative; }
    .select-native {
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
    }
    .select-trigger {
      @apply flex w-full cursor-pointer items-center justify-between gap-2 rounded-lg border-0 bg-white px-3.5 py-2.5 text-left text-sm text-ink shadow-sm ring-1 ring-inset ring-line transition hover:bg-surface/60 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-500;
    }
    .select-trigger[aria-expanded="true"] { @apply ring-2 ring-brand-500; }
    .select-trigger.is-placeholder { @apply text-muted/60; }
    .select-trigger .select-chevron { @apply size-4 shrink-0 text-muted transition-transform duration-200; }
    .select-trigger[aria-expanded="true"] .select-chevron { @apply rotate-180 text-brand-600; }
    .select-menu {
      @apply absolute left-0 right-0 z-[60] mt-1.5 hidden max-h-56 overflow-auto rounded-lg bg-white py-1 shadow-lg ring-1 ring-line;
    }
    .select-menu.is-open { @apply block; }
    .select-option {
      @apply flex cursor-pointer items-center gap-2 px-3.5 py-2 text-sm text-ink transition hover:bg-brand-50 hover:text-brand-700;
    }
    .select-option[aria-selected="true"] { @apply bg-brand-50 font-medium text-brand-700; }
    .select-option.is-disabled { @apply cursor-default text-muted/50 hover:bg-transparent hover:text-muted/50; }
    .select-check { @apply size-3.5 shrink-0 text-brand-600 opacity-0; }
    .select-option[aria-selected="true"] .select-check { @apply opacity-100; }

    .demo-banner {
      @apply border-b border-amber-200/80 bg-amber-50 px-4 py-2 text-center text-xs text-amber-950 sm:text-sm;
    }
    .demo-banner a { @apply font-semibold text-brand-700 underline-offset-2 hover:underline; }
  `;
  document.head.appendChild(style);
})();
