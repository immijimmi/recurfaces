import pytest
from pygame import Surface, Rect

from recurfaces import Recurface


@pytest.fixture
def res():
    class RecurfaceResources:
        surface_bg = Surface((800, 600))
        surface_1 = Surface((300, 200))
        surface_2 = Surface((100, 300))
        surface_3 = Surface((70, 60))

        recurface_no_position = Recurface(surface_1)
        recurface_1 = Recurface(surface=surface_1, position=(10, 20))
        recurface_2 = Recurface(surface=surface_2, position=(30, 40))
        recurface_3 = Recurface(surface=surface_3, position=(50, 60))
        recurface_no_surface = Recurface(position=(10, 20))

    return RecurfaceResources


class TestRecurface:
    def test_first_render(self, res):
        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_unchanged_render(self, res):
        res.recurface_1.render(res.surface_bg)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == []

    def test_moved_before_first_render(self, res):
        res.recurface_1.move_render_position(20)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(30, 20, 300, 200)]

    def test_moved_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.move_render_position(20)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200), Rect(30, 20, 300, 200)]

    def test_surface_changed_before_first_render(self, res):
        res.recurface_1.surface = res.surface_3

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 70, 60)]

    def test_surface_changed_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.surface = res.surface_2

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200), Rect(10, 20, 100, 300)]

    def test_surface_changed_to_contained_surface_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.surface = res.surface_3

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_added_child_before_first_render(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_added_child_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.add_child_recurface(res.recurface_2)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(40, 60, 100, 160)]

    def test_do_render_false_before_first_render(self, res):
        res.recurface_1.do_render = False

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == []

    def test_do_render_false_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.do_render = False

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_do_render_false_with_children_before_first_render(self, res):
        res.recurface_1.do_render = False
        res.recurface_1.add_child_recurface(res.recurface_2)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == []

    def test_child_do_render_false_after_first_render(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_1.render(res.surface_bg)
        res.recurface_2.do_render = False

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(40, 60, 100, 160)]

    def test_no_position_before_first_render(self, res):
        rects = res.recurface_no_position.render(res.surface_bg)
        assert rects == []

    def test_no_position_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.render_position = None

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_no_position_with_children_before_first_render(self, res):
        res.recurface_no_position.add_child_recurface(res.recurface_2)

        rects = res.recurface_no_position.render(res.surface_bg)
        assert rects == []

    def test_no_surface_before_first_render(self, res):
        rects = res.recurface_no_surface.render(res.surface_bg)
        assert rects == []

    def test_no_surface_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_1.surface = None

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200)]

    def test_no_surface_with_children_before_first_render(self, res):
        res.recurface_no_surface.add_child_recurface(res.recurface_2)
        res.recurface_no_surface.add_child_recurface(res.recurface_3)

        rects = res.recurface_no_surface.render(res.surface_bg)
        assert rects == [Rect(40, 60, 100, 300)]

    def test_move_position_multiple_ways_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.render_position = (25, 50)
        res.recurface_1.move_render_position(3, 6)
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200), Rect(28, 56, 300, 200)]

    def test_change_multiple_attributes_after_first_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.surface = res.surface_2
        res.recurface_1.render_position = (40, 30)
        res.recurface_1.add_child_recurface(res.recurface_2)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(10, 20, 300, 200), Rect(40, 30, 100, 300)]

    def test_add_top_level_update_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1._add_top_level_update_rects([Rect(1, 2, 3, 4)])
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(1, 2, 3, 4)]

    def test_add_child_after_child_moved(self, res):
        res.recurface_1.render(res.surface_bg)
        res.recurface_2.render(res.surface_bg)

        res.recurface_2.render_position = (40, 50)
        res.recurface_1.add_child_recurface(res.recurface_2)  # This will reset recurface_2

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(30, 40, 100, 300), Rect(50, 70, 100, 150)]

    def test_remove_child_after_child_moved(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_1.render(res.surface_bg)

        res.recurface_2.render_position = (40, 50)  # Should have no effect on returned rects once it is removed
        res.recurface_1.remove_child_recurface(res.recurface_2)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(40, 60, 100, 160)]

    def test_unlink_correctly_restructures_chain(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)

        assert [*res.recurface_1.child_recurfaces] == [res.recurface_2]
        assert [*res.recurface_2.child_recurfaces] == [res.recurface_3]

        res.recurface_2.unlink()

        assert [*res.recurface_2.child_recurfaces] == []
        assert res.recurface_2.parent_recurface is None

        assert [*res.recurface_1.child_recurfaces] == [res.recurface_3]
        assert res.recurface_3.parent_recurface == res.recurface_1

    def test_unlink_before_first_linked_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)
        # Repositioning recurface_2 should persist on recurface_3 even after unlinking
        res.recurface_2.move_render_position(4, 5)
        res.recurface_2.unlink()

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(94, 125, 70, 60)]

    def test_unlink_after_first_linked_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)
        res.recurface_2.move_render_position(4, 5)

        res.recurface_1.render(res.surface_bg)
        res.recurface_2.unlink()  # Should attach its rect to recurface_1 on the way out

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(44, 65, 100, 155), Rect(94, 125, 70, 60)]

    def test_copy_surface_with_no_surface(self, res):
        assert pytest.raises(ValueError, res.recurface_no_surface.generate_surface_copy)

    def test_before_render(self, res):
        res.recurface_1.before_render = lambda r: r.move_render_position(10)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(20, 20, 300, 200)]

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(20, 20, 300, 200), Rect(30, 20, 300, 200)]
