"""Pytest-обёртка для QA-05."""

import pytest

from tests.evaluation.evaluate_precision import run_precision_evaluation
from tests.helpers.stack import is_api_available


pytestmark = pytest.mark.evaluation


@pytest.fixture(scope="module")
def require_evaluation_stack():
    if not is_api_available():
        pytest.skip("Evaluation: запустите Backend, Elasticsearch и Redis")


def test_precision_at_3_report(require_evaluation_stack):
    results, report_path = run_precision_evaluation()

    hits = sum(1 for item in results if item.hit)
    precision = hits / len(results)

    assert report_path.exists()
    assert len(results) == 10
    assert precision >= 0.5, (
        f"Низкое качество поиска: Метрика Precision@3 составляет всего {precision:.0%}. "
        f"Отчёт: {report_path}"
    )