import pytest

from py_flare_common.epoch.epoch import Epoch, RewardEpoch, VotingEpoch
from py_flare_common.epoch.factory import (
    Factory,
    RewardEpochFactory,
    VotingEpochFactory,
)


class TestEpoch:
    @pytest.fixture
    def factory(self):
        def make(first_epoch_epoc=100, epoch_duration=10):
            factory = Factory(first_epoch_epoc, epoch_duration)
            return factory

        return make

    @pytest.fixture
    def epoch(self, factory):
        def make(id=17, first_epoch_epoc=100, epoch_duration=10):
            epoch = Epoch(id, factory(first_epoch_epoc, epoch_duration))
            return epoch

        return make

    def test_init(self, epoch, factory):
        epoch = epoch()
        assert isinstance(epoch, Epoch)
        assert epoch.id == 17
        assert epoch.factory == factory()

    def test_compare_eq(self, epoch):
        # Different factory instances with same atributes.
        epoch1 = epoch()
        epoch2 = epoch()
        assert epoch1 == epoch2

    @pytest.mark.parametrize("epoch_attr", [(0, 100, 10), (17, 0, 10), (17, 100, 0)])
    def test_compare_neq(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        assert epoch1 != epoch2

    @pytest.mark.parametrize("epoch_attr", [(17, 100, 10), (16, 100, 10)])
    def test_compare_gt(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        assert epoch1 >= epoch2

    @pytest.mark.parametrize("epoch_attr", [(17, 0, 10), (17, 100, 0)])
    def test_compare_gt_err(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        with pytest.raises(TypeError):
            assert epoch1 >= epoch2

    # epoch().start_s = 270, epoch().end_s = 280
    @pytest.mark.parametrize("i", [270, 279])
    def test_contains(self, epoch, i):
        epoch = epoch()
        assert i in epoch

    # epoch().start_s = 270, epoch().end_s = 280
    @pytest.mark.parametrize("i", [269, 280])
    def test_contains_not(self, epoch, i):
        epoch = epoch()
        assert i not in epoch

    def test_next(self, epoch, factory):
        epoch = epoch()
        next_epoch = epoch.next
        assert isinstance(next_epoch, Epoch)
        assert next_epoch.id == 18
        assert next_epoch.factory == factory()

    def test_previous(self, epoch, factory):
        epoch = epoch()
        next_epoch = epoch.previous
        assert isinstance(next_epoch, Epoch)
        assert next_epoch.id == 16
        assert next_epoch.factory == factory()

    def test_start_s(self, epoch):
        epoch = epoch()
        assert epoch.start_s == 270

    def test_end_s(self, epoch):
        epoch = epoch()
        assert epoch.end_s == 280


class TestVotingEpoch:
    @pytest.fixture
    def voting_epoch_factory(self):
        def make(
            first_epoch_epoc=100,
            epoch_duration=10,
            ftso_reveal_deadline=5,
            reward_first_epoch_epoc=200,
            reward_epoch_duration=20,
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
    def voting_epoch(self, voting_epoch_factory):
        def make(
            id=17,
            first_epoch_epoc=100,
            epoch_duration=10,
            ftso_reveal_deadline=5,
            reward_first_epoch_epoc=200,
            reward_epoch_duration=20,
        ):
            epoch = VotingEpoch(
                id,
                voting_epoch_factory(
                    first_epoch_epoc,
                    epoch_duration,
                    ftso_reveal_deadline,
                    reward_first_epoch_epoc,
                    reward_epoch_duration,
                ),
            )
            return epoch

        return make

    def test_init(self, voting_epoch, voting_epoch_factory):
        epoch = voting_epoch()
        assert isinstance(epoch, VotingEpoch)
        assert epoch.id == 17
        assert epoch.factory == voting_epoch_factory()

    def test_to_reward_epoch(self, voting_epoch):
        epoch = voting_epoch()
        reward_epoch = epoch.to_reward_epoch()
        assert isinstance(reward_epoch, RewardEpoch)
        assert reward_epoch.id == 3
        assert reward_epoch.factory == RewardEpochFactory(200, 20, 100, 10, 5)

    def test_reveal_deadline(self, voting_epoch):
        epoch = voting_epoch()
        assert epoch.reveal_deadline() == 275

    def test_compare(self, voting_epoch):
        epoch1 = voting_epoch()
        epoch2 = voting_epoch()
        assert epoch1 == epoch2
        assert hash(epoch1) == hash(epoch2)


class TestRewardEpoch:
    @pytest.fixture
    def reward_epoch_factory(self):
        def make(
            first_epoch_epoc=200,
            epoch_duration=20,
            voting_first_epoch_epoc=100,
            voting_epoch_duration=10,
            voting_ftso_reveal_deadline=5,
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

    @pytest.fixture
    def reward_epoch(self, reward_epoch_factory):
        def make(
            id=17,
            first_epoch_epoc=200,
            epoch_duration=20,
            voting_first_epoch_epoc=100,
            voting_epoch_duration=10,
            voting_ftso_reveal_deadline=5,
        ):
            epoch = RewardEpoch(
                id,
                reward_epoch_factory(
                    first_epoch_epoc,
                    epoch_duration,
                    voting_first_epoch_epoc,
                    voting_epoch_duration,
                    voting_ftso_reveal_deadline,
                ),
            )
            return epoch

        return make

    def test_to_first_voting_epoch(self, reward_epoch):
        epoch = reward_epoch()
        factory = VotingEpochFactory(100, 10, 5, 200, 20)
        id = factory._from_timestamp(540)
        assert epoch.to_first_voting_epoch() == VotingEpoch(id, factory)
