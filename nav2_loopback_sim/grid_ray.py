"""Integer grid traversal used by the loopback scan model."""


def iter_grid_ray(start_x: int, start_y: int, end_x: int, end_y: int):
    """Yield every grid cell on a Bresenham ray, including both endpoints."""
    x, y = start_x, start_y
    delta_x = abs(end_x - start_x)
    delta_y = -abs(end_y - start_y)
    step_x = 1 if start_x < end_x else -1
    step_y = 1 if start_y < end_y else -1
    error = delta_x + delta_y

    while True:
        yield x, y
        if x == end_x and y == end_y:
            return
        doubled_error = 2 * error
        if doubled_error >= delta_y:
            error += delta_y
            x += step_x
        if doubled_error <= delta_x:
            error += delta_x
            y += step_y
