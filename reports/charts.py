import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def weather_charts(df, city):
    charts = []
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["date"], y=df["temp_max"],
        name="Max Temp", line=dict(color="#E24B4A", width=2)))
    fig1.add_trace(go.Scatter(x=df["date"], y=df["temp_min"],
        name="Min Temp", line=dict(color="#378ADD", width=2),
        fill="tonexty", fillcolor="rgba(55,138,221,0.1)"))
    fig1.update_layout(title=f"Temperature Forecast — {city}",
        xaxis_title="Date", yaxis_title="Temperature (°C)",
        template="plotly_white", height=350)
    charts.append(fig1)

    fig2 = px.bar(df, x="date", y="precipitation",
        title=f"Daily Precipitation — {city}",
        color="precipitation", color_continuous_scale="Blues")
    fig2.update_layout(template="plotly_white", height=300)
    charts.append(fig2)

    fig3 = px.line(df, x="date", y="windspeed",
        title=f"Wind Speed — {city}", markers=True)
    fig3.update_traces(line_color="#1D9E75")
    fig3.update_layout(template="plotly_white", height=300)
    charts.append(fig3)
    return charts


def stock_charts(df, symbol):
    charts = []
    fig1 = go.Figure(data=[go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name=symbol)])
    fig1.add_trace(go.Scatter(x=df["date"], y=df["ma7"],
        name="7-day MA", line=dict(color="#6c63ff", width=1.5, dash="dot")))
    fig1.update_layout(title=f"{symbol} Price Chart",
        template="plotly_white", height=400,
        xaxis_rangeslider_visible=False)
    charts.append(fig1)

    colors = ["#1D9E75" if v >= 0 else "#E24B4A"
        for v in df["daily_change"].dropna()]
    fig2 = go.Figure(go.Bar(
        x=df["date"][1:], y=df["daily_change"].dropna(),
        marker_color=colors, name="Daily Change %"))
    fig2.update_layout(title=f"{symbol} Daily % Change",
        template="plotly_white", height=300)
    charts.append(fig2)

    fig3 = px.bar(df, x="date", y="volume",
        title=f"{symbol} Trading Volume",
        color_discrete_sequence=["#534AB7"])
    fig3.update_layout(template="plotly_white", height=300)
    charts.append(fig3)
    return charts


def ecommerce_charts(df, cols):
    charts = []
    rev   = cols["revenue_col"]
    cat   = cols["category_col"]
    prod  = cols["product_col"]
    qty   = cols["quantity_col"]
    date  = cols["date_col"]
    rating = cols["rating_col"]

    # --- FIX: verify product col has short values, else skip ---
    def col_ok(df, col, max_unique=500, max_len=80):
        if col is None:
            return False
        if df[col].nunique() > max_unique:
            return False
        if df[col].astype(str).str.len().mean() > max_len:
            return False
        return True

    # --- FIX: for large datasets limit to top N rows only ---
    MAX_CHART_ROWS = 5000
    df_chart = df.head(MAX_CHART_ROWS) if len(df) > MAX_CHART_ROWS else df

    # Revenue by category — limit to top 20 categories
    if cat and rev and col_ok(df_chart, cat, max_unique=5000, max_len=60):
        cat_rev = (df_chart.groupby(cat)[rev]
                   .sum().nlargest(20).reset_index())
        # Truncate long labels
        cat_rev[cat] = cat_rev[cat].astype(str).str[:30]
        fig1 = px.bar(
            cat_rev, x=cat, y=rev,
            title="Revenue by Top 20 Categories",
            color=cat,
            color_discrete_sequence=px.colors.qualitative.Set2)
        fig1.update_layout(
            template="plotly_white", height=400,
            showlegend=False,
            xaxis_tickangle=-35,
            xaxis_title="Category",
            yaxis_title="Revenue")
        fig1.update_xaxes(tickfont=dict(size=10))
        charts.append(fig1)

    # Top 10 products by revenue
    if col_ok(df_chart, prod) and rev:
        top_rev = (df_chart.groupby(prod)[rev]
                   .sum().nlargest(10).reset_index())
        top_rev[prod] = top_rev[prod].astype(str).str[:40]
        fig2 = px.bar(
            top_rev, x=rev, y=prod,
            orientation="h",
            title="Top 10 Products by Revenue",
            color=rev,
            color_continuous_scale="Viridis")
        fig2.update_layout(
            template="plotly_white", height=420,
            yaxis_title="",
            xaxis_title="Revenue",
            yaxis=dict(tickfont=dict(size=10)))
        charts.append(fig2)

    # Monthly revenue trend
    if date and rev:
        try:
            df_plot = df_chart.copy()
            df_plot[date] = pd.to_datetime(df_plot[date], errors="coerce", infer_datetime_format=True)

            # Fix Unix timestamp issue
            if df_plot[date].dt.year.median() < 1990:
                df_plot[date] = pd.to_datetime(
                    df_plot[date].astype(str), unit="ms", errors="coerce")

            df_plot = df_plot.dropna(subset=[date])

            if df_plot.empty:
                raise ValueError("No valid dates")

            trend = (df_plot.groupby(
                df_plot[date].dt.to_period("M"))[rev]
                .sum().reset_index())
            trend[date] = trend[date].astype(str)

            # Only plot if more than 1 month
            if len(trend) > 1:
                fig3 = px.line(
                    trend, x=date, y=rev,
                    title="Monthly Revenue Trend",
                    markers=True)
                fig3.update_traces(line_color="#6c63ff")
                fig3.update_layout(
                    template="plotly_white", height=350,
                    xaxis_title="Month",
                    yaxis_title="Revenue",
                    xaxis_tickangle=-35)
                charts.append(fig3)
        except Exception:
            pass

    # Top 10 products by quantity
    if col_ok(df_chart, prod) and qty:
        try:
            df_chart[qty] = pd.to_numeric(df_chart[qty], errors="coerce")
            top_qty = (df_chart.groupby(prod)[qty]
                       .sum().nlargest(10).reset_index())
            top_qty[prod] = top_qty[prod].astype(str).str[:40]
            fig4 = px.bar(
                top_qty, x=qty, y=prod,
                orientation="h",
                title="Top 10 Products by Quantity Sold",
                color_discrete_sequence=["#1D9E75"])
            fig4.update_layout(
                template="plotly_white", height=420,
                yaxis_title="",
                xaxis_title="Quantity",
                yaxis=dict(tickfont=dict(size=10)))
            charts.append(fig4)
        except Exception:
            pass

    # Rating distribution
    if rating:
        try:
            df_chart[rating] = pd.to_numeric(df_chart[rating], errors="coerce")
            fig5 = px.histogram(
                df_chart, x=rating, nbins=10,
                title="Rating Distribution",
                color_discrete_sequence=["#534AB7"])
            fig5.update_layout(
                template="plotly_white", height=300,
                xaxis_title="Rating",
                yaxis_title="Count")
            charts.append(fig5)
        except Exception:
            pass

    # Fallback — if no charts generated show basic stats
    if not charts:
        numeric_cols = df_chart.select_dtypes(include="number").columns[:4]
        for col in numeric_cols:
            fig = px.histogram(
                df_chart, x=col, nbins=30,
                title=f"Distribution of {col}",
                color_discrete_sequence=["#6c63ff"])
            fig.update_layout(template="plotly_white", height=300)
            charts.append(fig)

    return charts