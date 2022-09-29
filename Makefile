.PHONY: clean readme-toc tag

JOBS ?= 1

help:
	@echo "    clean"
	@echo "        Remove Python/build artifacts."
	@echo "	   readme-toc"
	@echo "		   Generate a Table Of Content for the README.md"
	@echo "    tag"
	@echo "        Create tag based on the current version and push to remote."

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	find . -name '__pycache__' -exec rm -r {} +
	find . -name 'README.md.*' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/
	rm -rf docs/_build
	# rm -rf *egg-info
	# rm -rf pip-wheel-metadata

readme-toc:
	# https://github.com/ekalinin/github-markdown-toc
	gh-md-toc --insert README.md

tag:
	git tag $$tag
	git push --tags
