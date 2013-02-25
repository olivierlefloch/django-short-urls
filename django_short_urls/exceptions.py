from django.db.utils import DatabaseError

# FIXME: Move to a dedicated ServiceUnavailable app
class DatabaseWriteDenied(DatabaseError):
    pass
