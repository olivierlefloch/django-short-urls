import urlparse
import re
from urllib import urlencode


VALID_REDIRECTIONS  = ('recruiter', 'share', 'search')
REDIRECT_PARAM_NAME = 'redirect_suffix'


def get_hash_from(path):
    '''
    Parses the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''

    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)

    if not match:
        return path, None
    return match.group(1), match.group(2)


def url_append_parameters(url, params_to_append):
    '''
    Appends the REDIRECT_PARAM_NAME param and the shorten's GET params
    to the long URL
    '''

    params_to_append = dict(params_to_append)

    if not params_to_append:
        return url

    (scheme, netloc, path, params, link_query, fragment) = urlparse.urlparse(url)

    # Convert a link query to a dict
    link_query = dict(urlparse.parse_qsl(link_query))
    link_query.update(params_to_append)

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        urlencode(link_query),
        fragment
    ))
