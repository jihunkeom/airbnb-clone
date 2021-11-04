from django import template

register = template.Library()


@register.filter
def sexy_capitals(value):  # html에서 filter 적용시킨 값이 value인자로 넘어온다!!
    print(value)
    return "lalalala"
