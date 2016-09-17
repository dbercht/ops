def avg(datapoints):
    count = 0
    sum_ = 0
    for value, _ in datapoints:
        if value is not None:
            count += 1
            sum_ += value
    if count:
        return float(sum_) / count
    return 0


def total(datapoints):
    total_ = 0
    for value, _ in datapoints:
        total_ += value or 0
    return total_
