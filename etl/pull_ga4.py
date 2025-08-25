"""Pull de GA4 usando Service Account.
Necesitas instalar: pip install google-analytics-data
"""
import json, pandas as pd
from .settings import get_setting
from .utils import get_engine

def run():
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest
    except Exception:
        print("Instala: pip install google-analytics-data")
        return

    prop_id = get_setting("ga4_property_id")
    sa_json = get_setting("ga4_service_json")
    if not prop_id or not sa_json:
        print("Configura GA4 en la página de Conectores.")
        return

    creds_info = json.loads(sa_json)
    client = BetaAnalyticsDataClient.from_service_account_info(creds_info)

    request = RunReportRequest(
        property=f"properties/{prop_id}",
        dimensions=[Dimension(name="date"), Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions"), Metric(name="conversions"), Metric(name="totalRevenue")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    resp = client.run_report(request)
    rows = []
    for r in resp.rows:
        rows.append({
            "date": r.dimension_values[0].value,
            "source": r.dimension_values[1].value,
            "medium": "",
            "country": "",
            "sessions": int(r.metric_values[0].value or 0),
            "transactions": int(r.metric_values[1].value or 0),
            "revenue": float(r.metric_values[2].value or 0.0),
            "users": None,
            "bounces": None,
        })
    df = pd.DataFrame(rows)
    df.to_sql("ga_sessions", get_engine(), if_exists="append", index=False)
    print(f"GA4: {len(df)} filas añadidas.")

if __name__ == "__main__":
    run()
