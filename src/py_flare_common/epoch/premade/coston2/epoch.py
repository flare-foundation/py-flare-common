from py_flare_common.epoch.premade.coston2.factory import (
    make_reward_epoch_factory,
    make_voting_epoch_factory,
)


def make_voting_epoch(id):
    return make_voting_epoch_factory().make_epoch(id)


def make_reward_epoch(id):
    return make_reward_epoch_factory().make_epoch(id)
