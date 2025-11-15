PYTHON = python
VENV = .venv

.PHONY: venv install run

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV)/Scripts/activate && pip install fastapi "uvicorn[standard]" && pip freeze > requirements.txt || \
	. $(VENV)/bin/activate && pip install fastapi "uvicorn[standard]" && pip freeze > requirements.txt

run: venv
	$(VENV)/Scripts/activate && pip install -r requirements.txt && uvicorn app.main:app --reload || \
	. $(VENV)/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload
