// Comportamentos globais da interface.
(function () {
  "use strict";

  // Confirmação antes de ações destrutivas (ação reversível/prevenção de erro).
  document.querySelectorAll("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (evento) {
      if (!window.confirm(form.dataset.confirmar)) {
        evento.preventDefault();
      }
    });
  });

  // Máscara simples de telefone: (99) 99999-9999
  document.querySelectorAll("input[data-mascara='telefone']").forEach(function (campo) {
    function formatar() {
      var d = campo.value.replace(/\D/g, "").slice(0, 11);
      var r = d;
      if (d.length > 10) {
        r = "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
      } else if (d.length > 6) {
        r = "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6);
      } else if (d.length > 2) {
        r = "(" + d.slice(0, 2) + ") " + d.slice(2);
      }
      campo.value = r;
    }
    campo.addEventListener("input", formatar);
    formatar();
  });
})();
