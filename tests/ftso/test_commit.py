import pytest

from py_flare_common.ftso.commit import commit_hash

# Real life examples:
# Example 1
#   submit1: https://flare-systems-explorer.flare.network/top-level-protocol/60aa107e05da3c10ec2d0d51c5424ca85907c170fb31c19f929b96b7ea49e6aa
#   submit2: https://flare-systems-explorer.flare.network/top-level-protocol/a65e3db73be6760559c2c13310bd0c3d8f2e456ea42a96838d3fc7f90bf33594
# Example 2
#   submit1: https://flare-systems-explorer.flare.network/top-level-protocol/60aa107e05da3c10ec2d0d51c5424ca85907c170fb31c19f929b96b7ea49e6aa
#   submit2: https://flare-systems-explorer.flare.network/top-level-protocol/a65e3db73be6760559c2c13310bd0c3d8f2e456ea42a96838d3fc7f90bf33594


@pytest.mark.parametrize(
    "submit_address, voting_round, random, feed_values, expected",
    [
        (
            "0xc4a19715F3Dd209F01E84ABe65De7c2E9C8b6269",
            812576,
            26613761005485227210124837044607206462361910438060874105373946905076167777370,
            bytes.fromhex(
                "801a963f8000dfca800039bc8000f4458007e5b5803311dc804"
                + "32212805ff7b9800098378089430f8001869f8000996b8007cd798000e83180223021"
                + "80311c9480027c2e8002001180064824800038ae800117e180095205800d1b0c8001c"
                + "afd800bd5d38014b103807c895c8007fd01800130fa80015bc48003979e8000931880"
                + "00a1b78060a3b7800ab8148008a8e18000db888000655e80215923800540998053243"
                + "580084836800045f8800d346480018695800186e5800654108000762b8001e52e80010feb"
            ),
            "05a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54",
        ),
        # (
        #     "0xc4a19715F3Dd209F01E84ABe65De7c2E9C8b6269",
        #     812576,
        #     26613761005485227210124837044607206462361910438060874105373946905076167777370,
        #     bytes.fromhex(
        #         "801a963f8000dfca800039bc8000f4458007e5b5803311dc804"
        #         + "32212805ff7b9800098378089430f8001869f8000996b8007cd798000e83180223021"
        #         + "80311c9480027c2e8002001180064824800038ae800117e180095205800d1b0c8001c"
        #         + "afd800bd5d38014b103807c895c8007fd01800130fa80015bc48003979e8000931880"
        #         + "00a1b78060a3b7800ab8148008a8e18000db888000655e80215923800540998053243"
        #         + "580084836800045f8800d346480018695800186e5800654108000762b8001e52e80010feb"
        #     ),
        #     "05a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54",
        # ),
    ],
)
def test_feed_epoch_init(submit_address, voting_round, random, feed_values, expected):
    hash = commit_hash(submit_address, voting_round, random, feed_values)
    assert hash == expected
