
## This is an account management RESTful APIs App running in docker containers
<img src="data-flow.drawio.png"
     alt="Markdown data flow"
     style="float: left; margin-right: 10px;" />

I used flask in python, SQLAlchemy(ORM) and Postgresql as a database, and running the flask app and postgresql in Docker containers.  




---

### Prerequisite
- Make sure you have docker running in the background(or docker desktop running).  


## Steps to run the Docker container
1. git clone 
```commandline
git clone https://github.com/she0930she/account-verify-api.git
```
2. use prefer IDE(Pycharm or VSCode) to open this package
```commandline
cd account-verify-api
```
3. If you are using Mac M1 chip, remember to have `platform: "linux/amd64"`
in the docker-compose.yml, other OS users needs to test on their own whether
need it or not
4. run docker-compose file using below command in the terminal
```commandline
docker compose up
```
5. You should see your containers are running (inside Docker Desktop *containers*). 
The container *account-verify-api* has 2 containers: *flask_db* and *flask_app*


## Please read API Document for further endpoint tests



- Some Docker commands
```commandline
docker login

** add a tag for the image **
docker tag image_name:_version_ she0930she/repo_name:tag_name
docker tag accountapi she0930she/accountVerifyAPI:v1.0

** push to DockerHub **
docker push she0930she/repo_name:tag_name
docker push she0930she/accountVerifyAPI:v1.0

** build and run docker-compose.yml **
docekr compose up 

** see all docker images **
docker images

** example: **
docker tag postgres:12 she0930she/accountapi:postgresql_db 
docker images
docker push she0930she/accountapi:postgresql_db
docker tag flask_live_app:1.0.0 she0930she/accountapi:flask_app
docker push she0930she/accountapi:flask_app
```