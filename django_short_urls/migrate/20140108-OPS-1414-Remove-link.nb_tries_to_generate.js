db.link.update({nb_tries_to_generate: {$exists: true}}, {$unset: {nb_tries_to_generate: 1}}, /*upsert*/ 0, /*multi*/ 1, 0)
