from django import template

register = template.Library()


def _query(context):
    return context["request"].GET.copy()


def _url(context, query):
    baza = context.get("url_lista") or context["request"].path
    sir = query.urlencode()
    return f"{baza}?{sir}" if sir else baza


@register.simple_tag(takes_context=True)
def url_cu(context, **parametri):
    query = _query(context)
    query.pop("pagina", None)
    for nume, valoare in parametri.items():
        if valoare is None or valoare == "":
            query.pop(nume, None)
        else:
            query[nume] = valoare
    return _url(context, query)


@register.simple_tag(takes_context=True)
def url_pagina(context, numar):
    query = _query(context)
    query["pagina"] = numar
    return _url(context, query)


@register.simple_tag(takes_context=True)
def url_adauga_tag(context, tag):
    query = _query(context)
    query.pop("pagina", None)
    taguri = query.getlist("tag")
    if tag not in taguri:
        taguri.append(tag)
    query.setlist("tag", taguri)
    return _url(context, query)


@register.simple_tag(takes_context=True)
def url_elimina_tag(context, tag):
    query = _query(context)
    query.pop("pagina", None)
    taguri = [t for t in query.getlist("tag") if t != tag]
    query.setlist("tag", taguri)
    return _url(context, query)
