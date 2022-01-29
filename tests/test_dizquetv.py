from tests.setup import client


def test_dizquetv_server_details():
    details = client().dizquetv_server_details
    assert details.server_version != ''
