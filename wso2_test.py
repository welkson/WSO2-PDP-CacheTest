# -*- coding: utf-8 -*-

from suds.client import Client
import logging
import requests.auth
import requests
import xmltodict

# ignore self-signed certificate
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# disable SSL warnings
import urllib3
urllib3.disable_warnings()

# WSO2 API URL (PAP and PDP)
wso2_pap_api = 'https://localhost:9443/services/EntitlementPolicyAdminService?wsdl'
wso2_pdp_api = "https://localhost:9443/api/identity/entitlement/decision/pdp"
wso2_admin_api = 'https://localhost:9443/services/EntitlementAdminService?wsdl'


# XACML Policy Test (resource-id = /new_ticket)
p1 = """
    <Policy xmlns="urn:oasis:names:tc:xacml:3.0:core:schema:wd-17" PolicyId="OnlyNewTicket" RuleCombiningAlgId="urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:deny-unless-permit" Version="1.0">
       <Target/>
       <Rule Effect="Permit" RuleId="Rule1">
          <Target>
             <AnyOf>
                <AllOf>
                   <Match MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal">
                      <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">/new_ticket</AttributeValue>
                      <AttributeDesignator AttributeId="urn:oasis:names:tc:xacml:1.0:resource:resource-id" Category="urn:oasis:names:tc:xacml:3.0:attribute-category:resource" DataType="http://www.w3.org/2001/XMLSchema#string" MustBePresent="true"/>
                   </Match>
                </AllOf>
             </AnyOf>
          </Target>
       </Rule>
    </Policy>
"""


def xacml_request_p1(attributes):
    headers = {'Accept': 'application/xml',
               'Content-Type': 'application/xml;charset=UTF-8',
               'Authorization': 'Basic YWRtaW46YWRtaW4='}           # admin/admin (base64)

    data = """
            <Request CombinedDecision="false" ReturnPolicyIdList="false" xmlns="urn:oasis:names:tc:xacml:3.0:core:schema:wd-17">
            <Attributes Category="urn:oasis:names:tc:xacml:3.0:attribute-category:resource">
                <Attribute AttributeId="urn:oasis:names:tc:xacml:1.0:resource:resource-id" IncludeInResult="false">
                    <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">%s</AttributeValue>
                </Attribute>
            </Attributes>
            </Request>
    """ % (attributes["resource-id"])

    request = requests.post(wso2_pdp_api, headers=headers, data=data, verify=False)

    return xmltodict.parse(request.text)['Response']['Result']['Decision'] == u'Permit'


def clear_cache():
    client_admin = Client(wso2_admin_api, username="admin", password="admin")
    client_admin.service.clearPolicyCache()
    return


if __name__ == '__main__':
    client = Client(wso2_pap_api, username="admin", password="admin")

    # clear cache before policy manipulation
    clear_cache()

    # PolicyDTO
    policyDTO = client.factory.create("ax2340:PolicyDTO")
    policyDTO.active = True
    policyDTO.policy = p1
    policyDTO.promote = True

    # add Policy in PAP and publish in PDP (promote=True)
    try:
        client.service.addPolicy(policyDTO)
        print u"Policy added."

    except Exception, e:
        if "Id already exists" in e.message :
            print u"Policy alread exists. Please see README. Aborting..."
        else:
            print u'Failed to add new policy: ' + str(e)
        exit()

    # Test 1: Access using resource=/new_ticket (PERMIT)
    print u"""\n\n---> Test Policy [OnlyNewTicket]:
          resource-id = /new_ticket
          Expected Result: PERMIT"""
    if xacml_request_p1({"resource-id": "/new_ticket"}):
        print u"Result: Access PERMIT"
    else:
        print u"Result: Access DENY"

    # Test 2: Access using resource=/cancel_ticket (DENY)
    print u"""\n\n---> Test Policy [OnlyNewTicket]:
          resource-id = /cancel_ticket
          Expected Result: DENY"""
    if xacml_request_p1({"resource-id": "/cancel_ticket"}):
        print u"Result: Access PERMIT"
    else:
        print u"Result: Access DENY"
