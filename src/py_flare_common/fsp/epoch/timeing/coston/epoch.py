from py_flare_common.epoch.epoch import RewardEpoch, VotingEpoch
from py_flare_common.epoch.factory import RewardEpochFactory, VotingEpochFactory
from py_flare_common.epoch.timeing.config import coston_chain_config

vef = VotingEpochFactory(
    first_epoch_epoc=coston_chain_config.voting_first_epoch_epoc,
    epoch_duration=coston_chain_config.voting_epoch_duration,
    ftso_reveal_deadline=coston_chain_config.voting_ftso_reveal_deadline,
    reward_first_epoch_epoc=coston_chain_config.reward_first_epoch_epoc,
    reward_epoch_duration=coston_chain_config.reward_epoch_duration,
)

ref = RewardEpochFactory(
    first_epoch_epoc=coston_chain_config.reward_first_epoch_epoc,
    epoch_duration=coston_chain_config.reward_epoch_duration,
    voting_first_epoch_epoc=coston_chain_config.voting_first_epoch_epoc,
    voting_epoch_duration=coston_chain_config.voting_epoch_duration,
    voting_ftso_reveal_deadline=coston_chain_config.voting_ftso_reveal_deadline,
)


def voting_epoch(id: int) -> VotingEpoch:
    return vef.make_epoch(id)


def reward_epoch(id: int) -> RewardEpoch:
    return ref.make_epoch(id)
