FROM astrocrpublic.azurecr.io/runtime:3.3-11
RUN python -m venv dbt_venv && \
    dbt_venv/bin/pip install --no-cache-dir dbt-core==1.12.7 dbt-snowflake==1.12.5