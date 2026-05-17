__all__ = ["ContextualEmbedder", "DMWrapperClass", "WICModel"]

from .contextual_embedder import ContextualEmbedder
from .model import WICModel

try:
    from .DM import DMWrapperClass
except Exception as exc:
    class DMWrapperClass:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "DeepMistake dependencies are not installed or are incompatible in this environment."
            ) from exc
