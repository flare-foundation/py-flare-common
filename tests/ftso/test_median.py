import pytest

from py_flare_common.ftso.median import calculate_median, FtsoMedian, FtsoVote



class TestCalculateMedian:
    def test_empty_list(self):
        assert calculate_median([]) is None

    @pytest.mark.parametrize(
        "votes",
        [
            [FtsoVote(10, 20)],
            [FtsoVote(10, 10)],
            [FtsoVote(10, 1)],
        ],
    )
    def test_one_entry(self, votes):
        median = calculate_median(votes)
        assert isinstance(median, FtsoMedian)
        assert median.value == 10
        assert median.first_quartile == 10
        assert median.third_quartile == 10
        assert median.sorted_votes == votes

    @pytest.mark.parametrize(
        "votes",
        [
            [
                FtsoVote(1, 20),
                FtsoVote(2, 20),
                FtsoVote(3, 20),
                FtsoVote(5, 20),
                FtsoVote(7, 20),
                FtsoVote(8, 20),
            ],
            [
                FtsoVote(1, 1),
                FtsoVote(2, 1),
                FtsoVote(3, 1),
                FtsoVote(5, 1),
                FtsoVote(7, 1),
                FtsoVote(8, 1),
            ],
            [
                FtsoVote(1, 12323),
                FtsoVote(2, 12323),
                FtsoVote(3, 12323),
                FtsoVote(5, 12323),
                FtsoVote(7, 12323),
                FtsoVote(8, 12323),
            ],
        ],
    )
    def test_same_weights(self, votes):
        median = calculate_median(votes)
        assert isinstance(median, FtsoMedian)
        assert median.value == 4
        assert median.first_quartile == 2
        assert median.third_quartile == 7

    @pytest.mark.parametrize(
        "votes",
        [
            [FtsoVote(7, 20), FtsoVote(9, 20)],
            [FtsoVote(1, 5), FtsoVote(5, 7), FtsoVote(11, 8), FtsoVote(12, 4)],
            [FtsoVote(11, 8), FtsoVote(5, 7), FtsoVote(12, 4), FtsoVote(1, 5)],
            [FtsoVote(2, 8), FtsoVote(8, 7), FtsoVote(9, 4), FtsoVote(10, 11)],
            [FtsoVote(10, 11), FtsoVote(2, 8), FtsoVote(8, 7), FtsoVote(9, 4)],
            [
                FtsoVote(1, 11),
                FtsoVote(7, 8),
                FtsoVote(9, 7),
                FtsoVote(9, 4),
                FtsoVote(12, 8),
            ],
        ],
    )
    def test_inner_median_if_block(self, votes):
        median = calculate_median(votes)
        assert isinstance(median, FtsoMedian)
        assert median.value == 8

    @pytest.mark.parametrize(
        "votes",
        [
            [
                FtsoVote(1, 6),
                FtsoVote(4, 4),
                FtsoVote(11, 3),
                FtsoVote(12, 4),
                FtsoVote(12, 2),
            ],
            [
                FtsoVote(11, 3),
                FtsoVote(12, 2),
                FtsoVote(1, 6),
                FtsoVote(4, 4),
                FtsoVote(12, 4),
            ],
            [FtsoVote(1, 6), FtsoVote(4, 4), FtsoVote(12, 4), FtsoVote(13, 1)],
        ],
    )
    def test_inner_median__block(self, votes):
        median = calculate_median(votes)
        assert isinstance(median, FtsoMedian)
        assert median.value == 4

    @pytest.mark.parametrize(
        "votes",
        [
            [
                FtsoVote(1, 2),
                FtsoVote(4, 7),
                FtsoVote(5, 1),
                FtsoVote(8, 4),
                FtsoVote(9, 2),
                FtsoVote(11, 6),
            ],
            [
                FtsoVote(1, 2),
                FtsoVote(5, 1),
                FtsoVote(8, 4),
                FtsoVote(9, 2),
                FtsoVote(11, 6),
                FtsoVote(4, 7),
            ],
            [
                FtsoVote(8, 4),
                FtsoVote(1, 2),
                FtsoVote(5, 1),
                FtsoVote(9, 2),
                FtsoVote(11, 6),
                FtsoVote(4, 7),
            ],
            [
                FtsoVote(8, 4),
                FtsoVote(1, 2),
                FtsoVote(11, 6),
                FtsoVote(5, 1),
                FtsoVote(9, 2),
                FtsoVote(4, 7),
            ],
            [
                FtsoVote(8, 4),
                FtsoVote(11, 6),
                FtsoVote(5, 1),
                FtsoVote(9, 2),
                FtsoVote(4, 7),
                FtsoVote(1, 2),
            ],
            [
                FtsoVote(11, 6),
                FtsoVote(5, 1),
                FtsoVote(8, 4),
                FtsoVote(9, 2),
                FtsoVote(4, 7),
                FtsoVote(1, 2),
            ],
        ],
    )
    def test_random_order(self, votes):
        median = calculate_median(votes)
        assert isinstance(median, FtsoMedian)
        assert median.value == 8
        assert median.first_quartile == 4
        assert median.third_quartile == 11
        assert median.sorted_votes == [
            FtsoVote(1, 2),
            FtsoVote(4, 7),
            FtsoVote(5, 1),
            FtsoVote(8, 4),
            FtsoVote(9, 2),
            FtsoVote(11, 6),
        ]
