import unittest
from edifact.models.message import MessageHeader, MessageTrailer, Message


class MessageHeaderTest(unittest.TestCase):
    """
    Test the generating of a message header
    """

    def test_message_header_to_edifact(self):
        msg_hdr = MessageHeader(sequence_number="00001").to_edifact()
        self.assertEqual(msg_hdr, "UNH+00001+FHSREG:0:1:FH:FHS001'")


class MessageTrailerTest(unittest.TestCase):
    """
    Test the generating of a message trailer
    """

    def test_message_trailer_to_edifact(self):
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001").to_edifact()
        self.assertEqual(msg_trl, "UNT+5+00001'")


class MessageTest(unittest.TestCase):
    """
    Test the generating of a message
    """

    def test_message_to_edifact(self):
        msg_hdr = MessageHeader(sequence_number="00001")
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number="00001")
        msg = Message(header=msg_hdr, trailer=msg_trl).to_edifact()
        self.assertEqual(msg, "UNH+00001+FHSREG:0:1:FH:FHS001'UNT+5+00001'")


if __name__ == '__main__':
    unittest.main()