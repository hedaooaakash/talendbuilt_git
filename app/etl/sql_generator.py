import json


def generate_sql(steps):

    source_table = None
    filter_condition = None
    aggregate_function = None
    aggregate_column = None
    group_by = None

    for step in steps:

        step_type = step["step_type"]

        config = step["config_json"]

        if isinstance(config, str):
            config = json.loads(config)

        if step_type == "EXTRACT_ORACLE":

            source_table = config.get("table")

        elif step_type == "FILTER":

            filter_condition = config.get(
                "condition"
            )

        elif step_type == "AGGREGATE":

            aggregate_function = config.get(
                "function"
            )

            aggregate_column = config.get(
                "column"
            )

            group_by = config.get(
                "group_by"
            )

    sql = ""

    if aggregate_function:

        sql += "SELECT "

        if group_by:

            sql += (
                ", ".join(group_by)
                + ", "
            )

        sql += (
            f"{aggregate_function}"
            f"({aggregate_column}) "
        )

        sql += (
            f"FROM {source_table} "
        )

        if filter_condition:

            sql += (
                f"WHERE {filter_condition} "
            )

        if group_by:

            sql += (
                "GROUP BY "
                + ", ".join(group_by)
            )

    else:

        sql += (
            f"SELECT * FROM "
            f"{source_table}"
        )

        if filter_condition:

            sql += (
                f" WHERE "
                f"{filter_condition}"
            )

    return sql