import time

import pytest

from py_flare_common.epoch.epoch import Epoch, RewardEpoch, VotingEpoch
from py_flare_common.epoch.factory import (
    Factory,
    RewardEpochFactory,
    VotingEpochFactory,
)


class TestFactory:
    @pytest.fixture
    def factory(self):
        def make(first_epoch_epoc=100, epoch_duration=10):
            factory = Factory(first_epoch_epoc, epoch_duration)
            return factory

        return make

    def test_init(self, factory):
        factory = factory()
        assert isinstance(factory, Factory)
        assert factory.first_epoch_epoc == 100
        assert factory.epoch_duration == 10

    def compare_eq(self, factory):
        factory1 = factory()
        factory2 = factory()
        assert factory2 == factory1

    @pytest.mark.parametrize("factory_attr", [(100, 0), (10, 0)])
    def compare_neq(self, factory, factory_attr):
        factory1 = factory()
        factory2 = factory(*factory_attr)
        assert factory2 != factory1

    def test_make_epoch(self, factory):
        factory = factory()
        epoch = factory.make_epoch(17)
        assert isinstance(epoch, Epoch)
        assert epoch.id == 17
        assert epoch.factory == factory

    def test_duration(self, factory):
        assert factory().duration() == 10

    def test__from_timestamp(self, factory):
        assert factory()._from_timestamp(1146) == 104

    def test_from_timestamp(self, factory):
        factory = factory()
        epoch = factory.from_timestamp(1146)
        assert isinstance(epoch, Epoch)
        assert epoch.id == 104
        assert epoch.factory == factory

    def test_now(self, factory):
        factory = factory()
        epoch = factory.now()
        assert isinstance(epoch, Epoch)
        assert epoch.id == (int(time.time()) - 100) // 10
        assert epoch.factory == factory

    def test_now_id(self, factory):
        assert factory().now_id() == (int(time.time()) - 100) // 10


class TestVotingEpochFactory:
    @pytest.fixture
    def voting_epoch_factory(self):
        factory = VotingEpochFactory(100, 10, 5, 200, 20)
        return factory

    def test_init(self, voting_epoch_factory):
        assert isinstance(voting_epoch_factory, VotingEpochFactory)
        assert voting_epoch_factory.first_epoch_epoc == 100
        assert voting_epoch_factory.epoch_duration == 10
        assert voting_epoch_factory.ftso_reveal_deadline == 5
        assert voting_epoch_factory.reward_first_epoch_epoc == 200
        assert voting_epoch_factory.reward_epoch_duration == 20

    def test_make_epoch(self, voting_epoch_factory):
        epoch = voting_epoch_factory.make_epoch(27)
        assert isinstance(epoch, VotingEpoch)
        assert epoch.id == 27
        assert epoch.factory == voting_epoch_factory

    def test_make_reward_epoch(self, voting_epoch_factory):
        epoch = voting_epoch_factory.make_reward_epoch(250)
        assert isinstance(epoch, RewardEpoch)
        assert epoch.id == 2
        assert epoch.factory == RewardEpochFactory(200, 20, 100, 10, 5)


class TestRewardEpochFactory:
    @pytest.fixture
    def reward_epoch_factory(self):
        factory = RewardEpochFactory(200, 20, 100, 10, 5)
        return factory

    @pytest.fixture
    def voting_epoch(self):
        factory = VotingEpochFactory(100, 10, 5, 200, 20)
        epoch = factory.make_epoch(24)
        return epoch

    @pytest.fixture(
        params=[
            (0, 10, 5, 200, 20),
            (100, 0, 5, 200, 20),
            (100, 10, 0, 200, 20),
            (100, 10, 5, 0, 20),
            (100, 10, 5, 200, 0),
        ]
    )
    def wrong_voting_epoch(self, request):
        factory = VotingEpochFactory(*request.param)
        epoch = factory.make_epoch(24)
        return epoch

    def test_init(self, reward_epoch_factory):
        assert isinstance(reward_epoch_factory, RewardEpochFactory)
        assert reward_epoch_factory.first_epoch_epoc == 200
        assert reward_epoch_factory.epoch_duration == 20
        assert reward_epoch_factory.voting_first_epoch_epoc == 100
        assert reward_epoch_factory.voting_epoch_duration == 10
        assert reward_epoch_factory.voting_ftso_reveal_deadline == 5

    def test_make_epoch(self, reward_epoch_factory):
        epoch = reward_epoch_factory.make_epoch(27)
        assert isinstance(epoch, RewardEpoch)
        assert epoch.id == 27
        assert epoch.factory == reward_epoch_factory

    def test_make_voting_epoch(self, reward_epoch_factory):
        epoch = reward_epoch_factory.make_voting_epoch(350)
        assert isinstance(epoch, VotingEpoch)
        assert epoch.id == 25
        assert epoch.factory == VotingEpochFactory(100, 10, 5, 200, 20)

    def test_from_voting_epoch(self, reward_epoch_factory, voting_epoch):
        epoch = reward_epoch_factory.from_voting_epoch(voting_epoch)
        assert isinstance(epoch, RewardEpoch)
        assert epoch.id == 7
        assert epoch.factory == reward_epoch_factory

    def test_from_voting_epoch_wrong_voting_epoch(
        self, reward_epoch_factory, wrong_voting_epoch
    ):
        with pytest.raises(ValueError):
            reward_epoch_factory.from_voting_epoch(wrong_voting_epoch)
