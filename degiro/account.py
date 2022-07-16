from datetime import datetime
import degiroapi

class Account(degiroapi.DeGiro):
    def __init__(self,username,password):
        super().__init__()
        self.login(username, password)

    @property
    def first_name(self):
        return self.client_info.first_name
    @property
    def last_name(self):
        return self.client_info.last_name
    @property
    def name(self):
        return self.first_name + " " + self.last_name
    @property
    def email(self):
        return self.client_info.email
    def __str__(self):
        print(f"<Degiro Account of {self.name}>")
    def __repr__(self):
        print(f"<Degiro Account of {self.name} logged in on {datetime.now()}>")




