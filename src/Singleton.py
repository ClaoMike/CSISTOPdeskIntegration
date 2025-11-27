from abc import ABC, abstractmethod

class Singleton(ABC):
    _instances = {}  # one instance per subclass

    def __new__(cls, *args, **kwargs):
        if cls is Singleton:
            raise TypeError("Singleton is abstract; subclass it instead.")

        # One instance per subclass
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance._initialized = False
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        # Only run initialization once per instance
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._init_singleton(*args, **kwargs)

    @abstractmethod
    def _init_singleton(self, *args, **kwargs):
        """Subclasses implement their one-time initialization here."""
        pass
