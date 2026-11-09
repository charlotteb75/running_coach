from datetime import date
from unittest.mock import Mock, patch

import pytest

from app.models import RunningHistory
from app.routes.running_history import get_distance_history, get_pace_history, get_bpm_history


@pytest.mark.parametrize(('view', 'expected'), [
    (get_distance_history, 7.0),
    (get_pace_history, 30.0 / 7.0),
    (get_bpm_history, (140 * 1200 + 160 * 600) / 1800),
])
def test_aggregate_uses_garmin_units(db_session, view, expected):
    for distance, duration, bpm in [(5000, 1200, 140), (2000, 600, 160)]:
        db_session.add(RunningHistory(run_date=date.today(), run_distance=distance,
                                      run_time=duration, bpm=bpm, elevation=0))
    db_session.commit()
    # Capture the route's SQL and execute its real aggregate on SQLite.
    # PostgreSQL's date_trunc grouping is deliberately outside this unit test.
    with patch.object(db_session, 'execute', return_value=Mock(all=lambda: [])) as execute:
        view()
        query = execute.call_args.args[0]
    aggregate = list(query.selected_columns)[1]
    query = query.with_only_columns(aggregate).group_by(None).order_by(None)
    assert db_session.scalar(query) == pytest.approx(expected)
