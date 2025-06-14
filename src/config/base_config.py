from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class BaseConfig:
    """Base configuration class for all configs."""
    type: str = field(init=False)
    
    def __post_init__(self):
        """Set the type based on the class name."""
        self.type = self.__class__.__name__.replace('Config', '').lower()