# Projeto 1 — Radar de Contratos com Red Flags

## 1) Definição do produto (entrega final)

O objetivo deste projeto é construir um **radar analítico de risco em contratos públicos** para apoiar priorização investigativa, auditoria e governança.

### Saídas principais

1. **Tabela gold de contratos**
   - Granularidade principal: `1 linha por contrato`.
   - Alternativa (quando houver detalhamento): `1 linha por contrato + item`.

2. **Tabela de red flags**
   - Flags booleanas (`0/1`).
   - Severidade (`low`, `med`, `high`).
   - Métricas de suporte para auditoria.
   - Evidência textual explicável.

3. **Tabela de score de risco (0–100)**
   - Score explicável por regra.
   - `risk_level` (Low/Med/High).
   - `top_reasons` (3 principais fatores de risco).

4. **Dashboard operacional**
   - Ranking de contratos.
   - Ranking de fornecedores.
   - Drill-down de casos com explicabilidade.

5. **Documentação de governança**
   - Dicionário de dados.
   - Metodologia de flags.
   - Metodologia do score.
   - Limitações e uso responsável.

### Usuários do produto

- Auditoria / Compliance / Governança.
- Analistas de dados para priorização de casos.
- Gestores com visão agregada por órgão/fornecedor/modalidade.

---

## 2) Escopo recomendado para MVP

### Escopo funcional

- **Fonte principal:** PNCP (contratações/contratos).
- **Enriquecimento:** CNPJ (idade, CNAE, UF, município, status).
- **Extra opcional no MVP:** sanções (CEIS/CNEP/CEPIM) como feature binária.

### Janela temporal

- Histórico inicial: **últimos 12 meses**.
- Rotina: **incremental diário** com reprocessamento dos **últimos 7 dias**.

### Granularidade

- Padrão: nível de **contrato**.
- Evolução: **contrato + item** para melhorar detecção de outliers/sobrepreço.

---

## 3) Componentes do projeto

### A) Ingestão / Extração

#### Requisitos de implementação

- Backfill mensal do histórico.
- Incremental diário (`D-1` a `D`) + reprocessamento de 7 dias.
- Controle de ETL com:
  - última data processada,
  - volume por execução,
  - status,
  - `batch_id`.
- Armazenamento **raw** do payload original (JSON/CSV) particionado por data de extração.

#### Robustez obrigatória

- Paginação.
- Retry com backoff.
- Idempotência (evitar duplicidade).
- Logs de volume e erro.

### B) Padronização e modelagem (Bronze/Silver)

#### Padronizações obrigatórias

- **CNPJ:** somente dígitos, 14 caracteres; inválidos = `null`.
- **Datas:** timezone consistente.
- **Moeda:** tipo numérico consistente.
- **Texto:** normalização de acento/caixa/espaços para matching.

#### Chaves

- Preferencial: `contract_id`.
- Fallback: chave composta (`orgão + número/ano + fornecedor + data`).

#### Modelo mínimo Silver

- `silver_contracts` (fato principal).
- `silver_suppliers` (dimensão fornecedor).
- `silver_agencies` (dimensão órgão).
- `silver_time` (dimensão de tempo opcional).

### C) Enriquecimento (CNPJ + sanções)

#### Features CNPJ (MVP)

- `company_open_date`
- `company_age_days_at_contract`
- `cnae_main`
- `uf`, `municipio`
- `company_status` (quando disponível)

#### Features sanções (opcional no MVP)

- `is_sanctioned`
- `sanction_type` (CEIS/CNEP/CEPIM)
- `sanction_active`

### D) Red flags (núcleo do projeto)

Cada red flag deve conter:

- Flag booleana (`0/1`)
- Métrica de suporte
- Severidade (`low`/`med`/`high`)
- Evidência textual

#### Pacote recomendado de flags MVP

1. Concentração de valor do fornecedor no órgão.
2. Concentração de quantidade de contratos no órgão.
3. Fracionamento em janela curta (7/15/30 dias).
4. Empresa nova com contrato alto.
5. Crescimento abrupto de fornecedor.
6. Recorrência de modalidade de exceção (dispensa/inexigibilidade).
7. Outlier de valor por categoria/órgão.
8. Pico no fim do ano/exercício.
9. CNAE potencialmente incompatível com objeto (heurística).
10. Fornecedor sancionado (se houver base de sanções).

### E) Score de risco

#### Método MVP (regras explicáveis)

`score = soma(peso_flag_i * flag_i)` normalizado para escala `0–100`.

#### Saídas obrigatórias

- `risk_level`: Low / Med / High
- `top_reasons`: top 3 flags mais relevantes
- `evidence_fields`: métricas de suporte do caso

### F) Dashboard / App

#### Páginas mínimas

- **Visão geral:** total contratos, total valor, % com flag, top órgãos, top fornecedores.
- **Ranking de contratos:** score, órgão, fornecedor, valor, data, top reasons.
- **Ranking de fornecedores:** score agregado, concentração, nº órgãos, crescimento.
- **Drill-down:** detalhes do contrato + flags + métricas + histórico do fornecedor.

#### Filtros obrigatórios

- Período
- Órgão
- UF/município
- Modalidade
- Categoria/objeto (quando disponível)

### G) Validação e governança

#### Validação operacional

- Revisão manual Top 20–50 casos.
- Checagem de falsos positivos.
- Ajuste iterativo de thresholds e pesos.

#### Data Quality checks (por execução)

- Volume diário vs média histórica.
- `% CNPJ válido`.
- `% datas e valores preenchidos`.
- Duplicidade por chave.
- Outliers impossíveis (valor <= 0, datas invertidas etc.).

#### Documentação obrigatória

- Dicionário de dados.
- Definição objetiva das flags.
- Metodologia do score.
- Limitações e uso responsável.

---

## 4) Estrutura inicial do repositório

```text
.
├── README.md
├── configs/
│   ├── flag_thresholds.yml
│   └── score_weights.yml
├── dashboards/
│   └── README.md
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── state/
├── docs/
│   ├── dicionario_dados.md
│   ├── definicao_flags.md
│   ├── metodologia_score.md
│   └── uso_responsavel.md
├── notebooks/
├── sql/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── marts/
└── src/
    ├── ingestion/
    ├── processing/
    ├── enrichment/
    ├── flags/
    ├── scoring/
    └── dq/
```

---

## 5) Próximos passos sugeridos

1. Implementar pipeline de ingestão PNCP (backfill + incremental).
2. Definir esquema de `silver_contracts` e dimensões.
3. Implementar 8–10 flags com thresholds em configuração externa.
4. Gerar tabela de score com explicabilidade.
5. Publicar primeiro dashboard com ranking + drill-down.
6. Rodar ciclo de validação manual e calibrar pesos.

