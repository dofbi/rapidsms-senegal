from apps.nodegraph.models import Node, NodeSet

# helpers
def user(name, *grps):
    u=Node(debug_id=name)
    u.save()
    for grp in grps:
        u.add_to_parent(grp)

    return u

def group(name, *children):
    g=NodeSet(debug_id=name)
    g.save()
    g.add_children(*children)
    return g

class Scaffolding(object):
    m_nodes=None
    w_nodes=None
    m_group=None
    w_group=None
    people_group=None
    
    m_names = ['matt','larry','jim','joe','mohammed']
    w_names = ['jen','julie','mary','fatou','sue']
    girl_names = ['jennie','susie']
    boy_names = ['johnny', 'jimmie']
    