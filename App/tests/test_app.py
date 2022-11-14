import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import *

from App.main import create_app
from App.database import create_db
from App.models import User, Author, Publication
from App.controllers import (
    create_user,
    get_all_users_json,
    authenticate,
    get_user,
    get_user_by_username,
    update_user
)

from wsgi import app


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    def test_user_toJSON(self):
        user = User("bob", "bobpass")
        user_json = user.toJSON()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)

class AuthorUnitTests(unittest.TestCase):

    def test_new_author(self):
        author = Author("Bob Moog", "05/08/2001", "BSc. Computer Science")
        assert author.name == "Bob Moog" and author.dob == datetime.strptime("05/08/2001", "%d/%m/%Y") and author.qualifications == "BSc. Computer Science"

    def test_author_toJSON(self):
        author = Author("Bob Moog", "05/08/2001", "BSc. Computer Science")
        author_json = author.toJSON()
        self.assertDictEqual(author_json, {
            "id": None,
            "name": "Bob Moog",
            "dob": datetime.strptime("05/08/2001", "%d/%m/%Y"),
            "qualifications": "BSc. Computer Science"
        })

    # def test_get_author_publications(self):
    #     # create author, create publication for that author, call author.get_publications
    #     authors = []
    #     author = Author("Bob Moog", "05/08/2001", "BSc. Computer Science")
    #     authors.append(author)
    #     publication = Publication("Intro to Computer Science", authors, [])
    #     author_publications = author.get_publications()
    #     # assert true if equal
    #     self.assertDictEqual(author_publications.pop(), publication.toJSON())

class PublicationUnitTests(unittest.TestCase):
    def test_new_publication(self):
        authors = []
        coauthors = []
        author = Author("Bob Moog", "05/08/2001", "BSc. Computer Science")
        authors.append(author)
        coauthor = Author("Bob Dule", "06/09/2002", "BSc. Computer Engineering")
        coauthors.append(coauthor)
        publication = Publication("Intro to Computer Science", authors, coauthors)
        assert (
            publication.title=="Intro to Computer Science" 
            and publication.authors==authors 
            and publication.coauthors==coauthors
        )

    def test_publication_toJSON(self):
        authors = []
        coauthors = []
        author = Author("Bob Moog", "05/08/2001", "BSc. Computer Science")
        authors.append(author)
        coauthor = Author("Bob Dule", "06/09/2002", "BSc. Computer Engineering")
        coauthors.append(coauthor)
        publication = Publication("Intro to Computer Science", authors, coauthors)
        publication_json = publication.toJSON()
        self.assertDictEqual(publication_json, {
            "id": None,
            "title": "Intro to Computer Science",
            "authors": [author.toJSON() for author in authors],
            "coauthors": [coauthor.toJSON() for coauthor in coauthors]
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
    user = create_user("Bob Moog", "bobpass")
    assert authenticate("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_author(self):
        author = create_user("Bob Moog", "05/08/2001", "BSc. Computer Science")
        assert author.name == "Bob Moog"

    def test_create_publication(self):
        publication=create_publication([{"title":"Intro to Computer Science"},{"authors":[author.toJSON() for author in authors]},{"coauthors":[coauthor.toJSON() for coauthor in coauthors]}])
        assert publication.title=="Intro to Computer Science"

    def test_get_author_json(self):
        author_json=get_author_json()
        self.assertListEqual([{"name": "Bob Moog"},{"dob":"05/08/2001"},{"qualifications":"BSc. Computer Engineering"}], author_json)


    def test_get_publication_json(self):
        publication_json= get_publication_json()
        self.assertListEqual([{"title":"Intro to Computer Science"},{"authors":[author.toJSON() for author in authors]},{"coauthors":[coauthor.toJSON() for coauthor in coauthors]}])

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
