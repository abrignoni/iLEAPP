format:
	black ilapfuncs.py contrib/
	importanize ilapfuncs.py contrib/

clean:
	rm -rf ILEAPP_Reports*
