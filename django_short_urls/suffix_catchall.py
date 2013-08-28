import urlparse
import re
from django.http import QueryDict


VALID_REDIRECTIONS = ('recruiter', 'share', 'search')
REDIRECT_PARAM_NAME = 'suffix_from_shortener'



def get_hash_from(path):
    ''' Parse the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''
    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)
    if not match:
        return path, None
    return match.group(1), match.group(2)


def append_url_parameter(url, app_data):
    ''' Appends the parameter REDIRECT_PARAM_NAME with the value ``app_data``
    to the url ``url``
    '''
    if not app_data:
        return url

    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

    query = QueryDict(query, mutable=True)
    query[REDIRECT_PARAM_NAME] = app_data

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        query.urlencode(),
        fragment
    ))

