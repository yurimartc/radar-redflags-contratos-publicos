import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Radar de Contratos", layout="wide")
st.title("Radar de Contratos com Red Flags")
st.caption("App inicial do dashboard (Streamlit) com base na arquitetura MinIO + Parquet/Delta.")

st.subheader("Status da arquitetura")
status = pd.DataFrame(
    [
        {"Componente": "Airflow", "Função": "Orquestração backfill/incremental", "Status": "Scaffold"},
        {"Componente": "Postgres", "Função": "Metadata/controle/observabilidade", "Status": "Scaffold"},
        {"Componente": "MinIO", "Função": "Data lake local raw/bronze/silver/gold", "Status": "Scaffold"},
        {"Componente": "Parquet/Delta", "Função": "Camada analítica", "Status": "Pendente ingestão real"},
        {"Componente": "DuckDB", "Função": "Consulta rápida local", "Status": "Opcional pronto para uso"},
    ]
)
st.dataframe(status, use_container_width=True)

st.subheader("Teste DuckDB local")
con = duckdb.connect(database=":memory:")
preview = con.execute("SELECT 'ok' AS healthcheck, current_timestamp AS ts").df()
st.dataframe(preview, use_container_width=True)
