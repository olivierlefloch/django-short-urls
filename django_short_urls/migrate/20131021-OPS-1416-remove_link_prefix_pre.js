// Run this PRE release

db.link.ensureIndex(
    { long_url: "hashed" },
    {
        background: true
    }
);
