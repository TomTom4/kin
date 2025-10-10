from fastapi import Router

router = Router(prefix="/events")


EVENTS = []


@router.get("/")
def get_all_events():
    return EVENTS
