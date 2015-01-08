heroku_manage:
	heroku run python ./manage.py ${cmd}

heroku_syncdb:
	make heroku_manage cmd=syncdb

heroku_shell:
	make heroku_manage cmd=shell
