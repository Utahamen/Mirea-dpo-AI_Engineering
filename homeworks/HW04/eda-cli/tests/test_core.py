from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


def test_top_categories_top_k_parameter():
    """Тест проверяет, что параметр top_k корректно ограничивает количество возвращаемых значений."""
    # Создаём DataFrame с категориальной колонкой, где больше 5 уникальных значений
    df = pd.DataFrame(
        {
            "category": ["A", "B", "C", "D", "E", "F", "G", "A", "B", "C"],
            "numeric": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )

    # Тест 1: top_k=3 должен вернуть только 3 значения
    top_cats_3 = top_categories(df, max_columns=5, top_k=3)
    assert "category" in top_cats_3
    category_table_3 = top_cats_3["category"]
    assert len(category_table_3) == 3
    assert "value" in category_table_3.columns
    assert "count" in category_table_3.columns
    assert "share" in category_table_3.columns

    # Тест 2: top_k=5 должен вернуть 5 значений (но в данных только 7 уникальных)
    top_cats_5 = top_categories(df, max_columns=5, top_k=5)
    assert "category" in top_cats_5
    category_table_5 = top_cats_5["category"]
    assert len(category_table_5) == 5

    # Тест 3: top_k=10 должен вернуть все уникальные значения (7)
    top_cats_10 = top_categories(df, max_columns=5, top_k=10)
    assert "category" in top_cats_10
    category_table_10 = top_cats_10["category"]
    assert len(category_table_10) == 7  # Все уникальные значения: A, B, C, D, E, F, G

    # Тест 4: проверяем, что значения отсортированы по частоте (count)
    counts = category_table_3["count"].tolist()
    assert counts == sorted(counts, reverse=True), "Значения должны быть отсортированы по убыванию частоты"

    # Тест 5: проверяем, что share суммируется корректно
    total_share = category_table_3["share"].sum()
    assert abs(total_share - 1.0) < 1e-6, f"Сумма долей должна быть равна 1.0, получено {total_share}"