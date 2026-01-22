.PHONY: harness harness-quick

PYTHON ?= python
HARNESS = scripts/run_harness.py

harness:
	$(PYTHON) $(HARNESS)

harness-quick:
	$(PYTHON) $(HARNESS) --quick
