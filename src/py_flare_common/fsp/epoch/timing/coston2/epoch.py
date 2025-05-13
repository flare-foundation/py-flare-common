from ...epoch import RewardEpoch, VotingEpoch
from ...factory import RewardEpochFactory, VotingEpochFactory
from ..config import coston2_chain_config

__all__ = [
    "voting_epoch",
    "reward_epoch",
    "voting_epoch_factory",
    "reward_epoch_factory",
]

voting_epoch_factory = VotingEpochFactory(
    first_epoch_epoc=coston2_chain_config.voting_first_epoch_epoc,
    epoch_duration=coston2_chain_config.voting_epoch_duration,
    ftso_reveal_deadline=coston2_chain_config.voting_ftso_reveal_deadline,
    reward_first_epoch_epoc=coston2_chain_config.reward_first_epoch_epoc,
    reward_epoch_duration=coston2_chain_config.reward_epoch_duration,
    initial_reward_epoch=coston2_chain_config.initial_reward_epoch,
)

reward_epoch_factory = RewardEpochFactory(
    first_epoch_epoc=coston2_chain_config.reward_first_epoch_epoc,
    epoch_duration=coston2_chain_config.reward_epoch_duration,
    voting_first_epoch_epoc=coston2_chain_config.voting_first_epoch_epoc,
    voting_epoch_duration=coston2_chain_config.voting_epoch_duration,
    voting_ftso_reveal_deadline=coston2_chain_config.voting_ftso_reveal_deadline,
    initial_reward_epoch=coston2_chain_config.initial_reward_epoch,
)


def voting_epoch(id: int) -> VotingEpoch:
    return voting_epoch_factory.make_epoch(id)


def reward_epoch(id: int) -> RewardEpoch:
    return reward_epoch_factory.make_epoch(id)
