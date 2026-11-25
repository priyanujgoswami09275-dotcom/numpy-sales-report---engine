"""Reusable NumPy-backed sales analytics and CSV validation."""

from __future__ import annotations

import calendar
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd


COLUMNS = ["store", "product", "month", "sales"]
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_TARGETS = np.linspace(30_000, 70_000, 12)
QUARTERS = ("Q1", "Q2", "Q3", "Q4")
DEFAULT_SAMPLE_CSV = Path(__file__).resolve().parent / "data" / "sample_sales.csv"

_MONTH_LOOKUP = {
    name.casefold(): month
    for month_number, month in enumerate(MONTHS, start=1)
    for name in (month, calendar.month_name[month_number])
}
_MONTH_NUMBER = {month: number for number, month in enumerate(MONTHS, start=1)}


class SalesDataError(ValueError):
    """A user-readable problem with a sales CSV or dataset."""


def _normalize_month(value: object) -> str:
    text = str(value).strip()
    month = _MONTH_LOOKUP.get(text.casefold())
    if month:
        return month

    try:
        number = float(text)
    except (TypeError, ValueError):
        number = float("nan")
    if np.isfinite(number) and number.is_integer() and 1 <= number <= 12:
        return MONTHS[int(number) - 1]
    raise SalesDataError(f"Invalid month {text!r}; use a month name or a number from 1 to 12.")


def _normalize_sales_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().casefold() for column in normalized.columns]
    if normalized.columns.duplicated().any():
        raise SalesDataError("Duplicate column names after normalization.")
    missing = [column for column in COLUMNS if column not in normalized.columns]
    if missing:
        raise SalesDataError(f"Missing required columns: {', '.join(missing)}")

    normalized = normalized[COLUMNS].copy()
    if normalized.empty:
        raise SalesDataError("The CSV file is empty or contains no sales rows.")

    for column in ("store", "product"):
        normalized[column] = normalized[column].astype("string").str.strip()
        if normalized[column].isna().any() or normalized[column].eq("").any():
            raise SalesDataError(f"The {column} column must not contain blank values.")

    sales = pd.to_numeric(normalized["sales"], errors="coerce")
    if sales.isna().any() or not np.isfinite(sales.to_numpy(dtype=float)).all():
        raise SalesDataError("sales must be numeric and contain finite values.")
    if sales.lt(0).any():
        raise SalesDataError("The sales column cannot contain negative sales.")

    normalized["month"] = normalized["month"].map(_normalize_month)
    # Object-backed numeric values use Python integer addition in groupby,
    # avoiding int64 wraparound when duplicate rows have a large combined sum.
    normalized["sales"] = sales.astype(object)
    normalized = (
        normalized.groupby(COLUMNS[:3], as_index=False, sort=False, observed=True)["sales"]
        .sum()
    )
    normalized["month"] = pd.Categorical(normalized["month"], categories=MONTHS, ordered=True)
    normalized = normalized.sort_values(COLUMNS[:3], kind="stable").reset_index(drop=True)
    normalized["month"] = normalized["month"].astype("string")
    return normalized[COLUMNS]


def load_sales_csv(source: str | Path | bytes | bytearray | BinaryIO) -> pd.DataFrame:
    """Load, validate, normalize and de-duplicate a sales CSV."""
    if isinstance(source, (bytes, bytearray)):
        source = BytesIO(source)
    elif hasattr(source, "getvalue"):
        source = BytesIO(source.getvalue())

    try:
        frame = pd.read_csv(source)
    except pd.errors.EmptyDataError as error:
        raise SalesDataError("The CSV file is empty.") from error
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise SalesDataError(f"Could not read the CSV file: {error}") from error
    return _normalize_sales_frame(frame)


def generate_sample_sales() -> pd.DataFrame:
    """Recreate the notebook's 11 × 5 × 12 deterministic sales dataset."""
    np.random.seed(11)
    values = np.random.randint(1_000, 100_001, (11, 5, 12))
    stores = [f"Store {index}" for index in range(11)]
    products = ["Laptop", "IOS Phone", "Android Phone", "Earbuds", "Meta Glasses"]
    return pd.DataFrame(
        {
            "store": np.repeat(stores, 5 * 12),
            "product": np.tile(np.repeat(products, 12), 11),
            "month": np.tile(MONTHS, 11 * 5),
            "sales": values.reshape(-1),
        },
        columns=COLUMNS,
    )


def write_sample_csv(path: str | Path = DEFAULT_SAMPLE_CSV) -> Path:
    """Write the deterministic sample dataset to a long-format CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_sample_sales().to_csv(output_path, index=False)
    return output_path


def total_revenue(data: pd.DataFrame) -> float:
    """Return total sales revenue for the supplied rows."""
    return float(np.sum(data["sales"].to_numpy(dtype=float)))


def _grouped_sales(data: pd.DataFrame, column: str) -> pd.Series:
    if data.empty:
        return pd.Series(dtype=float, name="sales", index=pd.Index([], name=column))
    return data.groupby(column, sort=False, observed=True)["sales"].sum().rename("sales")


def sales_per_store(data: pd.DataFrame) -> pd.Series:
    """Return filtered revenue totals indexed by store."""
    return _grouped_sales(data, "store")


def sales_per_product(data: pd.DataFrame) -> pd.Series:
    """Return filtered revenue totals indexed by product."""
    return _grouped_sales(data, "product")


def monthly_sales(data: pd.DataFrame) -> pd.Series:
    """Return revenue by month in calendar order."""
    if data.empty:
        return pd.Series(dtype=float, name="sales", index=pd.Index([], name="month"))
    totals = data.groupby("month", sort=False, observed=True)["sales"].sum()
    return totals.reindex([month for month in MONTHS if month in totals.index]).rename("sales")


def quarterly_sales(data: pd.DataFrame) -> pd.Series:
    """Return Q1–Q4 revenue totals, including zeroes for unselected quarters."""
    if data.empty:
        return pd.Series(0.0, index=pd.Index(QUARTERS, name="quarter"), name="sales")
    month_number = data["month"].map(_MONTH_NUMBER).astype(int)
    quarter = ((month_number - 1) // 3 + 1).map(lambda value: QUARTERS[value - 1])
    totals = data.assign(quarter=quarter).groupby("quarter", sort=False)["sales"].sum()
    return totals.reindex(QUARTERS, fill_value=0).rename("sales")


def average_store_sales(data: pd.DataFrame) -> float:
    """Return the mean annual (or filtered-period) revenue across stores."""
    totals = sales_per_store(data)
    return float(totals.mean()) if not totals.empty else 0.0


def _best_label(data: pd.DataFrame, column: str) -> str | None:
    totals = _grouped_sales(data, column)
    if totals.empty:
        return None
    return str(totals.idxmax())


def best_store(data: pd.DataFrame) -> str | None:
    """Return the store with the largest total in the supplied rows."""
    return _best_label(data, "store")


def best_product(data: pd.DataFrame) -> str | None:
    """Return the product with the largest total in the supplied rows."""
    return _best_label(data, "product")


def filter_sales(
    data: pd.DataFrame,
    stores: list[str] | tuple[str, ...] | None = None,
    products: list[str] | tuple[str, ...] | None = None,
    months: list[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Return matching rows; ``None`` means all and an empty selection means none."""
    filtered = data
    if stores is not None:
        filtered = filtered[filtered["store"].isin(stores)]
    if products is not None:
        filtered = filtered[filtered["product"].isin(products)]
    if months is not None:
        selected_months = {_normalize_month(month) for month in months}
        filtered = filtered[filtered["month"].isin(selected_months)]
    return filtered.loc[:, COLUMNS].copy().reset_index(drop=True)


def monthly_target_comparison(
    data: pd.DataFrame,
    all_data: pd.DataFrame | None = None,
    selected_combinations_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compare monthly actuals with targets scaled to selected combinations.

    The notebook defines a per-store-product target from 30,000 in January to
    70,000 in December. For each month, aggregate target is
    ``per_combination_target × all_combinations``; the displayed target is that
    aggregate multiplied by ``selected_combinations ÷ all_combinations``.
    ``all_data`` anchors the denominator to the complete dataset, while
    ``selected_combinations_data`` may preserve the store/product scope when
    ``data`` has also been filtered by month.
    """
    result_columns = ["actual", "target"]
    if data.empty:
        return pd.DataFrame(columns=result_columns, index=pd.Index([], name="month"))

    denominator_data = all_data if all_data is not None else data
    combinations_data = selected_combinations_data if selected_combinations_data is not None else data
    all_combinations = denominator_data[["store", "product"]].drop_duplicates().shape[0]
    selected_combinations = combinations_data[["store", "product"]].drop_duplicates().shape[0]
    if not all_combinations or not selected_combinations:
        return pd.DataFrame(columns=result_columns, index=pd.Index([], name="month"))

    ratio = selected_combinations / all_combinations
    actual = monthly_sales(data)
    month_numbers = [_MONTH_NUMBER[month] for month in actual.index]
    aggregate_targets = MONTH_TARGETS * all_combinations
    targets = pd.Series(
        [aggregate_targets[number - 1] * ratio for number in month_numbers],
        index=actual.index,
        name="target",
    )
    comparison = pd.concat([actual.rename("actual"), targets], axis=1)
    comparison.index.name = "month"
    return comparison[result_columns]
