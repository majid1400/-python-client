from contextlib import ContextDecorator
from dataclasses import dataclass


@dataclass
class ApmTransaction(ContextDecorator):
    apm_client: object
    transaction_type: str = "script"
    name: str = __name__
    result: str = "success"

    def __enter__(self):
        """Start a new Apm Transaction as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager Apm Transaction"""
        self.stop()

    def start(self) -> None:
        self.apm_client.begin_transaction(transaction_type=self.transaction_type)

    def stop(self) -> None:
        self.apm_client.end_transaction(name=self.name, result=self.result)
