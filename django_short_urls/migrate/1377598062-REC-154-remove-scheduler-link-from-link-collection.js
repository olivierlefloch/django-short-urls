db.link.update({}, {$unset: {scheduler_link: 1}}, /*upsert*/ 0, /*multi*/ 1, 0)
