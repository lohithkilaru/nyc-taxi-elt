"""Stand-ins for dbt_utils macros, used only so sqlfluff can lint models.

They return simple valid SQL. dbt itself uses the real macros.
"""


def date_spine(datepart, start_date, end_date):
    return "select cast('2025-01-01' as date) as date_day"


def generate_surrogate_key(field_list):
    return "md5('stand_in')"
