"""Базовые сценарии удержания мест."""
import pytest

from app.services import hold_service
from app.services.hold_service import SeatsNotFound, SeatsUnavailable


def test_create_and_get_hold(SessionFactory, seeded):
    db = SessionFactory()
    try:
        seat_ids = seeded["seat_ids"][:2]
        resp = hold_service.create_hold(
            db, seeded["event_id"], seat_ids, "sess-token-0001"
        )
        assert resp.status == "active"
        assert len(resp.seats) == 2
        assert resp.total_cents == 2000  # 2 места по 1000
        assert resp.seconds_remaining > 0

        got = hold_service.get_hold(db, resp.id)
        assert got is not None
        assert got.id == resp.id
    finally:
        db.close()


def test_second_hold_on_same_seat_conflicts(SessionFactory, seeded):
    db1 = SessionFactory()
    db2 = SessionFactory()
    try:
        seat = [seeded["seat_ids"][0]]
        hold_service.create_hold(db1, seeded["event_id"], seat, "sess-token-aaaa")
        with pytest.raises(SeatsUnavailable):
            hold_service.create_hold(db2, seeded["event_id"], seat, "sess-token-bbbb")
    finally:
        db1.close()
        db2.close()


def test_all_or_nothing(SessionFactory, seeded):
    """Если одно из мест занято — весь запрос отклоняется, свободное не удерживается."""
    db1 = SessionFactory()
    db2 = SessionFactory()
    try:
        s = seeded["seat_ids"]
        hold_service.create_hold(db1, seeded["event_id"], [s[1]], "sess-token-cccc")
        with pytest.raises(SeatsUnavailable):
            hold_service.create_hold(
                db2, seeded["event_id"], [s[0], s[1]], "sess-token-dddd"
            )
        # s[0] осталось свободным — его можно взять.
        ok = hold_service.create_hold(db2, seeded["event_id"], [s[0]], "sess-token-eeee")
        assert ok.status == "active"
    finally:
        db1.close()
        db2.close()


def test_unknown_seat_raises_not_found(SessionFactory, seeded):
    db = SessionFactory()
    try:
        with pytest.raises(SeatsNotFound):
            hold_service.create_hold(
                db, seeded["event_id"], [999999], "sess-token-ffff"
            )
    finally:
        db.close()


def test_release_frees_seats(SessionFactory, seeded):
    db = SessionFactory()
    try:
        s = seeded["seat_ids"][:2]
        hold = hold_service.create_hold(db, seeded["event_id"], s, "sess-token-gggg")
        hold_service.release_hold(db, hold.id)
        # После release места снова можно удержать.
        again = hold_service.create_hold(db, seeded["event_id"], s, "sess-token-hhhh")
        assert again.status == "active"
    finally:
        db.close()
