from tests.salary import calculate_salary


def test_calculate_salary():
    assert calculate_salary(20000, 10) == 22000
