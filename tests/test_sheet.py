"""Tests de df_to_sheet con una hoja falsa (sin red)."""

import numpy as np
import pandas as pd
import pytest

from sm_connectors.google import df_to_sheet, df_to_values


class FakeWorksheet:
    def __init__(self, rows=None, row_count=1000):
        self.rows = rows or []
        self.row_count = row_count

    def clear(self):
        self.rows = []

    def update(self, values, range_name):
        start = int(range_name[1:]) - 1  # solo se usan rangos "A<n>"
        assert range_name[0] == "A"
        assert start <= len(self.rows), "no debe dejar filas vacías en el medio"
        self.rows[start:start + len(values)] = [list(r) for r in values]

    def get_all_values(self):
        return self.rows

    def add_rows(self, n):
        self.row_count += n

    def row_values(self, n):
        return self.rows[n - 1] if len(self.rows) >= n else []


class FakeGC:
    def __init__(self, ws):
        self.ws = ws

    def open_by_key(self, _):
        return self

    def worksheet(self, _):
        return self.ws


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2], "b": ["x", None], "c": [np.nan, 3.5]})


def test_values_clean_nan_and_numpy(df):
    assert df_to_values(df) == [["a", "b", "c"], [1, "x", ""], [2, "", 3.5]]
    assert type(df_to_values(df)[1][0]) is int


def test_values_timestamp():
    d = pd.DataFrame({"f": [pd.Timestamp("2026-01-02 03:04:05")]})
    assert df_to_values(d)[1] == ["2026-01-02 03:04:05"]


def test_replace_overwrites(df):
    ws = FakeWorksheet([["viejo"], ["dato"], ["mas"], ["filas"]])
    assert df_to_sheet(FakeGC(ws), "id", "H", df, mode="replace") == 2
    assert ws.rows == [["a", "b", "c"], [1, "x", ""], [2, "", 3.5]]


def test_append_on_empty_writes_header(df):
    ws = FakeWorksheet()
    df_to_sheet(FakeGC(ws), "id", "H", df, mode="append")
    assert ws.rows[0] == ["a", "b", "c"] and len(ws.rows) == 3


def test_append_adds_rows_without_header(df):
    ws = FakeWorksheet([["a", "b", "c"], [0, "z", 1]])
    df_to_sheet(FakeGC(ws), "id", "H", df, mode="append")
    assert len(ws.rows) == 4 and ws.rows[2] == [1, "x", ""]


def test_append_twice_never_overwrites(df):
    ws = FakeWorksheet([["a", "b", "c"], [0, "z", 1]])
    df_to_sheet(FakeGC(ws), "id", "H", df.head(1), mode="append")
    df_to_sheet(FakeGC(ws), "id", "H", df.tail(1), mode="append")
    assert [r[0] for r in ws.rows] == ["a", 0, 1, 2]


def test_append_grows_grid_when_full(df):
    ws = FakeWorksheet([["a", "b", "c"], [0, "z", 1]], row_count=2)
    df_to_sheet(FakeGC(ws), "id", "H", df, mode="append")
    assert ws.row_count == 4 and len(ws.rows) == 4


def test_append_rejects_different_columns(df):
    ws = FakeWorksheet([["otra", "cosa"]])
    with pytest.raises(ValueError, match="no coinciden"):
        df_to_sheet(FakeGC(ws), "id", "H", df, mode="append")
    assert ws.rows == [["otra", "cosa"]]


class FakeReadWS:
    def __init__(self, records):
        self.records = records

    def get_all_records(self, head=1):
        return self.records


def test_sheet_to_df():
    from sm_connectors.google import sheet_to_df

    out = sheet_to_df(FakeGC(FakeReadWS([{"a": 1, "b": "x"}, {"a": 2, "b": ""}])), "id", "H")
    assert list(out.columns) == ["a", "b"] and out["a"].tolist() == [1, 2]


def test_sheet_to_df_empty_raises():
    from sm_connectors.google import sheet_to_df

    with pytest.raises(ValueError, match="no tiene filas"):
        sheet_to_df(FakeGC(FakeReadWS([])), "id", "H")


def test_invalid_mode(df):
    with pytest.raises(ValueError):
        df_to_sheet(FakeGC(FakeWorksheet()), "id", "H", df, mode="otro")
