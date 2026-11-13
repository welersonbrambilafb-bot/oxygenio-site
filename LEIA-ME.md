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
| `movimento.js` | O script do movimento. `var MOVIMENTO = true;` é a chave que desliga tudo. Com o computador pedindo menos movimento (o Windows em "melhor desempenho"), a página fica na versão suave: os blocos esmaecem e os traços se desenham, sem nada se deslocar (decisão do dono, 09/11/2026). As cenas (cadeado, placa de parada, ícones, conferência, fatos) começam com o bloco perto do meio da tela; o ritmo delas está em `--mov-gesto` e `--mov-espera`. | Só se souber o que faz |
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
  do dono: o nome da verificação do portal, a região do servidor, `R$`, `grátis`, `gratuito`, `LGPD`, `depoimento`, `garant`, `100%`, `com certeza`,
  `ponta a ponta`, `melhor do mercado`, e o tom de anúncio: `revolucion`, `potencializ`, `transforme`, `descubra`,
  `solução completa`, `de ponta`, `no mundo atual`, `sem complicação`, `em apenas alguns cliques`, `mais do que`,
  `não é apenas`, `inteligente`, `algoritmo`, `robô`, `milhares`, `o melhor`, `o mais rápido`, e o ponto de exclamação.
  Também não entram `IA`, `emita e envie` (o app não envia nota) e, no que fala do Oxygênio DMS (o antigo Build), cidade, ano ou número de
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
  direito, Entrar vem antes de Contratar. A página do Oxygênio DMS (`build.html`) não tem o Entrar, que leva ao login
  do Emissor (decisão do dono, 12/11/2026); ela termina num bloco que leva à página do Emissor, como a do Emissor
  termina num bloco que leva à do DMS. Os planos do Emissor levam direto ao WhatsApp, com a mensagem do plano.
- **Cabeçalho e rodapé iguais em todas as páginas** (só a mensagem do Contratar muda, e o DMS não tem o Entrar). Mudou
  um, mude em todas. No menu, o produto das DMS se chama "DMS"; nas frases, "Oxygênio DMS" ou "o aplicativo" (para
  não confundir o produto com a declaração); o nome completo, "Oxygênio Sistema de Automação de Obrigações Fiscais
  Municipal", aparece no alto da página dele.
- **As seções da página do emissor**, nesta ordem e com estes `id`: `beneficios`, `como-funciona`, `recursos`,
  `seguranca`, `planos`, `perguntas`, `dms`, `contato` (o DMS depois das perguntas, decisão do dono de 12/11/2026).
- **Nenhuma frase promete o que o app não faz** (rodada de 11/11/2026). O teste recusa as frases antigas que a rodada
  derrubou: o XML e o PDF "no histórico" (são baixados no computador), a conferência que "marca" cada campo, "em um
  clique", "compara com o mês anterior" (o DMS compara a mesma competência rodada de novo), "a conta bloqueia" (a
  entrada é freada), "a Oxygênio não consegue ler as senhas" (elas se abrem dentro do servidor).
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

Sem preço escrito (o preço é combinado com a equipe; a condição especial dos três primeiros meses do plano
Escritório é apresentada no WhatsApp), dois planos no Emissor na abertura por convite (Inicial: 1
empresa e até 5 notas por mês; Escritório: várias empresas; o Empresarial volta quando o app o tiver), uma conta por
escritório, do responsável (o acesso por pessoa só como algo que ainda vem), sem o nome da verificação do portal (o
download diz "o portal pede uma verificação"), sem prova social (depoimento, número
de clientes, logos de clientes), sem modo escuro, WhatsApp como único contato, o O² como marca principal, os dados nos
Estados Unidos, sem dizer a região (13/11/2026), cookies sem banner (uma linha no rodapé: o site não usa nenhum), e a faixa de prévia até zerar
a lista abaixo.

## O que não dizer sem o dono decidir

Preço, cidade ou quantidade de empresas do Oxygênio DMS, a região do servidor (só "nos Estados Unidos"),
o nome da verificação do portal, e-mail, endereço, razão social por extenso nos textos legais (até ele confirmar), prazos de guarda de dados.

## O que falta decidir (a lista que segura a prévia)

Cada item está marcado na página com `class="a-confirmar"` e repetido em `A_CONFIRMAR` no teste.

- Em toda página, no rodapé: o e-mail do encarregado de dados. Decidido (12/11/2026): um endereço no domínio da empresa,
  ainda a criar; até lá o site mostra só "@oxygenioautomacao.com.br". O endereço da empresa está decidido (08/11/2026):
  só "Cianorte, Paraná", sem rua nem CEP, no rodapé e nas páginas legais.
- `emissao-nacional.html` e `build.html`: nada pendente desde 12/11/2026 (planos, tempos, lista do DMS e prefeituras
  decididos).
- As páginas legais (versão 0.5, 13/11/2026: a 0.4 corrigiu com o que os apps fazem; a 0.5 alinhou ao app da
  abertura por convite, com uma conta por escritório, dois planos, o convite, a recuperação e os dados nos Estados
  Unidos; o emissor copia termos e privacidade para o app e pede novo aceite): razão
  social e CNPJ (já conferidos no cartão, o dono confirma o uso), o encarregado, o apagamento quando a conta termina (o
  emissor ainda não tem o procedimento), os prazos propostos (6 meses dos registros de acesso, 30 dias de aviso, 15 dias
  de resposta),
  o limite de responsabilidade (o que foi pago em 12 meses), o foro (Comarca de Cianorte), a base legal da
  transferência para os Estados Unidos (com o advogado), os papéis de controlador e operador, e a revisão de um advogado.

## Para publicar de verdade (depois de zerar a lista)

Tirar a faixa `<p class="previa">` e a `<meta name="robots" content="noindex, nofollow">` de cada página, trocar o teste
que exige os dois, e seguir o `README.md` ("Publicar no GitHub Pages").
