from app.etl.sql_generator import generate_sql

steps = [

    {
        "step_type": "EXTRACT_ORACLE",
        "config_json": {
            "table": "EMPLOYEE"
        }
    },

    {
        "step_type": "FILTER",
        "config_json": {
            "condition": "SALARY < 500"
        }
    },

    {
        "step_type": "AGGREGATE",
        "config_json": {
            "function": "MAX",
            "column": "SALARY",
            "group_by": [
                "DEPARTMENT"
            ]
        }
    }

]

sql = generate_sql(steps)

print(sql)