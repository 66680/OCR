from invstruct.utils.trace import generate_trace_id


def test_generate_trace_id_shape_and_uniqueness() -> None:
    first = generate_trace_id()
    second = generate_trace_id()
    assert first != second
    assert len(first) == 32
    assert len(second) == 32
