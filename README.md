
## This is an account management RESTful APIs in docker containers
I used flask in python, SQLAlchemy(ORM) and Postgresql as a database.  

---

### Prerequisite
- Make sure you have docker running in the background(or docker desktop running).  

---

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
4. run docker-compose file
```commandline
docker compose up
```
5. You should see your containers are running (inside Docker Desktop *containers*), 
inside container *account-verify-api* has 2 containers: *flask_db* and *flask_app*

---

# API Document




1. Check if docker endpoint is working, you should see 
``{"message": "test route"}``
```commandline
http://localhost:4000/testhealth
```
2. Create Account endpoint
```commandline
http://localhost:4000/createuser
```
Payload
```{
    "username":"Oneo@gmail.com",
    "password":"Aa12345678"
}
```
The return you should expect to see, and `status_code 201`
```
[
    {
        "message": "user created"
    },
    {
        "success": true
    },
    {
        "account_created": "Mon, 05 Aug 2024 17:47:58 GMT",
        "password": "$2b$12$6C2dkMj3iZ92Aw9ivGgplOqmlm9UBHV7m1AHlNccB9ICzIuoaKUrC",
        "username": "Oneo@gmail.com"
    }
]
```
3. Verify Account
```commandline
http://localhost:4000/v1/login
```
Payload
```
{
    "username":"jenny@gmail.com",
    "password":"Aa12345678"
}
```
The return you should expect to see, and `status_code 201`
```
[
    {
        "reason": "Login successful"
    },
    {
        "success": true
    }
]
```



docker build -t accountapi .
docker tag accountapi she0930she/accountVerifyAPI:v1.0

docker login
docker push she0930she/accountVerifyAPI:v1.0

sudo yum install tree
tree .

-docker-compose build
sudo curl
sudo chmod
docker-compose build

-run docker compose image
docker-compose up


# push to dockerHub
docker image ls
-add tag
docker tag image_name:_version_ she0930she/repo_name:tag_name
docker push she0930she/repo_name:tag_name

example:
docker tag postgres:12 she0930she/accountapi:postgresqldb 
docker images
docker push she0930she/accountapi:postgresqldb
docker tag flask_live_app:1.0.0 she0930she/accountapi:flask_app
docker push she0930she/accountapi:flask_app

