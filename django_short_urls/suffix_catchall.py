import urlparse
import re
from urlparse         import parse_qsl
from urllib           import urlencode


VALID_REDIRECTIONS  = ('recruiter', 'share', 'search')
REDIRECT_PARAM_NAME = 'redirect_suffix'
REF_PARAM_NAME      = 'ref'



def get_hash_from(path):
    ''' Parse the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''
    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)
    if not match:
        return path, None
    return match.group(1), match.group(2)


def append_url_parameter(url, shorten_query):
    ''' Appends the get_params with the REDIRECT_PARAM_NAME parameter
    to the url ``url``
    '''
    shorten_query = dict(parse_qsl(shorten_query))
    if REDIRECT_PARAM_NAME not in shorten_query:
        return url

    if REF_PARAM_NAME not in shorten_query:
        shorten_query[REF_PARAM_NAME] = 'shortener'

    (scheme, netloc, path, params, link_query, fragment) = urlparse.urlparse(url)
    link_query = dict(parse_qsl(link_query))
    link_query.update(shorten_query)

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        urlencode(shorten_query),
        fragment
    ))

