# Dicionário de Dados (MVP)

## Tabela: gold_contracts
- contract_key
- contract_id
- agency_id
- agency_name
- supplier_cnpj
- supplier_name
- contract_date
- contract_value
- modality
- object_description
- category

## Tabela: gold_red_flags
- contract_key
- flag_id
- flag_name
- flag_value
- severity
- evidence_text
- metric_1_name
- metric_1_value
- metric_2_name
- metric_2_value

## Tabela: gold_risk_score
- contract_key
- score_0_100
- risk_level
- top_reason_1
- top_reason_2
- top_reason_3
- generated_at
