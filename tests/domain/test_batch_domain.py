from assertpy import assert_that
from unittest.mock import PropertyMock, patch


@patch("shotgrid_leecher.mapper.hierarchy_mapper.shotgrid_to_avalon")
@patch("shotgrid_leecher.repository.shotgrid_hierarchy_repo")
@patch("shotgrid_leecher.utils.connectivity.get_shotgrid_client")
@patch("shotgrid_leecher.utils.connectivity.get_db_client")
def test_shotgrid_to_avalon_batch_when_overwrite_requested(
    get_mongo: PropertyMock,
    get_shotgrid: PropertyMock,
    repo: PropertyMock,
    mapper: PropertyMock,
):
    # Arrange
    # Act
    # Assert
    assert_that(True).is_false()
