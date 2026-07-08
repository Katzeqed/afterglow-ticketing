"""Главный тест: гонка за одно место — победитель ровно один.

Много потоков одновременно пытаются удержать одно и то же место, каждый в своей
сессии/соединении. Благодаря `SELECT ... FOR UPDATE` успех получает ровно один.
"""
from concurrent.futures import ThreadPoolExecutor

from app.services import hold_service
from app.services.hold_service import SeatsUnavailable

N_THREADS = 20


def _try_hold(SessionFactory, event_id: int, seat_id: int, idx: int) -> bool:
    db = SessionFactory()
    try:
        hold_service.create_hold(db, event_id, [seat_id], f"sess-race-{idx:04d}")
        return True
    except SeatsUnavailable:
        return False
    finally:
        db.close()


def test_concurrent_holds_single_winner(SessionFactory, seeded):
    seat_id = seeded["seat_ids"][0]
    event_id = seeded["event_id"]

    with ThreadPoolExecutor(max_workers=N_THREADS) as pool:
        results = list(
            pool.map(
                lambda i: _try_hold(SessionFactory, event_id, seat_id, i),
                range(N_THREADS),
            )
        )

    # Ровно один поток удержал место, остальные получили конфликт.
    assert sum(results) == 1, f"ожидали 1 победителя, получили {sum(results)}"
