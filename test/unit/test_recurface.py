import pytest
from pygame import display, Surface, Rect

from datetime import datetime
from json import loads, dumps
from subprocess import check_output

from recurfaces import Recurface


@pytest.fixture
def res():
    class RecurfaceResources:
        surface_bg = Surface((800, 600))
        surface_1 = Surface((300, 200))
        surface_2 = Surface((100, 300))
        surface_3 = Surface((70, 60))
        surface_simple = Surface((100, 100))

        recurface_no_position = Recurface(surface_1)
        recurface_1 = Recurface(surface=surface_1, position=(10, 20))
        recurface_2 = Recurface(surface=surface_2, position=(30, 40))
        recurface_3 = Recurface(surface=surface_3, position=(50, 60))
        recurface_no_surface = Recurface(position=(10, 20))

        recurface_simple_1 = Recurface(surface=surface_simple, position=(0, 0))
        recurface_simple_2 = Recurface(position=(1, 1))
        recurface_simple_3 = Recurface(surface=surface_simple, position=(1, 1))
        recurface_simple_4 = Recurface(position=(1, 1))
        recurface_simple_5 = Recurface(position=(1, 1))
        recurface_simple_6 = Recurface(surface=surface_simple, position=(1, 1))
        recurface_simple_7 = Recurface(surface=surface_simple, position=(1, 1))

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

        res.recurface_2.unlink(True)

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
        res.recurface_2.unlink(True)

        rects = res.recurface_1.render(res.surface_bg)
        assert rects == [Rect(94, 125, 70, 60)]

    def test_unlink_after_first_linked_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)
        res.recurface_2.move_render_position(4, 5)

        res.recurface_1.render(res.surface_bg)
        res.recurface_2.unlink(True)  # Should attach its rect to recurface_1 on the way out

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

    def test_long_chain_rects(self, res):
        """
        This test checks that a long recurface chain with a mix of surfaces and no surfaces returns the correct
        rects when heavily nested members of the chain are un-rendered and re-rendered.

        The rationale for this test is to ensure that the returned rects are correctly modified as they are
        passed up the chain, offsetting coordinates and truncating dimensions accordingly
        """

        res.recurface_simple_1.add_child_recurface(res.recurface_simple_2)
        res.recurface_simple_2.add_child_recurface(res.recurface_simple_3)
        res.recurface_simple_3.add_child_recurface(res.recurface_simple_4)
        res.recurface_simple_4.add_child_recurface(res.recurface_simple_5)
        res.recurface_simple_5.add_child_recurface(res.recurface_simple_6)
        res.recurface_simple_6.add_child_recurface(res.recurface_simple_7)

        res.recurface_simple_1.render(res.surface_bg)

        res.recurface_simple_7.do_render = False
        rects = res.recurface_simple_1.render(res.surface_bg)
        assert rects == [Rect(6, 6, 94, 94)]
        res.recurface_simple_7.do_render = True
        res.recurface_simple_1.render(res.surface_bg)

        res.recurface_simple_6.do_render = False
        rects = res.recurface_simple_1.render(res.surface_bg)
        assert rects == [Rect(5, 5, 95, 95)]
        res.recurface_simple_6.do_render = True
        res.recurface_simple_1.render(res.surface_bg)

        # 5 has no surface of its own, so the output should match 6
        res.recurface_simple_5.do_render = False
        rects = res.recurface_simple_1.render(res.surface_bg)
        assert rects == [Rect(5, 5, 95, 95)]
        res.recurface_simple_5.do_render = True
        res.recurface_simple_1.render(res.surface_bg)

        # Likewise with 4
        res.recurface_simple_4.do_render = False
        rects = res.recurface_simple_1.render(res.surface_bg)
        assert rects == [Rect(5, 5, 95, 95)]
        res.recurface_simple_4.do_render = True
        res.recurface_simple_1.render(res.surface_bg)

        res.recurface_simple_3.do_render = False
        rects = res.recurface_simple_1.render(res.surface_bg)
        assert rects == [Rect(2, 2, 98, 98)]

    def test_performance(self, res):
        """
        This test implements a broad check to ensure that performance has not significantly dropped due to
        applied changes.

        The target value should be calibrated by running this test on a specific baseline commit, with no other
        heavy tasks running on the same machine during calibration. This will generate a config.json file
        in the test folder.

        This test should then be run again, with that config file present, on the version which needs testing
        """

        def get_commit_hash():
            if calibration_commit is not None:
                return check_output("git show --pretty=format:'%H' --no-patch").decode("UTF-8")

        """
        This variable should be set to the relevant commit hash once this test is otherwise completed and committed.
        When making changes to this test, it should be set back to None in the commit which applies the changes,
        and then set to that commit's hash in the next commit
        """
        calibration_commit = None

        rounding_precision = 3
        target_ms = None
        json_file_path = "test/config.json"
        json_key = "test_performance_target_ms"
        config = {}
        current_commit = get_commit_hash()

        # Loading config
        try:
            with open(json_file_path, "r") as config_file:
                config = loads(config_file.read())
                target_ms = config[json_key]

            # No calibration needed, so should not be on the calibration commit
            assert current_commit != calibration_commit, (
                "the calibration commit is currently checked out."
                " Please checkout the desired commit for testing and re-run"
            )
        except (FileNotFoundError, KeyError):  # No valid config, calibrate and save a fresh config file
            assert current_commit == calibration_commit, (
                f"please checkout commit {calibration_commit} and re-run to calibrate this test"
            )

        # Running the test
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_1.surface.fill("white")
        res.recurface_1.flag_surface()
        res.recurface_2.surface.fill("red")
        res.recurface_2.flag_surface()

        display.init()
        window = display.set_mode((400, 300))

        start_time = datetime.now()
        for i in range(10000):
            if i % 2 == 0:
                res.recurface_2.move_render_position(50)
            else:
                res.recurface_2.move_render_position(-50)

            rects = res.recurface_1.render(window)
            display.update(rects)
        end_time = datetime.now()

        performance_ms = round((end_time - start_time).total_seconds() * 1000, rounding_precision)

        if target_ms is None:  # Store calibration results
            target_ms = performance_ms

            config[json_key] = target_ms
            with open(json_file_path, "w") as config_file:
                config_file.write(dumps(config))

            raise RuntimeError(
                f"test calibration completed ({performance_ms}ms), target performance stored in '{json_file_path}'."
                " Please run tests again with the desired commit checked out"
            )

        else:
            """
            As performance is heavily dependent on the specs and current state of the host machine, this test
            checks against each calibration value exactly once before deleting it from the config file.

            The intended usage is to calibrate just before running tests on a new commit (meaning that
            the state of the machine should be as close as possible between calibration and testing)
            """
            del config[json_key]
            with open(json_file_path, "w") as config_file:
                config_file.write(dumps(config))

            # Limits will be set to 5% above/below calibration performance (typical deviation is no more than 2-3%)
            upper_limit_ms = round(target_ms * 1.05, rounding_precision)
            lower_limit_ms = round(target_ms * 0.95, rounding_precision)

            assert performance_ms <= upper_limit_ms, (
                "test did not complete within the desired timeframe"
                f" ({performance_ms}ms > {upper_limit_ms}ms)"
            )

            if performance_ms < lower_limit_ms:
                raise RuntimeError(
                    "test completed faster than expected - please set a new calibration commit"
                    f" ({performance_ms}ms < {lower_limit_ms}ms)"
                )
