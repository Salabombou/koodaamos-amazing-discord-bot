class timedelta:
    @staticmethod
    def to_seconds(delta_time : str) -> float:
        h, m, s = delta_time.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)