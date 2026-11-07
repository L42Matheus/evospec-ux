# Especificação da Feature: Formulário de Inscrição Escolar (Matrícula Acadêmica)

**Feature Branch**: `001-inscricao-matricula`

**Created**: 2026-11-07

**Status**: Draft

**Version**: 1.0.0 (versão inicial; anotação de código: `@spec 001-inscricao-matricula@1.0.0`)

**Input**: Descrição do usuário: "Crie um formulário web de inscrição escolar (matrícula acadêmica). O estudante informa nome completo, CPF e e-mail e aciona o botão 'Continuar'. O CPF deve ser validado (dígitos verificadores; CPF com todos os dígitos iguais é inválido). Se o CPF for inválido, a inscrição não é enviada e uma mensagem de erro é mostrada. Se o CPF for válido e os campos estiverem preenchidos, a inscrição é enviada e aparece uma confirmação."

## Cenários de Usuário e Testes *(obrigatório)*

### História de Usuário 1 - Enviar inscrição com dados válidos (Prioridade: P1)

O estudante acessa a página de inscrição, informa nome completo, CPF e e-mail válidos e aciona o
botão "Continuar". A inscrição é enviada e o estudante vê uma confirmação clara de que ela foi
recebida.

**Por que esta prioridade**: é o objetivo principal da feature; sem ela não há matrícula.

**Teste independente**: preencher os três campos com dados válidos (ex.: CPF 529.982.247-25),
acionar "Continuar" e verificar que a confirmação aparece e que a inscrição foi registrada como
enviada.

**Cenários de aceitação**:

1. **Dado** que o formulário está vazio, **Quando** o estudante informa "Maria da Silva",
   "529.982.247-25" e "maria@exemplo.com" e aciona "Continuar", **Então** a inscrição é enviada e
   uma mensagem de confirmação é exibida.
2. **Dado** que o estudante informa o CPF sem pontuação ("52998224725") e os demais campos válidos,
   **Quando** aciona "Continuar", **Então** a inscrição é enviada e a confirmação é exibida.
3. **Dado** que a confirmação foi exibida, **Quando** um usuário de leitor de tela está na página,
   **Então** a confirmação é anunciada automaticamente, sem que ele precise procurá-la.

---

### História de Usuário 2 - Bloquear inscrição com CPF inválido (Prioridade: P1)

O estudante informa um CPF cujos dígitos verificadores não conferem, ou um CPF com todos os
dígitos iguais, e aciona "Continuar". A inscrição não é enviada e uma mensagem de erro explica o
problema, ligada ao campo CPF.

**Por que esta prioridade**: impedir inscrições com CPF inválido é uma regra de negócio explícita
do pedido; tem a mesma criticidade do envio.

**Teste independente**: preencher nome e e-mail válidos com CPF "111.111.111-11" ou
"529.982.247-24", acionar "Continuar" e verificar que nada é enviado e que a mensagem de erro é
exibida.

**Cenários de aceitação**:

1. **Dado** nome e e-mail válidos, **Quando** o estudante informa o CPF "529.982.247-24" (dígito
   verificador incorreto) e aciona "Continuar", **Então** a inscrição não é enviada e a mensagem
   "CPF inválido. Verifique os números digitados." é exibida junto ao campo CPF.
2. **Dado** nome e e-mail válidos, **Quando** o estudante informa "000.000.000-00" ou
   "111.111.111-11" e aciona "Continuar", **Então** a inscrição não é enviada e a mesma mensagem de
   erro é exibida.
3. **Dado** que a mensagem de erro do CPF foi exibida, **Quando** o estudante corrige o CPF para um
   valor válido e aciona "Continuar" novamente, **Então** a mensagem de erro desaparece, a inscrição
   é enviada e a confirmação é exibida.
4. **Dado** que o CPF tem quantidade de dígitos diferente de 11 (ex.: "123.456.789"), **Quando** o
   estudante aciona "Continuar", **Então** a inscrição não é enviada e a mensagem de CPF inválido é
   exibida.

---

### História de Usuário 3 - Orientar o preenchimento de campos obrigatórios (Prioridade: P2)

O estudante aciona "Continuar" deixando um ou mais campos vazios (ou com e-mail em formato
inválido). A inscrição não é enviada e cada campo com problema recebe uma mensagem específica.

**Por que esta prioridade**: o pedido exige que os campos estejam preenchidos para o envio; a
orientação por campo reduz erros e é necessária para acessibilidade.

**Teste independente**: acionar "Continuar" com o formulário vazio e verificar que nada é enviado e
que cada campo exibe sua mensagem.

**Cenários de aceitação**:

1. **Dado** o formulário vazio, **Quando** o estudante aciona "Continuar", **Então** a inscrição
   não é enviada, cada um dos três campos exibe a sua mensagem de obrigatoriedade e o foco vai para
   o primeiro campo com erro.
2. **Dado** nome e CPF válidos, **Quando** o estudante informa o e-mail "maria.exemplo.com" e
   aciona "Continuar", **Então** a inscrição não é enviada e a mensagem "Informe um e-mail válido,
   por exemplo nome@dominio.com." é exibida junto ao campo e-mail.
3. **Dado** que o nome contém apenas espaços, **Quando** o estudante aciona "Continuar", **Então**
   o nome é tratado como vazio e a mensagem de obrigatoriedade do nome é exibida.

---

### Casos de Borda

- CPF digitado com ou sem pontuação (pontos, hífen, espaços): os caracteres não numéricos são
  ignorados na validação.
- CPF com todos os 11 dígitos iguais (000.000.000-00 a 999.999.999-99): sempre inválido, mesmo que
  os dígitos verificadores calculados "confiram".
- CPF com letras misturadas aos números: as letras são ignoradas; se o restante não formar 11
  dígitos válidos, é inválido.
- Vários erros ao mesmo tempo: todas as mensagens são exibidas, e o foco vai para o primeiro campo
  com erro na ordem do formulário (nome, CPF, e-mail).
- Acionar "Continuar" várias vezes após uma inscrição bem-sucedida: a inscrição não é enviada em
  duplicidade enquanto a confirmação estiver exibida.
- Espaços no início/fim de nome e e-mail são desconsiderados.

## Requisitos *(obrigatório)*

### Requisitos Funcionais

- **FR-001**: O sistema MUST exibir um formulário de inscrição com os campos "Nome completo", "CPF"
  e "E-mail", cada um com rótulo visível e associado ao campo, e um botão "Continuar".
- **FR-002**: O sistema MUST validar o CPF pelo algoritmo oficial dos dois dígitos verificadores,
  considerando apenas os dígitos informados (pontuação é ignorada) e exigindo exatamente 11 dígitos.
- **FR-003**: O sistema MUST considerar inválido todo CPF cujos 11 dígitos sejam iguais.
- **FR-004**: Quando o CPF for inválido, o sistema MUST NOT enviar a inscrição e MUST exibir a
  mensagem "CPF inválido. Verifique os números digitados." associada ao campo CPF.
- **FR-005**: O sistema MUST exigir que nome completo, CPF e e-mail estejam preenchidos
  (desconsiderando espaços nas extremidades); campo vazio impede o envio e exibe mensagem
  específica associada ao campo ("Informe seu nome completo.", "Informe seu CPF.", "Informe seu
  e-mail.").
- **FR-006**: O sistema MUST exigir e-mail em formato válido (texto, "@", domínio com ao menos um
  ponto); formato inválido impede o envio e exibe "Informe um e-mail válido, por exemplo
  nome@dominio.com." associada ao campo e-mail.
- **FR-007**: Quando todos os campos estiverem preenchidos, o CPF for válido e o e-mail tiver
  formato válido, o sistema MUST enviar a inscrição ao acionar "Continuar".
- **FR-008**: Após o envio bem-sucedido, o sistema MUST exibir uma mensagem de confirmação
  ("Inscrição enviada com sucesso!") que inclua o nome do estudante.
- **FR-009**: As mensagens de erro e de confirmação MUST ser anunciadas a tecnologias assistivas;
  em caso de erro, o foco MUST ir para o primeiro campo inválido, e os campos inválidos MUST ser
  marcados como inválidos para tecnologias assistivas.
- **FR-010**: Quando o estudante corrigir um campo e acionar "Continuar" novamente, o sistema MUST
  remover as mensagens de erro dos campos que passaram a ser válidos.
- **FR-011**: O sistema MUST NOT enviar a mesma inscrição mais de uma vez enquanto a confirmação
  estiver exibida.
- **FR-012**: O formulário MUST ser totalmente operável por teclado e atender à WCAG 2.2 nível AA
  (contraste, foco visível, erros identificados em texto, não apenas por cor).

### Entidades-Chave

- **Inscrição**: pedido de matrícula de um estudante; atributos: nome completo, CPF (somente os 11
  dígitos), e-mail, data/hora do envio, situação (enviada).

## Critérios de Sucesso *(obrigatório)*

### Resultados Mensuráveis

- **SC-001**: Um estudante com dados válidos completa a inscrição em menos de 1 minuto.
- **SC-002**: 100% das tentativas com CPF inválido (dígito verificador errado, dígitos repetidos ou
  quantidade de dígitos diferente de 11) são bloqueadas e exibem a mensagem de erro.
- **SC-003**: 100% das tentativas com todos os campos válidos resultam em envio e confirmação.
- **SC-004**: A confirmação ou a mensagem de erro aparece em menos de 1 segundo após acionar
  "Continuar".
- **SC-005**: Zero violações de nível A/AA em verificação automática de acessibilidade, e a tarefa
  pode ser concluída apenas com teclado e com leitor de tela.

## Premissas

Decisões tomadas sem consulta ao usuário (nenhum usuário disponível para esclarecimentos):

- **Destino do envio**: não há serviço de back-end definido. "Enviar" significa registrar a
  inscrição localmente na própria página (simulação de envio), sem transmitir dados a servidores.
  A integração com um sistema acadêmico real está fora do escopo da versão 1.0.0.
- **Persistência**: a inscrição enviada não é armazenada de forma permanente; ao recarregar a
  página, o formulário volta vazio. Nenhum dado pessoal é gravado em arquivos ou em `evidence/`.
- **Momento da validação**: a validação ocorre ao acionar "Continuar" (não a cada tecla), para não
  interromper leitores de tela durante a digitação.
- **Formato do CPF**: aceito com ou sem máscara (pontos, hífen, espaços); a página não aplica
  máscara automática, mas pode orientar o formato em texto de ajuda.
- **Validação de e-mail**: verificação apenas de formato básico; não há confirmação por envio de
  mensagem.
- **Nome completo**: exige apenas preenchimento não vazio; não se exige nome e sobrenome, para não
  excluir pessoas com nome único.
- **Após a confirmação**: o formulário é substituído pela confirmação, que oferece a opção "Nova
  inscrição" para recomeçar; isso evita envio duplicado (FR-011).
- **Público**: estudantes que acessam por navegador web moderno, em desktop ou celular; idioma
  português do Brasil.
- **Duplicidade de CPF** entre inscrições diferentes não é verificada (não há base de dados).
