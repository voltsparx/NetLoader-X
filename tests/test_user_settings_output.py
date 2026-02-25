from core.user_settings import default_output_dir_home, get_default_output_dir


def test_default_output_dir_home_name():
    assert default_output_dir_home().lower().endswith("netloader-x-output")


def test_get_default_output_dir_returns_non_empty():
    value = get_default_output_dir()
    assert isinstance(value, str)
    assert value.strip() != ""
