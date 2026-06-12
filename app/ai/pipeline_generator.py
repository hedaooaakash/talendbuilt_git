def generate_pipeline(prompt: str):

    prompt_upper = prompt.upper()

    result = {
        "pipeline_name": "Generated_Pipeline",
        "source_type": None,
        "target_type": None,
        "steps": []
    }

    step_order = 1

    # Source

    if "ORACLE" in prompt_upper:

        result["source_type"] = "ORACLE"

        result["steps"].append({
            "step_order": step_order,
            "step_type": "EXTRACT_ORACLE",
            "config_json": {
                "table": "EMPLOYEE"
            }
        })

        step_order += 1

    # Filter

    if "LESS THAN 500" in prompt_upper:

        result["steps"].append({
            "step_order": step_order,
            "step_type": "FILTER",
            "config_json": {
                "condition": "SALARY < 500"
            }
        })

        step_order += 1

    # Aggregate

    if "MAX SALARY" in prompt_upper:

        result["steps"].append({
            "step_order": step_order,
            "step_type": "AGGREGATE",
            "config_json": {
                "function": "MAX",
                "column": "SALARY",
                "group_by": ["DEPARTMENT"]
            }
        })

        step_order += 1

    # Target

    if "POSTGRES" in prompt_upper:

        result["target_type"] = "POSTGRES"

        result["steps"].append({
            "step_order": step_order,
            "step_type": "LOAD_POSTGRES",
            "config_json": {
                "table": "MAX_EMPLOYEE"
            }
        })

    return result