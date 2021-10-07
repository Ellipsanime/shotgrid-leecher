import uuid

from assertpy import assert_that
from toolz import compose

from shotgrid_leecher.mapper.hierarchy_mapper import to_shot_row
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridShot,
    ShotgridShotParams,
)

_S = compose(str, uuid.uuid4)
_I64 = compose(
    lambda x: x if x % 5 == 0 else None,
    lambda: uuid.uuid4().int,
)


def test_to_shot_row_without_params():
    # Arrange
    shot = ShotgridShot(_S(), _S(), uuid.uuid4().int, None, None, None, None)
    # Act
    actual = to_shot_row(shot, _S())
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(set(actual.keys())).is_equal_to(
        {"_id", "src_id", "type", "parent"}
    )


def test_to_shot_row_with_params():
    # Arrange
    params = ShotgridShotParams(
        _I64(), _I64(), _I64(), _I64(), _I64(), _I64(), _I64(), _I64()
    )
    shot = ShotgridShot(_S(), _S(), uuid.uuid4().int, params, None, None, None)
    # Act
    actual = to_shot_row(shot, _S())
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual["params"]["clip_in"]).is_equal_to(params.cut_in)
    assert_that(actual["params"]["clip_out"]).is_equal_to(params.cut_out)
