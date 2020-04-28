from sequence.dynamo_sequence import DynamoSequenceGenerator
from sequence.sequence_factory import get_sequence_generator


class TransactionIdGenerator:
    """A component that provides sequential transaction id"""

    def __init__(self):
        self.table_name = 'transaction_id_counter'
        self.key = 'transaction_id'

    async def generate_transaction_id(self) -> int:
        transaction_generator = get_sequence_generator(self.table_name)
        return await transaction_generator.next(self.key)