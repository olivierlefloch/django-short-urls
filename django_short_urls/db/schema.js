// Schema config in addition to models.py

db.link.ensureIndex({ long_url: "hashed" }, { background: true });
