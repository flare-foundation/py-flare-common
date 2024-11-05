import pytest

from py_flare_common.epoch.factory import (
    Factory,
    RewardEpochFactory,
    VotingEpochFactory,
)


@pytest.fixture
def factory():
    def make(first_epoch_epoc=1658430000, epoch_duration=90):
        factory = Factory(first_epoch_epoc, epoch_duration)
        return factory

    return make


@pytest.fixture
def voting_epoch_factory():
    def make(
        first_epoch_epoc=1658430000,
        epoch_duration=90,
        ftso_reveal_deadline=45,
        reward_first_epoch_epoc=1658430000,
        reward_epoch_duration=302400,
    ):
        factory = VotingEpochFactory(
            first_epoch_epoc,
            epoch_duration,
            ftso_reveal_deadline,
            reward_first_epoch_epoc,
            reward_epoch_duration,
        )
        return factory

    return make


@pytest.fixture
def reward_epoch_factory():
    def make(
        first_epoch_epoc=1658430000,
        epoch_duration=302400,
        voting_first_epoch_epoc=1658430000,
        voting_epoch_duration=90,
        voting_ftso_reveal_deadline=45,
    ):
        factory = RewardEpochFactory(
            first_epoch_epoc,
            epoch_duration,
            voting_first_epoch_epoc,
            voting_epoch_duration,
            voting_ftso_reveal_deadline,
        )
        return factory

    return make
