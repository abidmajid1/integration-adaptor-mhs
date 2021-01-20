#!/bin/bash

source ../../export-env-vars.sh

set -ex

UUID=`uuidgen`

curl -i --request POST \
  --url http://localhost:80/ \
  --header 'content-type: application/json' \
  --header 'interaction-id: QUPC_IN160101UK05' \
  --header 'wait-for-response: true' \
  --data '{"payload": "<QUPC_IN160101UK05 xmlns=\"urn:hl7-org:v3\">\r\n            <id root=\"'$UUID'\" />\r\n            <creationTime value=\"20190927152035\"/>\r\n            <versionCode code=\"3NPfIT7.2.00\" />\r\n            <interactionId root=\"2.16.840.1.113883.2.1.3.2.4.12\" extension=\"QUPC_IN160101UK05\" />\r\n            <processingCode code=\"P\" />\r\n            <processingModeCode code=\"T\" />\r\n            <acceptAckCode code=\"NE\" />\r\n            <communicationFunctionRcv typeCode=\"RCV\">\r\n                <device classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n                    <id extension=\"X26-9199246\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n                </device>\r\n            </communicationFunctionRcv>\r\n            <communicationFunctionSnd typeCode=\"SND\">\r\n                <device classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n                    <id extension=\"918999198982\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n                </device>\r\n            </communicationFunctionSnd>\r\n            <ControlActEvent classCode=\"CACT\" moodCode=\"EVN\">\r\n                <author1 typeCode=\"AUT\">\r\n                    <AgentSystemSDS classCode=\"AGNT\">\r\n                        <agentSystemSDS classCode=\"DEV\" determinerCode=\"INSTANCE\">\r\n                            <id extension=\"918999198982\" root=\"1.2.826.0.1285.0.2.0.107\" />\r\n                        </agentSystemSDS>\r\n                    </AgentSystemSDS>\r\n                </author1>\r\n                <query>\r\n                    <dissentOverride>\r\n                        <semanticsText>DissentOverride</semanticsText>\r\n                        <value code=\"0\" codeSystem=\"2.16.840.1.113883.2.1.3.2.4.17.60\" displayName=\"Demonstration\">\r\n                            <originalText>Demonstration</originalText>\r\n                        </value>\r\n                    </dissentOverride>\r\n                    <filterParameters>\r\n                        <date>\r\n                            <semanticsText>Date</semanticsText>\r\n                            <value>\r\n                                <low value=\"20100908161126\"/>\r\n                                <high value=\"20190927152035\"/>\r\n                            </value>\r\n                        </date>\r\n                    </filterParameters>\r\n                    <nHSNumber>\r\n                        <semanticsText>NHSNumber</semanticsText>\r\n                        <value root=\"2.16.840.1.113883.2.1.4.1\" extension=\"9689177923\" />\r\n                    </nHSNumber>\r\n                </query>\r\n            </ControlActEvent>\r\n</QUPC_IN160101UK05>\r\n"}'
