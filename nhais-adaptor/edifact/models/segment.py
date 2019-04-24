class Segment(object):
    """
    A segment is the basic building block of an edifact message.
    It represent each line in the edifact message that will be generated.
    example: NAD+GP+4826940,281:900'
    """

    TERMINATOR = "'"

    def __init__(self, key, value):
        """
        A segment is a key value pair with a special terminator
        :param key: the key of the segment for example NAD, DTM ...
        :param value: the value of the segment
        """
        self.key = key
        self.value = value.upper()

    def to_edifact(self):
        """
        generates the edifact message of the segment
        :return: a string of the formatted edifact message using the key and value
        """
        edifact_segment = f"{self.key}+{self.value}{Segment.TERMINATOR}"
        return edifact_segment
