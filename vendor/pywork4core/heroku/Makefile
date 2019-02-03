heroku_manage:
	heroku run python ./manage.py ${cmd}

heroku_migrate:
	make heroku_manage cmd=migrate

heroku_shell:
	make heroku_manage cmd=shell
