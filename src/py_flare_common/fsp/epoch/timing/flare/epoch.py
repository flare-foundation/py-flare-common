from ...epoch import RewardEpoch, VotingEpoch
from ...factory import RewardEpochFactory, VotingEpochFactory
from ..config import flare_chain_config

vef = VotingEpochFactory(
    first_epoch_epoc=flare_chain_config.voting_first_epoch_epoc,
    epoch_duration=flare_chain_config.voting_epoch_duration,
    ftso_reveal_deadline=flare_chain_config.voting_ftso_reveal_deadline,
    reward_first_epoch_epoc=flare_chain_config.reward_first_epoch_epoc,
    reward_epoch_duration=flare_chain_config.reward_epoch_duration,
)

ref = RewardEpochFactory(
    first_epoch_epoc=flare_chain_config.reward_first_epoch_epoc,
    epoch_duration=flare_chain_config.reward_epoch_duration,
    voting_first_epoch_epoc=flare_chain_config.voting_first_epoch_epoc,
    voting_epoch_duration=flare_chain_config.voting_epoch_duration,
    voting_ftso_reveal_deadline=flare_chain_config.voting_ftso_reveal_deadline,
)


def voting_epoch(id: int) -> VotingEpoch:
    return vef.make_epoch(id)


def reward_epoch(id: int) -> RewardEpoch:
    return ref.make_epoch(id)