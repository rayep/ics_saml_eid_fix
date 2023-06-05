"""
ICS SAML Entity ID change fix v1.0

Script to fix ICS SAML null host-fqdn value issue by updating the cache with the global FQDN value.

Author: Ray A.
Email: ray@raysecure.ml

(c) 2023 Ray A. All rights reserved.

License:
This project is licensed under the terms of the MIT License.
See the LICENSE file for more information.
"""

import sys
import ssl
import argparse
import getpass
from urllib.error import HTTPError
from src.rest import RESTClient
from src.auth import HTTPAuthMgr
from src.fix import SAMLEidFix

# SSL Context for ignoring certificate errors.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

arguments = argparse.ArgumentParser(
    prog='ICS SAML Entity ID fix',
    usage='python3 saml_eid_fix.py [-h] --host HOST --username USERNAME [--dry-run]',
    description='Script to fix ICS SAML null host-fqdn value and entity ID change issue.',
    epilog='Created by Ray A. - v1.0')

arguments.add_argument('--host', action='store', type=str,
                       dest='host', required=True,
                       help="VPN server hostname/IP (without 'http/https' prefix)")
arguments.add_argument('--username', action='store', type=str,
                       dest='username', required=True, help='REST API Admin username')
arguments.add_argument('--dry-run', action='store_true',
                       help='Dry run - (Evaluate Only) Check if any SAML servers have null host-fqdn value.',
                       dest='dry')

if len(sys.argv) <= 1:
    print()
    arguments.print_help()
    print()
    input("Press any key to exit.")
    raise SystemExit()

args = arguments.parse_args()
print()
print('*** ICS SAML Entity ID fix - Start ***\n')

while True:
    admin_password = getpass.getpass(
        prompt="Enter REST API Admin password: ", stream=None)
    if admin_password:
        break


def get_api_key(uri, username: str, password: str = ''):
    """Get ICS REST API key"""
    creds = HTTPAuthMgr(uri=uri, username=username, password=password)
    request = RESTClient(creds)
    try:
        resp = request.get(url=f"https://{uri}/api/v1/auth")
    except HTTPError as exc:
        raise SystemExit(f"\n #!#! API_KEY ERROR: {exc}. \
Please check the admin credentials!") from None
    return resp['api_key']


api_key = get_api_key(args.host, args.username, admin_password)
print("\n^^^ API_KEY SUCCESS: REST API login successful ^^^\n")

auth = HTTPAuthMgr(uri=args.host,
                   username=api_key, password='')
client = RESTClient(auth)

saml_fix = SAMLEidFix(args.host, client)

if args.dry:
    saml_fix.start(dry_run=True)
else:
    saml_fix.start()

print('*** ICS SAML Entity ID fix - Complete ***')
