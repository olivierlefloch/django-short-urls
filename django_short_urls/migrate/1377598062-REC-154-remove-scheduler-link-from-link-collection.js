db.link.update({scheduler_link: {$exists: true}}, {$unset: {scheduler_link: 1}}, /*upsert*/ 0, /*multi*/ 1, 0)
