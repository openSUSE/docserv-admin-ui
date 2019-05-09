# docserv-admin-ui
Admin UI for DocServ

Package prerequisites:
 - Flask
 - python3-pycurl
 - python3-lxml

Prerequisites:
- Export the variable 'FLASK_APP' to 'app.py'
- Make sure that you have checked out the most recent version of the docserv configuration and documentation configuration
- Make sure that you have the paths to the checked out git repositories in 'config.py'
- Make sure that you have an DocServ instance running on another port than 5000.

The Admin UI is reachable on localhost:5000.

How to build documentation on the Admin UI:
- Open 'localhost:5000'
- Navigate to your desired product with the help of the sidebar and further hyperlinks
- Click on 'Build Me'
- The status of the build process can be checked on 'localhost:5000/queue'



