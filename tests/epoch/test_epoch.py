import pytest

from py_flare_common.fsp.epoch.epoch import Epoch, RewardEpoch, VotingEpoch
from py_flare_common.fsp.epoch.factory import (
    RewardEpochFactory,
    VotingEpochFactory,
)


class TestEpoch:
    @pytest.fixture
    def epoch(self, factory):
        def make(id=3361, first_epoch_epoc=1658430000, epoch_duration=90):
            epoch = Epoch(id, factory(first_epoch_epoc, epoch_duration))
            return epoch

        return make

    def test_init(self, epoch, factory):
        epoch = epoch()
        assert isinstance(epoch, Epoch)
        assert epoch.id == 3361
        assert epoch.factory == factory()

    def test_compare_eq(self, epoch):
        # Different factory instances with same atributes.
        epoch1 = epoch()
        epoch2 = epoch()
        assert id(epoch1) != id(epoch2)
        assert id(epoch1.factory) != id(epoch2.factory)
        assert epoch1 == epoch2
        assert hash(epoch1) == hash(epoch2)

    @pytest.mark.parametrize(
        "epoch_attr", [(0, 1658430000, 90), (3361, 0, 10), (3361, 1658430000, 0)]
    )
    def test_compare_neq(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        assert epoch1 != epoch2

    @pytest.mark.parametrize(
        "epoch_attr", [(3361, 1658430000, 90), (3360, 1658430000, 90)]
    )
    def test_compare_gt(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        assert epoch1 >= epoch2

    @pytest.mark.parametrize("epoch_attr", [(3361, 0, 90), (3361, 1658430000, 0)])
    def test_compare_gt_err(self, epoch, epoch_attr):
        epoch1 = epoch()
        epoch2 = epoch(*epoch_attr)
        with pytest.raises(TypeError):
            assert epoch1 >= epoch2

    def test_start_s(self, epoch):
        epoch = epoch()
        # 1658430000 + 90*3361 = 1658732490
        assert epoch.start_s == 1658732490

    def test_end_s(self, epoch):
        epoch = epoch()
        # 1658430000 + 90*3362 = 1658732580
        assert epoch.end_s == 1658732580

    # epoch().start_s = 1658732490, epoch().end_s = 1658732490
    @pytest.mark.parametrize("i", [1658732490, 1658732579])
    def test_contains(self, epoch, i):
        epoch = epoch()
        assert i in epoch

    # epoch().start_s = 1658732490, epoch().end_s = 1658732580
    @pytest.mark.parametrize("i", [1658732489, 1658732580])
    def test_contains_not(self, epoch, i):
        epoch = epoch()
        assert i not in epoch

    def test_next(self, epoch, factory):
        epoch = epoch()
        next_epoch = epoch.next
        assert isinstance(next_epoch, Epoch)
        assert next_epoch.id == 3362
        assert next_epoch.factory == factory()

    def test_previous(self, epoch, factory):
        epoch = epoch()
        next_epoch = epoch.previous
        assert isinstance(next_epoch, Epoch)
        assert next_epoch.id == 3360
        assert next_epoch.factory == factory()


class TestVotingEpoch:
    @pytest.fixture
    def voting_epoch(self, voting_epoch_factory):
        def make(
            id=3361,
            first_epoch_epoc=1658430000,
            epoch_duration=90,
            ftso_reveal_deadline=45,
            reward_first_epoch_epoc=1658430000,
            reward_epoch_duration=302400,
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
        assert epoch.id == 3361
        assert epoch.factory == voting_epoch_factory()

    def test_to_reward_epoch(self, voting_epoch):
        epoch = voting_epoch()
        reward_epoch = epoch.to_reward_epoch()
        assert isinstance(reward_epoch, RewardEpoch)
        # ((1658430000 + 3361*90) - 1658430000) // 302400 = 1
        assert reward_epoch.id == 1
        assert reward_epoch.factory == RewardEpochFactory(
            1658430000, 302400, 1658430000, 90, 45, 223
        )

    def test_reveal_deadline(self, voting_epoch):
        epoch = voting_epoch()
        # (1658430000 + 3361*90) + 45 = 1658732535
        assert epoch.reveal_deadline() == 1658732535

    def test_compare(self, voting_epoch):
        epoch1 = voting_epoch()
        epoch2 = voting_epoch()
        assert epoch1 == epoch2
        assert id(epoch1) != id(epoch2)
        assert id(epoch1.factory) != id(epoch2.factory)
        assert hash(epoch1) == hash(epoch2)


class TestRewardEpoch:
    @pytest.fixture
    def reward_epoch(self, reward_epoch_factory):
        def make(
            id=2,
            first_epoch_epoc=1658430000,
            epoch_duration=302400,
            voting_first_epoch_epoc=1658430000,
            voting_epoch_duration=90,
            voting_ftso_reveal_deadline=45,
            initial_reward_epoch=223,
        ):
            epoch = RewardEpoch(
                id,
                reward_epoch_factory(
                    first_epoch_epoc,
                    epoch_duration,
                    voting_first_epoch_epoc,
                    voting_epoch_duration,
                    voting_ftso_reveal_deadline,
                    initial_reward_epoch,
                ),
            )
            return epoch

        return make

    def test_to_first_voting_epoch(self, reward_epoch):
        epoch = reward_epoch()
        voting_epoch_factory = VotingEpochFactory(
            1658430000, 90, 45, 1658430000, 302400, 223
        )
        # ((1658430000 + 2*302400) - 1658430000) // 90 = 6720
        assert epoch.to_first_voting_epoch() == VotingEpoch(6720, voting_epoch_factory)

    def test_compare(self, reward_epoch):
        epoch1 = reward_epoch()
        epoch2 = reward_epoch()
        assert epoch1 == epoch2
        assert id(epoch1) != id(epoch2)
        assert id(epoch1.factory) != id(epoch2.factory)
        assert hash(epoch1) == hash(epoch2)
