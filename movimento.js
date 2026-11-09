/* O movimento da apresentação: blocos que aparecem ao entrar na tela (uma vez), os passos que acendem e trocam a
   tela ao lado, as perguntas que abrem com altura animada e o cabeçalho que ganha sombra ao rolar.
   Sem biblioteca: só IntersectionObserver e classes; o CSS (pagina.css, tokens --mov-*) faz o resto.
   MOVIMENTO = false desliga tudo de uma vez, para comparar o desempenho. A preferência do sistema por menos
   movimento (comum no Windows do escritório em "melhor desempenho") deixa a versão suave: os blocos esmaecem e os
   traços se desenham, sem nada se deslocar (decisão do dono, 09/11/2026). Sem JavaScript, a página aparece inteira, parada. */
(function () {
  "use strict";
  var MOVIMENTO = true;  // a chave única

  var html = document.documentElement;
  var reduzido = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!MOVIMENTO) { html.setAttribute("data-movimento", "desligado"); }
  else if (reduzido) { html.setAttribute("data-movimento", "suave"); }
  var semMovimento = html.getAttribute("data-movimento") === "desligado";
  var temObservador = "IntersectionObserver" in window;

  // 1. Aparecer ao entrar na tela, uma vez. O que já está na tela antes do script aparece na hora, sem piscar.
  var aparecem = Array.prototype.slice.call(document.querySelectorAll(".aparece"));
  var alturaDaTela = window.innerHeight || html.clientHeight;
  aparecem.forEach(function (elemento) {
    var caixa = elemento.getBoundingClientRect();
    if (semMovimento || !temObservador || caixa.top < alturaDaTela * 0.92) { elemento.classList.add("visivel"); }
  });
  html.classList.add("js");
  if (temObservador && !semMovimento) {
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) { entrada.target.classList.add("visivel"); observador.unobserve(entrada.target); }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
    aparecem.forEach(function (elemento) { if (!elemento.classList.contains("visivel")) { observador.observe(elemento); } });
  }

  // 1b. As cenas (o cadeado, a placa de parada, os ícones, os checks da conferência, os fatos) esperam o bloco passar da
  //     linha de 65% da altura da tela, perto de onde o olho está; antes, o bloco já apareceu, mas a cena não começou.
  //     No fim da página, o que está na tela entra em foco de uma vez (um bloco baixo nunca passa da linha).
  if (temObservador && !semMovimento) {
    var focar = function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) { entrada.target.classList.add("em-foco"); obs.unobserve(entrada.target); }
      });
    };
    var meioDaTela = new IntersectionObserver(focar, { rootMargin: "0px 0px -35% 0px" });
    aparecem.forEach(function (elemento) { meioDaTela.observe(elemento); });
    var noFim = function () {
      if (window.innerHeight + window.scrollY < html.scrollHeight - 4) { return; }
      aparecem.forEach(function (elemento) {
        if (elemento.getBoundingClientRect().top < window.innerHeight) { elemento.classList.add("em-foco"); }
      });
    };
    window.addEventListener("scroll", noFim, { passive: true });
    noFim();
  } else {
    aparecem.forEach(function (elemento) { elemento.classList.add("em-foco"); });
  }

  // 2. Como funciona: o passo no meio da tela acende, e a tela ao lado (em telas largas) troca para a dele.
  var passos = Array.prototype.slice.call(document.querySelectorAll(".passo"));
  var telas = Array.prototype.slice.call(document.querySelectorAll(".passos__tela .mini"));
  function ativar(indice) {
    passos.forEach(function (passo, i) { passo.classList.toggle("ativo", i === indice); });
    telas.forEach(function (tela, i) { tela.classList.toggle("ativa", i === indice); });
  }
  if (passos.length) {
    ativar(0);
    if (temObservador) {
      var observadorDosPassos = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
          if (entrada.isIntersecting) { ativar(passos.indexOf(entrada.target)); }
        });
      }, { rootMargin: "-40% 0px -45% 0px" });
      passos.forEach(function (passo) { observadorDosPassos.observe(passo); });
    }
  }

  // 3. Perguntas frequentes: abre e fecha; a altura e o giro do ícone são do CSS. Um endereço com a resposta (#p3) chega
  //    com a pergunta já aberta, para quem recebe o link pelo WhatsApp.
  Array.prototype.forEach.call(document.querySelectorAll(".pergunta__botao"), function (botao) {
    botao.addEventListener("click", function () {
      var aberta = botao.closest(".pergunta").classList.toggle("aberta");
      botao.setAttribute("aria-expanded", aberta ? "true" : "false");
    });
  });
  function abrirPeloEndereco() {
    var corpo = location.hash.length > 1 ? document.getElementById(location.hash.slice(1)) : null;
    if (!corpo || !corpo.classList.contains("pergunta__corpo")) { return; }
    var pergunta = corpo.closest(".pergunta");
    pergunta.classList.add("aberta");
    pergunta.querySelector(".pergunta__botao").setAttribute("aria-expanded", "true");
  }
  abrirPeloEndereco();
  window.addEventListener("hashchange", abrirPeloEndereco);

  // 4. O cabeçalho ganha a linha e a sombra depois que a página rola.
  var cabecalho = document.querySelector(".cabecalho");
  if (cabecalho) {
    var marcar = function () { cabecalho.classList.toggle("rolou", window.scrollY > 8); };
    window.addEventListener("scroll", marcar, { passive: true });
    marcar();
  }
})();
