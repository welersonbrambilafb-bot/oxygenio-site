# Site da Oxygênio Automação (oxygenioautomacao.com.br)

Site institucional e comercial da Oxygênio Automação, estático, publicado no GitHub Pages em
`www.oxygenioautomacao.com.br`. O dono (Welerson, contador em Cianorte/PR) mantém o site pelo Claude com o plugin do
GitHub: **cada mudança é um commit**, com mensagem em português. Quem edita aqui, pessoa ou IA, segue estas regras.

## Leia antes de começar
1. `README.md`: o que é, como ver no computador, como rodar o teste, como publicar.
2. `LEIA-ME.md`: as decisões do dono sobre os textos, o tom, o que o teste exige e a lista do que falta decidir.
3. `tests/test_site.py`: o que cada página tem de cumprir. Rode antes de cada commit.

## Regras da pasta (não negociáveis)
- **Site estático.** Só HTML, CSS, JavaScript próprio, fontes e imagens. Sem servidor, sem banco, sem formulário que
  grave ou envie nada (`form-action 'none'` na política de cada página). O único JavaScript é `movimento.js`.
- **Repositório público: nenhum dado de cliente, senha, chave, IP ou nome de servidor.** Nem em arquivo, nem em commit,
  nem em comentário. Dados de exemplo nas maquetes são fictícios (CNPJ `11.222.333/0001-81`). Da empresa, só o que
  é público: razão social, CNPJ `69.039.125/0001-21`, WhatsApp `(44) 99116-0421` e o que o dono mandar publicar.
- **No git só vai o que o site publica** (as páginas, o CSS, o script, as fontes e as imagens) e o que o mantém (README,
  este arquivo, LEIA-ME, teste). Relatórios de webdesign, documentos de decisão, propostas de texto e referências ficam
  em `docs/` e `Referencias/`, nesta pasta, **fora do git** (decisão do dono, 08/11/2026): o `.gitignore` já os exclui.
  Nunca tire essas pastas do `.gitignore`.
- **Decisões do dono que valem em todas as páginas:** sem preço, sem captcha, sem prova social (depoimento, número de
  clientes), sem modo escuro, WhatsApp como contato, o O² como marca principal, faixa de prévia e `noindex` até zerar
  a lista do que falta decidir (`LEIA-ME.md`).
- **"Entrar" (em toda página, menos na do Oxygênio DMS) sempre leva a `https://emissor.oxygenioautomacao.com.br/`.** "Contratar" leva ao WhatsApp da equipe,
  `https://wa.me/5544991160421`, com a mensagem pronta. São os dois únicos endereços de fora, mais os links entre as
  páginas do próprio site.
- **Textos legais** (`termos-de-uso.html`, `privacidade.html`, `lgpd.html`) **com data e versão no rodapé.** Mudou o
  texto, sobe a versão e a data. O que o dono ainda não confirmou fica marcado com `<span class="a-confirmar">`.
- **No GitHub só o site.** O emissor de NFS-e, os motores, as senhas e os processos do escritório ficam no servidor da
  Oxygênio, nunca neste repositório (decisão do dono, 08/11/2026). Nenhum arquivo versionado aqui cita o código do
  emissor ou do Oxygênio DMS: nem nome de pasta, nem caminho de arquivo, nem nome de módulo (o teste confere). As pastas
  deles no computador do dono são só leitura: daqui não se altera nada lá; de lá só vem o que o texto público já diz.
- **Fonte e ícone só locais** (`fontes/`, `imagens/`). Nada do Google Fonts, de CDN ou de qualquer endereço de fora.
- **Mensagens, textos e commits em português.** Linguagem de escritório contábil, não de programador.
- **Nada de `git push` sem o usuário pedir.** Publicar é dele.

## Como trabalhar
- Um lote por commit. Antes do commit: `uv run pytest -q` passando e a página conferida em `http://127.0.0.1:8795/`
  (configuração `site` de `.claude/launch.json`, ou `python -m http.server 8795 --bind 127.0.0.1`).
- Todas as páginas compartilham `estilos.css` (tokens e fontes), `pagina.css` (o desenho) e `movimento.js`. Cabeçalho e
  rodapé são iguais em todas: mudou um, mude em todas (o teste confere).
- Salve em UTF-8 sem BOM. Nunca pelo Word.
- Dúvida de texto legal, de regra fiscal ou de negócio: pergunte ao dono. Não invente.
