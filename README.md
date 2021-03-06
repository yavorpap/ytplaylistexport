ytplaylist
========

A small library that allows exporting Youtube playlists to .pls files.

Scope
--------
This library contains a GUI based on Tkinter, a Console UI and
a CLI interface allowing the user export a particular playlist.


License
--------
The library is licensed under the GPLv3. For more information about 
the license, check the file `LICENSE`.

Usage
--------
Example usage:

* List "username"'s playlists

        ./main.py -u username -l

* Export particular playlist (titled TestPlaylist)
	
        ./main.py -u username -e playlist.pls -t TestPlaylist
	
* Run the GUI
	
        ./main.py
	
* Run the console UI
	
        ./main.py -c

Dependencies
--------
The main dependency is the Google Youtube Data API v3.
Note that it allows only OAuth login and no username/password 
authentication.

Installation
--------
Standard Python installation should work:

	python setup.py install
	