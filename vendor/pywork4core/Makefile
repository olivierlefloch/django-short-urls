#############
# VARIABLES #
#############

PROJECT_DIR = $(dir $(firstword $(MAKEFILE_LIST)))
APP_DIR = ${PROJECT_DIR}${APP_NAME}/
APP_TESTS_DIR = ${APP_DIR}tests/

WORK4CORE_DIR = $(dir $(lastword $(MAKEFILE_LIST)))
WORK4CORE_BIN = ${WORK4CORE_DIR}bin/
WORK4CORE_TESTS_DIR = ${WORK4CORE_DIR}django_app/tests/

TEMP_DIR = ${PROJECT_DIR}temp/
PYTHONHOME ?= ${PROJECT_DIR}venv/
VENV_WRAPPER_DIR = $(abspath ${PYTHONHOME})/.virtualenvs/

SETTINGS_TPL_FILE = ${APP_DIR}local_settings.tpl.py
SETTINGS_FILE = ${APP_DIR}local_settings.py

ifeq (${WORK4CORE_DIR}, ${PROJECT_DIR})
	IN_WORK4CORE_PROJECT = TRUE
else
	IN_WORK4CORE_PROJECT = FALSE
endif

ifeq (${IN_WORK4CORE_PROJECT}, TRUE)
	VENDOR_DIR = ${PROJECT_DIR}
else
	VENDOR_DIR = ${PROJECT_DIR}vendor/
endif

ACTIVATE_VENV = . ${PYTHONHOME}bin/activate

RUNNER = ${ACTIVATE_VENV} &&

ifeq ($(wildcard $(PROJECT_DIR).env),)
	RUN_CMD = ${RUNNER}
else
	RUN_CMD = ${RUNNER} foreman run
endif


######################
# PLATFORM DEPENDENT #
######################

UNAME_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')

ifeq (${UNAME_S}, Darwin)
	CFLAGS = CFLAGS="-I /opt/local/include -L /opt/local/lib"
endif

##########
# CONFIG #
##########

.SILENT: deep_clean_ask confirm install install_pre install_do install_project install_post

all: clean install lint test

#########
# RULES #
#########

################
# Installation #
################

install: install_pre install_do install_project install_post

install_pre:

install_do:
	mkdir -p ${TEMP_DIR}
	(test -d ${PYTHONHOME} || virtualenv ${PYTHONHOME})
	${CFLAGS} ${PYTHONHOME}bin/pip install --upgrade -r ${WORK4CORE_DIR}requirements.txt
	(test -f ${PROJECT_DIR}requirements.txt && ${CFLAGS} ${PYTHONHOME}bin/pip install --upgrade -r ${PROJECT_DIR}requirements.txt) || true
	(test -d ${VENV_WRAPPER_DIR} || mkdir -p ${VENV_WRAPPER_DIR})
	# Explicit bash call required for virtualenvwrapper compatibility
	# https://bitbucket.org/dhellmann/virtualenvwrapper#rst-header-supported-shells
	# virtualenvwrapper needs to be sourced for add2virtualenv
	bash -c "${ACTIVATE_VENV} && WORKON_HOME='${VENV_WRAPPER_DIR}' source ${PYTHONHOME}bin/virtualenvwrapper.sh && add2virtualenv ${VENDOR_DIR}"

install_project::

install_post:
	echo "Copying settings..."
	([ ! -f ${SETTINGS_TPL_FILE} ] && echo "Project does not have any local settings.") || \
		([ -f ${SETTINGS_FILE} ] && echo "Settings file already exists.") || \
			(cp -n ${SETTINGS_TPL_FILE} ${SETTINGS_FILE} && vi ${SETTINGS_FILE})


######################
# Temp file handling #
######################

clean:
	(test -d ${TEMP_DIR} && rm -rf ${TEMP_DIR}* ) || true

# The code below helps reset the repository completely to its pre-install state
deep_clean: deep_clean_ask confirm deep_clean_do

deep_clean_ask:
	echo "This will remove any unversioned files, except for the settings file"

deep_clean_do: clean_pyc
	rm -rf ${TEMP_DIR} ${PYTHONHOME}

clean_pyc:
	find ${PROJECT_DIR} -name "*.pyc" -exec rm -f {} \;


###################
# Code validation #
###################

pep8:
	# Please ensure pep8 is happy first (before tests or linting)
	${PYTHONHOME}bin/pep8 --config=${WORK4CORE_DIR}config/pep8.cfg ${PROJECT_DIR}

PYLINT_RC = ${WORK4CORE_DIR}config/pylint.rc
EXTRA_ARGS_FOR_TESTS = --method-rgx='([a-z_][a-z0-9_]{2,30}|(setUp|tearDown)(Class)?)$$' --disable=C0111,R0904,C0321
lint: pep8
	${PYTHONHOME}bin/pylint --rcfile=${PYLINT_RC} ${WORK4CORE_DIR}
	${PYTHONHOME}bin/pylint --rcfile=${PYLINT_RC} ${EXTRA_ARGS_FOR_TESTS} ${WORK4CORE_TESTS_DIR}
ifeq (${IN_WORK4CORE_PROJECT}, TRUE)
else
	${PYTHONHOME}bin/pylint --rcfile=${PYLINT_RC} ${APP_DIR}
	${PYTHONHOME}bin/pylint --rcfile=${PYLINT_RC} ${EXTRA_ARGS_FOR_TESTS} ${APP_TESTS_DIR}
endif


#########
# Tests #
#########

COVERAGE_RC = ${WORK4CORE_DIR}config/coverage.rc

test: pep8
	${RUN_CMD} ${PYTHONHOME}bin/coverage run --rcfile=${COVERAGE_RC} --source=${APP_DIR},${WORK4CORE_DIR} ${PROJECT_DIR}manage.py test --traceback --noinput
	@${PYTHONHOME}bin/coverage report --rcfile=${COVERAGE_RC} --fail-under=100 || (printf "\033[31mTest coverage is less than 100%%!\033[0m\n" && exit 1)

test_report:
	${PYTHONHOME}bin/coverage html --rcfile=${COVERAGE_RC}
	${WORK4CORE_BIN}/open ${TEMP_DIR}/coverage_html/index.html


################################
# Running the app and commands #
################################

run:
ifeq (${RUNNER},)
	${PROJECT_DIR}manage.py run_server
else
	${RUNNER} start
endif

shell:
	${RUN_CMD} ${PROJECT_DIR}manage.py shell


##########################
# Git Subtree Management #
##########################

ifeq (${IN_WORK4CORE_PROJECT}, TRUE)
	# Git subtree commands cannot be run from the PyWork4Core project
else
git-subtree = git subtree ${1} --prefix=vendor/pywork4core --squash pywork4core master

git_subtree_pull:
	$(call git-subtree, pull)

git_subtree_push:
	$(call git-subtree, push)
endif

###########
# Helpers #
###########

confirm:
	${WORK4CORE_BIN}/confirm

PASS:
