Django Gizmo
============
**Django app allowing for configurable targetting of template inclusion tags.**

Installation
------------

#. Add **gizmo** to your **INSTALLED APPS** setting.

#. Add ROOT_GIZMOCONF value to your projects settings file::
    
    ROOT_GIZMOCONF = 'project.gizmos'

#. Create your gizmos config file in the form::

    gizmos = (
        ('<loader name>', '<tag name>', '<slot name>'),
    )

With:

* <loader name> being the name you would normally pass to Django's load tag, i.e. **myapp_inclusion_tags** for **{% load myapp_icnlusion_tags %}**.
* <tag name> being the name of the tag you want to include, i.e. **advert** for **{% advert %}**
* <slot name> being the name of the slot you want the tag to show up in, i.e. **home_advert**.

#. Specify your gizmo conf file in your projects settings file:
    

Usage
-----

Gizmos are stock standard Django inclusion tags. The only diffirence is that instead of specifying tags within a template you specify tags from a distance by using a gizmo conf file in conjunction with the gizmos tag.

For example, lets say we have an **advert** tag specified in **myapp**'s inclusion tags which we only want to call  in gizmo slots named **home_advert**:

#. Create your tags as normal.

#. Create your gizmos config file in the form::
    gizmos = (
        ('myapp_inclusion_tag', 'advert', 'home_advert'),
    )

#. In your template load the gizmo inclusion tags and include a gizmos tag with a slot name of home_advert::

    {% load gizmo_inclusion_tags %}

    ...some html...

    {% gizmos 'home_advert' %}

    ...some more html...
