from attrs import frozen


@frozen
class FtsoVote:
    value: int
    weight: int


@frozen
class FtsoMedian:
    value: int
    first_quartile: int
    third_quartile: int
    sorted_votes: list[FtsoVote]
