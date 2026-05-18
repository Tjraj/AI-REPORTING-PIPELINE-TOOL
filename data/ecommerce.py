import pandas as pd


def fetch_ecommerce(filepath):

    if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath, encoding="latin1")

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    revenue_col = next((c for c in df.columns if any(x in c for x in ["revenue", "sales", "total", "amount", "price", "gmv"])), None)
    category_col = next((c for c in df.columns if any(x in c for x in ["category", "department", "type", "segment", "product_type"])), None)
    product_col = next((c for c in df.columns if any(x in c for x in ["product", "item", "name", "title", "sku", "description"])), None)
    quantity_col = next((c for c in df.columns if any(x in c for x in ["quantity", "qty", "units", "count", "ordered"])), None)
    order_col = next((c for c in df.columns if any(x in c for x in ["order", "transaction", "invoice", "id"])), None)
    rating_col = next((c for c in df.columns if any(x in c for x in ["rating", "score", "review", "stars"])), None)
    date_col = next((c for c in df.columns if any(x in c for x in ["date", "time", "day", "month", "created", "ordered_at"])), None)

    is_large = len(df) > 10000

    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "platform": "Uploaded Store Data",
        "analysis_mode": "Top Insights (Large Dataset)" if is_large else "Full Analysis",
    }

    if revenue_col:
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")
        summary["total_revenue"] = round(float(df[revenue_col].sum()), 2)
        summary["avg_order_value"] = round(float(df[revenue_col].mean()), 2)
        summary["max_order_value"] = round(float(df[revenue_col].max()), 2)

    if order_col:
        summary["total_orders"] = int(df[order_col].nunique())

    if rating_col:
        df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
        summary["avg_rating"] = round(float(df[rating_col].mean()), 2)
        above4 = float((df[rating_col] >= 4).sum()) / len(df) * 100
        summary["pct_above_4_stars"] = round(above4, 1)

    if category_col and revenue_col:
        cat_rev = df.groupby(category_col)[revenue_col].sum()
        summary["total_categories"] = int(df[category_col].nunique())
        summary["top_category"] = str(cat_rev.idxmax())
        if is_large:
            summary["top_3_categories"] = {str(k): round(float(v), 2) for k, v in cat_rev.nlargest(3).items()}
            summary["bottom_3_categories"] = {str(k): round(float(v), 2) for k, v in cat_rev.nsmallest(3).items()}
        else:
            summary["revenue_by_category"] = {str(k): round(float(v), 2) for k, v in cat_rev.items()}

    if product_col and revenue_col:
        prod_rev = df.groupby(product_col)[revenue_col].sum()
        n = 5 if is_large else 10
        summary[f"top_{n}_products_by_revenue"] = {str(k): round(float(v), 2) for k, v in prod_rev.nlargest(n).items()}

    if product_col and quantity_col:
        df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
        prod_qty = df.groupby(product_col)[quantity_col].sum()
        n = 5 if is_large else 10
        summary[f"top_{n}_products_by_quantity"] = {str(k): round(float(v), 0) for k, v in prod_qty.nlargest(n).items()}

    if date_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True)
            if df[date_col].dt.year.median() < 1990:
                df[date_col] = pd.to_datetime(df[date_col].astype(str), unit="ms", errors="coerce")
            df = df.dropna(subset=[date_col])
            if not df.empty and revenue_col:
                monthly_rev = df.groupby(df[date_col].dt.to_period("M"))[revenue_col].sum()
                if len(monthly_rev) > 1:
                    summary["best_month"] = str(monthly_rev.idxmax())
                    summary["worst_month"] = str(monthly_rev.idxmin())
                    if not is_large:
                        summary["monthly_revenue"] = {str(k): round(float(v), 2) for k, v in monthly_rev.items()}
            summary["date_range"] = str(df[date_col].min().date()) + " to " + str(df[date_col].max().date())
        except Exception:
            pass

    if revenue_col:
        summary["null_revenue_rows"] = int(df[revenue_col].isna().sum())
        summary["duplicate_rows"] = int(df.duplicated().sum())

    cols_detected = {
        "revenue_col": revenue_col,
        "category_col": category_col,
        "product_col": product_col,
        "quantity_col": quantity_col,
        "date_col": date_col,
        "rating_col": rating_col
    }

    return df, summary, cols_detected