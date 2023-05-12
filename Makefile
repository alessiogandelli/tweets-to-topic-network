VENV := venv

all: venv
$(VENV)/bin/activate: requirements.txt
	python3.9 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt


venv: $(VENV)/bin/activate

run: venv
	./$(VENV)/bin/python3 src/main.py $(tweet_file) $(user_file)

clean:
	rm -rf  $(VENV)
	find . -type f -name '*.pyc' -delete


.PHONY: all venv run clean