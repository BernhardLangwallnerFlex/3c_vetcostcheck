from abc import ABC, abstractmethod

class InvoiceProcessor(ABC):
    @abstractmethod
    def extract(self, prompt: str, file_path: str) -> dict:
        pass