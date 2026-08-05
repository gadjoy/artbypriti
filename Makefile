# Local development helpers. Requires Hugo Extended (see [module.hugoVersion] in hugo.toml).
# Run `make` or `make help` for the list.

.DEFAULT_GOAL := help
.PHONY: help serve build check new clean

help: ## Show this help
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1m%-8s\033[0m %s\n", $$1, $$2}'

serve: ## Dev server with drafts at http://localhost:1313
	hugo server -D

build: ## Production build into ./public
	hugo --minify --gc

check: ## Validate artwork front matter, then confirm the site builds
	python3 scripts/check-content.py
	hugo --minify --gc --printPathWarnings --destination $(CURDIR)/public-check
	@rm -rf $(CURDIR)/public-check

new: ## Scaffold an artwork: make new SLUG=my-painting
	@test -n "$(SLUG)" || { echo "usage: make new SLUG=my-painting"; exit 1; }
	hugo new content/$(SLUG)/index.md
	@echo
	@echo "Next: put the image in content/$(SLUG)/ (named $(SLUG).jpg, or update"
	@echo "the 'resources' src), fill in description/dimensions, set draft: false."

clean: ## Remove build output and the local image-variant cache
	rm -rf public public-check resources/_gen
	hugo --gc >/dev/null 2>&1 || true
