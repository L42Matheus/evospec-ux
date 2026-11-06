# Matriz de rastreabilidade — EvoSpec-UX

Gerada em 2026-11-06T19:37:22-03:00 · linha de base: commit `31cdfc7`

| Critério | Spec@versão | Evidência | Proposta (decisão) | Teste | Resultado |
|---|---|---|---|---|---|
| AC-04.1 | SPEC-04@2 | — (versão inicial) | — | `cpf_invalido_bloqueia_envio` | passa |
| AC-04.2 | SPEC-04@2 | — (versão inicial) | — | `cpf_invalido_exibe_mensagem` | passa |
| AC-04.3 | SPEC-04@2 | — (versão inicial) | — | `cpf_valido_envia` | passa |
| AC-04.4 | SPEC-04@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `foco_vai_para_cpf` | passa |
| AC-04.5 | SPEC-04@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `cpf_marcado_invalido_com_descricao` | passa |
| AC-04.6 | SPEC-04@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `mensagem_em_regiao_viva` | passa |
| AC-06.1 | SPEC-06@1 | — (versão inicial) | — | `dados_preservados_apos_erro` | passa |

## Evidências

- **EVD-17** (teste com usuário (sessão moderada), leitor de tela (NVDA + Chrome)): O participante acionou "Continuar" três vezes sem perceber a mensagem de erro do campo CPF. O leitor de tela não verbalizou nenhuma mensagem após o envio. O participante precisou de ajuda do moderador para concluir a tarefa. → CR-001
