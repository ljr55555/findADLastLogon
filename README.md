# findADLastLogon #

This script gets the last logon time for an ID across all registered domain controllers. The replicated lastLogonTimestamp attribute does not have the most recent logon, so more accurate results are obtained by querying each domain controller for the non-replicated lastLogon value. Failing back to lastLogonTimestamp when no lastLogon value is set.

Copy config.example to config.py and update variables as needed for your Active Directory organization
