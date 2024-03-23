run:
	python3 main.py
install:
	pip3 install -r requirements.txt
package:
	pip3 freeze > requirements_draft.txt
