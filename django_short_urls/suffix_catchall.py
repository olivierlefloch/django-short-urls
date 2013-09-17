import urlparse
import re
from django.http import QueryDict


VALID_REDIRECTIONS = ('recruiter', 'share', 'search')
REDIRECT_PARAM_NAME = 'redirect_suffix'
REF_PARAM_NAME      = 'ref'



def get_hash_from(path):
    ''' Parse the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''
    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)
    if not match:
        return path, None
    return match.group(1), match.group(2)


def append_url_parameter(url, get_params):
    ''' Appends the get_params with the REDIRECT_PARAM_NAME parameter
    to the url ``url``
    '''
    if REDIRECT_PARAM_NAME not in get_params:
        return url

    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

    if REF_PARAM_NAME not in get_params:
        get_params[REF_PARAM_NAME] = 'shortener'

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        get_params.urlencode(),
        fragment
    ))

