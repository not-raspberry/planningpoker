"""
Storage backends.

Concrete implementations are to be injected into each view.
"""
from planningpoker.persistence.base import BasePersistence
from planningpoker.persistence.memory import ProcessMemoryPersistence
