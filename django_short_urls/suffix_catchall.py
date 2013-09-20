import urlparse
import re
from urllib import urlencode


VALID_REDIRECTIONS  = ('recruiter', 'share', 'search')
REDIRECT_PARAM_NAME = 'redirect_suffix'



def get_hash_from(path):
    ''' Parse the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''
    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)
    if not match:
        return path, None
    return match.group(1), match.group(2)


def append_url_parameter(url, shorten_query):
    ''' Appends REDIRECT_PARAM_NAME param and the shorten's GET params
    to the long URL
    '''

    # Convert a shorten query from a=1&b=3
    # to a dict { a : 1 , b : 3}
    shorten_query = dict(urlparse.parse_qsl(shorten_query))

    if REDIRECT_PARAM_NAME not in shorten_query:
        return url

    (scheme, netloc, path, params, link_query, fragment) = urlparse.urlparse(url)

    # Convert a link query to a dict
    link_query = dict(urlparse.parse_qsl(link_query))
    link_query.update(shorten_query)

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        urlencode(shorten_query),
        fragment
    ))

