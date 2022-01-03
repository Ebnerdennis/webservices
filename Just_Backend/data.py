import pandas as pd
import numpy as np
import uuid

new_uuid = uuid.uuid4()
users = [
    {
        "sex": "Mr",
        "firstName": "Yoshi",
        "lastName": "Süßigkeit",
        "address": "Dogstreet 1",
        "city": "Dogstown",
        "zipCode": 12345,
        "phoneNumber": 123456789,
        "email": "dog@dogs.de",
        "password": "dog123",
        "uuid": new_uuid
    },
    {
        "sex": "Ms",
        "firstName": "Madelaine",
        "lastName": "Kramer",
        "address": "Topsecetroad 5",
        "city": "Topsecret",
        "zipCode": 99999,
        "phoneNumber": 999999999,
        "email": "Madelaine@g.com",
        "password": "1%(22Ac!",
        "uuid": "bc1f4951-1e57-4000-9353-0c69030a8461"
    }
]


class Data:
    users_df = pd.DataFrame()
    users_df_uuid = pd.DataFrame()

    def __init__(self):
        df = pd.DataFrame.from_dict(users)

        df.reset_index(drop=True, inplace=True)

        self.users_df = df

        self.users_df_uuid = df

    def set_df(self, df):
        self.users_df = df

    def get_df(self):
        return self.users_df

    def set_df_uuid(self, df):
        self.users_df_uuid = df

    def get_df_uuid(self):
        return self.users_df_uuid
