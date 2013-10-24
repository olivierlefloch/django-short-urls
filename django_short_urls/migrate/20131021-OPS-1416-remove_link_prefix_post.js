// Run this POST release

db.link.dropIndex({"prefix": 1, "long_url": 1})

db.link.update(
    {short_path: {$exists: true}},
    {$unset: {prefix: 1, short_path: 1, created_at: 1}},
    /* upsert */ false,
    /* multi */ true
);
