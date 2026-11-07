# Matriz de rastreabilidade — EvoSpec-UX

Gerada em 2026-11-07T10:11:22-03:00 · linha de base: commit `e2298ec`

| Critério | Spec@versão | Evidência | Proposta (decisão) | Teste | Resultado |
|---|---|---|---|---|---|
| 001/FR-001 | 001-validacao-cpf@2 | — (versão inicial) | — | `cpf_invalido_bloqueia_envio` | passa |
| 001/FR-002 | 001-validacao-cpf@2 | — (versão inicial) | — | `cpf_invalido_exibe_mensagem` | passa |
| 001/FR-003 | 001-validacao-cpf@2 | — (versão inicial) | — | `cpf_valido_envia` | passa |
| 001/FR-004 | 001-validacao-cpf@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `foco_vai_para_cpf` | passa |
| 001/FR-005 | 001-validacao-cpf@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `cpf_marcado_invalido_com_descricao` | passa |
| 001/FR-006 | 001-validacao-cpf@2 | EVD-17 | CR-001 (approved, Lucas Matheus Silva) | `mensagem_em_regiao_viva` | passa |
| 002/FR-001 | 002-preservacao-dados@1 | — (versão inicial) | — | `dados_preservados_apos_erro` | passa |

## Evidências

- **EVD-17** (teste com usuário (sessão moderada), leitor de tela (NVDA + Chrome)): O participante acionou "Continuar" três vezes sem perceber a mensagem de erro do campo CPF. O leitor de tela não verbalizou nenhuma mensagem após o envio. O participante precisou de ajuda do moderador para concluir a tarefa. → CR-001
