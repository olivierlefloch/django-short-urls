db.link.update({creator: {$exists: true}}, {$unset: {creator: 1}}, {multi : true})
