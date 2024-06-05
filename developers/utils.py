import math

def exponential_cdf(x):
    return 1 - 2 ** -x

def log_normal_cdf(x):
    # approximation
    return x / (1 + x)


THRESHOLDS = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
LEVELS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

def calculate_rank(total_commits, total_repos, contributed_days):
    commits_median = 250
    commits_weight = 2

    repos_median = 5
    repos_weight = 3

    contributed_days_median = 100
    contributed_days_weight = 3

    total_weight = (
        commits_weight +
        repos_weight +
        contributed_days_weight
    )

    rank = (
        1 - (
            commits_weight * exponential_cdf(total_commits / commits_median) +
            repos_weight * exponential_cdf(total_repos / repos_median) +
            contributed_days_weight * exponential_cdf(contributed_days / contributed_days_median)
        ) / total_weight
    )

    level = LEVELS[THRESHOLDS.index(next(t for t in THRESHOLDS if rank * 100 <= t))]

    return (level, rank * 100)
