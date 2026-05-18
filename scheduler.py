import schedule
import time
from datetime import datetime
from data.weather import fetch_weather
from data.stocks import fetch_stocks
from data.ecommerce import fetch_ecommerce
from insights import generate_insights
from reports.pdf_report import generate_pdf_report
import os

def run_weather_report():
    print(f"[{datetime.now()}] Running weather report...")
    df, summary = fetch_weather("New York", 7)
    insights = generate_insights("weather", summary)
    pdf = generate_pdf_report("weather", summary, insights)
    os.makedirs("output_reports", exist_ok=True)
    filename = f"output_reports/weather_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf)
    print(f"Report saved: {filename}")

def run_stock_report():
    print(f"[{datetime.now()}] Running stock report...")
    df, summary = fetch_stocks("IBM", 30)
    insights = generate_insights("stocks", summary)
    pdf = generate_pdf_report("stocks", summary, insights)
    os.makedirs("output_reports", exist_ok=True)
    filename = f"output_reports/stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf)
    print(f"Report saved: {filename}")

def run_ecommerce_report():
    print(f"[{datetime.now()}] Running ecommerce report...")
    df_products, df_orders, summary = fetch_ecommerce()
    insights = generate_insights("ecommerce", summary)
    pdf = generate_pdf_report("ecommerce", summary, insights)
    os.makedirs("output_reports", exist_ok=True)
    filename = f"output_reports/ecommerce_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf)
    print(f"Report saved: {filename}")

# Schedule daily runs
schedule.every().day.at("08:00").do(run_weather_report)
schedule.every().day.at("08:05").do(run_stock_report)
schedule.every().day.at("08:10").do(run_ecommerce_report)

if __name__ == "__main__":
    print("Scheduler running. Reports fire daily at 08:00 AM.")
    print("Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)