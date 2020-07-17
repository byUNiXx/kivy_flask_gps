import pytest

from server.src.models.phone import Moving


class TestModelPhone:

    def test_validate_coordinates(self):
        valid_coords = [(-90.000, 0.0), (90.000, 0.0), (0.0, -180.000), (0.0, 180.000)]

        invalid_coords = [(-90.001, 0.0), (90.001, 0.0), (0.0, -180.001), (0.0, 180.001)]
        pid = "197c92f1-ef0d-41b2-8192-1444b232a5fd"
        for coord in valid_coords:
            vehicle = Moving(pid, None, None, None, coord[0], coord[1], None, None)
            assert vehicle.lat == coord[0]
            assert vehicle.lon == coord[1]

        for coord in invalid_coords:
            with pytest.raises(ValueError):
                Moving(pid, None, None, None, coord[0], coord[1], None, None)
