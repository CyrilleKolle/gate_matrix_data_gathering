import dataclasses


@dataclasses.dataclass
class Acceleration:
    timestamp: int
    timestamp_local: str
    ax: float
    ay: float
    az: float
    fall_state: str

    def as_csv_field(self):
        return [
            self.timestamp,
            self.timestamp_local,
            self.ax,
            self.ay,
            self.az,
            self.fall_state,
        ]
