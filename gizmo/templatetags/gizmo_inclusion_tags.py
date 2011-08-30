from django import template
from django.conf import settings
from django.core import urlresolvers
from django.core.urlresolvers import RegexURLResolver, Resolver404
from django.template import Template
from django.utils.encoding import smart_str

register = template.Library()


@register.tag
def gizmos(parser, token):
    """
    Outputs set of inclusion tags found by path and slot.
    TODO: Fail silently
    """
    try:
        tag_name, slot_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('filter_menu tag requires 1 \
                argument (slot_name), %s given' % \
                (len(token.split_contents()) - 1))
    return GizmosNode(slot_name)


class GizmosNode(template.Node):
    def __init__(self, slot_name):
        self.slot_name = template.Variable(slot_name)

    def resolve_pattern_name(self, resolver, path):
        tried = []
        match = resolver.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in resolver.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([(pattern.regex.pattern + '   ' + t) \
                                for t in sub_tried])
                    else:
                        tried.append(pattern.regex.pattern)
                else:
                    if sub_match:
                        sub_match_dict = dict([(smart_str(k), v) for k, v in \
                                match.groupdict().items()])
                        sub_match_dict.update(resolver.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[smart_str(k)] = v
                        try:
                            return pattern.name
                        except AttributeError:
                            return self.resolve_pattern_name(pattern, new_path)
                    tried.append(pattern.regex.pattern)
            raise Resolver404, {'tried': tried, 'path': new_path}
        raise Resolver404, {'path': path}

    def get_gizmos(self, slot_name, request):
        """
        Returns a list of slots for the given slot as configured in a gizmos \
                variable specified in a module
        pointed to by settings.ROOT_GIZMOCONF.

        For example in project.gizmos (with settings.ROOT_GIZMOCONF = \
                'project.gizmos'):

            gizmos = (
                ('loader_name', 'tag_name', 'slot_name', 'url_name'),
            )
        """
        slot_gizmos = []
        try:
            gizmo_conf = __import__(settings.ROOT_GIZMOCONF, globals(), \
                    locals(), ['gizmos', ], -1)
        except AttributeError:
            return slot_gizmos

        gizmos = gizmo_conf.gizmos

        for gizmo in gizmos:
            if gizmo[2] == slot_name:
                try:
                    gizmo_url_names = gizmo[3]
                    urlconf = getattr(request, "urlconf", \
                            settings.ROOT_URLCONF)
                    resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
                    try:
                        url_name = self.resolve_pattern_name(resolver, \
                                request.path)
                    except Resolver404:
                        url_name = None
                    if url_name:
                        if url_name in gizmo_url_names:
                            slot_gizmos.append(gizmo)
                except IndexError:
                    slot_gizmos.append(gizmo)

        return slot_gizmos

    def render(self, context):
        slot_name = self.slot_name.resolve(context)
        request = context['request']

        gizmos = self.get_gizmos(slot_name, request)

        load_string = "".join(["{%% load %s %%}" % gizmo[0] for gizmo in \
                gizmos])
        tag_string = "".join(["{%% %s %%}" % gizmo[1] for gizmo in gizmos])

        t = Template("%s%s" % (load_string, tag_string))

        context.update({'gizmo_slot_name': slot_name})
        return t.render(context)
