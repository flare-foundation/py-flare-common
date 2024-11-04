from py_flare_common.epoch.factory import RewardEpochFactory, VotingEpochFactory
from py_flare_common.epoch.premade.config import coston_chain_config


def make_voting_epoch_factory():
    return VotingEpochFactory(
        first_epoch_epoc=coston_chain_config.voting_first_epoch_epoc,
        epoch_duration=coston_chain_config.voting_epoch_duration,
        ftso_reveal_deadline=coston_chain_config.voting_ftso_reveal_deadline,
        reward_first_epoch_epoc=coston_chain_config.reward_first_epoch_epoc,
        reward_epoch_duration=coston_chain_config.reward_epoch_duration,
    )


def make_reward_epoch_factory():
    return RewardEpochFactory(
        first_epoch_epoc=coston_chain_config.reward_first_epoch_epoc,
        epoch_duration=coston_chain_config.reward_epoch_duration,
        voting_first_epoch_epoc=coston_chain_config.voting_first_epoch_epoc,
        voting_epoch_duration=coston_chain_config.voting_epoch_duration,
        voting_ftso_reveal_deadline=coston_chain_config.voting_ftso_reveal_deadline,
    )
