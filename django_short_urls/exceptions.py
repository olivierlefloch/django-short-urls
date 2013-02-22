# FIXME: Move to a dedicated ServiceUnavailable app
from django.db.utils import DatabaseError

class DatabaseWriteDenied(DatabaseError):
    pass
