from locust import HttpUser, task, between

# Loading the test JSON data


'''data = {
    "website": "https://www.gustiitaliani.com/boutique/vins-et-alcool/dolcetto-dalba-doc-2018-cantina-filippino-domenico-piemont/"}'''
data = {
    "get_list": "https://www.gustiitaliani.com/boutique/vins-et-alcool/dolcetto-dalba-doc-2018-cantina-filippino-domenico-piemont/"}

auth_header = {'content-type': 'application/json',
               'Authorization': 'Token 45375db1d21d9f099da95b7461b3be1df87f06ea'}


# Creating an API User class inheriting from Locust's HttpUser class
class APIUser(HttpUser):
    # Setting the host name and wait_time
    wait_time = between(3, 5)

    # Defining the post task using the JSON test data
    '''@task()
    def predict_endpoint(self):
        self.client.post('/api/v1/web-scrap/', json=data, headers=auth_header)'''

    @task()
    def predict_endpoint(self):
        self.client.get('/api/v1/get-collection/', json=data, headers=auth_header)
