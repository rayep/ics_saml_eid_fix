### Ivanti Connect Secure SAML Entity ID change fix.
Script to fix ICS SAML null host-fqdn value issue by updating the cache with the global FQDN value.

Download the script from [here](https://github.com/rayep/ics_saml_eid_fix/archive/refs/heads/master.zip)

---
#### Prerequisites:

- Python 3.x _(Standalone or Windows Store version)_ | _Created & Tested using Python 3.9_
- Admin user account with REST API access enabled. <br>
_For enabling REST API access. Please refer to the [REST API guide](https://help.ivanti.com/ps/help/en_US/ICS/22.x/apig/rest_api_soln_guide/ovw.htm#_Toc53640462)_

---
#### Workflow:

- Fetches the global host-fqdn from SAML settings.
- Downloads all auth-server config and parses the SAML auth-type instances.
- Check if the SAML instance has valid host-fqdn value.
- If an instance with NULL host-fqdn value found, issues HTTP PUT request with correct FQDN value.

---
#### Usage:
```
usage: python3 saml_eid_fix.py [-h] --host HOST --username USERNAME [--dry-run]

Script to fix ICS SAML null host-fqdn issue by Ray A.

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          VPN server hostname/IP (without 'http/https' prefix)
  --username USERNAME  REST API Admin username
  --dry-run            Dry run - (Evaluate Only) Check if any SAML servers have null host-fqdn value.
  ```
 
 ---
 #### Examples:
 
 ##### _Apply the fix to VPN server 10.1.1.100 - use admin account 'adminuser' for API operations._
 
 ```
 > python3 saml_eid_fix.py --host 10.1.1.100 --username adminuser
 ```
 
 ##### _Dry run operation - Evaluate if the VPN server has any problematic SAML instances. No PUT request will be sent_
 ```
 > python3 saml_eid_fix.py --host 10.1.1.100 --username adminuser --dry-run
 ```
