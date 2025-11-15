PYTHON = python3
VENV = .venv

.PHONY: venv install run import-tcgdex

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV)/Scripts/activate && pip install -r requirements.in && pip freeze > requirements.txt || \
	. $(VENV)/bin/activate && pip install -r requirements.in && pip freeze > requirements.txt

run: venv
	$(VENV)/Scripts/activate && pip install -r requirements.txt && uvicorn app.main:app --reload || \
	. $(VENV)/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

import-tcgdex: venv
	$(VENV)/Scripts/activate && PYTHONPATH=. $(PYTHON) scripts/import_tcgdex.py || \
	. $(VENV)/bin/activate && PYTHONPATH=. $(PYTHON) scripts/import_tcgdex.py
