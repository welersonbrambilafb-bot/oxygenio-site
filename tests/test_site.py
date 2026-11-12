"""O site da Oxygênio Automação: páginas estáticas, sem cookie, sem formulário, sem nada de fora, com um script próprio e
pequeno para o movimento; e, enquanto não for público de verdade, com o que falta decidir à vista (LEIA-ME.md).
Veio do teste da apresentação antiga, que morava junto do emissor, adaptado para a pasta nova e para mais de uma página."""

from __future__ import annotations

import functools
import http.server
import itertools
import os
import re
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
COMERCIAIS = ["index.html", "emissao-nacional.html", "build.html"]
LEGAIS = ["termos-de-uso.html", "privacidade.html", "lgpd.html"]
PAGINAS = COMERCIAIS + LEGAIS
HTML = {nome: (RAIZ / nome).read_text(encoding="utf-8") for nome in PAGINAS}
TOKENS = (RAIZ / "estilos.css").read_text(encoding="utf-8")
FOLHA = (RAIZ / "pagina.css").read_text(encoding="utf-8")
SCRIPT = (RAIZ / "movimento.js").read_text(encoding="utf-8")
ENTRAR = "https://emissor.oxygenioautomacao.com.br/"
WHATSAPP = "https://wa.me/5544991160421"
CONTRATAR = 'Contratar<span class="tudo-oculto"> (abre o WhatsApp)</span>'
INDEPENDENCIA = "sem vínculo com a Receita Federal, com prefeituras nem com o Portal Nacional"
# O que falta para publicar, por página (LEIA-ME.md). Decidiu um, tire daqui e da página.
# A faixa de prévia e o rodapé, em toda página. Endereço: só "Cianorte, Paraná" (decisão do dono, 08/11/2026). O e-mail
# do encarregado fica num endereço do domínio da empresa, ainda a criar (decisão do dono, 12/11/2026): marcado até existir.
RODAPE_A_CONFIRMAR = {"a confirmar", "e-mail a confirmar"}
LEGAL_A_CONFIRMAR = {"revisão de advogado a confirmar", "razão social a confirmar"}
A_CONFIRMAR: dict[str, set[str]] = {
    "index.html": RODAPE_A_CONFIRMAR,
    # decididos em 12/11/2026: os três planos, a condição dos três primeiros meses, sem promessa de tempo, a lista do
    # DMS conferida pelo dono e as prefeituras "em ampliação"
    "emissao-nacional.html": RODAPE_A_CONFIRMAR,
    "build.html": RODAPE_A_CONFIRMAR,
    "termos-de-uso.html": RODAPE_A_CONFIRMAR | LEGAL_A_CONFIRMAR | {
        "CNPJ a confirmar", "limite de responsabilidade a confirmar", "apagamento a confirmar",
        "prazo de aviso a confirmar", "foro a confirmar"},
    "privacidade.html": RODAPE_A_CONFIRMAR | LEGAL_A_CONFIRMAR | {
        "CNPJ a confirmar", "papéis a confirmar com advogado", "local do servidor a confirmar", "apagamento a confirmar",
        "prazo de guarda a confirmar", "prazo de resposta a confirmar", "encarregado a confirmar"},
    "lgpd.html": RODAPE_A_CONFIRMAR | LEGAL_A_CONFIRMAR | {"papéis a confirmar com advogado", "apagamento a confirmar",
                                                          "prazo de resposta a confirmar", "encarregado a confirmar"},
}
BLOCO_ROOT = re.compile(r"^:root \{.*?^\}\n", re.DOTALL | re.MULTILINE)


def _texto(pagina: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pagina)).casefold()


def _cabecalho(pagina: str) -> str:
    return pagina[pagina.index('<header class="cabecalho">'):pagina.index("</header>")]


def _cnpj_valido(cnpj: str) -> bool:
    numeros = [int(c) for c in cnpj if c.isdigit()]
    if len(numeros) != 14 or len(set(numeros)) == 1:
        return False
    for tamanho in (12, 13):
        pesos = list(range(tamanho - 7, 1, -1)) + list(range(9, 1, -1))
        soma = sum(n * p for n, p in zip(numeros[:tamanho], pesos, strict=True))
        if numeros[tamanho] != (0 if soma % 11 < 2 else 11 - soma % 11):
            return False
    return True


@pytest.mark.parametrize("nome", PAGINAS)
def test_a_pagina_nao_depende_de_nada_de_fora(nome: str) -> None:
    pagina = HTML[nome]
    assert "<form" not in pagina and "<iframe" not in pagina
    assert "style=" not in pagina and "onclick" not in pagina  # a política da página recusa estilo e script em linha
    assert re.findall(r"<script\b[^>]*>", pagina) == ['<script src="movimento.js" defer>']
    enderecos = re.findall(r'(?:src|href)="([^"]+)"', pagina)
    de_fora = {e for e in enderecos if "//" in e}
    assert all(e == ENTRAR or e.startswith(WHATSAPP + "?text=") for e in de_fora), de_fora
    for folha in (TOKENS, FOLHA):
        assert not re.search(r"https?://|@import", folha)
    for e in enderecos:
        if e in de_fora:
            continue
        arquivo, _, ancora = e.partition("#")
        if arquivo:
            assert (RAIZ / arquivo).is_file(), e
        if ancora:
            alvo = HTML.get(arquivo, pagina) if arquivo else pagina
            assert ancora in set(re.findall(r'\bid="([^"]+)"', alvo)), e
    for e in re.findall(r'url\("([^"]+)"\)', TOKENS + FOLHA):
        assert (RAIZ / e).is_file(), e


@pytest.mark.parametrize("nome", PAGINAS)
def test_a_politica_da_pagina_e_fechada(nome: str) -> None:
    politica = re.search(r'Content-Security-Policy" content="([^"]+)"', HTML[nome])
    assert politica and "default-src 'none'" in politica.group(1) and "form-action 'none'" in politica.group(1)
    assert "script-src 'self'" in politica.group(1) and "unsafe" not in politica.group(1)


def test_as_cores_ficam_so_no_root() -> None:
    assert BLOCO_ROOT.search(TOKENS), "estilos.css tem o :root do app"
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", BLOCO_ROOT.sub("", TOKENS)), "cor fora do :root (estilos.css)"
    assert BLOCO_ROOT.search(FOLHA), "pagina.css começa com o :root dele"
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", BLOCO_ROOT.sub("", FOLHA)), "cor fora do :root (pagina.css)"
    assert "color-scheme: light;" in TOKENS and "prefers-color-scheme" not in FOLHA  # sem modo escuro (decisão do dono)


def test_o_movimento_tem_tokens_uma_chave_e_cabe_no_orcamento() -> None:
    """Durações e curva num lugar só; uma chave desliga tudo; o script fica bem abaixo dos 60 KB do orçamento."""
    for token in ("--mov-entrada", "--mov-hover", "--mov-suave", "--mov-passo", "--mov-maquete", "--mov-pausa", "--mov-cena", "--mov-tela",
                  "--mov-esmaecer", "--mov-gesto", "--mov-espera", "--mov-gesto-curva"):
        assert f"{token}:" in FOLHA, token
    for cena in re.findall(r"--mov-(?:maquete|cena): (\d+)ms", FOLHA):  # cena que começa sozinha: até 5 s, senão pede botão de pausa
        assert int(cena) <= 5000, cena
    assert "var MOVIMENTO = true;" in SCRIPT and 'data-movimento="desligado"' in FOLHA
    assert "prefers-reduced-motion: reduce" in FOLHA and "prefers-reduced-motion" in SCRIPT
    # com a chave desligada, tudo parado de verdade (U-16); com a preferência do sistema, as maquetes também param, mas
    # fica a versão suave: o esmaecer e os traços (decisão do dono, 09/11/2026), sem o arco do cadeado se mexer
    parados = re.findall(r'(?:html\[data-movimento="desligado"\]|@media \(prefers-reduced-motion: reduce\)) \{[^}]*?--mov-entrada: 1ms;[^}]*?--mov-maquete: 1ms;[^}]*?--mov-pausa: 0ms; --mov-cena: 1ms; --mov-tela: 1ms;', FOLHA)
    assert len(parados) == 2, parados
    desligado = re.search(r'html\[data-movimento="desligado"\] \{[^}]*\}', FOLHA).group()
    assert all(f"{t}: " in desligado for t in ("--mov-esmaecer", "--mov-gesto", "--mov-espera")), desligado
    suave = FOLHA[FOLHA.index("@media (prefers-reduced-motion: reduce)"):]
    suave = suave[:suave.index("\n}")]
    assert not any(t in suave for t in ("--mov-esmaecer", "--mov-gesto", "--mov-espera")), suave
    assert ".cadeado__arco { transform: none; transition: none; }" in suave
    assert 'html.setAttribute("data-movimento", "suave")' in SCRIPT and '"em-foco"' in SCRIPT
    assert "@media print" in FOLHA and "stroke-dasharray: 60" not in FOLHA  # impressão prevista (U-04); traço inteiro (U-05)
    assert "view-transition-name: cabecalho" in FOLHA and "::view-transition-group(cabecalho) { animation: none; }" in FOLHA  # M-15
    assert "hashchange" in SCRIPT and 'classList.contains("pergunta__corpo")' in SCRIPT  # a pergunta aberta pelo endereço (U-15)
    assert not re.search(r"animation: \w+ \.?\d+m?s\b", FOLHA), "duração fixa fora dos tokens: não para com o movimento reduzido"
    assert "@keyframes assentar { from { transform: translateY(var(--mov-desloc)); } }" in FOLHA  # o texto do destaque nunca some (U-03)
    assert (RAIZ / "movimento.js").stat().st_size <= 60 * 1024
    assert "IntersectionObserver" in SCRIPT and "fetch(" not in SCRIPT and "XMLHttpRequest" not in SCRIPT


def test_fontes_locais_com_a_licenca() -> None:
    licencas = (RAIZ / "fontes/LICENCAS.txt").read_text(encoding="utf-8")
    for nome in ("PlusJakartaSans-latin-v1.woff2", "IBMPlexMono-Regular-latin-v1.woff2"):
        assert (RAIZ / "fontes" / nome).is_file() and nome in licencas, nome
    assert "SIL OPEN FONT LICENSE" in licencas
    assert TOKENS.count("@font-face") == 3 and "fonts.googleapis" not in TOKENS + FOLHA


@pytest.mark.parametrize("nome", PAGINAS)
def test_as_logos_sao_as_combinadas(nome: str) -> None:
    """O O² do app das DMS é a marca principal; o emissor usa o ícone com NFS-e escrito; o símbolo solto não entra;
    a logo do governo (NFSe verde e amarela) não entra; sem foto da tela, que ficava quadriculada."""
    nomes = {p.name for p in (RAIZ / "imagens").iterdir()}
    assert nomes == {"check.svg", "oxygenio_badge_192.png", "oxygenio_icon_256.png", "oxygenio_nfse_icon.svg"}
    cabecalho = _cabecalho(HTML[nome])
    assert 'src="imagens/oxygenio_badge_192.png"' in cabecalho and "Oxygênio" in cabecalho
    assert 'rel="icon" href="imagens/oxygenio_badge_192.png"' in HTML[nome]


@pytest.mark.parametrize("nome", PAGINAS)
def test_entrar_vai_ao_emissor_e_contratar_ao_whatsapp(nome: str) -> None:
    pagina = HTML[nome]
    # U-13 (lote 8b, aprovado em 08/11/2026): dentro do Contratar, um aviso só para leitor de tela diz que abre o WhatsApp;
    # a regex pega o conteúdo inteiro do botão, para o teste continuar conferindo cada um
    principais = re.findall(r'<a class="botao" href="([^"]+)">(.*?)</a>', pagina)
    assert principais and all(texto == CONTRATAR and destino.startswith(WHATSAPP + "?text=") for destino, texto in principais)
    secundarios = re.findall(r'<a class="botao discreto" href="([^"]+)">([^<]+)</a>', pagina)
    if nome == "build.html":  # a página do DMS não tem Entrar: ele leva ao login do Emissor (decisão do dono, 12/11/2026)
        assert not secundarios and ">Entrar<" not in pagina
        return
    assert secundarios and all(texto == "Entrar" and destino == ENTRAR for destino, texto in secundarios)
    whats = re.findall(r'<a class="botao whatsapp" href="([^"]+)">', pagina)
    assert len(whats) <= 1 and all(w.startswith(WHATSAPP + "?text=") for w in whats)
    acoes = _cabecalho(pagina)
    acoes = acoes[acoes.index("cabecalho__acoes"):]
    assert acoes.index(">Entrar<") < acoes.index(">Contratar<")


def test_as_secoes_do_emissor_na_ordem_combinada() -> None:
    pagina = HTML["emissao-nacional.html"]
    ids = re.findall(r'<section id="([^"]+)"', pagina)
    # o bloco do DMS depois das perguntas (decisão do dono, 12/11/2026): quem decide sobre o Emissor não encontra outro
    # produto no meio do caminho
    assert ids == ["beneficios", "como-funciona", "recursos", "seguranca", "planos", "perguntas", "dms", "contato"]
    assert pagina.count(INDEPENDENCIA) == 2  # Segurança e rodapé
    assert "emita e baixe" in _texto(pagina) and "copiar nota" in _texto(pagina)
    # a maquete do destaque conta o fluxo (copiar, trocar o valor, conferir, emitir) e a descrição da figura diz o mesmo;
    # só rótulos na conferência, sem valor de ISS (decisão de 08/11/2026: regra fiscal não é do design)
    maquete = re.search(r'<figure class="maquete maquete--emissor" role="img" aria-label="([^"]+)">.*?</figure>', pagina, re.DOTALL)
    assert maquete
    for trecho in ("Copiar nota", "Copiada da nº 34", "maquete__valor-antigo", "maquete__valor-novo", "maquete__conferencia"):
        assert trecho in maquete.group(), trecho
    assert re.findall(r"<li>(?:<svg[^>]*>.*?</svg>)([^<]+)</li>", maquete.group()) == ["ISS", "Retenções", "Líquido"]
    for palavra in ("copiada", "valor", "conferência", "Emitida"):
        assert palavra in maquete.group(1), palavra
    # a conferência lado a lado (lote 5): os títulos são os da tela do app, as linhas aprovadas pelo dono, sem valor de ISS.
    # Rodada de 11/11: o app não marca campo por campo (quem compara é a pessoa) e o aceite do ISS retido com CPF vem antes,
    # no formulário; o aviso da figura é um dos alertas que o app mostra de verdade
    recursos = re.search(r'<section id="recursos".*?</section>', pagina, re.DOTALL)
    assert recursos and recursos.group().index('class="conferencia aparece"') < recursos.group().index('class="recursos"')
    for trecho in ("O que o app vai enviar", "O que o portal mostra", "Valor do serviço", "Tomador", "ISS retido", "Valor líquido",
                   "Alíquota do ISS acima do comum: confira antes de emitir.",
                   "lado a lado o que o app vai enviar e o que o portal mostra",
                   "o app avisa ou pede o seu aceite antes de seguir"):
        assert trecho in recursos.group(), trecho
    assert len(re.findall(r'class="conferencia__linha"', recursos.group())) == 4
    assert "conferencia__ok" not in recursos.group()
    assert "alíquota foge do comum" not in pagina


def test_o_produto_das_dms_fala_so_do_que_faz() -> None:
    dms = re.search(r'<section id="dms".*?</section>', HTML["emissao-nacional.html"], re.DOTALL)
    assert dms
    assert "Encerramento das DMS" in dms.group() and "Aplicativo de computador, por enquanto" in dms.group()
    assert ">Contratar<" in dms.group() and ">Entrar<" not in dms.group() and 'href="build.html"' in dms.group()
    assert 'src="imagens/oxygenio_icon_256.png"' in dms.group()
    def so_o_conteudo(pagina: str) -> str:  # o rodapé tem o endereço da empresa; a regra é sobre o que se diz do Build
        return pagina[:pagina.index('<footer class="rodape">')]

    for trecho in (dms.group(), so_o_conteudo(HTML["build.html"]), so_o_conteudo(HTML["index.html"])):
        for fora in ("Cianorte", "2025", "70 ", "Elotech", "Oxy "):  # decisão de 03/11/2026: sem cidade, prazo nem uso
            assert fora not in trecho, fora
        for faz in ("serviços prestados", "serviços tomados", "guia de ISS", "CND", "XML"):
            assert faz in trecho, faz
    build = HTML["build.html"]
    assert re.findall(r'<section id="([^"]+)"', build) == ["o-que-faz", "conferencia", "como-funciona", "limites",
                                                            "perguntas", "emissor", "contato"]
    assert "Aplicativo de computador, por enquanto" in build and "Windows" in build
    # sem ano nem contagem de empresas em lugar nenhum do que fala do Build, maquetes incluídas (decisão do dono, 08/11/2026)
    assert not re.search(r"\b20\d\d\b|\b\d+ empresas\b|\b\d+ de \d+\b", so_o_conteudo(build))
    assert 'class="parada"' in build and 'class="cadeado"' not in build  # o sinal de parada, não o cadeado (M-14)
    assert build.count("maquete__cartao--atencao") == 1
    assert len(re.findall(r'<span class="mini__chip(?: mini__chip--arquivo)?"><svg', build)) == 4  # as etiquetas com o check (M-13)


def test_a_pagina_inicial_mostra_as_duas_pistas_e_os_cartoes_levam_ao_produto() -> None:
    """Lote 6 (M-11, M-12): as pistas só com frases aprovadas pelo dono, sem mês, ano nem número; um link por cartão."""
    pagina = HTML["index.html"]
    pistas = re.search(r'<figure class="pistas" role="img" aria-label="([^"]+)">.*?</figure>', pagina, re.DOTALL)
    assert pistas and pistas.group().index(">Notas dos clientes</p>") < pistas.group().index(">DMS do mês</p>")
    passos = re.findall(r'<li><span class="pista__numero">\d</span>([^<]+)</li>', pistas.group())
    assert passos == ["Copiar nota", "Conferência: ISS, retenções e líquido", "Emitida; XML e PDF no computador",
                      "Encerra a DMS", "Gera a guia de ISS e emite a CND", "Mostra o que mudou desde o último fechamento"]
    assert pistas.group().count("O contador confere.") == 1 and "o contador confere" in pistas.group(1)
    conteudo = pagina[pagina.index('<main id="principal">'):pagina.index('<footer class="rodape">')]
    assert not re.search(r"\b20\d\d\b|\b\d+ empresas\b", conteudo)  # sem ano nem contagem de empresas na página da empresa
    cartoes = re.findall(r'<article class="cartao-produto aparece">.*?</article>', pagina, re.DOTALL)
    assert len(cartoes) == 2
    for cartao, destino in zip(cartoes, ("emissao-nacional.html", "build.html"), strict=True):
        assert cartao.count("<a ") == 1 and f'href="{destino}"' in cartao, destino  # o link esticado cobre o cartão inteiro


def _cabecalho_sem_o_que_muda(pagina: str) -> str:
    """O cabeçalho é o mesmo em toda página; só mudam a página marcada no menu e a mensagem pronta do WhatsApp."""
    cabecalho = _cabecalho(pagina).replace(' aria-current="page"', "")
    cabecalho = re.sub(r'\n\s*<a class="botao discreto" href="[^"]+">Entrar</a>', "", cabecalho)  # o DMS não tem Entrar
    return re.sub(r"\?text=[^\"]*", "", cabecalho)


def test_cabecalho_e_rodape_iguais_em_todas_as_paginas() -> None:
    cabecalhos = {_cabecalho_sem_o_que_muda(p) for p in HTML.values()}
    assert len(cabecalhos) == 1, "cabeçalho diferente entre páginas"
    rodapes = {p[p.index('<footer class="rodape">'):] for p in HTML.values()}
    assert len(rodapes) == 1, "rodapé diferente entre páginas"
    for nome, pagina in HTML.items():
        assert pagina.count(' aria-current="page"') == (1 if nome in COMERCIAIS else 0), nome
        if nome in COMERCIAIS:
            assert f'<a href="{nome}" aria-current="page">' in pagina
    menu = _cabecalho(HTML["index.html"])
    assert re.findall(r'<nav class="cabecalho__menu"[^>]*>(.*?)</nav>', menu, re.DOTALL)
    for destino in ("index.html", "emissao-nacional.html", "build.html"):
        assert f'href="{destino}"' in menu, destino


@pytest.mark.parametrize("nome", LEGAIS)
def test_as_paginas_legais_sao_rascunhos_com_data_e_versao(nome: str) -> None:
    pagina = HTML[nome]
    assert '<article class="largura legal">' in pagina
    assert re.search(r'<p class="versao">Versão \d+\.\d+, (rascunho de )?\d{1,2} de [a-zç]+ de \d{4}\.</p>', pagina), nome
    assert '<p class="aviso"><strong>Rascunho.</strong>' in pagina
    assert len(re.findall(r"<h2\b", pagina)) >= 5
    assert "LGPD" in pagina  # as páginas legais nomeiam a lei; as comerciais não (decisão do dono)
    assert "controlador" in pagina.casefold() and "operador" in pagina.casefold()  # os papéis da LGPD, em toda legal
    if nome != "termos-de-uso.html":  # a política e a página simples: direitos, incidente, encarregado e a quem reclamar
        for exigido in (r"art(igo|\.) 18\b", r"art(igo|\.) 48\b", "ANPD", r"gov\.br/anpd", "encarregado"):
            assert re.search(exigido, pagina), (nome, exigido)
    assert nome == "privacidade.html" or 'href="privacidade.html"' in pagina  # as outras remetem à política


@pytest.mark.parametrize("nome", PAGINAS)
def test_o_que_falta_decidir_fica_a_vista_e_a_pagina_nao_se_indexa(nome: str) -> None:
    """Enquanto houver item aqui, a faixa de prévia e o noindex ficam. Quem publica resolve a lista inteira."""
    pagina = HTML[nome]
    marcados = set(re.findall(r'<span class="a-confirmar">([^<]+)</span>', pagina))
    assert marcados == A_CONFIRMAR.get(nome, set()), nome
    assert '<meta name="robots" content="noindex, nofollow">' in pagina
    assert 'class="previa"' in pagina and "ainda não é pública" in pagina


PROIBIDOS = [
    # o que não foi decidido ou não é verdade
    "com certeza", "LGPD", "ponta a ponta", "garant", "100%", "R$", "depoimento", "gratuito", "grátis",
    # o nome da verificação do portal e a região do servidor, montados em pedaços: o dono decidiu que nem os arquivos
    # publicados no GitHub os mostram (12/11/2026)
    "o escritório deixa de conferir", "melhor do mercado", "cap" + "tcha", "Oh" + "io",
    # o tom de anúncio e de texto gerado (briefing de 03/11/2026)
    "revolucion", "potencializ", "transforme", "descubra", "solução completa", "de ponta", "no mundo atual",
    "sem complicação", "em apenas alguns cliques", "mais do que", "não é apenas", "inteligente", "algoritmo", "robô",
    "milhares", "o melhor", "o mais rápido", "!", "emita e envie", " ia ",
]


@pytest.mark.parametrize("nome", COMERCIAIS)
@pytest.mark.parametrize("proibido", PROIBIDOS)
def test_a_pagina_nao_promete_o_que_nao_foi_decidido_nem_soa_como_anuncio(nome: str, proibido: str) -> None:
    assert proibido.casefold() not in _texto(HTML[nome]), (nome, proibido)


@pytest.mark.parametrize("nome", PAGINAS)
def test_o_cnpj_e_o_conferido_e_o_aviso_de_independencia_aparece(nome: str) -> None:
    pagina = HTML[nome]
    numeros = set(re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", pagina))
    assert numeros <= {"69.039.125/0001-21", "11.222.333/0001-81"} and _cnpj_valido("69039125000121")  # o 11.222... é o de exemplo
    rodape = pagina[pagina.index('<footer class="rodape">'):]
    assert INDEPENDENCIA in rodape and "69.039.125/0001-21" in rodape
    assert "<p>Cianorte, Paraná</p>" in rodape and "Pare" + "cis" not in pagina  # só a cidade (decisão do dono, 08/11/2026)
    for destino in ("termos-de-uso.html", "privacidade.html", "lgpd.html"):  # as páginas legais, em todo rodapé
        assert f'href="{destino}"' in rodape, destino
    assert "LGPD" not in re.sub(r"<[^>]+>", "", rodape)  # o link chama "Proteção de dados": a sigla fica fora das comerciais
    assert pagina.count("(44) 99116-0421") <= 1


@pytest.mark.parametrize("nome", PAGINAS)
def test_cabecalho_acessivel_titulos_em_ordem_e_imagens_com_medida(nome: str) -> None:
    pagina = HTML[nome]
    assert '<html lang="pt-BR"' in pagina and re.search(r"<title>Oxyg[êe]nio [^<]+</title>", pagina)
    assert 'name="description"' in pagina and pagina.count("<h1") == 1 and 'class="pular"' in pagina
    niveis = [int(n) for n in re.findall(r"<h([1-6])\b", pagina)]
    assert niveis[0] == 1 and all(b - a <= 1 for a, b in itertools.pairwise(niveis)), niveis
    for imagem in re.findall(r"<img\b[^>]*>", pagina):
        assert 'alt="' in imagem and 'width="' in imagem and 'height="' in imagem, imagem
        assert 'loading="lazy"' not in imagem
    for botao in re.findall(r'<button\b[^>]*class="pergunta__botao"[^>]*>', pagina):
        assert 'aria-expanded="false"' in botao and 'aria-controls="' in botao, botao


@pytest.mark.parametrize("nome", PAGINAS)
def test_cada_pagina_com_o_que_baixa_cabe_no_orcamento(nome: str) -> None:
    """Tudo que o navegador baixa para uma página, somado: bem abaixo do que uma foto só pesava."""
    compartilhado = [RAIZ / "estilos.css", RAIZ / "pagina.css", RAIZ / "movimento.js"]
    compartilhado += [p for pasta in ("fontes", "imagens") for p in (RAIZ / pasta).iterdir() if p.suffix != ".txt"]
    total = (RAIZ / nome).stat().st_size + sum(p.stat().st_size for p in compartilhado)
    assert total <= 160 * 1024, (nome, total)
    servidos = list(RAIZ.glob("*")) + list((RAIZ / "imagens").iterdir())  # o que o site publica (Referencias/ fica fora)
    assert not [p for p in servidos if p.suffix.lower() in (".jpg", ".jpeg")]


# ------------------------------------------------------------------ no navegador
class _Quieto(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_: object) -> None:
        pass


def _servir(pasta: Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quieto, directory=str(pasta)))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor, f"http://127.0.0.1:{servidor.server_address[1]}"


@pytest.fixture
def endereco() -> Iterator[str]:
    servidor, base = _servir(RAIZ)
    yield base
    servidor.shutdown()


def _canal() -> str | None:
    canal = os.environ.get("NFSE_NAVEGADOR_DE_TESTE", "chromium")
    return None if canal == "chromium" else canal


@pytest.mark.navegador
@pytest.mark.parametrize("largura", [360, 768, 1440])
@pytest.mark.parametrize("nome", PAGINAS)
def test_sem_rolagem_lateral_sem_cookie_e_com_os_botoes_a_vista(endereco: str, nome: str, largura: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        nav = p.chromium.launch(channel=_canal(), headless=True)
        contexto = nav.new_context(viewport={"width": largura, "height": 800}, reduced_motion="no-preference")
        pagina = contexto.new_page()
        erros: list[str] = []
        pagina.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
        pedidos: list[str] = []
        pagina.on("request", lambda r: pedidos.append(r.url))
        pagina.goto(f"{endereco}/{nome}", wait_until="networkidle")
        assert pagina.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0
        assert contexto.cookies() == [] and erros == []
        assert all(u.startswith(endereco) for u in pedidos), pedidos
        assert pagina.evaluate("document.fonts.ready.then(() => document.fonts.check('16px \"Plus Jakarta Sans\"'))")
        assert pagina.evaluate("document.documentElement.classList.contains('js')")
        if pagina.locator(".destaque").count():  # o texto do destaque está à vista já no primeiro quadro (U-03), sem esperar
            for seletor in (".destaque h1 > span:last-child", ".destaque__frase", ".destaque__acoes"):
                assert pagina.evaluate(f"getComputedStyle(document.querySelector('{seletor}')).opacity") == "1", seletor
        cabecalho = pagina.locator(".cabecalho__acoes")
        for texto in (("Contratar",) if nome == "build.html" else ("Entrar", "Contratar")):  # o DMS não tem Entrar
            caixa = cabecalho.get_by_role("link", name=texto).bounding_box()
            assert caixa and caixa["x"] >= 0 and caixa["x"] + caixa["width"] <= largura and caixa["y"] < 150
        if nome == "index.html":  # as pistas vêm depois do Contratar no celular e ao lado no computador; tudo aceso ao fim
            contratar = pagina.locator(".destaque .botao").bounding_box()
            pistas = pagina.locator(".pistas").bounding_box()
            assert contratar and pistas
            if largura < 960:
                assert pistas["y"] > contratar["y"] + contratar["height"] and contratar["y"] + contratar["height"] <= 800
            else:
                assert pistas["x"] > contratar["x"] + contratar["width"]
            pagina.wait_for_timeout(2500)
            assert pagina.evaluate("[...document.querySelectorAll('.pista__passos li, .pista__selo')].every(e => getComputedStyle(e).opacity === '1')")
        marca = pagina.locator(".cabecalho .marca").bounding_box()
        entrar = cabecalho.locator("a").first.bounding_box()  # o Entrar; na página do DMS, que não o tem, o Contratar
        assert marca and entrar and marca["x"] + marca["width"] + 8 <= entrar["x"], "a marca encosta no botão (U-02)"
        links = pagina.locator(".cabecalho__menu a").all()  # as três páginas à vista em toda largura, com 44 px de toque (U-01, U-06)
        assert len(links) == 3
        fim_do_cabecalho = pagina.locator(".cabecalho").bounding_box()["y"] + pagina.locator(".cabecalho").bounding_box()["height"]
        for link in links:
            caixa = link.bounding_box()
            assert caixa and caixa["height"] >= 44 and caixa["x"] >= 0 and caixa["x"] + caixa["width"] <= largura, caixa
            assert caixa["y"] + caixa["height"] <= fim_do_cabecalho + 1, (caixa, fim_do_cabecalho)  # dentro do cabeçalho preso
        if nome in COMERCIAIS:
            assert pagina.locator('.cabecalho__menu a[aria-current="page"]').get_attribute("href") == nome
        if nome == "emissao-nacional.html" and largura == 1440:  # a cena da maquete termina sozinha, em até 5 s, no estado final
            pagina.wait_for_timeout(5200)
            for seletor, esperado in ((".maquete__emitida", "1"), (".maquete__valor-novo", "1"), (".maquete__nota--nova", "1"),
                                      (".maquete__processando", "0"), (".maquete__valor-antigo", "0")):
                assert pagina.evaluate(f"getComputedStyle(document.querySelector('{seletor}')).opacity") == esperado, seletor
            assert pagina.evaluate("[...document.querySelectorAll('.maquete__conferencia path')].every(p => getComputedStyle(p).strokeDashoffset === '0px')")
            # a tela do passo 2 se preenche quando o passo fica ativo: a nº 35 nasce "pronta para conferir" (M-03)
            # o passo acende quando entra na faixa do meio da tela (movimento.js: rootMargin -40% / -45%)
            pagina.evaluate("window.scrollBy({top: document.querySelector('#passo-2').getBoundingClientRect().top - innerHeight * .42, behavior: 'instant'})")
            pagina.wait_for_timeout(1500)
            assert pagina.locator("#passo-2").get_attribute("class") == "passo ativo"
            nova = pagina.locator(".passos__tela .mini.ativa .mini__linha--nova")
            assert nova.count() == 1 and "Nota nº 35" in nova.inner_text()
            assert pagina.evaluate("getComputedStyle(document.querySelector('.passos__tela .mini.ativa .mini__linha--nova')).opacity") == "1"
            pagina.evaluate("window.scrollTo(0, 0)")
        if nome == "emissao-nacional.html" and largura == 1440:  # impresso, tudo à vista: nada transparente, perguntas abertas (U-04)
            pagina.emulate_media(media="print")
            assert pagina.evaluate("[...document.querySelectorAll('.aparece:not(.visivel)')].every(e => getComputedStyle(e).opacity === '1')")
            assert pagina.evaluate("getComputedStyle(document.querySelector('.pergunta__texto')).visibility") == "visible"
            assert pagina.evaluate("getComputedStyle(document.querySelector('.cabecalho')).position") == "static"
            pagina.emulate_media(media="screen")
        # o foco pelo teclado começa no "Ir para o conteúdo" e é visível
        pagina.keyboard.press("Tab")
        assert pagina.evaluate("document.activeElement.className") == "pular"
        if pagina.locator(".pergunta__botao").count():
            # a pergunta abre pelo teclado e a resposta passa a ser lida
            botao = pagina.locator(".pergunta__botao").first
            botao.focus()
            pagina.keyboard.press("Enter")
            assert botao.get_attribute("aria-expanded") == "true"
            pagina.locator(".pergunta__texto p").first.wait_for(state="visible")
            # um endereço com a resposta (#p3) chega com a pergunta aberta (U-15)
            pagina.evaluate("location.hash = '#p3'")
            pagina.wait_for_timeout(300)
            assert pagina.locator("#p3-botao").get_attribute("aria-expanded") == "true"
            pagina.locator("#p3 p").wait_for(state="visible")
            pagina.evaluate("history.replaceState(null, '', location.pathname); window.scrollTo(0, 0)")
        if nome == "emissao-nacional.html":  # a âncora para no conteúdo, não atrás do cabeçalho (que é mais alto no celular)
            pagina.evaluate("location.hash = '#planos'")
            pagina.wait_for_timeout(900)
            topo_secao = pagina.evaluate("document.querySelector('#planos').getBoundingClientRect().top")
            fim_cabecalho = pagina.evaluate("document.querySelector('.cabecalho').getBoundingClientRect().bottom")
            assert topo_secao >= fim_cabecalho - 1, (topo_secao, fim_cabecalho)
            pagina.evaluate("history.replaceState(null, '', location.pathname); window.scrollTo(0, 0)")
        altura_total = pagina.evaluate("document.documentElement.scrollHeight")
        for y in range(0, altura_total, 300):  # rola como uma pessoa, de pouco em pouco
            pagina.evaluate(f"window.scrollTo(0, {y})")
            pagina.wait_for_timeout(120)
        pagina.wait_for_timeout(3500)  # a cena mais longa (o cadeado e os quatro fatos) termina em uns 3 s
        assert pagina.locator(".aparece:not(.visivel)").count() == 0
        assert pagina.locator(".aparece:not(.em-foco)").count() == 0
        if pagina.locator(".conferencia").count():  # depois de rolar, a conferência está desenhada e o fluxo inteiro à vista
            assert pagina.evaluate("[...document.querySelectorAll('.conferencia__ok path')].every(p => getComputedStyle(p).strokeDashoffset === '0px')")
            assert pagina.evaluate("[...document.querySelectorAll('.conferencia__aviso, .fluxo > *')].every(e => getComputedStyle(e).opacity === '1')")
        if pagina.locator(".fatos").count():  # os fatos chegaram e as bordas acenderam; os ícones dos recursos, desenhados (M-07, M-06)
            assert pagina.evaluate("[...document.querySelectorAll('.fatos li')].every(e => getComputedStyle(e).opacity === '1')")
            assert pagina.evaluate("[...document.querySelectorAll('.recurso__icone svg *')].every(e => getComputedStyle(e).strokeDashoffset === '0px')")
        if pagina.locator(".parada").count():  # no Build: o sinal de parada desenhado e as etiquetas do progresso todas à vista
            assert pagina.evaluate("[...document.querySelectorAll('.parada path, .maquete__progresso path')].every(p => getComputedStyle(p).strokeDashoffset === '0px')")
            assert pagina.evaluate("[...document.querySelectorAll('.maquete__progresso .mini__chip')].every(e => getComputedStyle(e).opacity === '1')")
        nav.close()


@pytest.mark.navegador
def test_com_o_movimento_desligado_tudo_aparece_parado() -> None:
    """A chave única (MOVIMENTO = false) e a preferência do sistema deixam a página inteira à vista, sem transição."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as pasta:
        copia = Path(pasta) / "site"
        copia.mkdir()
        for nome in [*PAGINAS, "estilos.css", "pagina.css", "movimento.js"]:  # só o que o site serve, nada do resto da pasta
            shutil.copyfile(RAIZ / nome, copia / nome)
        for subpasta in ("fontes", "imagens"):
            shutil.copytree(RAIZ / subpasta, copia / subpasta)
        script = (copia / "movimento.js").read_text(encoding="utf-8").replace("var MOVIMENTO = true;", "var MOVIMENTO = false;")
        (copia / "movimento.js").write_text(script, encoding="utf-8")
        _conferir_parado(copia)


def _conferir_parado(copia: Path) -> None:
    from playwright.sync_api import sync_playwright

    servidor, base = _servir(copia)
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch(channel=_canal(), headless=True)
            for reduzido in (False, True):
                contexto = nav.new_context(viewport={"width": 1200, "height": 800},
                                           reduced_motion="reduce" if reduzido else "no-preference")
                pagina = contexto.new_page()
                pagina.goto(f"{base}/emissao-nacional.html", wait_until="networkidle")
                assert pagina.evaluate("document.documentElement.dataset.movimento") == "desligado"
                assert pagina.locator(".aparece:not(.visivel)").count() == 0
                assert pagina.evaluate("getComputedStyle(document.querySelector('.beneficio')).opacity") == "1"
                # a cena da maquete abre direto no estado final: nº 35 com o valor novo, os três conferidos, Emitida
                for seletor in (".maquete__emitida", ".maquete__nota--nova", ".maquete__valor-novo", ".maquete__nota--anterior"):
                    assert pagina.evaluate(f"getComputedStyle(document.querySelector('{seletor}')).opacity") == "1", seletor
                for seletor in (".maquete__processando", ".maquete__valor-antigo"):
                    assert pagina.evaluate(f"getComputedStyle(document.querySelector('{seletor}')).opacity") == "0", seletor
                assert pagina.evaluate("[...document.querySelectorAll('.maquete__conferencia path, .maquete__emitida path')]"
                                       ".every(p => getComputedStyle(p).strokeDashoffset === '0px')")
                # as telas dos passos: tudo preenchido e à vista, inclusive a nº 35 e os arquivos (M-03)
                assert pagina.evaluate("[...document.querySelectorAll('.passos__tela .mini.ativa *')]"
                                       ".every(e => getComputedStyle(e).opacity === '1' && !/100%/.test(getComputedStyle(e).clipPath))")
                assert pagina.locator(".passos__tela .mini__linha--nova").count() == 1
                assert pagina.locator(".passo .mini .mini__linha--nova").count() == 1  # a cópia do celular também
                # a conferência e os fluxos (lote 5): checks desenhados, aviso e todas as peças à vista
                assert pagina.evaluate("[...document.querySelectorAll('.conferencia__ok path')].every(p => getComputedStyle(p).strokeDashoffset === '0px')")
                assert pagina.evaluate("[...document.querySelectorAll('.conferencia__aviso, .fluxo > *')].every(e => getComputedStyle(e).opacity === '1')")
                assert pagina.evaluate("[...document.querySelectorAll('.fluxo__seta')].every(e => getComputedStyle(e).transform === 'none')")
                pagina.goto(f"{base}/index.html", wait_until="networkidle")  # as pistas da página inicial: acesas desde o início
                assert pagina.evaluate("[...document.querySelectorAll('.pista__passos li, .pista__selo, .pistas')].every(e => getComputedStyle(e).opacity === '1')")
                contexto.close()
            nav.close()
    finally:
        servidor.shutdown()


def test_nada_do_emissor_no_repositorio() -> None:
    """No GitHub só o site (decisão do dono, 08/11/2026): nenhum arquivo versionado cita o código do emissor de NFS-e nem o
    do Build, por nome de pasta, caminho ou módulo. A lista é montada em pedaços para este arquivo não se acusar."""
    import subprocess

    versionados = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=True).stdout.decode().split("\0")
    proibidos = ["nfse" + "-app", "src/" + "nfse", "motor" + "_atual", "site_" + "comercial", "Oxygenio" + "_Build",
                 "key" + "ring", "segre" + "dos/", "C:\\Automacoes", "C:\\Users"]
    for caminho in filter(None, versionados):
        arquivo = RAIZ / caminho
        if arquivo.suffix in {".woff2", ".woff", ".png", ".jpg", ".ico"}:
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for palavra in proibidos:
            assert palavra not in texto, (caminho, palavra)
    for pasta in ("docs", "Referencias"):
        assert not any(c.startswith(pasta + "/") for c in versionados), pasta
    for caminho in filter(None, versionados):  # e as duas palavras que o dono escondeu do GitHub (12/11/2026)
        arquivo = RAIZ / caminho
        if arquivo.suffix in {".woff2", ".woff", ".png", ".jpg", ".ico"}:
            continue
        texto = arquivo.read_text(encoding="utf-8").casefold()
        for palavra in ("cap" + "tcha", "oh" + "io"):
            assert palavra not in texto, (caminho, palavra)


@pytest.mark.navegador
def test_a_cena_espera_o_meio_da_tela_e_a_versao_suave_nao_desloca_nada(endereco: str) -> None:
    """Lote 9 (09/11/2026): o cadeado não começa com a seção no pé da tela, só quando ela chega perto do meio; e, com o
    sistema pedindo menos movimento, a página fica na versão suave: maquete no estado final, nada se desloca, mas o check
    se desenha e os fatos chegam."""
    from playwright.sync_api import sync_playwright

    def levar(pagina: object, fracao: float) -> None:  # põe o topo da seção de segurança nesta fração da altura da tela
        pagina.evaluate(f"window.scrollBy({{top: document.querySelector('.seguranca').getBoundingClientRect().top - innerHeight * {fracao}, behavior: 'instant'}})")

    check = "getComputedStyle(document.querySelector('.cadeado__check')).strokeDashoffset"
    arco = "new DOMMatrix(getComputedStyle(document.querySelector('.cadeado__arco')).transform).f"  # quanto o arco está acima
    with sync_playwright() as p:
        nav = p.chromium.launch(channel=_canal(), headless=True)
        for reduzido in (False, True):
            contexto = nav.new_context(viewport={"width": 1440, "height": 800}, reduced_motion="reduce" if reduzido else "no-preference")
            pagina = contexto.new_page()
            pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
            assert pagina.evaluate("document.documentElement.dataset.movimento") == ("suave" if reduzido else "ligado")
            if reduzido:  # a maquete do destaque abre no estado final, como antes
                for seletor in (".maquete__emitida", ".maquete__valor-novo"):
                    assert pagina.evaluate(f"getComputedStyle(document.querySelector('{seletor}')).opacity") == "1", seletor
            levar(pagina, .75)  # a seção apareceu no pé da tela (abaixo da linha de 65%): o bloco esmaece, a cena espera
            pagina.wait_for_timeout(1200)
            classes = pagina.locator(".seguranca").get_attribute("class")
            assert "visivel" in classes and "em-foco" not in classes, classes
            assert pagina.evaluate(check) == "12px"
            levar(pagina, .4)  # perto do meio: a cena começa, o check vem depois do arco
            pagina.wait_for_timeout(500)
            assert "em-foco" in pagina.locator(".seguranca").get_attribute("class")
            assert pagina.evaluate(check) == "12px"
            if reduzido:  # na versão suave o arco nunca se mexe e nenhum bloco se desloca
                assert pagina.evaluate(arco) == 0
                assert pagina.evaluate("[...document.querySelectorAll('.aparece, .fatos li')].every(e => new DOMMatrix(getComputedStyle(e).transform).f === 0)")
            else:
                assert pagina.evaluate(arco) < 0  # ainda descendo
            pagina.wait_for_timeout(3000)
            assert pagina.evaluate(check) == "0px"
            assert pagina.evaluate(arco) == 0  # fechado
            assert pagina.evaluate("[...document.querySelectorAll('.fatos li')].every(e => getComputedStyle(e).opacity === '1')")
            contexto.close()
        nav.close()


# ------------------------------------------------------------------ L1 (12/11/2026): segurança dita como ela é
# Rodada de 11/11/2026 (docs/decisoes-site-2026-11-11.md): o servidor do emissor abre as senhas dos portais para emitir,
# o Build não tem cofre nem senha-mestra, o bloqueio por tentativas freia a entrada sem trancar a conta, e o Build manda o
# CNPJ a serviços públicos de consulta quando a pessoa pede. O site diz isso, e não o contrário.
@pytest.mark.parametrize("nome", PAGINAS)
def test_sem_promessa_de_conhecimento_zero(nome: str) -> None:
    texto = _texto(HTML[nome])
    for frase in ("não consegue lê-las", "não a conhece", "não lemos as senhas", "só o escritório tem a senha-mestra",
                  "só o escritório conhece"):
        assert frase not in texto, frase


def test_senha_mestra_so_no_emissor() -> None:
    secao = re.search(r'<section id="como-trabalhamos".*?</section>', HTML["index.html"], re.DOTALL)
    assert secao
    itens = [_texto(item) for item in re.findall(r"<li>.*?</li>", secao.group(), re.DOTALL)]
    assert itens and all("emissor" in item for item in itens if "senha-mestra" in item), itens


@pytest.mark.parametrize("nome", PAGINAS)
def test_sem_conta_bloqueia(nome: str) -> None:
    assert "a conta bloqueia" not in _texto(HTML[nome])


def test_build_destinos_dos_dados() -> None:
    pagina = HTML["build.html"]
    assert "nada sai para fora" not in _texto(pagina)
    resposta = re.search(r'<div class="pergunta__corpo" id="p4">.*?</div></div>', pagina, re.DOTALL)
    assert resposta and "CNPJ" in resposta.group() and "Atualizar razão social" in resposta.group()


def test_aviso_contra_golpe() -> None:
    """O cliente reconhece o emissor verdadeiro pelo endereço, escrito por extenso (não só no link do Entrar), e sabe que
    a equipe nunca pede senha, senha-mestra nem o código do celular."""
    pagina = HTML["emissao-nacional.html"]
    endereco = ENTRAR.split("//")[1].strip("/")
    aviso = re.search(r'<p class="aviso">.*?</p>', pagina, re.DOTALL)
    # no celular, a linha quebra depois de "emissor." (o <wbr>), nunca no meio do domínio
    assert aviso and f'<strong class="endereco">{endereco}</strong>' in aviso.group().replace("<wbr>", "")
    assert "emissor.<wbr>" in aviso.group()
    assert "nunca pede" in aviso.group() and "senha-mestra" in aviso.group() and "código do celular" in aviso.group()
    secao = re.search(r'<section id="seguranca".*?</section>', pagina, re.DOTALL)
    assert secao and aviso.group() in secao.group()


# ------------------------------------------------------------------ L2 (12/11/2026): os textos legais na versão 0.4
# O servidor do emissor não guarda o XML nem o PDF (o download é pelo computador do escritório), só as senhas e a cópia
# de segurança são cifradas pelo app, a cópia diária vai ao Backblaze B2, e o aceite guarda versão, hora, origem e
# navegador. Os textos legais dizem isso.
@pytest.mark.parametrize("nome", LEGAIS)
def test_legais_sem_guarda_de_arquivo(nome: str) -> None:
    texto = _texto(HTML[nome])
    for frase in ("guarda o xml e o pdf", "guarda uma cópia", "disponíveis para download por 90 dias",
                  "os dados continuam cifrados", "cada ação no sistema (entrar, emitir, cancelar)",
                  "o pdf que o emissor guarda", "eles estão no histórico"):
        assert frase not in texto, (nome, frase)
    assert '<p class="versao">Versão 0.3,' not in HTML[nome]


def test_politica_cita_a_copia_de_seguranca() -> None:
    pagina = HTML["privacidade.html"]
    assert "Backblaze B2" in pagina and "cifrada" in pagina
    for nome in LEGAIS:  # apagar quando a conta termina ainda não tem procedimento no app: fica marcado
        for apagamos in re.finditer(r"[Aa]pagamos os dados[^<]*", HTML[nome]):
            resto = HTML[nome][apagamos.end():apagamos.end() + 300]
            assert '<span class="a-confirmar">apagamento a confirmar</span>' in resto, nome


def test_politica_diz_o_que_o_aceite_guarda() -> None:
    secao = re.search(r"<h3>Registros técnicos</h3>.*?</ul>", HTML["privacidade.html"], re.DOTALL)
    assert secao and "navegador" in secao.group() and "versão aceita" in secao.group()


@pytest.mark.parametrize("nome", PAGINAS)
def test_email_do_encarregado_no_dominio_da_empresa(nome: str) -> None:
    """O e-mail pessoal saiu do site (decisão do dono, 12/11/2026); fica o domínio da empresa até o endereço existir."""
    pagina = HTML[nome]
    assert "gmail" not in pagina.casefold()
    rodape = pagina[pagina.index("<footer"):]
    assert "e-mail @oxygenioautomacao.com.br" in rodape


# ------------------------------------------------------------------ L3, L4, L5 e L10 (12/11/2026)
# O Emissor e o DMS ditos como são (rodada de 11/11/2026, docs/decisoes-site-2026-11-11.md, e as respostas do dono).
@pytest.mark.parametrize("nome", COMERCIAIS)
def test_download_dito_como_e(nome: str) -> None:
    """O servidor não guarda o XML nem o PDF: cada arquivo é baixado no computador, com a extensão, e o portal pede uma
    verificação da pessoa (dito sem a palavra que o dono deixou fora do site)."""
    texto = _texto(HTML[nome])
    for frase in ("ficam no histórico da empresa", "xml e pdf no histórico", "xml e pdf na pasta da empresa",
                  "prontos para mandar ao cliente"):
        assert frase not in texto, (nome, frase)
    if nome == "emissao-nacional.html":
        passo = re.search(r'<li class="passo" id="passo-3">.*?</li>', HTML[nome], re.DOTALL)
        assert passo and all(p in passo.group() for p in ("computador", "extensão", "verificação", "Downloads"))


def test_conferencia_sem_marca_por_campo() -> None:
    texto = _texto(HTML["emissao-nacional.html"])
    for frase in ("conferidos um a um", "como conferidos", "ela para e pergunta", "campo a campo"):
        assert frase not in texto, frase


@pytest.mark.parametrize("nome", COMERCIAIS)
def test_sem_exagero_no_que_o_emissor_faz(nome: str) -> None:
    texto = _texto(HTML[nome])
    for frase in ("já está no histórico", "em um clique", "tomadores e serviços por empresa", "uma manhã",
                  "dá conta de mais clientes", "histórico · setembro", "o mesmo login", "cclasstrib", "a nota real",
                  "sem fila", "só o que existe"):
        assert frase not in texto, (nome, frase)


def test_antes_de_contratar_o_emissor() -> None:
    pagina = HTML["emissao-nacional.html"]
    antes = re.search(r'<div class="antes aparece">.*?</div>', pagina, re.DOTALL)
    assert antes and all(p in antes.group() for p in ("autenticador", "Portal Nacional", "Chrome", "Edge"))
    def resposta(i: str) -> str:
        corpo = re.search(rf'<div class="pergunta__corpo" id="{i}">.*?</div></div>', pagina, re.DOTALL)
        assert corpo, i
        return corpo.group()
    assert all(p in resposta("p7") for p in ("autenticador", "senha-mestra", "CNPJ"))
    assert ">O que o Emissor não faz?<" in pagina and all(p in resposta("p8") for p in ("tomador", "certificado", "obra"))
    assert ">Funciona no celular?<" in pagina and "computador" in resposta("p9")
    assert "solicitação de cancelamento é enviada ao Emissor Nacional" in resposta("p5")
    for botao in re.findall(r'<button\b[^>]*class="pergunta__botao"[^>]*>', pagina):
        assert 'aria-expanded="false"' in botao


def test_tres_planos_com_mensagem_pronta() -> None:
    """Inicial, Empresarial e Escritório (decisão do dono, 12/11/2026), sem preço escrito; cada um leva direto ao WhatsApp
    com a mensagem do plano; a condição dos três primeiros meses é apresentada pela equipe."""
    pagina = HTML["emissao-nacional.html"]
    planos = re.search(r'<section id="planos".*?</section>', pagina, re.DOTALL)
    assert planos
    assert re.findall(r"<h3>([^<]+)</h3>", planos.group()) == ["Inicial", "Empresarial", "Escritório"]
    for limite in ("1 empresa", "Até 5 notas por mês", "Até 100 notas por mês", "Várias empresas"):
        assert limite in planos.group(), limite
    acoes = re.findall(r'<p class="plano__acao"><a class="link-seta" href="([^"]+)">([^<]+)<span class="tudo-oculto"> \(abre o WhatsApp\)</span></a></p>', planos.group())
    assert len(acoes) == 3 and all(href.startswith(WHATSAPP + "?text=") and "plano" in href for href, _ in acoes)
    assert "três primeiros meses" in planos.group() and "código de teste" not in planos.group()
    contato = re.search(r'<section id="contato".*?</section>', pagina, re.DOTALL)
    assert contato and "o Emissor ou as DMS" not in contato.group()


def test_dms_sem_mes_anterior_e_com_licenca_por_computador() -> None:
    """O Oxygênio DMS compara a mesma competência rodada de novo, não o mês anterior; a licença vale por computador; a
    página dele termina no Emissor, como a do Emissor termina nele (decisão do dono, 12/11/2026)."""
    dms = re.search(r'<section id="dms".*?</section>', HTML["emissao-nacional.html"], re.DOTALL)
    assert dms
    for trecho in (HTML["index.html"], HTML["build.html"], dms.group()):
        texto = _texto(trecho)
        for frase in ("mês anterior", "o mês com o anterior", "comparado com setembro", "login do portal</span>"):
            assert frase not in texto, frase
    build = HTML["build.html"]
    assert "por computador" in build and "Oxygênio Sistema de Automação de Obrigações Fiscais Municipal" in build
    emissor = re.search(r'<section id="emissor".*?</section>', build, re.DOTALL)
    assert emissor and 'href="emissao-nacional.html"' in emissor.group()
    for nome in PAGINAS:  # o nome antigo saiu do site
        assert "Build" not in HTML[nome][HTML[nome].index("<body"):], nome


# ------------------------------------------------------------------ L6 a L12 (12/11/2026)
def test_movimento_texto_nunca_espera_e_links_de_pergunta() -> None:
    """L6: nenhuma regra esconde os fatos à espera da cena. L7: o link de uma pergunta rola até ela, e abrir uma pergunta
    põe o endereço dela na barra. L11: o valor da maquete não quebra no meio."""
    for regra in re.findall(r"[^}]*:not\(\.em-foco\)[^{]*\.fatos li[^{]*\{[^}]*\}", FOLHA):
        assert "opacity: 0" not in regra, regra
    assert "scrollIntoView" in SCRIPT and "replaceState" in SCRIPT and ".maquete--emissor" in SCRIPT
    assert re.search(r"\.maquete__valor \{[^}]*white-space: nowrap", FOLHA)
    assert re.search(r"@media \(max-height: 32rem\) \{\s*\.cabecalho \{ position: static; \}", FOLHA)


@pytest.mark.parametrize("nome", PAGINAS)
def test_faixa_de_previa_curta(nome: str) -> None:
    faixa = re.search(r'<p class="previa">(.*?)</p>', HTML[nome], re.DOTALL)
    assert faixa
    texto = re.sub(r"<[^>]+>", "", faixa.group(1))
    assert len(texto) <= 70 and "ainda não é pública" in texto, texto


def test_siglas_explicadas_e_nfse_no_alto_da_inicial() -> None:
    inicial = HTML["index.html"]
    destaque = inicial[inicial.index('<section class="destaque"'):inicial.index("</section>")]
    assert "NFS-e" in destaque and "declaração mensal" in destaque
    build = HTML["build.html"]
    assert "declaração mensal" in build and "certidão negativa" in build
    assert "Nomenclatura Brasileira de Serviços" in HTML["emissao-nacional.html"]


def test_readme_tem_verificacao_do_dominio() -> None:
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert "Verificar o domínio" in readme and "TXT" in readme and "_github-pages-challenge" in readme


def _abrir(p: object, largura: int, altura: int, reduzido: bool = False, escala: float = 1) -> tuple[object, object]:
    nav = p.chromium.launch(channel=_canal(), headless=True)
    contexto = nav.new_context(viewport={"width": largura, "height": altura}, device_scale_factor=escala,
                               reduced_motion="reduce" if reduzido else "no-preference")
    return nav, contexto.new_page()


@pytest.mark.navegador
def test_fatos_nunca_em_branco(endereco: str) -> None:
    """L6: com o bloco no terço de baixo da tela, o texto dos fatos já está à vista, nas duas versões; perto do meio da
    tela, a borda de cada fato acende na cor da marca."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        for largura, altura in ((1440, 800), (360, 740)):
            for reduzido in (False, True):
                nav, pagina = _abrir(p, largura, altura, reduzido)
                pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
                pagina.evaluate("window.scrollBy({top: document.querySelector('.seguranca').getBoundingClientRect().top - innerHeight * .72, behavior: 'instant'})")
                pagina.wait_for_timeout(1500)
                classes = pagina.locator(".seguranca").get_attribute("class")
                assert "visivel" in classes and "em-foco" not in classes, (largura, reduzido, classes)
                assert pagina.evaluate("getComputedStyle(document.querySelector('.seguranca')).opacity") == "1"
                assert pagina.evaluate("[...document.querySelectorAll('.fatos li')].every(e => getComputedStyle(e).opacity === '1')")
                marca = pagina.evaluate("getComputedStyle(document.querySelector('.cadeado')).color")
                assert pagina.evaluate("getComputedStyle(document.querySelector('.fatos li')).borderLeftColor") != marca
                pagina.evaluate("window.scrollBy({top: document.querySelector('.seguranca').getBoundingClientRect().top - innerHeight * .3, behavior: 'instant'})")
                pagina.wait_for_timeout(3500)
                bordas = pagina.evaluate("[...document.querySelectorAll('.fatos li')].map(e => getComputedStyle(e).borderLeftColor)")
                assert all(b == marca for b in bordas), (largura, reduzido, bordas, marca)
                nav.close()


@pytest.mark.navegador
def test_a_cena_do_destaque_espera_o_foco_no_celular(endereco: str) -> None:
    from playwright.sync_api import sync_playwright

    emitida = "getComputedStyle(document.querySelector('.maquete--emissor .maquete__emitida')).opacity"
    with sync_playwright() as p:
        nav, pagina = _abrir(p, 390, 844)
        pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
        pagina.wait_for_timeout(2000)
        assert "em-foco" not in pagina.locator(".maquete--emissor").get_attribute("class")
        assert pagina.evaluate("getComputedStyle(document.querySelector('.maquete__nota--anterior')).opacity") == "1"
        assert pagina.evaluate(emitida) == "0"
        pagina.evaluate("window.scrollBy({top: document.querySelector('.maquete--emissor').getBoundingClientRect().top - innerHeight * .4, behavior: 'instant'})")
        pagina.wait_for_timeout(5500)
        assert pagina.evaluate(emitida) == "1"
        nav.close()
        nav, pagina = _abrir(p, 1440, 800)
        pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
        pagina.wait_for_timeout(5500)
        assert pagina.evaluate(emitida) == "1"
        nav.close()


@pytest.mark.navegador
def test_cabecalho_em_tela_baixa_e_link_da_pergunta(endereco: str) -> None:
    """L7: com zoom de 200% (683 x 384), o cabeçalho rola junto; numa tela normal continua preso. O link de uma pergunta
    mostra a pergunta abaixo do cabeçalho, e abrir uma pergunta põe o endereço dela na barra. L9: a 360 px, o Contratar
    do destaque fica na primeira tela."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        nav, pagina = _abrir(p, 683, 384, escala=2)
        pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
        assert pagina.evaluate("getComputedStyle(document.querySelector('.cabecalho')).position") == "static"
        nav.close()
        nav, pagina = _abrir(p, 1366, 768)
        pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
        assert pagina.evaluate("getComputedStyle(document.querySelector('.cabecalho')).position") == "sticky"
        nav.close()
        nav, pagina = _abrir(p, 360, 740)
        pagina.goto(f"{endereco}/emissao-nacional.html#p3", wait_until="networkidle")
        pagina.wait_for_timeout(1200)
        assert pagina.locator("#p3-botao").get_attribute("aria-expanded") == "true"
        topo = pagina.evaluate("document.querySelector('#p3-botao').getBoundingClientRect().top")
        fim_do_cabecalho = pagina.evaluate("document.querySelector('.cabecalho').getBoundingClientRect().bottom")
        assert topo >= fim_do_cabecalho - 1 and topo < 740, (topo, fim_do_cabecalho)
        pagina.locator("#p2-botao").click()
        assert pagina.evaluate("location.hash") == "#p2"
        pagina.goto(f"{endereco}/emissao-nacional.html", wait_until="networkidle")
        contratar = pagina.locator(".destaque .botao").bounding_box()
        assert contratar and contratar["y"] + contratar["height"] <= 740, contratar
        nav.close()


@pytest.mark.navegador
def test_letras_das_maquetes_legiveis_no_celular(endereco: str) -> None:
    """L11: a 360 px, nenhuma letra das maquetes, das pistas e das mini telas abaixo de 12 px."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        nav, pagina = _abrir(p, 360, 740, reduzido=True)
        for nome in COMERCIAIS:
            pagina.goto(f"{endereco}/{nome}", wait_until="networkidle")
            pequenas = pagina.evaluate("""() => [...document.querySelectorAll('.maquete *, .pistas *, .mini *, .conferencia__figura *')]
              .filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))
              .filter(e => parseFloat(getComputedStyle(e).fontSize) < 12)
              .map(e => (e.className || e.tagName) + ' ' + getComputedStyle(e).fontSize)""")
            assert not pequenas, (nome, pequenas)
            assert pagina.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0
        nav.close()

