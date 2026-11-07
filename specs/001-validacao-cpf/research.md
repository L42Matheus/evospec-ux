# Research: Validação do CPF na matrícula acadêmica

**Spec Version**: 2

## R1. Regra de validação do CPF

- **Decision**: validar pelos dois dígitos verificadores (módulo 11), considerando só os dígitos e
  rejeitando sequências repetidas (ex.: 111.111.111-11) e tamanhos diferentes de 11.
- **Rationale**: é a regra oficial e não exige serviço externo (premissa da spec).
- **Alternatives considered**: consulta à Receita Federal (fora do escopo; exige credenciais e rede).

## R2. Como comunicar o erro a tecnologias assistivas (FR-004 a FR-006)

- **Decision**: (a) mover o foco para o campo CPF com `focus()`; (b) marcar o campo com
  `aria-invalid="true"` e associar a mensagem com `aria-describedby`; (c) manter um contêiner de
  mensagem com `role="alert"` presente desde o carregamento e inserir o texto do erro nele.
- **Rationale**: atende WCAG 3.3.1 (Identificação de erros) e 4.1.3 (Mensagens de status). O foco no
  campo faz o leitor de tela ler o rótulo, o estado inválido e a descrição; a região viva garante o
  anúncio mesmo se o foco não mudar. A região precisa existir antes da inserção do texto, porque
  regiões vivas criadas junto com o conteúdo podem não ser anunciadas.
- **Alternatives considered**: `alert()` nativo (interrompe o fluxo, ruim para todos os usuários);
  resumo de erros no topo (útil com muitos campos, excessivo para um único campo).

## R3. Por que a verificação automática não basta

- **Decision**: manter testes de aceitação específicos para FR-004 a FR-006, além do axe-core.
- **Rationale**: na versão 1 o axe-core não apontou violações, embora a evidência EVD-17 mostre a
  tarefa interrompida (princípio I da constituição).
- **Alternatives considered**: confiar apenas no axe-core (rejeitado pela evidência).
