
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
test:
	python -m pytest tests

.PHONY: build
build base:
	docker build . -f Dockerfile -t python-base


.PHONY: build all base server-one server-two job-a job-b job-c
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
