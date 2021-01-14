from pygame import Surface

from ...recurface import Recurface


def test_no_position_on_first_render_returns_no_rects():
    surf_bg = Surface((800, 600))
    surf_1 = Surface((300, 300))
    surf_2 = Surface((100, 100))

    recurface = Recurface(surf_1, (0, 0))
    recurface.position = (0, 0)
    recurface.surface = surf_2
    recurface.position = None

    rects = recurface.render(surf_bg)

    assert rects == []
