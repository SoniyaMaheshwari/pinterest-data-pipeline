import datetime
import json
import requests
import random
import sqlalchemy
from time import sleep
import yaml

random.seed(100)

class AWSDBConnector:

    def __init__(self):
        self.creds={}

    def read_db_creds(self):
        """
        Returns the database credentials from the yaml file
        """
        with open('creds.yaml') as yaml_file:
            self.creds = yaml.safe_load(yaml_file)
        return self.creds

        
    def create_db_connector(self):
        """
        creates and returns database engine using credentials from yaml file 
        """
        config=self.read_db_creds()
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['DATABASE']}?charset=utf8mb4")
        return engine

def datetime_converter(date_time):
    """
    Converts datetime to string

    Paramenter: 
    date_time : datetime
    """
    if isinstance(date_time, datetime.datetime):
        return date_time.__str__()

def run_infinite_post_data_loop():
    """
    Creates a connection to the database to emulate row data that is generated randomly into AWS S3
    """
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()
        headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
       
        with engine.connect() as connection:
            tablenames_topics = {'pinterest_data':'0a70d64d47bd.pin', 'geolocation_data':'0a70d64d47bd.geo', 'user_data':'0a70d64d47bd.user'}
            for table_name, topic in tablenames_topics.items():
                sql_string = sqlalchemy.text(f"SELECT * FROM {table_name} LIMIT {random_row}, 1")
                selected_row = connection.execute(sql_string)
                invoke_url = f"https://0elc7pj8qe.execute-api.us-east-1.amazonaws.com/testing/topics/{topic}"
                for row in selected_row:
                    result = dict(row._mapping)
                    payload = json.dumps({"records": [{ "value": result}]}, default=datetime_converter)
                    response = requests.request("POST", invoke_url, headers=headers, data=payload)
                    print(response.status_code)

new_connector = AWSDBConnector()
if __name__ == "__main__":
    run_infinite_post_data_loop()
    
