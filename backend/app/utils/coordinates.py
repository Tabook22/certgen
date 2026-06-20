def scale_coordinate(value: float, source_size: float, target_size: float) -> float:
    if source_size <= 0:
        raise ValueError("source_size must be greater than zero")
    return value * (target_size / source_size)
