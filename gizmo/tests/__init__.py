import unittest

from django import template
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.template import Template
from django.test import Client

from gizmo.templatetags import gizmo_inclusion_tags


class RequestFactory(Client):
    """
    Taken from DjangoSnippet 963, http://www.djangosnippets.org/snippets/963/

    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        request = WSGIRequest(environ)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            middleware_method(request)

        return request


class InclusionTagsTestCase(unittest.TestCase):
    def setUp(self):
        request = RequestFactory().request()
        self.context = template.Context({'request': request})

    def test_get_gizmos(self):
        from django.conf import settings
        node = gizmo_inclusion_tags.GizmosNode('bogus')
        request = self.context['request']

        #del settings.ROOT_URLCONF
        settings.ROOT_URLCONF = 'gizmo.tests.urls'

        # if no conf is provided return the empty list
        del settings.ROOT_GIZMOCONF
        gizmos = node.get_gizmos('slot_name', request)
        self.failUnlessEqual(gizmos, [])

        # if a conf is provided that does not contain gizmos, raise an error
        settings.ROOT_GIZMOCONF = 'gizmo.tests.empty_gizmos'
        self.failUnlessRaises(AttributeError, node.get_gizmos, 'slot_name', \
                request)

        # if a conf is provided that contains gizmos but not for the provided
        # slot, return the empty list
        settings.ROOT_GIZMOCONF = 'gizmo.tests.gizmos'
        gizmos = node.get_gizmos('bogus_slot_name', request)
        self.failUnlessEqual(gizmos, [])

        # if a conf is provided that contains gizmos for the provided
        # slot, return a list of gizmos matching the slot and current url
        # pattern name. Gizmos are only filtered by url name if a url name
        # is provided in the gizmo.
        settings.ROOT_GIZMOCONF = 'gizmo.tests.gizmos'
        gizmos = node.get_gizmos('slot_name', request)
        self.failIfEqual(gizmos, [])

        # are gizmos properly filtered by url name
        settings.ROOT_GIZMOCONF = 'gizmo.tests.gizmos'
        gizmos = node.get_gizmos('another_slot_name', request)
        self.failUnlessEqual(gizmos, [('gizmo_test_tags', 'test_simple_tag', \
                'another_slot_name', ['url_name'])])

    def test_gizmos_tag(self):
        # load gizmos tag without fail
        t = Template("{% load gizmo_inclusion_tags %}{% gizmos \
                'bogus_slot_name' %}")
        result = t.render(self.context)

        # if no gizmos are found for the slot return the empty string
        self.failUnlessEqual(result, '')

        # if gizmos are found for the slot return their results
        t = Template("{% load gizmo_inclusion_tags %}{% gizmos 'slot_name' %}")
        result = t.render(self.context)
        self.failUnlessEqual(result, u'test simple tag result')
