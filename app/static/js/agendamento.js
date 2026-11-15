// Formulário de agendamento: carrega profissionais e horários livres via JSON.
(function () {
  "use strict";

  var form = document.getElementById("form-agendamento");
  if (!form) return;

  var selServico = document.getElementById("servico_id");
  var selProf = document.getElementById("profissional_id");
  var inpData = document.getElementById("data");
  var selHora = document.getElementById("horario");
  var aviso = document.getElementById("aviso-horarios");

  var profAtual = form.dataset.profissionalAtual || "";
  var horaAtual = form.dataset.horarioAtual || "";

  function resetar(select, texto) {
    select.innerHTML = "";
    var opcao = document.createElement("option");
    opcao.value = "";
    opcao.textContent = texto;
    select.appendChild(opcao);
    select.disabled = true;
  }

  function carregarProfissionais() {
    aviso.textContent = "";
    resetar(selHora, "Escolha serviço, profissional e data");
    if (!selServico.value) {
      resetar(selProf, "Escolha primeiro o serviço");
      return Promise.resolve();
    }
    var url = form.dataset.urlProfissionais.replace(/0$/, selServico.value);
    return fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (lista) {
        resetar(selProf, lista.length ? "Selecione…" : "Nenhum profissional disponível");
        lista.forEach(function (p) {
          var o = document.createElement("option");
          o.value = p.id;
          o.textContent = p.nome;
          if (String(p.id) === String(profAtual)) o.selected = true;
          selProf.appendChild(o);
        });
        selProf.disabled = lista.length === 0;
      })
      .catch(function () {
        resetar(selProf, "Erro ao carregar profissionais");
      });
  }

  function carregarHorarios() {
    if (!selServico.value || !selProf.value || !inpData.value) {
      resetar(selHora, "Escolha serviço, profissional e data");
      return;
    }
    var params = new URLSearchParams({
      servico_id: selServico.value,
      profissional_id: selProf.value,
      data: inpData.value
    });
    aviso.textContent = "Buscando horários…";
    fetch(form.dataset.urlHorarios + "?" + params.toString())
      .then(function (r) { return r.json(); })
      .then(function (horarios) {
        resetar(selHora, horarios.length ? "Selecione…" : "Sem horários livres");
        horarios.forEach(function (h) {
          var o = document.createElement("option");
          o.value = h;
          o.textContent = h;
          if (h === horaAtual) o.selected = true;
          selHora.appendChild(o);
        });
        selHora.disabled = horarios.length === 0;
        aviso.textContent = horarios.length
          ? horarios.length + " horário(s) livre(s)."
          : "Não há horários livres nesta data. Tente outro dia ou profissional.";
      })
      .catch(function () {
        aviso.textContent = "Não foi possível carregar os horários. Tente novamente.";
      });
  }

  selServico.addEventListener("change", function () {
    profAtual = "";
    horaAtual = "";
    carregarProfissionais().then(carregarHorarios);
  });
  selProf.addEventListener("change", function () { horaAtual = ""; carregarHorarios(); });
  inpData.addEventListener("change", function () { horaAtual = ""; carregarHorarios(); });

  // Reaproveita valores quando a página é reexibida após erro de validação.
  carregarProfissionais().then(carregarHorarios);
})();
