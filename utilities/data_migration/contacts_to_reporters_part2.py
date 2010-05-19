#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

11/29/09 The following script is used to trim redundant fields
from contacts and to link it to reporters properly

"""
from django.db import connection
from django.db import transaction

@transaction.commit_manually
def run():
    """ Upgrade contacts to be consistent with latest db """
    cursor = connection.cursor()
    # set reporter_id to be required
    
    from smsforum.models import Village, Community
    communities = Community.objects.all()
    for c in communities:
        print "INSERT INTO `smsforum_village` VALUES (%d);" % c.pk
        print c.name
        cursor.execute("INSERT INTO `smsforum_village` VALUES (%d);" % c.pk)
        print "Village %s created" % c.name
    print "done"
    transaction.commit()

