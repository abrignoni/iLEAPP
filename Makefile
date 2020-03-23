install:
	pip install -r requirements.txt

format:
	black --exclude "/(parse3.py|ccl_bplist.py)" .
	importanize .

clean:
	rm -rf ILEAPP_Reports*

add_plugin:
	mkdir -p contrib/$(name)
	touch contrib/$(name)/__init__.py
	touch contrib/$(name)/main.py
	echo "from .main import *" > contrib/$(name)/__init__.py

test:
	@if [ ! -d ./test_images ]; then \
		echo "[ERROR] The tests depend on test images being present in a ./test_images/ directory"; \
		echo "Please refer documentation in the docstring of tests.py for more details."
	fi
	time python tests.py
