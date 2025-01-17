import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import *

from App.main import create_app
from App.database import create_db,db
from App.models import  Author, Publication
from App.controllers import (
    create_author,
    create_publication,
    get_publication_by_title,
    get_publications_by_field,
    get_publication,
    authenticate,
    get_author_by_id,
    get_author_by_name,
    get_all_authors,
    add_authors_to_publication,
    author_publication_tree
)

from wsgi import app


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class AuthorUnitTests(unittest.TestCase):

    def test_new_author(self):
        author = Author("John","Doe","JohnDoe@mail.com","bobpass")
        assert author.first_name == "John" and author.last_name == "Doe" and author.email == "JohnDoe@mail.com"
    
    def test_author_toDict(self):
        author = Author("John","Doe","JohnDoe@mail.com","bobpass")
        author_json = author.toDict()
        self.assertDictEqual(author_json, {
            'id': None,
            'first_name': "John",
            'last_name': "Doe",
            'email': "JohnDoe@mail.com"
        })
    
    def test_password(self):
        author = Author("John","Doe","JohnDoe@mail.com","bobpass")
        self.assertNotEqual("bobpass",author.password)



class PublicationUnitTests(unittest.TestCase):
    def test_new_publication(self):
        authors = []
        publication = Publication("test", "comp", "10/10/10")
        self.assertTrue("test" == publication.title and publication.field == "comp" and publication.publication_date == "10/10/10")

    def test_publication_toDict(self):
        publication = Publication("Intro to Computer Science", "comp", "10/10/10")
        publication_json = publication.toDict()
        self.assertDictEqual(publication_json, {
            "id": None,
            "title": "Intro to Computer Science",
            "field": "comp",
            "publication_date": "10/10/10"
        })

'''
    Integration Tests
'''
# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app.config.update({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db(app)
    yield app.test_client()
    os.unlink(os.getcwd()+'/App/test.db')


def test_authenticate():
    author = create_author("John","Black","JohnBlack@mail.com","bobpass")
    assert authenticate("JohnBlack@mail.com", "bobpass") != None

class AuthorIntegrationTests(unittest.TestCase):

    def test_create_author(self):
        author = create_author("John","Doe","JohnDoe@mail.com","bobpass")
        self.assertIsNotNone(Author.query.filter_by(email="JohnDoe@mail.com").first())

    def test_get_author_by_id(self):
        author = get_author_by_id(1)
        self.assertIsNotNone(author)

    def test_get_author_by_name(self):
        author = get_author_by_name("John","Doe")
        self.assertIsNotNone(author)

    def test_get_author_publications(self):
        author = get_author_by_name("John","Doe")
        publications = author.getPublications()
        self.assertEquals([], publications)


    
class PublicationIntegrationTests(unittest.TestCase):

    def test_create_publication(self):
        date = datetime.now()
        publication = create_publication("tests", "comp", date)
        self.assertIsNotNone(publication)

    def test_get_publication_by_title(self):
        publication =  get_publication_by_title("tests")
        self.assertIsNotNone(publication)

    def test_get_publication_by_id(self):
        publication = get_publication(1)
        self.assertIsNotNone(publication)
    
    def test_get_publications_by_field(self):
        publication = get_publications_by_field("comp")
        self.assertFalse(publication==None)

    def test_get_publication_tree(self):
        date = datetime.now()
        test_publication1 = create_publication("test1", "testing", date)
        test_publication2 = create_publication("test2", "testing", date)
        authors = [
            {
                "first_name":"John",
                "last_name":"Smith",
                "email":"johnsmith@mail.com"
            },
            {
                "first_name":"John",
                "last_name" :"Lennon",
                "email":"johnlennon@mail.com"
            }
        ]
        add_authors_to_publication(test_publication1.id, authors)
        add_authors_to_publication(test_publication2.id, [authors[1]])
        author = get_author_by_name("John", "Lennon")
        root, authors, publications = author_publication_tree(author.id)
        self.assertTrue(publications[0] == test_publication1 and publications[1] == test_publication2)