"""This module defines the asynchronous express workflow."""
import asyncio
from typing import Tuple, Optional

import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from exceptions import MaxRetriesExceeded
from tornado import httpclient
from utilities import timing

from mhs_common import workflow
from mhs_common.errors.soap_handler import handle_soap_error
from mhs_common.routing import routing_reliability
from mhs_common.state import persistence_adaptor
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger('ASYNC_EXPRESS_WORKFLOW')


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                 transmission: transmission_adaptor.TransmissionAdaptor = None,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None,
                 inbound_queue_max_retries: int = None,
                 inbound_queue_retry_delay: int = None,
                 persistence_store_max_retries: int = None,
                 routing: routing_reliability.RoutingAndReliability = None):
        super(AsynchronousExpressWorkflow, self).__init__(party_key, persistence_store, transmission,
                                                          queue_adaptor, inbound_queue_max_retries,
                                                          inbound_queue_retry_delay, persistence_store_max_retries,
                                                          routing)

        self.workflow_specific_interaction_details = dict(duplicate_elimination=False,
                                                          ack_requested=False,
                                                          ack_soap_actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH",
                                                          sync_reply=True)

    @timing.time_function
    async def handle_outbound_message(self,
                                      message_id: str,
                                      correlation_id: str,
                                      interaction_details: dict,
                                      payload: str,
                                      wdo: Optional[wd.WorkDescription]) -> Tuple[int, str]:

        logger.info('0001', 'Entered async express workflow to handle outbound message')
        if not wdo:
            wdo = wd.create_new_work_description(self.persistence_store,
                                                 message_id,
                                                 workflow.ASYNC_EXPRESS,
                                                 wd.MessageStatus.OUTBOUND_MESSAGE_RECEIVED
                                                 )
            await wdo.publish()

        try:
            url, to_party_key, cpa_id = await self._lookup_endpoint_details(interaction_details)
        except Exception:
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error obtaining outbound URL'

        error, http_headers, message = await self._serialize_outbound_message(message_id, correlation_id,
                                                                              interaction_details,
                                                                              payload, wdo, to_party_key, cpa_id)
        if error:
            return error

        logger.info('0004', 'About to make outbound request')
        start_time = timing.get_time()
        try:
            response = await self.transmission.make_request(url, http_headers, message)
            end_time = timing.get_time()
        except httpclient.HTTPClientError as e:
            logger.warning('0005', 'Received HTTP errors from Spine. {HTTPStatus} {Exception}',
                           {'HTTPStatus': e.code, 'Exception': e})
            self._record_outbound_audit_log(workflow.ASYNC_EXPRESS,
                                            timing.get_time(),
                                            start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)

            if e.response:
                return handle_soap_error(e.response.code, e.response.headers, e.response.body)

            return 500, f'Error(s) received from Spine: {e}'
        except Exception as e:
            logger.warning('0006', 'Error encountered whilst making outbound request. {Exception}', {'Exception': e})
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
            return 500, 'Error making outbound request'

        if response.code == 202:
            self._record_outbound_audit_log(workflow.ASYNC_EXPRESS,
                                            end_time,
                                            start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_ACKD)
            await wd.update_status_with_retries(wdo, wdo.set_outbound_status, wd.MessageStatus.OUTBOUND_MESSAGE_ACKD,
                                                self.store_retries)
            return 202, ''
        else:
            logger.warning('0008', "Didn't get expected HTTP status 202 from Spine, got {HTTPStatus} instead",
                           {'HTTPStatus': response.code})
            self._record_outbound_audit_log(workflow.ASYNC_EXPRESS,
                                            end_time,
                                            start_time,
                                            wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            await wdo.set_outbound_status(wd.MessageStatus.OUTBOUND_MESSAGE_NACKD)
            return 500, "Didn't get expected success response from Spine"

    @timing.time_function
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('0009', 'Entered async express workflow to handle inbound message')
        await wd.update_status_with_retries(work_description,
                                            work_description.set_inbound_status,
                                            wd.MessageStatus.INBOUND_RESPONSE_RECEIVED,
                                            self.store_retries)

        retries_remaining = self.inbound_queue_max_retries
        while True:
            try:
                await self.queue_adaptor.send_async(payload, properties={'message-id': message_id,
                                                                         'correlation-id': correlation_id})
                break
            except Exception as e:
                logger.warning('0010', 'Failed to put message onto inbound queue due to {Exception}', {'Exception': e})
                retries_remaining -= 1
                if retries_remaining <= 0:
                    logger.error("0012",
                                 "Exceeded the maximum number of retries, {max_retries} retries, when putting "
                                 "message onto inbound queue", {"max_retries": self.inbound_queue_max_retries})
                    await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_FAILED)
                    raise MaxRetriesExceeded('The max number of retries to put a message onto the inbound queue has '
                                             'been exceeded') from e

                logger.info("0013", "Waiting for {retry_delay} seconds before retrying putting message onto inbound "
                                    "queue", {"retry_delay": self.inbound_queue_retry_delay})
                await asyncio.sleep(self.inbound_queue_retry_delay)

        logger.info('0011', 'Placed message onto inbound queue successfully')
        await work_description.set_inbound_status(wd.MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)
