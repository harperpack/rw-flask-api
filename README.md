# rw-flask-api
A simple API allowing POST requests to write to and read from json files.


## Local Development Use
- Clone this repository
- **OPTIONAL for development purposes**: 
  - Navigate to <code>./core/app.py</code> line 15 and set <code>VERBOSE = True</code>
- Run <code>sh local_dev.sh</code>
- The server should now be running at <code>http://127.0.0.1:5000</code>
- Review <code>examples.txt</code> for guidance on interacting with the API and its endpoints
- Files written can be found in <code>./files/</code>

- The deployed version of this repo can be found at <code>http://api.the-singularity-show.com/api/</code>
  - *following the instructions in the Digital Ocean tutorials for 
    - [setting up a server](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-22-04)
    - [installing NGINX](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04)
    - [serving up a Flask application on a server running NGINX](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04)
