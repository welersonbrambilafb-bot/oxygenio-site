# Site da Oxygênio Automação

O site institucional e comercial da Oxygênio Automação, em `www.oxygenioautomacao.com.br`: a empresa, os dois
produtos (a Oxygênio Emissão Nacional, emissor de NFS-e para escritórios de contabilidade, e o Oxygênio DMS, o
aplicativo que encerra as DMS da prefeitura), os textos legais e o contato pelo WhatsApp.

É um site **estático**: só HTML, CSS, um script próprio para o movimento, fontes e imagens, tudo nesta pasta. Não tem
servidor, banco, formulário nem cookie. Fica hospedado no GitHub Pages, e cada mudança é um commit.

## As páginas

| Arquivo | O que é |
|---|---|
| `index.html` | A empresa: o que faz, os dois produtos, contato |
| `emissao-nacional.html` | A Oxygênio Emissão Nacional, o emissor de NFS-e |
| `build.html` | O Oxygênio DMS, o aplicativo das DMS |
| `termos-de-uso.html` | Termos de uso do emissor (rascunho, com data e versão no rodapé) |
| `privacidade.html` | Política de privacidade (rascunho, com data e versão no rodapé) |
| `lgpd.html` | Como a empresa trata dados pessoais, em linguagem simples (rascunho) |

Os arquivos que todas compartilham: `estilos.css` (tokens de cor e fontes), `pagina.css` (o desenho), `movimento.js`
(o movimento; `var MOVIMENTO = true;` é a chave que desliga tudo), `fontes/` e `imagens/`. Para mexer nos textos, leia
antes o `LEIA-ME.md`: ele traz as decisões do dono, o tom, o que o teste exige e o que ainda falta decidir.

## Ver no computador

Na pasta do site:

```
python -m http.server 8795 --bind 127.0.0.1
```

e abra `http://127.0.0.1:8795/`. No Claude, a configuração `site` de `.claude/launch.json` faz o mesmo.

## Testar

O teste confere cada página: política fechada, nada de fora, cabeçalho e rodapé iguais, títulos em ordem, imagens com
medida, as palavras que não entram, os CNPJs, o aviso de independência e a lista do que falta decidir.

```
uv run pytest -q
```

Na primeira vez o `uv` cria a pasta `.venv` com o pytest e o Playwright (os dois ficam fora do Git). Para o teste no
navegador, que abre as páginas em 360, 768 e 1440 px:

```
uv run pytest -q -m navegador
```

Se o Chromium do Playwright não abrir, use o Edge que já está no Windows, no PowerShell:

```
$env:NFSE_NAVEGADOR_DE_TESTE = "msedge"; uv run pytest -q -m navegador
```

## Publicar no GitHub Pages

Um passo de cada vez. Os passos 1 a 4 são feitos uma vez só; depois, publicar é só fazer o commit e o `git push`.

### 1. Criar o repositório público no GitHub

1. Entre em `https://github.com/new`.
2. Nome do repositório: `oxygenio-site`. Visibilidade: **Public** (o GitHub Pages gratuito pede repositório público).
3. Não marque "Add a README", "Add .gitignore" nem licença: a pasta já tem tudo.
4. Clique em **Create repository** e copie o endereço que aparece (`https://github.com/<usuário>/oxygenio-site.git`).

### 2. Enviar a pasta

Na pasta do site, no PowerShell (troque `<usuário>` pelo seu usuário do GitHub):

```
git remote add origin https://github.com/<usuário>/oxygenio-site.git
```

```
git push -u origin main
```

O GitHub pede para entrar na primeira vez. Confira na página do repositório que os arquivos apareceram, inclusive o
`CNAME` e o `.nojekyll`.

### 3. Ligar o GitHub Pages

1. No repositório, **Settings** → **Pages** (menu da esquerda).
2. Em **Build and deployment**, **Source**: `Deploy from a branch`.
3. **Branch**: `main`, pasta `/ (root)`. **Save**.
4. Espere um ou dois minutos. A página mostra o endereço provisório, `https://<usuário>.github.io/oxygenio-site/`.
   Abra e confira que o site aparece. Enquanto o domínio não estiver apontado, é só esse endereço que funciona.

### 4. Apontar o domínio no Registro.br

O arquivo `CNAME` desta pasta já diz ao GitHub que o site responde em `www.oxygenioautomacao.com.br`. Falta o
Registro.br mandar o domínio para o GitHub. Entre em `https://registro.br`, abra o domínio `oxygenioautomacao.com.br`,
**Editar zona** (DNS), e crie estes registros:

| Nome | Tipo | Valor |
|---|---|---|
| *(vazio: a raiz do domínio)* | A | `185.199.108.153` |
| *(vazio)* | A | `185.199.109.153` |
| *(vazio)* | A | `185.199.110.153` |
| *(vazio)* | A | `185.199.111.153` |
| *(vazio)* | AAAA | `2606:50c0:8000::153` |
| *(vazio)* | AAAA | `2606:50c0:8001::153` |
| *(vazio)* | AAAA | `2606:50c0:8002::153` |
| *(vazio)* | AAAA | `2606:50c0:8003::153` |
| `www` | CNAME | `<usuário>.github.io` |

Os endereços A e AAAA são os do GitHub Pages; antes de salvar, confira na documentação deles que continuam os mesmos
(`https://docs.github.com/pages`, "Managing a custom domain"). Apague registros A ou CNAME antigos do mesmo nome, se
houver (o `emissor`, que é outro servidor, não se mexe). O Registro.br leva de alguns minutos a algumas horas para
espalhar a mudança.

### 5. Confirmar o domínio no GitHub e ligar o HTTPS

1. De volta em **Settings** → **Pages**, em **Custom domain**, confira que aparece `www.oxygenioautomacao.com.br`
   (veio do arquivo `CNAME`). Se não, digite e **Save**.
2. Espere a verificação ficar verde ("DNS check successful"). Se ficar vermelha, o DNS ainda não espalhou: espere e
   recarregue.
3. Marque **Enforce HTTPS**. O certificado pode levar até uma hora para ficar pronto.
4. Abra `https://www.oxygenioautomacao.com.br/` e `https://oxygenioautomacao.com.br/` (a raiz redireciona para o
   `www`). Confira as seis páginas e os botões Entrar e Contratar.

### 6. Verificar o domínio na conta do GitHub

Feito em 09/11/2026. Impede que outra conta do GitHub publique um site no domínio da Oxygênio se o Pages um dia for
desligado com o DNS ainda apontando para lá.

1. No GitHub, na foto do canto superior direito, **Settings** (da conta, não do repositório) → **Pages** →
   **Add a domain**. Digite `oxygenioautomacao.com.br`, sem o `www`.
2. O GitHub mostra um registro TXT, com o nome `_github-pages-challenge-<usuário>` e um código. Crie esse registro
   no Registro.br, na mesma zona do passo 4.
3. Depois que o Registro.br publicar a zona (alguns minutos), volte e clique em **Verify**. Não apague o TXT.

### 7. Depois de publicado

- Cada mudança no site é um commit e um `git push`; o GitHub republica em um ou dois minutos.
- Enquanto a lista do `LEIA-ME.md` ("o que falta decidir") não zerar, as páginas ficam com a faixa de prévia e com
  `noindex`: o site abre, mas não aparece nas buscas. Zerou a lista, tire os dois e troque o teste.
- O emissor passa a apontar o cadastro para `termos-de-uso.html` e `privacidade.html` deste site, e deixa
  de servir a apresentação antiga. Isso é feito lá, não aqui.
