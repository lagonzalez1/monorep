.PHONY: lint
lint:
	# TODO(take-home-only)
	ruff check .

.PHONY: check
check:
	@echo "Directories"
	@ls -d lib/ scripts/ test/

.PHONY: check
test:
	python -m pytest tests

.PHONY: build
build-base:
	docker build . -f Dockerfile -t python-base


# List all apps under apps/
APPS := $(patsubst apps/%,%,$(wildcard apps/*))
BASE_IMAGE := python-base

.PHONY: all $(APPS:%=build-%)

# Default target: build every app that has changed
all: $(APPS:%=build-%)

# build-<app> checks for git changes then builds
build-%:
	@echo "→ Checking changes for apps/$*"
	@if git diff --quiet HEAD -- apps/$*; then \
		echo "✔ No changes in apps/$*, skipping build"; \
	else \
		echo "⏳ Building $*..."; \
		docker build \
			--build-arg BASE_IMAGE=$(BASE_IMAGE) \
			-t $*:latest \
			-f apps/$*/Dockerfile .; \
		echo "✅ Built apps/$*"; \
	fi

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
