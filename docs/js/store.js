/** Persistência em localStorage para a demo (reinicia com ?reset=1). */
window.DemoStore = (function () {
  const KEY = "psycomanager-static-demo-v1";

  function clone(v) {
    return JSON.parse(JSON.stringify(v));
  }

  function seed() {
    const s = window.DEMO_SEED;
    return {
      pacientes: clone(s.pacientes),
      tarefas: clone(s.tarefas),
      consultas: clone(s.consultas),
      nextIds: clone(s.nextIds),
    };
  }

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return seed();
      return JSON.parse(raw);
    } catch (_) {
      return seed();
    }
  }

  function save(state) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  function get() {
    if (new URLSearchParams(location.search).get("reset") === "1") {
      const fresh = seed();
      save(fresh);
      const url = new URL(location.href);
      url.searchParams.delete("reset");
      history.replaceState(null, "", url.pathname + url.search + url.hash);
      return fresh;
    }
    return load();
  }

  function update(fn) {
    const state = get();
    fn(state);
    save(state);
    return state;
  }

  function reset() {
    const fresh = seed();
    save(fresh);
    return fresh;
  }

  return { get: get, update: update, reset: reset, save: save };
})();
