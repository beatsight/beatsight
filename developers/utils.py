import math

def exponential_cdf(x):
    return 1 - 2 ** -x

def log_normal_cdf(x):
    # approximation
    return x / (1 + x)


THRESHOLDS = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
LEVELS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]

def calculate_rank(total_commits, total_repos, active_days_ratio, total_modifications):
    commits_median = 250
    commits_weight = 2

    repos_median = 5
    repos_weight = 3

    active_days_ratio_median = 0.3
    active_days_ratio_weight = 3

    modifications_median = 10000
    modifications_weight = 2

    total_weight = (
        commits_weight +
        repos_weight +
        active_days_ratio_weight +
        modifications_weight
    )

    rank = (
        1 - (
            commits_weight * exponential_cdf(total_commits / commits_median) +
            repos_weight * exponential_cdf(total_repos / repos_median) +
            active_days_ratio_weight * exponential_cdf(active_days_ratio / active_days_ratio_median) +
            modifications_weight * exponential_cdf(total_modifications / modifications_median)
        ) / total_weight
    )

    level = LEVELS[THRESHOLDS.index(next(t for t in THRESHOLDS if rank * 100 <= t))]

    return (level, rank * 100)
