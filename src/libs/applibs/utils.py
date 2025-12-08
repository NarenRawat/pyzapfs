def lerp(a, b, t):
    return a + (b - a) * t


def clip(lower, value, upper):
    return max(lower, min(value, upper))


def hr_size(nbytes):
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024
        i += 1

    size = f"{nbytes:.2f}".rstrip("0.")
    return f"{size} {suffixes[i]}"
