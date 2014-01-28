import string
from django import forms

class SurveyForm(forms.Form):
    email = forms.CharField(required=False)

    def __init__(self, fields, *args, **kwargs):
        super(SurveyForm, self).__init__(fields, *args, **kwargs)
        a_to_z = zip(list(string.ascii_lowercase), list(string.ascii_lowercase))
        for i in fields:
            val = fields.getlist(i)
            if len(val) > 1:
                self.fields[i] = forms.MultipleChoiceField(choices=a_to_z)
            else:
                self.fields[i] = forms.CharField()

        self.fields['email'] = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super(SurveyForm, self).clean()

        for name, field in self.fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                cleaned_data[name] = ','.join(cleaned_data[name])

        return cleaned_data
