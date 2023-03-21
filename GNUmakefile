PYSCRIPTS:=vs-project-survey.py

lint: $(PYSCRIPTS)
	flake8 $^

pretty: black

prerequisites: requirements.txt install-python-prerequisites.sh
	./install-python-prerequisites.sh

black: $(PYSCRIPTS)
	$@ $^

vulture: $(PYSCRIPTS)
	$@ $^

all: black lint vulture

.PHONY: all black lint pretty prerequisites vulture
