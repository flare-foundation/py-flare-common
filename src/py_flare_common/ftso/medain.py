from py_flare_common.ftso.types import FtsoVote, FtsoMedian



def calculate_median(votes: list[FtsoVote]) -> FtsoMedian | None:
        if len(votes) == 0:
            return None

        votes.sort(key=lambda x: x.value)
        total_weight = sum([vote.weight for vote in votes])
        median_weight = total_weight // 2 + (total_weight % 2)
        current_weight_sum = 0

        median = None
        quartile_weight = total_weight // 4
        quartile_1 = None
        quartile_3 = None
        high = None
        low = None
        extreme_weight = int(0.05 * total_weight)

        for i, vote in enumerate(votes):
            current_weight_sum += vote.weight

            if low is None and current_weight_sum > extreme_weight:
                low = vote.value

            if quartile_1 is None and current_weight_sum > quartile_weight:
                quartile_1 = vote.value

            if median is None and current_weight_sum >= median_weight:
                if current_weight_sum == median_weight and total_weight % 2 == 0:
                    next_vote = votes[i + 1]
                    median = (vote.value + next_vote.value) // 2
                else:
                    median = vote.value

            if median is not None and quartile_1 is not None:
                break

        current_weight_sum = 0

        for i in range(len(votes) - 1, -1, -1):
            vote = votes[i]
            current_weight_sum += vote.weight
            if current_weight_sum > extreme_weight and high is None:
                high = vote.value
            if current_weight_sum > quartile_weight:
                quartile_3 = vote.value
                break

        assert median is not None
        assert quartile_1 is not None
        assert quartile_3 is not None
        assert high is not None
        assert low is not None

        if low < median * 0.95:
            try:
                low = next(filter(lambda x: x.value >= median * 0.95, votes)).value
            except StopIteration:
                low = median

        if high > median * 1.05:
            try:
                high = next(filter(lambda x: x.value <= median * 1.05, votes[::-1])).value
            except StopIteration:
                high = median

        return FtsoMedian(
            value=median,
            first_quartile=quartile_1,
            third_quartile=quartile_3,
            high=high,
            low=low,
        )