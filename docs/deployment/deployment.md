## Deploying to Production

There are quite a few ways to deploy a FastAPI app to production. There is a
very good discussion about this on the FastAPI [Deployment
Guide](https://fastapi.tiangolo.com/deployment/) which covers using Uvicorn,
Gunicorn and Containers.

- My Personal preference is to serve with Gunicorn, using uvicorn workers behind
an Nginx proxy, though this does require you having your own server. There is a
pretty decent tutorial on this at
[Vultr](https://www.vultr.com/docs/how-to-deploy-fastapi-applications-with-gunicorn-and-nginx-on-ubuntu-20-04/).
- For deploying to AWS Lambda with API Gateway, there is a really excellent Medium
post (and it's followup)
[Here](https://medium.com/towards-data-science/fastapi-aws-robust-api-part-1-f67ae47390f9),
- For AWS Elastic Beanstalk there is a very comprehensive tutorial at
[testdriven.io](https://testdriven.io/blog/fastapi-elastic-beanstalk/)

> Remember:  you still need to set up a virtual environment, install all the
> dependencies, setup your `.env` file (or use Environment variables if your
> hosting provider uses these - for example Vercel or Heroku) and set up and
> migrate your Database, exactly the same as for Develpment as desctribed above.
