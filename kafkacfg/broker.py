from dataclasses import dataclass


@dataclass
class BrokerAttributes:
    num_cpus: int
    num_disks: int
