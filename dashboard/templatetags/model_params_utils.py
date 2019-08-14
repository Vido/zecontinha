from django import template

register = template.Library()

@register.simple_tag
def get_param(obj, period, key, floatformat, *args, **kwargs):
    fformat = '%.' + '%d' % int(floatformat) + 'f'
    return fformat % obj.model_params[period][key]

# TODO, fazer class e CSS
@register.simple_tag
def color_adf(value, threshold):
    try:
        if value > threshold:
            return 'background-color:#e9bdba;'
        print(value, threshold, value > threshold)
    except (ValueError, TypeError) as e:
        print(e)

    return ''

@register.simple_tag
def color_zscore(value, threshold):
    try:
        if (value > threshold) or (value < -threshold):
            return 'background-color:#bde9ba;'
        print(value, threshold, (value > threshold) or (value < -threshold))
    except (ValueError, TypeError) as e:
        print(e)

    return ''

@register.simple_tag
def n_p_coint(obj, pvalue):
    return obj.n_p_coint(pvalue)