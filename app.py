"""Sales Engine Streamlit dashboard."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sales_engine as engine


SAMPLE_CSV = Path(__file__).resolve().parent / "data" / "sample_sales.csv"

st.set_page_config(page_title="Sales Engine", page_icon="📈", layout="wide")


CUSTOM_CSS = """
<style>
:root {
  --color-stone-canvas: #fafaf9;
  --color-pure-white: #ffffff;
  --color-stone-border: #e8e6e5;
  --color-stone-muted: #d6d3d1;
  --color-ash-gray: #a8a29e;
  --color-warm-gray: #78716c;
  --color-ink-black: #0c0a09;
  --color-soot: #1c1917;
  --color-sky-wash: #c1e1f7;
  --color-cyan-signal: #3ba6f1;
  --color-cyan-edge: #3398e1;

  --font-roobert: 'Roobert', 'Inter Tight', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-inter: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  --text-caption: 10px;
  --leading-caption: 2.3;
  --tracking-caption: 0px;
  --text-body-lg: 16px;
  --leading-body-lg: 1.69;
  --tracking-body-lg: 0.048px;
  --text-subheading: 20px;
  --leading-subheading: 1.2;
  --tracking-subheading: -0.1px;
  --text-heading-sm: 32px;
  --leading-heading-sm: 1.25;
  --tracking-heading-sm: -0.8px;
  --text-display: 52px;
  --leading-display: 1.12;
  --tracking-display: -1.092px;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  --spacing-unit: 4px;
  --spacing-4: 4px;
  --spacing-8: 8px;
  --spacing-12: 12px;
  --spacing-16: 16px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-40: 40px;
  --spacing-48: 48px;
  --spacing-64: 64px;
  --spacing-80: 80px;
  --spacing-96: 96px;
  --spacing-160: 160px;

  --page-max-width: 1200px;
  --section-gap: 96px;
  --card-padding: 24px;
  --element-gap: 8px;

  --radius-md: 4px;
  --radius-lg: 10px;
  --radius-2xl: 16px;
  --radius-full: 9999px;
  --radius-tags: 9999px;
  --radius-cards: 10px;
  --radius-icons: 4px;
  --radius-inputs: 6px;
  --radius-buttons: 9999px;
  --radius-feature-card: 16px;

  --shadow-md: rgba(0, 0, 0, 0.05) 0px 4px 16px 0px;
  --shadow-sm: rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -2px;
  --shadow-subtle: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
  --shadow-xl: rgba(17, 12, 46, 0.12) 0px 12px 45px 0px;

  --surface-canvas: #fafaf9;
  --surface-card: #ffffff;
  --surface-floating-preview: #ffffff;
  --surface-inverted-section: #1c1917;
}

html, body, [class*="stApp"] {
  background: var(--surface-canvas);
  color: var(--color-ink-black);
  font-family: var(--font-inter);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.64;
  letter-spacing: 0.004em;
}

[data-testid="stMainBlockContainer"],
section.main > div.block-container {
  max-width: var(--page-max-width);
  padding-top: var(--spacing-48);
  padding-bottom: var(--spacing-64);
  padding-left: var(--spacing-24);
  padding-right: var(--spacing-24);
}

section[data-testid="stSidebar"] {
  background: var(--surface-canvas);
  border-right: 1px solid var(--color-stone-border);
}

h1, h2, h3, h4 {
  color: var(--color-ink-black);
  font-family: var(--font-roobert);
  font-weight: 400;
}

h1 {
  margin: var(--spacing-8) 0 var(--spacing-12);
  font-size: var(--text-display);
  line-height: var(--leading-display);
  letter-spacing: var(--tracking-display);
}

h2, h3 {
  font-size: var(--text-heading-sm);
  line-height: var(--leading-heading-sm);
  letter-spacing: var(--tracking-heading-sm);
}

p, label, .stCaption, [data-testid="stMetricLabel"] {
  color: var(--color-warm-gray);
  font-family: var(--font-inter);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.64;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-8);
  color: var(--color-ink-black);
  font-family: var(--font-inter);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.brand-mark {
  display: inline-flex;
  width: 16px;
  height: 16px;
  align-items: center;
  justify-content: center;
}

.brand-subtitle {
  margin-top: var(--spacing-4);
  color: var(--color-warm-gray);
  font-size: 13px;
}

.page-description {
  margin: 0;
  max-width: 620px;
  color: var(--color-warm-gray);
  font-size: 14px;
  line-height: 1.64;
}

.headline-highlight {
  padding: 2px 8px;
  border-radius: var(--radius-icons);
  background: var(--color-sky-wash);
  color: var(--color-cyan-edge);
  font-weight: 400;
}

.source-pill {
  display: inline-flex;
  margin-top: var(--spacing-16);
  padding: 4px 12px;
  border: 1px solid var(--color-stone-border);
  border-radius: var(--radius-tags);
  background: var(--color-pure-white);
  color: var(--color-warm-gray);
  font-size: 12px;
  line-height: 1.5;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--color-stone-border) !important;
  border-radius: var(--radius-cards) !important;
  background: var(--surface-card) !important;
  box-shadow: none !important;
}

[data-testid="stMetric"] {
  padding: var(--spacing-8) 0;
}

[data-testid="stMetricValue"] {
  color: var(--color-ink-black);
  font-family: var(--font-roobert);
  font-size: 26px;
  font-weight: 400;
  letter-spacing: -0.5px;
}

[data-testid="stMetricLabel"] {
  color: var(--color-warm-gray);
  font-size: 13px;
}

[data-testid="stDownloadButton"] button {
  width: 100%;
  border: 1px solid var(--color-stone-border) !important;
  border-radius: var(--radius-buttons);
  background: transparent !important;
  color: var(--color-ink-black) !important;
  font-family: var(--font-inter);
  font-weight: 400;
  padding: 8px 16px;
}

[data-testid="stButton"] button {
  border: 1px solid var(--color-stone-border);
  border-radius: var(--radius-buttons);
  background: transparent;
  color: var(--color-ink-black);
  font-family: var(--font-inter);
  font-weight: 400;
  padding: 8px 16px;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stMultiSelect"] input {
  border: 1px solid var(--color-stone-muted);
  border-radius: var(--radius-inputs);
  background: var(--color-pure-white);
  color: var(--color-ink-black);
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stMultiSelect"] input:focus {
  border-color: var(--color-cyan-signal);
  box-shadow: 0 0 0 2px var(--color-cyan-signal);
}

[data-testid="stFileUploader"] section {
  border: 1px dashed var(--color-stone-muted);
  border-radius: var(--radius-inputs);
  background: var(--color-pure-white);
}

.chart-heading {
  margin: 0 0 var(--spacing-8);
  color: var(--color-ink-black);
  font-family: var(--font-roobert);
  font-size: var(--text-subheading);
  font-weight: 400;
  line-height: var(--leading-subheading);
  letter-spacing: var(--tracking-subheading);
}

.sidebar-title {
  margin: 0 0 var(--spacing-16);
  color: var(--color-ink-black);
  font-family: var(--font-roobert);
  font-size: 20px;
  font-weight: 400;
  letter-spacing: -0.1px;
}

@media (max-width: 700px) {
  [data-testid="stMainBlockContainer"],
  section.main > div.block-container {
    padding: var(--spacing-32) var(--spacing-16);
  }
  h1 {
    font-size: 40px;
    letter-spacing: -0.84px;
  }
}
</style>
"""


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _initialize_filters(stores: list[str], products: list[str], months: list[str]) -> None:
    """Keep filter selections valid when the available data changes."""
    options = (stores, products, months)
    prior_options = st.session_state.get("filter_options")
    if prior_options != options:
        st.session_state["store_filter"] = stores
        st.session_state["product_filter"] = products
        st.session_state["month_filter"] = months
        st.session_state["filter_options"] = options
    else:
        st.session_state.setdefault("store_filter", stores)
        st.session_state.setdefault("product_filter", products)
        st.session_state.setdefault("month_filter", months)


def _chart_layout(figure: go.Figure, *, show_legend: bool = False) -> go.Figure:
    figure.update_layout(
        height=310,
        margin={"l": 8, "r": 8, "t": 16, "b": 8},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, system-ui, sans-serif", "size": 12, "color": "#78716c"},
        showlegend=show_legend,
        legend={"orientation": "h", "y": 1.1, "x": 0},
        xaxis={"showgrid": False, "zeroline": False, "linecolor": "#e8e6e5"},
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "linecolor": "#e8e6e5",
            "tickprefix": "$",
            "tickformat": ",.0s",
        },
    )
    return figure


def _show_charts(
    filtered: pd.DataFrame,
    all_data: pd.DataFrame,
    selected_combinations_data: pd.DataFrame,
) -> None:
    monthly = engine.monthly_sales(filtered)
    by_store = engine.sales_per_store(filtered)
    by_product = engine.sales_per_product(filtered)
    top_store = by_store.idxmax()
    top_product = by_product.idxmax()
    comparison = engine.monthly_target_comparison(
        filtered,
        all_data=all_data,
        selected_combinations_data=selected_combinations_data,
    )

    chart_columns = st.columns(2, gap="large")
    with chart_columns[0]:
        with st.container(border=True):
            st.markdown('<div class="chart-heading">Monthly sales trend</div>', unsafe_allow_html=True)
            figure = go.Figure(
                go.Scatter(
                    x=monthly.index.tolist(),
                    y=monthly.tolist(),
                    mode="lines+markers",
                    line={"color": "#3ba6f1", "width": 2},
                    marker={"color": "#3ba6f1", "size": 6},
                    hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
                )
            )
            figure.update_layout(yaxis_title="Revenue")
            st.plotly_chart(_chart_layout(figure), width="stretch", config={"displayModeBar": False})

    with chart_columns[1]:
        with st.container(border=True):
            st.markdown('<div class="chart-heading">Sales by store</div>', unsafe_allow_html=True)
            figure = go.Figure(
                go.Bar(
                    x=by_store.index.tolist(),
                    y=by_store.tolist(),
                    marker_color=[
                        "#3ba6f1" if store == top_store else "#d6d3d1"
                        for store in by_store.index
                    ],
                    hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
                )
            )
            figure.update_layout(yaxis_title="Revenue")
            figure.update_xaxes(tickangle=-35)
            st.plotly_chart(_chart_layout(figure), width="stretch", config={"displayModeBar": False})

    chart_columns = st.columns(2, gap="large")
    with chart_columns[0]:
        with st.container(border=True):
            st.markdown('<div class="chart-heading">Sales by product</div>', unsafe_allow_html=True)
            figure = go.Figure(
                go.Bar(
                    x=by_product.index.tolist(),
                    y=by_product.tolist(),
                    marker_color=[
                        "#3ba6f1" if product == top_product else "#d6d3d1"
                        for product in by_product.index
                    ],
                    hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
                )
            )
            figure.update_layout(yaxis_title="Revenue")
            figure.update_xaxes(tickangle=-25)
            st.plotly_chart(_chart_layout(figure), width="stretch", config={"displayModeBar": False})

    with chart_columns[1]:
        with st.container(border=True):
            st.markdown('<div class="chart-heading">Monthly sales vs target</div>', unsafe_allow_html=True)
            figure = go.Figure()
            figure.add_trace(
                go.Bar(
                    x=comparison.index.tolist(),
                    y=comparison["actual"].tolist(),
                    name="Actual",
                    marker_color="#d6d3d1",
                    hovertemplate="%{x}<br>Actual $%{y:,.0f}<extra></extra>",
                )
            )
            figure.add_trace(
                go.Scatter(
                    x=comparison.index.tolist(),
                    y=comparison["target"].tolist(),
                    name="Target",
                    mode="lines+markers",
                    line={"color": "#3ba6f1", "width": 2},
                    marker={"color": "#3ba6f1", "size": 6},
                    hovertemplate="%{x}<br>Target $%{y:,.0f}<extra></extra>",
                )
            )
            figure.update_layout(barmode="group", yaxis_title="Revenue")
            st.plotly_chart(_chart_layout(figure, show_legend=True), width="stretch", config={"displayModeBar": False})


def main() -> None:
    st.sidebar.markdown('<div class="sidebar-title">Sales Engine</div>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload a sales CSV", type=["csv"], key="sales_upload")
    st.sidebar.download_button(
        "Download sample CSV",
        data=SAMPLE_CSV.read_bytes(),
        file_name="sample_sales.csv",
        mime="text/csv",
        type="secondary",
    )

    if uploaded_file is None:
        data = engine.load_sales_csv(SAMPLE_CSV)
        source_label = "Sample Data"
    else:
        try:
            data = engine.load_sales_csv(uploaded_file)
        except engine.SalesDataError as error:
            st.sidebar.error(str(error))
            st.info("Upload a valid sales CSV to view the dashboard.")
            return
        source_label = "Uploaded Data"

    stores = data["store"].drop_duplicates().tolist()
    products = data["product"].drop_duplicates().tolist()
    months = [month for month in engine.MONTHS if month in set(data["month"])]
    _initialize_filters(stores, products, months)

    if st.sidebar.button("Reset filters", key="reset_filters"):
        st.session_state["store_filter"] = stores
        st.session_state["product_filter"] = products
        st.session_state["month_filter"] = months

    selected_stores = st.sidebar.multiselect("Stores", options=stores, key="store_filter")
    selected_products = st.sidebar.multiselect("Products", options=products, key="product_filter")
    selected_months = st.sidebar.multiselect("Months", options=months, key="month_filter")

    selected_combinations_data = engine.filter_sales(
        data,
        stores=selected_stores,
        products=selected_products,
    )
    filtered = engine.filter_sales(
        selected_combinations_data,
        months=selected_months,
    )

    st.markdown(
        '<div class="brand-row"><span class="brand-mark" aria-hidden="true">'
        '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="#3ba6f1" stroke-width="1">'
        '<path d="M8 1.5v4M8 10.5v4M1.5 8h4M10.5 8h4M3.4 3.4l2.8 2.8m3.6 3.6 2.8 2.8m0-9.2-2.8 2.8m-3.6 3.6-2.8 2.8"/>'
        '</svg></span><span>Sales Engine</span></div>'
        '<div class="brand-subtitle">Sales performance, simply analysed.</div>'
        '<h1>Sales <span class="headline-highlight">Overview</span></h1>'
        '<p class="page-description">Monitor revenue, store performance and product trends.</p>'
        f'<div class="source-pill">{source_label}</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No sales match these filters. Adjust your store, product, or month selections to see results.")
        return

    kpi_columns = st.columns(4, gap="medium")
    kpis = [
        ("Total Revenue", f"${engine.total_revenue(filtered):,.0f}", "Across selected filters"),
        ("Total Stores", f"{len(engine.sales_per_store(filtered)):,}", "In the current selection"),
        ("Best Performing Store", engine.best_store(filtered) or "—", "By revenue in this selection"),
        ("Best Selling Product", engine.best_product(filtered) or "—", "By revenue in this selection"),
    ]
    for column, (label, value, caption) in zip(kpi_columns, kpis):
        with column:
            with st.container(border=True):
                st.metric(label, value)
                st.caption(caption)

    _show_charts(filtered, data, selected_combinations_data)


main()
