#
# Run this first on a computer with a web browser, in order to get a valid app code.
# A second run with the code filled in below will cause the script to save a session
# file, which is needed by the upload script on the target machine.
#

import sys
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer

# fill these in based on your registered onedrive app:
client_id = ''
client_secret = ''

# fill this in after you run the script once, see below
code = ''

client = onedrivesdk.get_default_client(client_id=client_id,
                                        scopes=['wl.signin',
                                                'wl.offline_access',
                                                'onedrive.readwrite'])

if not code:
    # do this to get an auth code on a machine with a browser:

    redirect_uri = 'https://login.live.com/oauth20_desktop.srf'
    auth_url = client.auth_provider.get_auth_url(redirect_uri)
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
else:
    client.auth_provider.authenticate(code, redirect_uri, client_secret)
    client.auth_provider.save_session()
