from unittest import TestCase
from app.tests.models.test_models import TestGroup, TestUser, TestProject
from app.models.project import ProjectNotEmpty, InvalidOwner
from time import sleep
from pymongo.errors import DuplicateKeyError

TEST_PROJECT_NAME = "testCase.my_unique_test_project"
TEST_GROUP_NAME = "testCase.my_unique_test_group"


class TestProjectModel(TestCase):

    @classmethod
    def setUpClass(cls):
        TestProject.destroy_all()
        TestProject.ensure_indexes()
        TestGroup.destroy_all()
        TestGroup.ensure_indexes()
        TestUser.destroy_all()
        TestUser.ensure_indexes()
        cls.owner = TestUser(username='viert', password_hash='hash')
        cls.owner.save()
        TestProject.ensure_indexes()

    @classmethod
    def tearDownClass(cls):
        cls.owner.destroy()

    def setUp(self):
        TestGroup.destroy_all()
        p = TestProject.find_one({ "name": TEST_PROJECT_NAME })
        if p is not None:
            p.destroy()

    def tearDown(self):
        TestGroup.destroy_all()
        p = TestProject.find_one({ "name": TEST_PROJECT_NAME })
        if p is not None:
            p.destroy()

    def test_unique_index(self):
        p = TestProject(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        p = TestProject(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        self.assertRaises(DuplicateKeyError, p.save)

    def test_touch_on_save(self):
        p = TestProject(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        dt1 = p.updated_at
        sleep(1)
        p.save()
        dt2 = p.updated_at
        self.assertNotEqual(dt1, dt2, msg="updated_at not changed while saving Project")

    def test_delete_non_empty(self):
        p = TestProject(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        g = TestGroup(name=TEST_GROUP_NAME, project_id=p._id)
        g.save()
        self.assertRaises(ProjectNotEmpty, p.destroy)
        g.destroy()
        p.destroy()

    def test_owner(self):
        p = TestProject(name="TEST_PROJECT_NAME", owner_id="arbitrary")
        self.assertRaises(InvalidOwner, p.save)
