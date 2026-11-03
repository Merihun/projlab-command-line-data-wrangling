.PHONY: data lint check

data:  ## (re)create incoming/ and app-logs/ exactly as they were
	python -m fernhill_files generate

lint:  ## check every script with shellcheck
	shellcheck bin/*.sh scripts/*.sh

check:  ## run the project's checks on your machine: needs the local check kit in .projlabs/ (Review page)
	python .projlabs/check.py
