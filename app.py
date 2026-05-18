import streamlit as st
import tempfile
import os
from datetime import datetime
from data.weather import fetch_weather
from data.stocks import fetch_stocks
from data.ecommerce import fetch_ecommerce
from reports.charts import weather_charts, stock_charts, ecommerce_charts
from insights import generate_insights
from reports.pdf_report import generate_pdf_report

st.set_page_config(page_title="AI Reporting Pipeline", layout="wide")
st.title("📊 Automated Reporting Pipeline")
st.caption("Live data → AI analysis → PDF report. Three domains. Zero manual work.")

source = st.selectbox(
    "Select data source",
    ["Weather Analytics", "Stock Market", "E-commerce Store"]
)

source_map = {
    "Weather Analytics": "weather",
    "Stock Market": "stocks",
    "E-commerce Store": "ecommerce"
}

source_type = source_map.get(source, "weather")

col1, col2 = st.columns(2)
city = "New York"
symbol = "IBM"
days = 7
uploaded_file = None

if source_type == "weather":
    with col1:
        city = st.selectbox("City", ["New York", "London", "Mumbai", "Delhi", "Sydney"])
    with col2:
        days = st.slider("Forecast days", 3, 14, 7)

elif source_type == "stocks":
    with col1:
        symbol = st.text_input("Stock symbol", "IBM").upper()
    with col2:
        days = st.slider("Days of history", 7, 90, 30)

elif source_type == "ecommerce":
    st.info("Upload your store export CSV or Excel. Works with Shopify, WooCommerce, Amazon, Flipkart, Meesho, or any platform CSV export.")
    uploaded_file = st.file_uploader(
        "Upload store data (CSV or Excel)",
        type=["csv", "xlsx", "xls"]
    )
    if uploaded_file:
        st.success(f"File loaded: {uploaded_file.name}")
    else:
        st.warning("Upload your store data file to continue.")

st.markdown("---")

pipeline_cols = st.columns(5)
steps = ["Fetch Data", "Clean", "Analyse", "AI Summary", "Export PDF"]
for i, (col, step) in enumerate(zip(pipeline_cols, steps)):
    col.markdown(f"**{i+1}. {step}**")

st.markdown("---")

button_disabled = (source_type == "ecommerce" and uploaded_file is None)

if st.button("Run Pipeline Now", type="primary", disabled=button_disabled):
    progress = st.progress(0)
    status = st.empty()
    ecom_cols = None

    try:
        status.info("Step 1 — Fetching data...")

        if source_type == "weather":
            df, summary = fetch_weather(city, days)

        elif source_type == "stocks":
            df, summary = fetch_stocks(symbol, days)

        elif source_type == "ecommerce":
            suffix = ".csv" if uploaded_file.name.endswith(".csv") else ".xlsx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            df, summary, ecom_cols = fetch_ecommerce(tmp_path)
            os.unlink(tmp_path)

        progress.progress(25)
        status.info("Step 2 — Generating charts...")

        if source_type == "weather":
            charts = weather_charts(df, city)
        elif source_type == "stocks":
            charts = stock_charts(df, symbol)
        else:
            charts = ecommerce_charts(df, ecom_cols)

        progress.progress(50)
        status.info("Step 3 — AI writing executive summary...")

        if source_type not in ["weather", "stocks", "ecommerce"]:
            source_type = "weather"

        insights = generate_insights(source_type, summary)

        progress.progress(75)
        status.info("Step 4 — Building PDF report...")
        pdf_bytes = generate_pdf_report(source_type, summary, insights)

        progress.progress(100)
        status.success("Pipeline complete!")

        st.subheader("Key Metrics")
        metric_items = [(k, v) for k, v in summary.items() if k not in ["columns_detected"]][:4]
        metric_cols = st.columns(4)
        for col, (k, v) in zip(metric_cols, metric_items):
            col.metric(k.replace("_", " ").title(), str(v))

        st.subheader("Charts")
        for chart in charts:
            st.plotly_chart(chart, use_container_width=True)

        st.subheader("AI Executive Summary")
        st.markdown(insights)

        st.subheader("Download Report")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "Download PDF Report",
                data=pdf_bytes,
                file_name=f"{source_type}_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        with dl2:
            st.download_button(
                "Download Summary TXT",
                data=insights,
                file_name=f"{source_type}_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

    except Exception as e:
        status.error(f"Pipeline error: {e}")
        st.error(f"Details: {e}")

else:
    if not button_disabled:
        st.info("Click Run Pipeline to generate your report.")

st.markdown("---")
st.caption("Scheduler runs automatically at 08:00 AM daily via scheduler.py")