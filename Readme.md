# running the application

navigate to the project folder

run command docker-compose up --build

# performing the task

    by default

    it will run in port 8000

if you run in local-server api-endpoint will be
http://localhost:8000/api/v1/web-scrap/

sample_token = 45375db1d21d9f099da95b7461b3be1df87f06ea

# Api Endpoint to start scrap website

    requesty method = post
    endpoint = yourdomain/api/v1/web-scrap/
    request body = {"website":"website.com"}

# Api Endpoint to get scrapped data-collection

    request method = get
    endpoint is dynamic as per your request querry parameter
    endpoint prefix = yourdomain/api/v1/get-collection/
    query parameter followed by ===> ?id=YOUR-REQUIRED-URL-STRING-HERE

    sample = yourdomain/api/v1/get-collection/?id=https://cannolive.fr/huile-dolive-fruitee/110-1l-huile-d-olive-vierge-extra-fruitee.html
    

