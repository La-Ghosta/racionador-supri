# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue a convenção de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-04-11

### Adicionado
- Estrutura inicial do projeto com pastas `src/`, `tests/` e `.github/workflows/`.
- Modelos de domínio (`Pessoa`, `Suprimento`, `Grupo`) com validações.
- Cálculo automático do fator de consumo por faixa etária
  (criança < 12 anos = 0.6, adulto = 1.0, idoso > 65 anos = 0.8).
- Lógica pura de racionamento em `racionamento.py`:
  - cálculo de dias restantes;
  - alerta de suprimentos críticos;
  - sugestão de corte percentual no consumo;
  - relatório completo classificando suprimentos em OK / ALERTA / CRÍTICO.
- Persistência do estado do grupo em arquivo JSON local.
- Interface de linha de comando construída com Typer e Rich.
- Comandos disponíveis: `init`, `add-pessoa`, `add-suprimento`,
  `atualizar-suprimento`, `remover-pessoa`, `remover-suprimento`,
  `listar`, `status`, `sugerir`.
- Tabela colorida no comando `status` (verde, amarelo, vermelho)
  conforme o nível de alerta.
- Suíte de 20 testes automatizados com pytest cobrindo caminho feliz,
  entradas inválidas e casos limite.
- Linter `ruff` configurado com regras de estilo, qualidade e boas práticas.
- Pipeline de Integração Contínua com GitHub Actions executando lint
  e testes em Python 3.10, 3.11 e 3.12.

### Corrigido
- Bug onde os comandos `add-pessoa` e `add-suprimento` aceitavam itens
  com nomes duplicados, causando inconsistência no relatório de status.
- Avisos do linter `B904` ajustados com `raise ... from None` nos
  handlers de erro da CLI.