/** Utilitários partilhados da demo estática. */
(function () {
  const AUTH_KEY = "psycomanager-demo-auth";

  window.DemoAuth = {
    isLoggedIn: function () {
      return sessionStorage.getItem(AUTH_KEY) === "1";
    },
    login: function () {
      sessionStorage.setItem(AUTH_KEY, "1");
    },
    logout: function () {
      sessionStorage.removeItem(AUTH_KEY);
    },
    require: function () {
      if (!this.isLoggedIn()) {
        location.href = "entrar.html";
        return false;
      }
      return true;
    },
  };

  window.DemoFmt = {
    queixa: function (code) {
      return (window.DEMO_SEED && window.DEMO_SEED.QUEIXAS[code]) || code;
    },
    freq: function (code) {
      return (window.DEMO_SEED && window.DEMO_SEED.FREQ[code]) || code;
    },
    dateTime: function (iso) {
      const d = new Date(iso);
      const pad = function (n) {
        return String(n).padStart(2, "0");
      };
      return (
        pad(d.getDate()) +
        "/" +
        pad(d.getMonth() + 1) +
        "/" +
        d.getFullYear() +
        " " +
        pad(d.getHours()) +
        ":" +
        pad(d.getMinutes())
      );
    },
    dateShort: function (iso) {
      const d = new Date(iso);
      const pad = function (n) {
        return String(n).padStart(2, "0");
      };
      return pad(d.getDate()) + "/" + pad(d.getMonth() + 1);
    },
    dateOnly: function (iso) {
      const d = new Date(iso);
      const pad = function (n) {
        return String(n).padStart(2, "0");
      };
      return pad(d.getDate()) + "/" + pad(d.getMonth() + 1) + "/" + d.getFullYear();
    },
    publicLink: function (consultaId) {
      const base = location.href.replace(/[^/]+$/, "");
      return base + "consulta.html?id=" + consultaId;
    },
  };

  window.showToast = function (text, level) {
    let root = document.getElementById("toast-root");
    if (!root) {
      root = document.createElement("div");
      root.id = "toast-root";
      root.className =
        "pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(100%-2rem,22rem)] flex-col gap-2";
      root.setAttribute("aria-live", "polite");
      document.body.appendChild(root);
    }
    if (!text) return;
    const el = document.createElement("div");
    const isError = level === "error";
    el.className =
      "pointer-events-auto rounded-lg px-3.5 py-2.5 text-sm shadow-lg ring-1 transition " +
      (isError
        ? "bg-red-50 text-red-800 ring-red-600/15"
        : "bg-green-50 text-green-800 ring-green-600/15");
    el.setAttribute("role", "status");
    el.textContent = text;
    root.appendChild(el);
    setTimeout(function () {
      el.style.opacity = "0";
      el.style.transform = "translateY(0.25rem)";
      setTimeout(function () {
        el.remove();
      }, 250);
    }, 4200);
  };

  function injectBanner() {
    if (document.getElementById("demo-banner")) return;
    const banner = document.createElement("div");
    banner.id = "demo-banner";
    banner.className = "demo-banner";
    banner.innerHTML =
      "<strong>Demo estática</strong> — preview no GitHub Pages, sem Django. " +
      'Os dados ficam só neste browser. <a href="pacientes.html?reset=1">Repor dados</a> · ' +
      '<a href="https://github.com/GuilhermeRoesler/PsycoManager" target="_blank" rel="noopener">Ver código</a>';
    document.body.prepend(banner);
  }

  function wireCopy() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        const value = btn.getAttribute("data-copy") || "";
        try {
          await navigator.clipboard.writeText(value);
          window.showToast("Link copiado", "success");
        } catch (_) {
          window.showToast("Não foi possível copiar o link", "error");
        }
      });
    });
  }

  function wireConfirm() {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        const msg = form.getAttribute("data-confirm") || "Confirmar?";
        if (!window.confirm(msg)) e.preventDefault();
      });
    });
  }

  /* Selects customizados (igual ao base.html) */
  function enhanceSelects() {
    const LAYOUT_RE =
      /^(w-|min-w-|max-w-|sm:w-|md:w-|lg:w-|mt-|mb-|ml-|mr-|mx-|my-|m-|flex-|shrink-|grow-)/;
    const CHEVRON =
      '<svg class="select-chevron" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" /></svg>';
    const CHECK =
      '<svg class="select-check" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clip-rule="evenodd" /></svg>';

    function splitClasses(select) {
      const layout = [];
      const rest = [];
      (select.className || "")
        .split(/\s+/)
        .filter(Boolean)
        .forEach(function (c) {
          if (c === "input-field") return;
          if (LAYOUT_RE.test(c)) layout.push(c);
          else rest.push(c);
        });
      return { layout: layout, rest: rest };
    }

    function enhanceSelect(select) {
      if (select.dataset.enhanced === "1") return;
      select.dataset.enhanced = "1";
      const parts = splitClasses(select);
      const root = document.createElement("div");
      root.className = ["select-root"].concat(parts.layout).filter(Boolean).join(" ");

      const trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className = ["select-trigger"].concat(parts.rest).filter(Boolean).join(" ");
      trigger.setAttribute("aria-haspopup", "listbox");
      trigger.setAttribute("aria-expanded", "false");

      const labelEl = document.createElement("span");
      labelEl.className = "select-label truncate";
      trigger.appendChild(labelEl);
      trigger.insertAdjacentHTML("beforeend", CHEVRON);

      const menu = document.createElement("ul");
      menu.className = "select-menu";
      menu.setAttribute("role", "listbox");

      select.className = "select-native";
      select.parentNode.insertBefore(root, select);
      root.appendChild(trigger);
      root.appendChild(menu);
      root.appendChild(select);

      let open = false;
      let activeIndex = -1;

      function options() {
        return Array.from(select.options);
      }
      function selectedOption() {
        return select.options[select.selectedIndex] || null;
      }
      function isPlaceholder(opt) {
        return !opt || (opt.disabled && !opt.value);
      }
      function syncLabel() {
        const opt = selectedOption();
        const text = opt ? opt.textContent.trim() : "";
        labelEl.textContent = text || "Selecionar";
        trigger.classList.toggle("is-placeholder", isPlaceholder(opt) || !(opt && opt.value));
      }
      function buildMenu() {
        menu.innerHTML = "";
        options().forEach(function (opt, i) {
          const li = document.createElement("li");
          li.className = "select-option" + (opt.disabled ? " is-disabled" : "");
          li.setAttribute("role", "option");
          li.setAttribute("aria-selected", opt.selected ? "true" : "false");
          li.innerHTML = CHECK + '<span class="truncate">' + opt.textContent.trim() + "</span>";
          if (!opt.disabled) {
            li.addEventListener("click", function (e) {
              e.preventDefault();
              choose(i);
            });
          }
          menu.appendChild(li);
        });
      }
      function setActive(index) {
        const all = menu.querySelectorAll(".select-option");
        all.forEach(function (el) {
          el.classList.remove("bg-brand-50");
        });
        if (index < 0 || index >= all.length || all[index].classList.contains("is-disabled")) {
          activeIndex = -1;
          return;
        }
        activeIndex = index;
        all[index].classList.add("bg-brand-50");
        all[index].scrollIntoView({ block: "nearest" });
      }
      function choose(index) {
        const opt = select.options[index];
        if (!opt || opt.disabled) return;
        select.selectedIndex = index;
        select.dispatchEvent(new Event("input", { bubbles: true }));
        select.dispatchEvent(new Event("change", { bubbles: true }));
        syncLabel();
        buildMenu();
        close();
        trigger.focus();
      }
      function openMenu() {
        if (select.disabled) return;
        buildMenu();
        open = true;
        menu.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
        setActive(select.selectedIndex >= 0 ? select.selectedIndex : 0);
      }
      function close() {
        open = false;
        menu.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        activeIndex = -1;
      }
      trigger.addEventListener("click", function (e) {
        e.preventDefault();
        if (open) close();
        else openMenu();
      });
      select.addEventListener("change", syncLabel);
      document.addEventListener("click", function (e) {
        if (open && !root.contains(e.target)) close();
      });
      syncLabel();
    }

    document.querySelectorAll("select.input-field").forEach(enhanceSelect);
  }

  window.DemoUI = {
    openDrawer: function (drawer, overlay) {
      if (overlay) overlay.classList.remove("hidden");
      if (drawer) drawer.classList.remove("translate-x-full");
      document.body.style.overflow = "hidden";
    },
    closeDrawer: function (drawer, overlay) {
      if (overlay) overlay.classList.add("hidden");
      if (drawer) drawer.classList.add("translate-x-full");
      document.body.style.overflow = "";
    },
    wireDrawer: function (opts) {
      const drawer = document.getElementById(opts.drawerId);
      const overlay = document.getElementById(opts.overlayId);
      const openers = (opts.openerIds || [])
        .map(function (id) {
          return document.getElementById(id);
        })
        .filter(Boolean);
      const closer = opts.closerId ? document.getElementById(opts.closerId) : null;
      openers.forEach(function (btn) {
        btn.addEventListener("click", function () {
          window.DemoUI.openDrawer(drawer, overlay);
          if (opts.focusId) {
            const el = document.getElementById(opts.focusId);
            if (el) setTimeout(function () {
              el.focus();
            }, 280);
          }
        });
      });
      if (closer)
        closer.addEventListener("click", function () {
          window.DemoUI.closeDrawer(drawer, overlay);
        });
      if (overlay)
        overlay.addEventListener("click", function () {
          window.DemoUI.closeDrawer(drawer, overlay);
        });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") window.DemoUI.closeDrawer(drawer, overlay);
      });
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    // Processa ?reset=1 antes de qualquer página depender do store
    if (window.DemoStore) window.DemoStore.get();

    injectBanner();
    wireCopy();
    wireConfirm();
    enhanceSelects();

    const logoutBtn = document.getElementById("btn-sair");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", function () {
        window.DemoAuth.logout();
        location.href = "entrar.html";
      });
    }
  });
})();
