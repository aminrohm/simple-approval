from django import template

register = template.Library()

@register.simple_tag
def textify_status(value):
    text=""
    if value==0:
        text="CANCELLED"
    if value==1:
        text="CREATED"
    if value==2:
        text="REVISED"
    if value==3:
        text="CHECKED"
    if value==4:
        text="RETURNED"
    if value==5:
        text="APPROVED"
    return text

#@register.filter
#def textify_status(value):
#    return '%sxx' % value

#register.filter('textify_status', textify_status)
register.simple_tag(name='textify_status')
