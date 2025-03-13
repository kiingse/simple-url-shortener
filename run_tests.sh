#! /bin/bash

export ENV=.env.test
poetry run pytest -v $@
