from .model import WSIModel

__all__ = [
    "WSIModel",
    "ClusterSpectral",
    "ClusterChineseWhispers",
    "ClusterCorrelation",
]

try:
    from .spectral import ClusterSpectral
except Exception as exc:
    class ClusterSpectral:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Spectral clustering dependencies are not installed or are incompatible in this environment."
            ) from exc

try:
    from .chinese_whispers import ClusterChineseWhispers
except Exception as exc:
    class ClusterChineseWhispers:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Chinese Whispers dependencies are not installed or are incompatible in this environment."
            ) from exc

try:
    from .correlation_clustering import ClusterCorrelation
except Exception as exc:
    class ClusterCorrelation:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Correlation clustering dependencies are not installed or are incompatible in this environment."
            ) from exc
