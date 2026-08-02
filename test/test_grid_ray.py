from nav2_loopback_sim.grid_ray import iter_grid_ray


def test_grid_ray_covers_endpoints_and_intermediate_cells() -> None:
    assert list(iter_grid_ray(1, 1, 4, 3)) == [(1, 1), (2, 2), (3, 2), (4, 3)]


def test_grid_ray_handles_reverse_axis_aligned_ray() -> None:
    assert list(iter_grid_ray(3, 2, 0, 2)) == [(3, 2), (2, 2), (1, 2), (0, 2)]
