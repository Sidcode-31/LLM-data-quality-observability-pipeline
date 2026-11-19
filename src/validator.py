import great_expectations as gx
import pandas as pd

def validate_dataframe(df: pd.DataFrame) -> dict:
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas("pandas_source")
    data_asset = data_source.add_dataframe_asset(name="orders_asset")
    batch_def = data_asset.add_batch_definition_whole_dataframe("batch_def")

    suite = context.suites.add(gx.ExpectationSuite(name="orders_dq_suite"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="transaction_id"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="amount", min_value=0.01))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchRegex(
        column="email", regex=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    ))

    validation_def = context.validation_definitions.add(
        gx.ValidationDefinition(name="orders_validation", data=batch_def, suite=suite)
    )
    results = validation_def.run(batch_parameters={"dataframe": df})

    failed_rules = []
    for res in results.results:
        if not res.success:
            failed_rules.append({
                "rule": res.expectation_config.type,
                "column": res.expectation_config.kwargs.get("column"),
                "unexpected_count": res.result.get("unexpected_count", 0),
                "unexpected_percent": round(res.result.get("unexpected_percent", 0.0), 2)
            })

    total_checks = len(results.results)
    passed_checks = sum(1 for r in results.results if r.success)
    dq_score = round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0.0

    return {
        "passed": bool(results.success),
        "dq_score": dq_score,
        "failed_rules": failed_rules
    }