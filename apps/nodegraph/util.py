"""
These utilities are actually all for the unit tests
But because we are declaring models, django complains
if we put this in the tests/ directory

"""
from apps.nodegraph.models import Node, NodeSet

class Person(Node):
    @property
    def who_am_i(self):
        return 'Person'

class Parent(Person):
    @property
    def who_am_i(self):
        return 'Parent'

class Family(NodeSet):
    @property
    def who_am_i(self):
        return 'Family'
    