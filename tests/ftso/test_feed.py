import pytest

from py_flare_common.ftso.feed import FtsoFeed


@pytest.mark.parametrize(
    "feed_id",
    [
        b"123456789012345678901",
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00",
        bytes.fromhex("014254432f55534400000000000000000000000000"),
    ],
)
def test_feed_epoch_init(feed_id):
    feed_epoch = FtsoFeed(feed_id)
    assert feed_epoch.feed_id == feed_id


@pytest.mark.parametrize(
    "feed_id",
    [
        b"12345678901234567890",
        b"1234567890123456789012",
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x00",
    ],
)
def test_feed_epoch_init_wrong_length(feed_id):
    with pytest.raises(ValueError):
        FtsoFeed(feed_id)


@pytest.mark.parametrize(
    "feed_id",
    [
        b"123456789012345678901",
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00",
        bytes.fromhex("014254432f55534400000000000000000000000000"),
    ],
)
def test_compare(feed_id):
    feed_epoch1 = FtsoFeed(feed_id)
    feed_epoch2 = FtsoFeed(feed_id)
    assert feed_epoch1 == feed_epoch2


def test_compare_not_eq():
    feed_epoch1 = FtsoFeed(b"123456789012345678901")
    feed_epoch2 = FtsoFeed(b"123456789012345678902")
    with pytest.raises(AssertionError):
        assert feed_epoch1 == feed_epoch2


@pytest.mark.parametrize(
    "feed_id, type, representation",
    [
        (bytes.fromhex("01444f47452f555344000000000000000000000000"), 1, "DOGE/USD"),
        (bytes.fromhex("014254432f55534400000000000000000000000000"), 1, "BTC/USD"),
    ],
)
def test_representation_and_type(feed_id, type, representation):
    feed_epoch = FtsoFeed(feed_id)
    assert feed_epoch.representation == representation
    assert feed_epoch.type == type


@pytest.mark.parametrize(
    "feed_id, type, representation",
    [
        (bytes.fromhex("01444f47452f555344000000000000000000000000"), 1, "DOGE/USD"),
        (bytes.fromhex("014254432f55534400000000000000000000000000"), 1, "BTC/USD"),
    ],
)
def test_from_representation_and_type(feed_id, type, representation):
    feed_epoch = FtsoFeed.from_represenation_and_type(type, representation)
    assert feed_epoch.feed_id == feed_id


@pytest.mark.parametrize(
    "hexstr",
    [
        "01444f47452f555344000000000000000000000000",
        "014254432f55534400000000000000000000000000",
    ],
)
def test_from_hexstr(hexstr):
    feed_epoch = FtsoFeed.fromhex(hexstr)
    assert feed_epoch.feed_id == bytes.fromhex(hexstr)
