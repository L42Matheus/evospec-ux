# Pesquisa (Fase 0): Formulário de Inscrição Escolar

**Especificação de origem**: `001-inscricao-matricula@1.0.0`

Não restaram itens "NEEDS CLARIFICATION" no Contexto Técnico; as decisões abaixo consolidam as
escolhas de tecnologia e as lacunas resolvidas nas Premissas da especificação.

## R1. Algoritmo de validação do CPF

- **Decision**: remover tudo que não for dígito; exigir 11 dígitos; rejeitar se todos forem iguais;
  1º DV = (Σ dᵢ·(10−i), i=0..8) · 10 mod 11, com 10 → 0; 2º DV = (Σ dᵢ·(11−i), i=0..9) · 10 mod 11,
  com 10 → 0. Válido se ambos conferem com as posições 10 e 11.
- **Rationale**: é o algoritmo oficial da Receita Federal (módulo 11); a regra dos dígitos
  repetidos é exigida explicitamente (FR-003), pois esses números passam no cálculo.
- **Alternatives considered**: expressão regular de formato (não valida DV — rejeitada);
  biblioteca externa (viola Princípio V — rejeitada).

## R2. Significado de "enviar a inscrição"

- **Decision**: envio simulado no cliente — a inscrição validada é registrada num array em memória
  (`window.inscricoesEnviadas`) e um evento `inscricao:enviada` é disparado no `document`. Nenhuma
  requisição de rede.
- **Rationale**: não existe back-end no workspace; a spec (Premissas) define o envio como local.
  O registro em memória torna o envio observável pelos testes (FR-004, FR-007, FR-011) sem
  persistir dados pessoais.
- **Alternatives considered**: `fetch` para endpoint fictício (falharia sem servidor);
  `localStorage` (persistiria dados pessoais — contraria Premissas).

## R3. Validação nativa do navegador vs. validação própria

- **Decision**: `<form novalidate>` e validação própria em JavaScript, com mensagens em pt-BR
  ligadas por `aria-describedby`; atributos `required`/`autocomplete`/`inputmode` mantidos como
  pistas semânticas.
- **Rationale**: as bolhas nativas variam por navegador e idioma, somem sozinhas e não são
  anunciadas de forma consistente por leitores de tela; a spec exige textos específicos (FR-004..006).
- **Alternatives considered**: `setCustomValidity` + bolhas nativas (texto/tempo não controláveis).

## R4. Padrão acessível de erros e confirmação

- **Decision**: (a) cada campo tem `<p id="…-erro">` referenciado em `aria-describedby`; (b)
  `aria-invalid="true"` nos inválidos; (c) foco no primeiro inválido (o leitor de tela anuncia
  rótulo + erro); (d) resumo de erros em região `role="alert"` acima do formulário; (e)
  confirmação em contêiner com `role="status"` e foco programático no título da confirmação
  (`tabindex="-1"`).
- **Rationale**: atende WCAG 2.2 SC 3.3.1 (identificação de erro), 3.3.3 (sugestão), 4.1.3
  (mensagens de status), 2.4.3 (ordem de foco), 2.4.7/2.4.11 (foco visível/não encoberto).
- **Alternatives considered**: apenas cor vermelha (viola 1.4.1); `alert()` (intrusivo e não
  estilizável).

## R5. Validação de e-mail

- **Decision**: após `trim`, regex `^[^\s@]+@[^\s@]+\.[^\s@]+$`.
- **Rationale**: reproduz a regra da spec (texto, "@", domínio com ponto) sem rejeitar endereços
  válidos incomuns.
- **Alternatives considered**: regex RFC 5322 completa (complexa, sem ganho para o caso).

## R6. Ferramenta de teste de aceitação

- **Decision**: pytest + Playwright Python, Chrome headless, abrindo `file://…/app/index.html`.
- **Rationale**: ferramentas do método em Python (Princípio V); navegador real necessário para foco
  e ARIA; ambos já instalados.
- **Alternatives considered**: Selenium (mais verboso); Node + Playwright (fora da regra "ferramentas
  em Python"); jsdom (não instalado, foco/ARIA menos fiéis).

## R7. Prevenção de envio duplicado (FR-011)

- **Decision**: após o envio, o formulário é ocultado (`hidden`) e substituído pela confirmação;
  um sinalizador `enviando` impede reentrada; o botão "Nova inscrição" limpa e reexibe o formulário.
- **Rationale**: simples e evidente para o usuário; evita duplo clique/Enter repetido.
- **Alternatives considered**: apenas `disabled` no botão (botões desabilitados perdem foco e
  podem confundir leitores de tela).
