from django import template
from django.conf import settings
from django.template import Template

register = template.Library()

def get_gizmos_by_slot(slot):
    """
    Returns a list of slots for the given slot as configured in a gizmos variable specified in a module 
    pointed to by settings.ROOT_GIZMOCONF.

    For example in project.gizmos (with settings.ROOT_GIZMOCONF = 'project.gizmos':
    
        gizmos = (
            ('loader_name', 'tag_name', 'slot_name'),
        )
    """

    slot_gizmos = []
    try:
        gizmo_conf = __import__(settings.ROOT_GIZMOCONF, globals(), locals(), ['gizmos', ], -1)
    except AttributeError:
        return slot_gizmos

    gizmos = gizmo_conf.gizmos

    for gizmo in gizmos:
        if gizmo[2] == slot:
            slot_gizmos.append(gizmo)

    return slot_gizmos

@register.simple_tag
def gizmos(slot):
    """
    TODO: Fail silently
    """
    gizmos = get_gizmos_by_slot(slot)
    load_string = "".join(["{%% load %s %%}" % gizmo[0] for gizmo in gizmos])
    tag_string = "".join(["{%% %s %%}" % gizmo[1] for gizmo in gizmos])

    t = Template("%s%s" % (load_string, tag_string))
    context = template.Context({})
    return t.render(context)
