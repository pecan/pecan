from pecan.jsonify import jsonify, encode
from pecan import Pecan, expose
from webtest import TestApp
from simplejson import loads
import simplegeneric

class Person(object):
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
    
    @property
    def name(self):
        return '%s %s' % (self.first_name, self.last_name)
    
def test_simple_rule():    
    # create a Person instance
    p = Person('Jonathan', 'LaCour')
    
    # encode the object using the existing "default" rules
    result = loads(encode(p))
    assert result['first_name'] == 'Jonathan'
    assert result['last_name'] == 'LaCour'
    assert len(result) == 2
    
    # register a generic JSON rule
    @jsonify.when_type(Person)
    def jsonify_person(obj):
        return dict(
            name=obj.name
        )
    
    # encode the object using our new rule
    result = loads(encode(p))
    assert result['name'] == 'Jonathan LaCour'
    assert len(result) == 1


class TestJsonify(object):
    
    def test_simple_jsonify(self):    

        # register a generic JSON rule
        @jsonify.when_type(Person)
        def jsonify_person(obj):
            return dict(
                name=obj.name
            )
    

        class RootController(object):
            @expose('json')
            def index(self):
                # create a Person instance
                p = Person('Jonathan', 'LaCour')
                return p
            
        
        app = TestApp(Pecan(RootController()))


        r = app.get('/')
        assert r.status_int == 200
        assert loads(r.body) == {'name':'Jonathan LaCour'}
        