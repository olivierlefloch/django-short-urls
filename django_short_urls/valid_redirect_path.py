import urllib
import urlparse


VALID_PATHS = ('/recruiter', '/share', '/search')


def get_hash_from(path):
    if any(path.endswith(p) for p in VALID_PATHS):
        splitted = path.split('/')
        return '/'.join(splitted[:-1]), splitted[-1]
    return path, None


def add_parameter(url, redirect_param):
    if not redirect_param:
        return url

    query_update = {
        'short_redirect': redirect_param
    }

    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(query_update)

    url_parts[4] = urllib.urlencode(query)

    return urlparse.urlunparse(url_parts)


