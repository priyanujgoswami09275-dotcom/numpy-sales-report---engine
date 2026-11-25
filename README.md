# Sales Engine

Sales Engine is a small Streamlit dashboard for exploring sales by store, product, and month. It uses the deterministic NumPy dataset from `Sales.ipynb` by default and supports replacing it with a CSV upload.

## Features

- Filter sales by store, product, and month.
- View revenue, store count, best-performing store, and best-selling product KPIs.
- Explore monthly trends, store totals, product totals, and actual sales versus monthly targets.
- Download the deterministic sample dataset.
- Validate uploaded sales CSVs and combine duplicate store/product/month rows.

Monthly targets follow the notebook: each store-product combination has a target from 30,000 in January to 70,000 in December. The displayed aggregate target is the per-combination target multiplied by the selected store-product combinations divided by all combinations in the loaded dataset.

## Stack

- Python
- Streamlit
- NumPy
- Pandas
- Plotly
- pytest (development and verification)

## Structure

```text
app.py                  # Streamlit UI and Plotly charts
sales_engine.py         # NumPy generation, analytics, filtering, CSV validation
README.md
requirements.txt
data/sample_sales.csv   # Deterministic long-format sample data
tests/test_sales_engine.py
Sales.ipynb             # Original notebook, unchanged
DESIGN.md               # Existing visual reference, unchanged
```

## Install and run

```bash
pip install -r requirements.txt
streamlit run app.py
```

On systems that manage the system Python environment, create and activate a virtual environment before installing dependencies.

Run the tests with:

```bash
pytest
```

## CSV format

The CSV must contain these columns:

```csv
store,product,month,sales
Store 0,Laptop,Jan,11137
Store 0,Laptop,February,32105
```

`month` accepts month names (full or abbreviated, case-insensitive) or numbers from 1 to 12. Sales must be numeric and non-negative. Duplicate store/product/month rows are summed when loaded. Empty files, missing columns, invalid months, invalid sales, and negative sales are rejected with readable messages.
