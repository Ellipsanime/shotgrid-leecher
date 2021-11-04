from assertpy import assert_that

from shotgrid_leecher.utils.strings import snakify_camel


def test_snakify_camel():
    # Arrange
    target = "ABloodyBright_String"
    # Act
    actual = snakify_camel(target)
    # Assert
    assert_that(actual).is_equal_to("a_bloody_bright_string")
