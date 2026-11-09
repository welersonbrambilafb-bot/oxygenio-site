# Os textos do site: como mexer, o que foi decidido e o que falta

Este site veio da apresentação da Oxygênio Automação que morava junto do código do emissor (
03 e 04/11/2026) e, por decisão de 06/11/2026, passou a viver aqui, no GitHub Pages, com páginas próprias para a
empresa, para cada produto e para os textos legais. Ainda **não é público de verdade**: enquanto a lista do fim deste
arquivo não zerar, cada página fica com `noindex` e com a faixa de prévia. Quem edita aqui, pessoa ou IA, segue o que
está abaixo. A história das decisões está no repositório do emissor, em `docs/site-v2-2026-11-03.md` e
`docs/plano-site-2026-11-03.md` (só leitura).

## Os arquivos

| Arquivo | O que é | Pode editar? |
|---|---|---|
| `*.html` | As páginas. **Todos os textos estão nelas**, entre as tags, em português. | Sim |
| `pagina.css` | O desenho: cores (só no bloco `:root` do começo), fontes, espaços e o movimento (tokens `--mov-*`). | Sim, com cuidado |
| `movimento.js` | O script do movimento. `var MOVIMENTO = true;` é a chave que desliga tudo. | Só se souber o que faz |
| `estilos.css` | As fontes e o `:root` do app do emissor, copiados sem mudar nada (as maquetes ficam iguais à tela de verdade). | Só copiando de novo do app |
| `fontes/` | Plus Jakarta Sans e IBM Plex Mono, com as licenças em `LICENCAS.txt`. | Não |
| `imagens/` | As logos: `oxygenio_badge_192.png` e `oxygenio_icon_256.png` (o O², marca principal), `oxygenio_nfse_icon.svg` (o emissor, com "NFS-e" escrito), `check.svg`. | Não |

Salve sempre em **UTF-8 sem BOM**, com editor de texto (VS Code, Notepad++, Bloco de notas em UTF-8). Nunca pelo Word.

## Para mudar um texto

1. Abra a página, ache a frase e troque. Mantenha as tags em volta (`<p>`, `<h2>`, `<li>`, `<strong>`...).
2. Rode o teste, na pasta do site: `uv run pytest -q`.
3. Veja o resultado em `http://127.0.0.1:8795/` (`python -m http.server 8795 --bind 127.0.0.1`, ou a configuração
   `site` de `.claude/launch.json`).
4. Para o navegador conferir também (Playwright): `uv run pytest -q -m navegador`. Se o Chromium não abrir, use o Edge:
   `$env:NFSE_NAVEGADOR_DE_TESTE = "msedge"` antes do comando.
5. Faça o commit, com a mensagem em português. Publicar (`git push`) é do dono.

## O que o teste exige (e por quê)

- **Palavras que não entram nas páginas comerciais** (`index.html`, `emissao-nacional.html`, `build.html`), por decisão
  do dono: `captcha`, `Ohio`, `R$`, `grátis`, `gratuito`, `LGPD`, `depoimento`, `garant`, `100%`, `com certeza`,
  `ponta a ponta`, `melhor do mercado`, e o tom de anúncio: `revolucion`, `potencializ`, `transforme`, `descubra`,
  `solução completa`, `de ponta`, `no mundo atual`, `sem complicação`, `em apenas alguns cliques`, `mais do que`,
  `não é apenas`, `inteligente`, `algoritmo`, `robô`, `milhares`, `o melhor`, `o mais rápido`, e o ponto de exclamação.
  Também não entram `IA`, `emita e envie` (o app não envia nota) e, no que fala do Build, cidade, ano ou número de
  empresas (decisão de 03/11/2026: só os benefícios). As páginas legais podem dizer "LGPD": é o nome da lei.
- **O aviso de independência** aparece em toda página, no rodapé, com o texto exato:
  `sem vínculo com a Receita Federal, com prefeituras nem com o Portal Nacional`. Na página do emissor, aparece também
  na seção Segurança (duas vezes na página).
- **O CNPJ** é só o `69.039.125/0001-21` (mais o de exemplo `11.222.333/0001-81` nas maquetes). O WhatsApp é
  `(44) 99116-0421`, uma vez por página, no máximo.
- **Os botões:** `Entrar` (`botao discreto`) vai sempre para o endereço do emissor, `https://emissor.oxygenioautomacao.com.br/`.
  `Contratar` (`botao`) vai sempre para o WhatsApp da equipe, `https://wa.me/5544991160421`, com a mensagem pronta no
  `?text=` (a mensagem muda conforme o produto da página). Dentro de cada Contratar vai o aviso
  `<span class="tudo-oculto"> (abre o WhatsApp)</span>`, que só o leitor de tela lê (decisão de 08/11/2026). `Chamar no
  WhatsApp` é o único `botao whatsapp`. Outras chamadas são links com `class="link-seta"`. No canto superior
  direito, Entrar vem antes de Contratar.
- **Cabeçalho e rodapé iguais em todas as páginas** (só a mensagem do Contratar muda). Mudou um, mude em todas.
- **As seções da página do emissor**, nesta ordem e com estes `id`: `beneficios`, `como-funciona`, `recursos`, `dms`,
  `seguranca`, `planos`, `perguntas`, `contato`.
- **Um `<h1>` só** por página, títulos em ordem (`h2` depois de `h1`, `h3` depois de `h2`), toda `<img>` com `alt`,
  `width` e `height`.
- **Páginas legais com data e versão** no fim do texto: `<p class="versao">Versão X, de D de mês de AAAA</p>`.
  Mudou o texto, sobe a versão e troca a data.
- **O que falta decidir** fica marcado na página com `<span class="a-confirmar">…</span>`, e a lista de cada página tem
  de ser igual à `A_CONFIRMAR` em `tests/test_site.py`. Decidiu um item: tire o `<span>` da página **e** a frase da
  lista do teste. Enquanto a lista não zera, a página fica com `noindex` e a faixa de prévia.
- Sem `<form>`, `<iframe>`, `style="..."`, `onclick` e sem nada de fora (as únicas exceções são os dois endereços:
  Entrar e WhatsApp). Cada página, com o que ela baixa, cabe em 160 KB.

## O tom dos textos

Como um contador explicando a ferramenta a um colega. Frases curtas, "você", o vocabulário do ofício (prestador,
tomador, competência, Simples, MEI, retenção, Emissor Nacional, DMS). Benefício do dia a dia, não tecnologia. Nada que
não seja verdade nem que não exista no produto: sem número inventado, sem promessa. O foco decidido pelo dono para o
emissor: **Copiar nota** e **todos os clientes num sistema só**. Se uma frase soar como anúncio ou como texto de robô,
reescreva. Nos textos legais, linguagem de escritório, direta, sem juridiquês além do necessário.

## As decisões do dono que valem no site inteiro

Sem preço (o preço é combinado com a equipe), sem captcha (omitido por enquanto), sem prova social (depoimento, número
de clientes, logos de clientes), sem modo escuro, WhatsApp como único contato, o O² como marca principal, "servidor da
Amazon" sem dizer onde, cookies sem banner (uma linha no rodapé: o site não usa nenhum), e a faixa de prévia até zerar
a lista abaixo.

## O que não dizer sem o dono decidir

Preço, limites do plano pago, cidade ou quantidade de empresas do Build, onde o servidor fica (só "servidor da Amazon"),
o captcha, e-mail, endereço, razão social por extenso nos textos legais (até ele confirmar), prazos de guarda de dados.

## O que falta decidir (a lista que segura a prévia)

Cada item está marcado na página com `class="a-confirmar"` e repetido em `A_CONFIRMAR` no teste.

- Em toda página, no rodapé: o e-mail do encarregado de dados, preenchido com o que o dono já publica no DANFSe.tools;
  ele confirma se quer esse mesmo no site. O endereço está decidido (08/11/2026): só "Cianorte, Paraná", sem rua nem CEP,
  no rodapé e nas páginas legais.
- `emissao-nacional.html`: tempos ("uma manhã" vira "alguns minutos"), a lista do que o Build faz, os limites do plano
  Escritório, o prazo do código de teste (30 dias).
- `build.html`: a lista do que ele faz e quais prefeituras atende (dizer ou não a cidade é decisão do dono).
- As páginas legais (versão 0.2, 08/11/2026, escritas com as referências que o dono deixou em `Referencias/`, pasta
  fora do git): razão social e CNPJ (já conferidos no cartão, o dono confirma o uso), o encarregado, os prazos propostos
  (90 dias de guarda depois do encerramento, 6 meses dos registros de acesso, 30 dias de aviso, 15 dias de resposta),
  o limite de responsabilidade (o que foi pago em 12 meses), o foro (Comarca de Cianorte), o local do servidor (para
  a transferência internacional), os papéis de controlador e operador, e a revisão de um advogado.

## Para publicar de verdade (depois de zerar a lista)

Tirar a faixa `<p class="previa">` e a `<meta name="robots" content="noindex, nofollow">` de cada página, trocar o teste
que exige os dois, e seguir o `README.md` ("Publicar no GitHub Pages").
