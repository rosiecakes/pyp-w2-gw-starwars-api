from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError
import json, requests

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        if isinstance(json_data, str):    #catch if json_data is still a string
            json_data = json.loads(json_data)
            
        for key, val in json_data.items():
            setattr(self, key, val)
        
            

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        if cls.RESOURCE_NAME == 'people':
            results = api_client.get_people(resource_id)  
        elif cls.RESOURCE_NAME == 'films':
            results = api_client.get_films(resource_id)
        else:
            raise SWAPIClientError()
        return cls(results)
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME == 'people':
            make_qs = PeopleQuerySet()            
        elif cls.RESOURCE_NAME == 'films':
            make_qs = FilmsQuerySet()
        else:
            raise SWAPIClientError() #not quite the right error
        return make_qs


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object): 

    def __init__(self):
        if self.RESOURCE_NAME == 'people':
            self.result = api_client.get_people()  
        elif self.RESOURCE_NAME == 'films':
            self.result = api_client.get_films()
        
        self.objects = self.count()

    def __iter__(self):
        #Make the initial request
        return self    
        

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        try:
            if self.RESOURCE_NAME == 'people':
                return People(self.result['results'].pop(0))
            elif self.RESOURCE_NAME == 'films':
                return Films(self.result['results'].pop(0))
        except:
            if not self.result['next']:
                raise StopIteration()
            else:
                self.result = requests.get(self.result['next'])
                if self.result.status_code == 200:
                    self.result = self.result.json()
                    if self.RESOURCE_NAME == 'people':
                        return People(self.result['results'].pop(0))
                    elif self.RESOURCE_NAME == 'films':
                        return Films(self.result['results'].pop(0))        #next item and if end of page next page
        

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.result['count']


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(self.objects))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(self.objects))
