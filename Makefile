
.PHONY: lint format
lint:
	ruff check .
format:
	ruff format .

.PHONY: check
check:
	@echo "Directories in repo"
	@ls -d lib/ scripts/ tests/ apps/ static_data/

.PHONY: test
ALLOWED := job-a job-b job-c server-one server-two server-three test-base
test-base:
	python -m pytest tests; 

test:
	@$(eval JOB_ARG = $(word 2,$(MAKECMDGOALS)))
	@if [ "$(JOB_ARG)" = "all" ]; then \
		echo "Running all tests"; \
		python -m pytest apps/; \
	elif echo "$(JOBS)" | grep -qw "$(JOB_ARG)"; then \
		echo "Running tests for $(JOB_ARG)" and installing dependencies; \
		pip install -r apps/$(JOB_ARG)/requirements.txt &&  \
		python -m pytest apps/$(JOB_ARG)/tests; \
	else \
		echo "Error: unknown job '$(JOB_ARG)'"; \
		echo "Usage: make test [all|job_name]"; \
		echo "Available jobs: $(JOBS)"; \
		exit 1; \
	fi


.PHONY: build base
build base:
	docker build . -f Dockerfile -t python-base


.PHONY: build all base server-one server-two server-three job-a job-b job-c
APP_ARG = $(word 2,$(MAKECMDGOALS))
build:
	@$(eval SUBAPPS := $(notdir $(wildcard apps/*)))
	@if [ "$(APP_ARG)" = "base" ]; then \
		echo "Building base image.."; \
		docker build . -f Dockerfile -t python-base; \
	elif [ "$(APP_ARG)" = "all" ]; then \
		for app in $(SUBAPPS); do \
			docker build . -f apps/$$app/Dockerfile -t python-$$app; \
		done; \
	elif echo "$(SUBAPPS)" | grep -qw "$(APP_ARG)"; then \
		echo "Building single app: $(APP_ARG)"; \
		docker build . -f apps/$(APP_ARG)/Dockerfile -t python-$(APP_ARG); \
	else \
		echo "Error: unknown target '$(APP_ARG)'"; \
		echo "Usage: make build [base|all|app_name]"; \
		echo "Available apps: $(SUBAPPS)"; \
		exit 1; \
	fi
