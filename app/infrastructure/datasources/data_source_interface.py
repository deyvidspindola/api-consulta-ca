
from abc import ABC, abstractmethod
import pandas as pd

class DataSourceInterface(ABC):

    @abstractmethod
    async def get_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    async def update_data(self) -> bool:
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        pass
