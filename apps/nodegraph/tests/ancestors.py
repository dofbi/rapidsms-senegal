from rapidsms.tests.scripted import TestScript
from app import App
import apps.nodegraph.app as nodegraph_app
from apps.nodegraph.models import Node, NodeSet
from nodegraph.util import *
from util import *

class TestAncestors (Scaffolding, TestScript):
    apps = (App, nodegraph_app.App)
    
    def setUp(self):
        TestScript.setUp(self)
            
        # make some nodes and graphs
        # imagine this is users and groups for clarity
        self.m_nodes = [user(n) for n in self.m_names]
        self.w_nodes = [user(n) for n in self.w_names]
        self.girl_nodes = [user(n) for n in self.girl_names]
        self.boy_nodes = [user(n) for n in self.boy_names]
        self.m_group = group('men',*self.m_nodes)
        self.w_group = group('women',*self.w_nodes)
        self.g_group = group('girls',*self.girl_nodes)
        self.g_group.add_to_parent(self.w_group)
        self.b_group = group('boys',*self.boy_nodes)
        self.b_group.add_to_parent(self.m_group)

        self.people_group = group('people', self.m_group, self.w_group)

        # set up Cyclic(A(B(*A,woman),man))
        self.cyc_a=group('a',self.m_nodes[0])
        self.cyc_b=group('b',self.cyc_a,self.w_nodes[0])
        self.cyc_a.add_children(self.cyc_b)
        self.cyclic_group=group('cyclic',self.cyc_a)
               
        # simple tree 
        self.leaf1=user('leaf1')
        self.leaf2=user('leaf2')
        self.simple_tree=group('tree', group('L1',group('L2',self.leaf1, group('L3',self.leaf2))))
        
        self.all_groups = [
                        self.simple_tree,
                        self.cyclic_group,
                        self.cyc_a,
                        self.cyc_b,
                        self.people_group,
                        self.b_group,
                        self.g_group,
                        self.m_group,
                        self.w_group
                        ]
        
    def tearDown(self):
        all_nodes=set()
        for g in self.all_groups:
            all_nodes.update(g.flatten())
        for n in all_nodes:
            n.delete()
            
        for g in self.all_groups:
            g.delete()

    def testAncestorDepth(self):
        print
        print "TEST ANCESTOR COUNT"
        depth = self.boy_nodes[0].get_depth()
        self.assertTrue(depth == 3)
