from mongoengine import *

class User(Document):
    login = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email = StringField(required=True)

class Link(Document):
    # FIXME: Add unit tests
    
    short_path = StringField(required=True)
    short_path_to_lower = StringField(required, unique=True)
    long_url = StringField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        
        self.short_path_to_lower = short_path.lower()
    
    @classmethod
    def new(cls, long_url, short_path=None):
        if short_path is None:
            raise NotImplementedError
        
        link = cls(short_path=short_path, long_url=long_url)
        
        if not link.new():
            raise Exception('Short path "%s" has already been bound.' % short_path)
        
        link.save()
        
        return link
    
    @classmethod
    def find_by_short_path(cls, short_path):
        """Return Link with matching short path (ignores case)"""
        
        return cls.objects(short_path_to_lower=path.lower()).first()
        
    
    def __str__(self):
        return "%s -> %s\n" % (self.short_path, self.long_url)
