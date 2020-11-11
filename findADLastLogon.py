################################################################################
##      This script gets the last logon time for an ID across all registered
## domain controllers. The replicated lastLogonTimestamp attribute does not
## have the most recent logon, so more accurate results are obtained by
## querying each domain controller for the non-replicated lastLogon value. 
## Failing back to lastLogonTimestamp when no lastLogon value is set.
################################################################################
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, ALL_ATTRIBUTES, ALL, DEREF_NEVER
from srvresolver.srv_resolver import SRVResolver
import json
import datetime

from config import strADDomain, strLDAPUsername, strLDAPPassword, strFilter, strSearchBase

dictLastLogons = dict()

# Use SRV record to get list of all registered domain controllers
objLDAPServers = SRVResolver.resolve(f"_ldap._tcp.{strADDomain}")

for objLDAPServer in objLDAPServers:
	strDC = objLDAPServer.host
	try:
		server = Server(strDC, get_info=ALL)
		conn = Connection(server, strLDAPUsername, strLDAPPassword, auto_bind=True)
		conn.search(search_base=strSearchBase, search_filter=strFilter,search_scope=SUBTREE,attributes=['lastLogonTimestamp','lastLogon','sAMAccountName'])
		if len(conn.entries) > 0:
			for entry in conn.entries:
				jsonEntry = entry.entry_to_json()
				dictEntry = json.loads(jsonEntry)
				strLogonID = dictEntry['attributes']['sAMAccountName'][0]
				if dictEntry['attributes'].get('lastLogon'):
					strLastLogon = dictEntry['attributes']['lastLogon'][0]
					strLastLogon = strLastLogon.split("+")[0]
					dateLastLogon = datetime.datetime.strptime(strLastLogon, '%Y-%m-%d %H:%M:%S.%f')
					if (strLogonID not in dictLastLogons) or (dateLastLogon > dictLastLogons[strLogonID] ):
						dictLastLogons[strLogonID] = dateLastLogon
				elif dictEntry['attributes'].get('lastLogonTimestamp'):
					strLastLogon = dictEntry['attributes']['lastLogonTimestamp'][0]
					strLastLogon = strLastLogon.split("+")[0]
					dateLastLogon = datetime.datetime.strptime(strLastLogon, '%Y-%m-%d %H:%M:%S.%f')
					if (strLogonID not in dictLastLogons) or (dateLastLogon > dictLastLogons[strLogonID] ):
						dictLastLogons[strLogonID] = dateLastLogon
		else:
			print(f"No ID found matching filter strFilter on {strDC}.")
		conn.unbind()
	except:
		print(f"Unable to connect to host {strDC}.")
		
print("Last Logon Report")
print("Username\tLast Logon")
for key in dictLastLogons:
	print(f"{key}\t{dictLastLogons[key]}")