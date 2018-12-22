from __future__ import unicode_literals

from json import dumps

from django.template import Context, Library
from django.template.defaultfilters import truncatechars
from django.template.loader import get_template
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

import mayan
from mayan.apps.appearance.settings import setting_max_title_length

from ..classes import Collection
from ..literals import MESSAGE_SQLITE_WARNING
from ..utils import check_for_sqlite, resolve_attribute

register = Library()


@register.simple_tag
def check_sqlite():
    if check_for_sqlite():
        return MESSAGE_SQLITE_WARNING


@register.simple_tag
def get_collections():
    return Collection.get_all()


@register.filter
def get_encoded_parameter(item, parameters_dict):
    result = {}
    for key, value in parameters_dict.items():
        result[key] = resolve_attribute(obj=item, attribute=value)
    return dumps(result)


@register.filter
def get_type(value):
    return force_text(type(value))


@register.filter
def object_property(value, arg):
    return resolve_attribute(obj=value, attribute=arg)


@register.simple_tag
def project_information(attribute_name):
    return getattr(mayan, attribute_name)


@register.simple_tag(takes_context=True)
def render_subtemplate(context, template_name, template_context):
    """
    Renders the specified template with the mixed parent and
    subtemplate contexts
    """
    new_context = Context(context.flatten())
    new_context.update(Context(template_context))
    return get_template(template_name).render(new_context.flatten())


@register.simple_tag(takes_context=True)
def common_calculate_title(context):
    if context.get('title'):
        return truncatechars(
            value=context.get('title'), arg=setting_max_title_length.value
        )
    else:
        if context.get('delete_view'):
            return _('Confirm delete')
        else:
            if context.get('form'):
                if context.get('object'):
                    return _('Edit %s') % context.get('object')
                else:
                    return _('Confirm')
            else:
                if context.get('read_only'):
                    return _('Details for: %s') % context.get('object')
                else:
                    if context.get('object'):
                        return _('Edit: %s') % context.get('object')
                    else:
                        return _('Create')
