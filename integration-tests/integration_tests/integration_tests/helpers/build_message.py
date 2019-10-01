import datetime

from utilities import message_utilities
from integration_tests.helpers import message_builder
from integration_tests.helpers.asid_provider import get_asid

TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

UUID = 'uuid'
TIMESTAMP = 'timestamp'
ASID = 'asid'
PATIENT_NHS_NUMBER = 'patient_nhs_number'
TO_PARTY_ID = 'to_party_id'
FILE_UPLOAD = 'file_upload'
DISSENT_OVERRIDE = 'dissentOverride'
USE_DATE_FILTER = 'useDateFilter'
DOCUMENT_TYPE = 'documentType'
TO_ASID = 'to_asid'


def build_message(template, patient_nhs_number, message_id: str = None):
    """Build an upload message

    :param message_id: message id
    :param template: The Name of the template to be used.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :return: A tuple of the message and the message id (UUID) used in it.
    """
    current_utc_time = datetime.datetime.utcnow()
    timestamp = current_utc_time.strftime(TIMESTAMP_FORMAT)
    to_party_id = 'YES-0000806'
    file_upload = 'test file will go here'
    dissent_override = '0'
    use_date_filter = False
    document_type = '196971000000103'
    message_id = message_id if message_id is not None else message_utilities.MessageUtilities.get_uuid()

    message = message_builder.MustacheMessageBuilder(template).build_message({
        UUID: message_id,
        TIMESTAMP: timestamp,
        ASID: get_asid(),
        TO_ASID: '928942012545',
        PATIENT_NHS_NUMBER: patient_nhs_number,
        TO_PARTY_ID: to_party_id,
        FILE_UPLOAD: file_upload,
        DISSENT_OVERRIDE: dissent_override,
        USE_DATE_FILTER: use_date_filter,
        DOCUMENT_TYPE: document_type
    })

    return message, message_id