db.link.update({nb_tries_to_generate: {$exists: true}}, {$unset: {nb_tries_to_generate: 1}}, {multi : true})
