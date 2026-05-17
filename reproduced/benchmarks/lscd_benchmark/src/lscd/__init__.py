from .apd import APD
from .cos import Cos
from .model import BinaryThresholdModel, GradedLSCDModel
from .permutation import Permutation

__all__ = [
    "APD",
    "ClusterJSD",
    "Cos",
    "GradedLSCDModel",
    "BinaryThresholdModel",
    "Permutation"
]

try:
    from .cluster_jsd import ClusterJSD
except Exception as exc:
    class ClusterJSD:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ClusterJSD dependencies are not installed or are incompatible in this environment."
            ) from exc
