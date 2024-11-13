import time

import pytest

from py_flare_common.fsp.epoch.epoch import Epoch, RewardEpoch, VotingEpoch
from py_flare_common.fsp.epoch.factory import (
    Factory,
    RewardEpochFactory,
    VotingEpochFactory,
)


class TestFactory:
    def test_init(self, factory):
        factory = factory()
        assert isinstance(factory, Factory)
        assert factory.first_epoch_epoc == 1658430000
        assert factory.epoch_duration == 90

    def test_compare_eq(self, factory):
        factory1 = factory()
        factory2 = factory()
        assert id(factory1) != id(factory2)
        assert factory2 == factory1

    @pytest.mark.parametrize("factory_attr", [(1658430000, 0), (0, 90)])
    def test_compare_neq(self, factory, factory_attr):
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
        assert factory().duration() == 90

    def test__from_timestamp(self, factory):
        # (2000000000 - 1658430000) // 90 = 3795222
        assert factory()._from_timestamp(2000000000) == 3795222

    def test_from_timestamp(self, factory):
        factory = factory()
        epoch = factory.from_timestamp(2000000000)
        assert isinstance(epoch, Epoch)
        assert epoch.id == 3795222
        assert epoch.factory == factory

    def test_now(self, factory):
        factory = factory()
        epoch = factory.now()
        assert isinstance(epoch, Epoch)
        assert epoch.id == (int(time.time()) - 1658430000) // 90
        assert epoch.factory == factory

    def test_now_id(self, factory):
        assert factory().now_id() == (int(time.time()) - 1658430000) // 90


class TestVotingEpochFactory:
    def test_init(self, voting_epoch_factory):
        voting_epoch_factory = voting_epoch_factory()
        assert isinstance(voting_epoch_factory, VotingEpochFactory)
        assert voting_epoch_factory.first_epoch_epoc == 1658430000
        assert voting_epoch_factory.epoch_duration == 90
        assert voting_epoch_factory.ftso_reveal_deadline == 45
        assert voting_epoch_factory.reward_first_epoch_epoc == 1658430000
        assert voting_epoch_factory.reward_epoch_duration == 302400

    def test_make_epoch(self, voting_epoch_factory):
        voting_epoch_factory = voting_epoch_factory()
        epoch = voting_epoch_factory.make_epoch(27)
        assert isinstance(epoch, VotingEpoch)
        assert epoch.id == 27
        assert epoch.factory == voting_epoch_factory

    def test_make_reward_epoch(self, voting_epoch_factory):
        epoch = voting_epoch_factory().make_reward_epoch(1658430000 + 302400 * 13)
        assert isinstance(epoch, RewardEpoch)
        assert epoch.id == 13
        assert epoch.factory == RewardEpochFactory(
            1658430000, 302400, 1658430000, 90, 45
        )


class TestRewardEpochFactory:
    def test_init(self, reward_epoch_factory):
        reward_epoch_factory = reward_epoch_factory()
        assert isinstance(reward_epoch_factory, RewardEpochFactory)
        assert reward_epoch_factory.first_epoch_epoc == 1658430000
        assert reward_epoch_factory.epoch_duration == 302400
        assert reward_epoch_factory.voting_first_epoch_epoc == 1658430000
        assert reward_epoch_factory.voting_epoch_duration == 90
        assert reward_epoch_factory.voting_ftso_reveal_deadline == 45

    def test_make_epoch(self, reward_epoch_factory):
        reward_epoch_factory = reward_epoch_factory()
        epoch = reward_epoch_factory.make_epoch(27)
        assert isinstance(epoch, RewardEpoch)
        assert epoch.id == 27
        assert epoch.factory == reward_epoch_factory

    def test_make_voting_epoch(self, reward_epoch_factory):
        epoch = reward_epoch_factory().make_voting_epoch(1658430000 + 90 * 13)
        assert isinstance(epoch, VotingEpoch)
        assert epoch.id == 13
        assert epoch.factory == VotingEpochFactory(
            1658430000, 90, 45, 1658430000, 302400
        )

    def test_from_voting_epoch(self, reward_epoch_factory, voting_epoch_factory):
        reward_epoch_factory = reward_epoch_factory()
        voting_epoch = voting_epoch_factory().make_epoch(3361)
        epoch = reward_epoch_factory.from_voting_epoch(voting_epoch)
        assert isinstance(epoch, RewardEpoch)
        # ((1658430000 + 3361*90) - 1658430000) // 302400 = 1
        assert epoch.id == 1
        assert epoch.factory == reward_epoch_factory

    @pytest.mark.parametrize(
        "factory_attr",
        [
            (0, 90, 45, 1658430000, 302400),
            (1658430000, 0, 45, 1658430000, 302400),
            (1658430000, 90, 0, 1658430000, 302400),
            (1658430000, 90, 45, 0, 302400),
            (1658430000, 90, 45, 1658430000, 0),
        ],
    )
    def test_from_voting_epoch_wrong_voting_factory(
        self, reward_epoch_factory, voting_epoch_factory, factory_attr
    ):
        voting_epoch = voting_epoch_factory(*factory_attr).make_epoch(18)
        with pytest.raises(ValueError):
            reward_epoch_factory().from_voting_epoch(voting_epoch)
