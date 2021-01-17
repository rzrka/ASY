from django import forms

class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item[0]
        data_list += '</datalist>'

        return (text_html + data_list)


class ListNumericWidget(forms.NumberInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListNumericWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListNumericWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item[0]
        data_list += '</datalist>'

        return (text_html + data_list)



class ScaleTranslateCreateWidget(forms.RadioSelect):
    LABEL_SIZE = 10
    def __init__(self, create_form, name, *args, **kwargs):
        super(ScaleTranslateCreateWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._form = create_form

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ScaleTranslateCreateWidget, self).render(name, value, attrs=attrs)
        render_data = '<ul class="input-scale-transform-list">'
        for field in self._form:
            render_data += "<li><span>{label}{point}:</span>{input}</li>".format(
                label = field.label[:self.LABEL_SIZE],
                point = ('.' if len(field.label)>self.LABEL_SIZE else ''),
                input = field.__str__(),
            )
        render_data += '</ul>'
        return (text_html + render_data)


class GeneralCriterions_link(forms.CheckboxInput):
    def __init__(self, old_form, href, *args, **kwargs):
        super(GeneralCriterions_link, self).__init__(*args, **kwargs)
        self._old_form = old_form
        self._href = href

    def render(self, name, value, attrs=None, renderer=None):
        text_html = self._old_form.render(name, value, attrs=attrs)
        render_data = '<a class="simple-link td-simple-link" href="' + self._href + '">Перейти к критериям</a>'
        return (text_html + render_data)
