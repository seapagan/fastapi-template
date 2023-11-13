# Deployment

## Deploying to Production

There are quite a few ways to deploy a FastAPI app to production. There is a
very good discussion about this on the FastAPI [Deployment
Guide][fastapi-deployment]{: target="_blank"} which covers
using Uvicorn, Gunicorn and Containers.

!!! info "Remember"
    Whichever method you choose, you still need to set up a virtual environment,
    install all the dependencies, setup your `.env` file (or use Environment
    variables if your hosting provider uses these - for example Vercel or Heroku)
    and set up and migrate your Database, exactly the same as for Development as
    desctribed previously.

### Nginx

My Personal preference is to serve with Gunicorn, using uvicorn workers behind
an Nginx proxy, though this does require you having your own server. There is a
pretty decent tutorial on this at [Vultr][vultr]{: target="_blank"}.

### AWS Lambda

For deploying to AWS Lambda with API Gateway, there is a really excellent
Medium post (and it's followup) [Here][medium]{: target="_blank"}

### AWS Elastic Beanstalk

For AWS Elastic Beanstalk there is a very comprehensive tutorial at
[testdriven.io][testdriven]{: target="_blank"}

### Docker Container

Deploy a Docker container or Kubernetes cluster. There are many services which
allow this including AWS, Google Cloud and more. See [Develop with
Docker](../development/docker.md) in this documentation for how to containerize
this project, and the
[Offical FastAPI docs section][fastapi-docker]{: target="_blank"}
for more information.

[vultr]:  https://www.vultr.com/docs/how-to-deploy-fastapi-applications-with-gunicorn-and-nginx-on-ubuntu-20-04/
[medium]: https://medium.com/towards-data-science/fastapi-aws-robust-api-part-1-f67ae47390f9
[testdriven]: https://testdriven.io/blog/fastapi-elastic-beanstalk/
[fastapi-docker]: https://fastapi.tiangolo.com/deployment/docker/
[fastapi-deployment]: https://fastapi.tiangolo.com/deployment/
