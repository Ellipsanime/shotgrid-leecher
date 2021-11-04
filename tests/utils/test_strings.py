from assertpy import assert_that

from shotgrid_leecher.utils.strings import snakify_camel, avalonify_snake_case


def test_snakify_camel():
    # Arrange
    target = "ABloodyBright_String"
    # Act
    actual = snakify_camel(target)
    # Assert
    assert_that(actual).is_equal_to("a_bloody_bright_string")


def test_avalonify_snake_case_without_exception():
    # Arrange
    target = "avalon_are_you_serious"
    # Act
    actual = avalonify_snake_case(target)
    # Assert
    assert_that(actual).is_equal_to("avalonAreYouSerious")


def test_avalonify_snake_case_when_exception():
    # Arrange
    target = "tools_env"
    # Act
    actual = avalonify_snake_case(target)
    # Assert
    assert_that(actual).is_equal_to("tools_env")
