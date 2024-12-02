.PHONY: env, install-dev, tag
.PHONY: test, check-style

ifeq ($(BRANCH_NAME),)
BRANCH_NAME="$$(git rev-parse --abbrev-ref HEAD)"
endif

env:
	virtualenv -p python3.13 env

install-dev: env
	pip install -r requirements-dev.txt

tag:
	@if [ "$(BRANCH_NAME)" != "main" ]; then \
		echo "You must be on main to update the version"; \
		exit 1; \
	fi;
	@if [ "$(VERSION_PART)" = '' ]; then \
		echo "Must specify VERSION_PART to bump (major, minor, patch)."; \
		exit 1; \
	fi;
	pip install bumpversion
	git push origin main
	git stash && \
	git fetch --all && \
	git reset --hard origin/main && \
	bumpversion $(VERSION_PART) && \
	git push origin --tags && \
	git push origin main && \
	git stash pop

check-style:
	flake8 pushoverflow --count --show-source --statistics
	flake8 tests --count --show-source --statistics

test:
	py.test --junitxml=junit.xml \
		--cov=pushoverflow \
		--cov-branch \
		--cov-report=xml:coverage.xml \
		--cov-config=setup.cfg \
		tests
	coverage report -m

test-all: test check-style
