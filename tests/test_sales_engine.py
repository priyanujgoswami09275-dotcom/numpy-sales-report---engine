from io import BytesIO
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sales_engine as engine


SAMPLE_CSV = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"


def test_generated_totals_match_notebook_values():
    sales = engine.generate_sample_sales()

    assert engine.total_revenue(sales) == 32_599_356
    assert engine.sales_per_store(sales).tolist() == [
        3_079_446,
        3_206_475,
        3_039_067,
        3_022_909,
        2_798_817,
        2_917_472,
        2_369_025,
        2_883_524,
        3_146_814,
        3_043_176,
        3_092_631,
    ]
    assert engine.sales_per_product(sales).tolist() == [
        6_041_676,
        6_642_898,
        6_866_607,
        6_938_544,
        6_109_631,
    ]
    assert engine.monthly_sales(sales).tolist() == [
        2_737_962,
        2_832_880,
        2_928_487,
        2_540_172,
        2_879_953,
        2_375_255,
        2_866_909,
        2_729_448,
        2_362_466,
        3_032_122,
        2_298_197,
        3_015_505,
    ]
    assert engine.quarterly_sales(sales).tolist() == [
        8_499_329,
        7_795_380,
        7_958_823,
        8_345_824,
    ]
    assert engine.average_store_sales(sales) == pytest.approx(2_963_577.8181818184)
    assert engine.best_store(sales) == "Store 1"
    assert engine.best_product(sales) == "Earbuds"


def test_monthly_and_quarterly_sums_equal_grand_total():
    sales = engine.generate_sample_sales()

    assert engine.monthly_sales(sales).sum() == engine.total_revenue(sales)
    assert engine.quarterly_sales(sales).sum() == engine.total_revenue(sales)


def test_sample_csv_loads_and_round_trips(tmp_path):
    original = engine.load_sales_csv(SAMPLE_CSV)
    exported_path = engine.write_sample_csv(tmp_path / "round_trip.csv")
    round_tripped = engine.load_sales_csv(exported_path)

    pd.testing.assert_frame_equal(original, round_tripped)
    assert len(original) == 11 * 5 * 12
    assert not original.duplicated(["store", "product", "month"]).any()


def test_csv_accepts_month_names_and_numbers_and_sums_duplicates():
    csv_data = BytesIO(
        b"store,product,month,sales\n"
        b"A,Widget,January,10\n"
        b"A,Widget,jan,20\n"
        b"A,Widget,2,30\n"
        b"A,Widget,FEB,40\n"
    )

    result = engine.load_sales_csv(csv_data)

    assert result[["month", "sales"]].values.tolist() == [["Jan", 30], ["Feb", 70]]


def test_duplicate_integer_sales_do_not_overflow_during_aggregation():
    csv_data = BytesIO(
        b"store,product,month,sales\n"
        b"A,Widget,Jan,9000000000000000000\n"
        b"A,Widget,Jan,9000000000000000000\n"
        b"A,Widget,Jan,9000000000000000000\n"
    )

    result = engine.load_sales_csv(csv_data)

    assert int(result.loc[0, "sales"]) == 27_000_000_000_000_000_000


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"store,product,month\nA,Widget,Jan\n", "Missing required columns: sales"),
        (b"store,product,month,sales\nA,Widget,Jan,abc\n", "sales must be numeric"),
        (b"store,product,month,sales\nA,Widget,Jan,-1\n", "negative sales"),
        (b"store,product,month,sales\nA,Widget,Smarch,10\n", "Invalid month"),
        (b"store,product,month,sales, SALES \nA,Widget,Jan,10,20\n", "Duplicate column names after normalization"),
        (b"", "empty"),
        (b"store,product,month,sales\n", "empty"),
    ],
)
def test_invalid_csv_has_a_clear_error(content, message):
    with pytest.raises(engine.SalesDataError, match=message):
        engine.load_sales_csv(BytesIO(content))


def test_monthly_target_scales_to_selected_combinations():
    all_sales = engine.generate_sample_sales()
    cases = [
        (["Store 0"], None, 5 / 55),
        (["Store 0"], ["Laptop"], 1 / 55),
        (["Store 0", "Store 1"], ["Laptop", "Earbuds"], 4 / 55),
        (None, None, 1.0),
    ]

    for stores, products, ratio in cases:
        selected = engine.filter_sales(all_sales, stores=stores, products=products)
        comparison = engine.monthly_target_comparison(selected, all_data=all_sales)
        expected_targets = np.linspace(30_000, 70_000, 12) * 55 * ratio

        assert comparison["target"].tolist() == pytest.approx(expected_targets)
        assert comparison["actual"].sum() == engine.total_revenue(selected)


def test_target_comparison_respects_selected_months():
    all_sales = engine.generate_sample_sales()
    selected = engine.filter_sales(
        all_sales,
        stores=["Store 0"],
        products=["Laptop"],
        months=["Mar", "Jan"],
    )

    comparison = engine.monthly_target_comparison(selected, all_data=all_sales)

    assert comparison.index.tolist() == ["Jan", "Mar"]
    assert comparison["target"].tolist() == pytest.approx([30_000, 37_272.72727272727])


def test_target_uses_store_product_selection_even_when_month_data_is_sparse():
    all_sales = engine.load_sales_csv(
        BytesIO(
            b"store,product,month,sales\n"
            b"A,Widget,Jan,10\n"
            b"B,Widget,Feb,20\n"
        )
    )
    january = engine.filter_sales(all_sales, months=["Jan"])
    selected_combinations = engine.filter_sales(
        all_sales,
        stores=["A", "B"],
        products=["Widget"],
    )

    comparison = engine.monthly_target_comparison(
        january,
        all_data=all_sales,
        selected_combinations_data=selected_combinations,
    )

    assert comparison.loc["Jan", "target"] == 60_000


def test_filters_can_return_an_empty_dataframe_without_error():
    sales = engine.generate_sample_sales()

    result = engine.filter_sales(sales, stores=["missing store"])

    assert result.empty
    assert list(result.columns) == ["store", "product", "month", "sales"]
    assert engine.total_revenue(result) == 0
    assert engine.best_store(result) is None
    assert engine.best_product(result) is None


def test_explicitly_empty_filter_matches_no_rows():
    sales = engine.generate_sample_sales()

    result = engine.filter_sales(sales, stores=[])

    assert result.empty


def test_app_loads_with_four_kpis_and_charts():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()

    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.get("plotly_chart")) == 4
    assert any("Sales Engine" in element.value for element in app.sidebar.markdown)
    assert any("Sales Engine" in element.value for element in app.markdown)


def test_app_filters_update_kpis():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    all_revenue = app.metric[0].value

    app.multiselect(key="store_filter").set_value(["Store 0"])
    app.multiselect(key="product_filter").set_value(["Laptop"])
    app.multiselect(key="month_filter").set_value(["Jan"])
    app.run()

    assert not app.exception
    assert app.metric[0].value != all_revenue
    assert len(app.get("plotly_chart")) == 4


def test_app_accepts_uploaded_csv():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    upload = b"store,product,month,sales\nA,Widget,Jan,120\nA,Widget,Feb,180\n"

    app.file_uploader[0].upload("uploaded.csv", upload, "text/csv")
    app.run()

    assert not app.exception
    assert len(app.metric) == 4
    assert any("Uploaded Data" in element.value for element in app.markdown)


def test_invalid_upload_keeps_error_and_sample_download_available():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    invalid_upload = b"store,product,month,sales\nA,Widget,Jan,not-a-number\n"

    app.file_uploader[0].upload("invalid.csv", invalid_upload, "text/csv")
    app.run()

    assert not app.exception
    assert any("sales must be numeric" in element.value for element in app.sidebar.error)
    assert len(app.sidebar.get("download_button")) == 1


def test_store_and_product_charts_highlight_only_the_top_bar():
    import json

    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()

    for chart_index in (1, 2):
        chart = json.loads(app.get("plotly_chart")[chart_index].proto.spec)["data"][0]
        values = chart["y"]
        colors = chart["marker"]["color"]
        top_index = values.index(max(values))

        assert colors[top_index] == "#3ba6f1"
        assert all(color == "#d6d3d1" for index, color in enumerate(colors) if index != top_index)
