import unittest

from django.conf import settings
from django import template
from django.template import Template
        
from gizmo.templatetags import gizmo_inclusion_tags

class InclusionTagsTestCase(unittest.TestCase):
    def setUp(self):
        self.context = template.Context({})

    def test_get_gizmos_by_slot(self):
        # if no conf is provided return the empty list
        del settings.ROOT_GIZMOCONF
        gizmos = gizmo_inclusion_tags.get_gizmos_by_slot('slot_name')
        self.failUnlessEqual(gizmos, [])

        # if a conf is provided that does not contain gizmos, raise an error
        settings.ROOT_GIZMOCONF = 'gizmo.tests.empty_gizmos'
        self.failUnlessRaises(AttributeError, gizmo_inclusion_tags.get_gizmos_by_slot, 'slot_name')

        # if a conf is provided that contains gizmos but not for the provided slot, return the empty list
        settings.ROOT_GIZMOCONF = 'gizmo.tests.gizmos'
        gizmos = gizmo_inclusion_tags.get_gizmos_by_slot('bogus_slot_name')
        self.failUnlessEqual(gizmos, [])
        
        # if a conf is provided that contains gizmos for the provided slot, return a list of slots
        settings.ROOT_GIZMOCONF = 'gizmo.tests.gizmos'
        gizmos = gizmo_inclusion_tags.get_gizmos_by_slot('slot_name')
        self.failIfEqual(gizmos, [])

    def test_gizmos_tag(self):
        # load gizmos tag without fail
        t = Template("{% load gizmo_inclusion_tags %}{% gizmos 'bogus_slot_name' %}")
        result = t.render(self.context)

        # if no gizmos are found for the slot return the empty string
        self.failUnlessEqual(result, '')
        
        # if gizmos are found for the slot return their results
        t = Template("{% load gizmo_inclusion_tags %}{% gizmos 'slot_name' %}")
        result = t.render(self.context)
        self.failUnlessEqual(result, u'test simple tag result')
