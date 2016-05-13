#############
# VARIABLES #
#############
ifndef PROJECT_DIR
    $(error PROJECT_DIR must be defined when including the virtualenv Makefile)
endif

PYTHONHOME ?= ${PROJECT_DIR}venv/
VENV_WRAPPER_DIR = $(abspath ${PYTHONHOME})/.virtualenvs/

PIP_VERSION = 8.1.2
PYTHON_VERSION = python2.7

ACTIVATE_VENV = . ${PYTHONHOME}/bin/activate

################
# Installation #
################

.PHONY: venv

venv: venv_init venv_prereqs venv_deps venv_wrapper

venv_init:
	(test -d ${PYTHONHOME} || virtualenv --python=${PYTHON_VERSION} --no-site-packages ${PYTHONHOME})
	${CFLAGS} ${PYTHONHOME}/bin/pip install --upgrade pip==${PIP_VERSION}

venv_prereqs:
	(test -f $(PROJECT_DIR)pre_requirements.txt && ${PYTHONHOME}/bin/pip install --upgrade -r $(PROJECT_DIR)pre_requirements.txt) || ! test -f $(PROJECT_DIR)pre_requirements.txt

venv_deps:
	${CFLAGS} ${PYTHONHOME}/bin/pip install --upgrade -r $(PROJECT_DIR)requirements.txt

venv_wrapper:
	(test -d ${VENV_WRAPPER_DIR} || mkdir -p ${VENV_WRAPPER_DIR})
	@# PW4C_DIR will be added to the virtual env path if set
ifdef PW4C_DIR
	# Explicit bash call required for virtualenvwrapper compatibility, make uses sh by default
	# https://bitbucket.org/dhellmann/virtualenvwrapper#rst-header-supported-shells
	# virtualenvwrapper needs to be sourced for add2virtualenv
	bash -c "${ACTIVATE_VENV} && WORKON_HOME='${VENV_WRAPPER_DIR}' source ${PYTHONHOME}/bin/virtualenvwrapper.sh && add2virtualenv ${PW4C_DIR}"
endif

venv_check_versions:
	${ACTIVATE_VENV} && pip list --outdated
