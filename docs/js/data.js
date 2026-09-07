/** Dados seed da demo estática (espelham o carregar_demo). */
window.DEMO_SEED = (function () {
  const QUEIXAS = {
    TDAH: "TDAH",
    D: "Depressão",
    A: "Ansiedade",
    TAG: "Transtorno de Ansiedade Generalizada",
  };

  const FREQ = {
    D: "Diário",
    "1S": "1 vez por semana",
    "2S": "2 vezes por semana",
    "3S": "3 vezes por semana",
    N: "Ao necessitar",
  };

  const AVATAR_COLORS = [
    "2a9d8f", "1f7a6f", "3b82f6", "10b981", "f43f5e",
    "f59e0b", "8b5cf6", "0ea5e9", "ec4899", "22c55e",
  ];

  function avatar(nome, idx) {
    const bg = AVATAR_COLORS[idx % AVATAR_COLORS.length];
    return (
      "https://ui-avatars.com/api/?name=" +
      encodeURIComponent(nome) +
      "&background=" +
      bg +
      "&color=fff&size=128&bold=true"
    );
  }

  function daysAgo(n, hour, minute) {
    const d = new Date();
    d.setDate(d.getDate() - n);
    d.setHours(hour, minute, 0, 0);
    return d.toISOString();
  }

  const tarefas = [
    { id: 1, tarefa: "Diário de humor", instrucoes: "Anote 3 vezes ao dia (manhã, tarde e noite) o humor de 1 a 5 e o que estava a sentir.", frequencia: "D" },
    { id: 2, tarefa: "Respiração diafragmática", instrucoes: "Pratique 5 minutos de respiração lenta: inspire 4s, segure 2s, expire 6s.", frequencia: "D" },
    { id: 3, tarefa: "Exercício de grounding 5-4-3-2-1", instrucoes: "Identifique 5 coisas que vê, 4 que toca, 3 que ouve, 2 que cheira e 1 que saboreia.", frequencia: "N" },
    { id: 4, tarefa: "Registo de pensamentos automáticos", instrucoes: "Quando notar ansiedade, escreva a situação, o pensamento e uma alternativa mais realista.", frequencia: "D" },
    { id: 5, tarefa: "Caminhada consciente", instrucoes: "Caminhe 20 minutos prestando atenção ao ritmo dos passos e à respiração.", frequencia: "1S" },
    { id: 6, tarefa: "Higiene do sono", instrucoes: "Deite-se e levante-se à mesma hora; evite ecrãs 30 min antes de dormir.", frequencia: "D" },
  ];

  const pacientesRaw = [
    ["Ana Beatriz Costa", "ana.costa@email.com", "(11) 98765-4321", "A", true],
    ["Bruno Henrique Lima", "bruno.lima@email.com", "(11) 97654-3210", "TDAH", true],
    ["Camila Ferreira Santos", "camila.santos@email.com", "(21) 99876-5432", "D", true],
    ["Diego Almeida Rocha", "diego.rocha@email.com", "(21) 98765-1098", "TAG", false],
    ["Eduarda Martins Souza", "eduarda.souza@email.com", "(31) 99123-4567", "A", true],
    ["Felipe Nogueira Dias", "felipe.dias@email.com", "(31) 98234-5678", "TDAH", true],
    ["Isabela Ribeiro Campos", "isabela.campos@email.com", "(51) 98111-2233", "A", false],
    ["João Pedro Oliveira", "joao.oliveira@email.com", "(51) 99222-3344", "TDAH", true],
  ];

  const pacientes = pacientesRaw.map(function (p, i) {
    return {
      id: i + 1,
      nome: p[0],
      email: p[1],
      telefone: p[2],
      queixa: p[3],
      pagamento_em_dia: p[4],
      foto: avatar(p[0], i),
    };
  });

  const consultas = [
    { id: 1, paciente_id: 1, humor: 3, registro_geral: "Sessão focada em ansiedade antecipatória no trabalho.", data: daysAgo(21, 10, 0), video: false, tarefas: [1, 2], views_total: 4, views_unicas: 2 },
    { id: 2, paciente_id: 1, humor: 4, registro_geral: "Melhora no humor; manteve o diário.", data: daysAgo(14, 10, 30), video: true, tarefas: [1, 4], views_total: 2, views_unicas: 1 },
    { id: 3, paciente_id: 1, humor: 4, registro_geral: "Praticou grounding com bons resultados.", data: daysAgo(7, 11, 0), video: true, tarefas: [2, 3], views_total: 1, views_unicas: 1 },
    { id: 4, paciente_id: 2, humor: 2, registro_geral: "Dificuldade de foco na semana de provas.", data: daysAgo(10, 15, 0), video: false, tarefas: [5], views_total: 0, views_unicas: 0 },
    { id: 5, paciente_id: 2, humor: 3, registro_geral: "Introduziu técnica Pomodoro.", data: daysAgo(3, 15, 0), video: true, tarefas: [5, 6], views_total: 3, views_unicas: 2 },
    { id: 6, paciente_id: 3, humor: 2, registro_geral: "Humor baixo; reforço de higiene do sono.", data: daysAgo(12, 9, 0), video: false, tarefas: [6], views_total: 1, views_unicas: 1 },
    { id: 7, paciente_id: 5, humor: 5, registro_geral: "Sessão positiva; consolidou estratégias.", data: daysAgo(5, 16, 30), video: true, tarefas: [1, 2, 3], views_total: 5, views_unicas: 3 },
  ];

  return {
    DEMO_USERNAME: "demo",
    DEMO_PASSWORD: "demo123",
    QUEIXAS: QUEIXAS,
    FREQ: FREQ,
    QUEIXA_CHOICES: Object.keys(QUEIXAS).map(function (k) {
      return [k, QUEIXAS[k]];
    }),
    FREQ_CHOICES: Object.keys(FREQ).map(function (k) {
      return [k, FREQ[k]];
    }),
    tarefas: tarefas,
    pacientes: pacientes,
    consultas: consultas,
    nextIds: { paciente: 9, tarefa: 7, consulta: 8 },
  };
})();
