import pytest

from py_flare_common.fsp.epoch import timing
from py_flare_common.fsp.epoch.timing.config import (
    ChainConfig,
    coston2_chain_config,
    coston_chain_config,
    flare_chain_config,
    songbird_chain_config,
)

CHAINS = [
    ("flare", flare_chain_config),
    ("songbird", songbird_chain_config),
    ("coston", coston_chain_config),
    ("coston2", coston2_chain_config),
]


class TestTimingReExports:
    @pytest.mark.parametrize(("chain", "config"), CHAINS)
    def test_voting_epoch_factory(self, chain: str, config: ChainConfig):
        factory = getattr(timing, f"{chain}_voting_epoch_factory")
        assert factory.first_epoch_epoc == config.voting_first_epoch_epoc
        assert factory.epoch_duration == config.voting_epoch_duration
        assert factory.ftso_reveal_deadline == config.voting_ftso_reveal_deadline
        assert factory.reward_first_epoch_epoc == config.reward_first_epoch_epoc
        assert factory.reward_epoch_duration == config.reward_epoch_duration
        assert factory.initial_reward_epoch == config.initial_reward_epoch

    @pytest.mark.parametrize(("chain", "config"), CHAINS)
    def test_reward_epoch_factory(self, chain: str, config: ChainConfig):
        factory = getattr(timing, f"{chain}_reward_epoch_factory")
        assert factory.first_epoch_epoc == config.reward_first_epoch_epoc
        assert factory.epoch_duration == config.reward_epoch_duration
        assert factory.voting_first_epoch_epoc == config.voting_first_epoch_epoc
        assert factory.voting_epoch_duration == config.voting_epoch_duration
        assert factory.voting_ftso_reveal_deadline == config.voting_ftso_reveal_deadline
        assert factory.initial_reward_epoch == config.initial_reward_epoch

    @pytest.mark.parametrize(("chain", "config"), CHAINS)
    def test_epoch_constructors_use_own_factory(self, chain: str, config: ChainConfig):
        voting_epoch = getattr(timing, f"{chain}_voting_epoch")(0)
        reward_epoch = getattr(timing, f"{chain}_reward_epoch")(0)
        assert voting_epoch.start_s == config.voting_first_epoch_epoc
        assert reward_epoch.start_s == config.reward_first_epoch_epoc

    # NOTE: flare/coston2 and songbird/coston differ by a 45s voting epoch offset
    def test_mainnet_and_testnet_epochs_are_distinct(self):
        assert (
            timing.flare_voting_epoch_factory.first_epoch_epoc
            != timing.coston_voting_epoch_factory.first_epoch_epoc
        )
        assert (
            timing.coston2_voting_epoch_factory.first_epoch_epoc
            != timing.coston_voting_epoch_factory.first_epoch_epoc
        )
