import string
from django import forms

class SurveyForm(forms.Form):
    email = forms.CharField(required=False)
    permission = forms.CharField(required=True)

    def __init__(self, fields, *args, **kwargs):
        super(SurveyForm, self).__init__(fields, *args, **kwargs)
        a_to_z = zip(list(string.ascii_lowercase), list(string.ascii_lowercase))
        for i in fields:
            if i == 'csrfmiddlewaretoken':
                continue
            val = fields.getlist(i)
            if len(val) > 1:
                self.fields[i] = forms.MultipleChoiceField(choices=a_to_z)
            else:
                self.fields[i] = forms.CharField(required=False)

        self.fields['email'] = forms.EmailField(required=False)
        self.fields['permission'].required = True

    def clean(self):
        cleaned_data = super(SurveyForm, self).clean()

        perm_msg = 'Please agree to the terms and conditions before taking part'
        if 'permission' not in cleaned_data or cleaned_data['permission'] == 'No':
            self._errors['permission'] = self.error_class([perm_msg])

        for name, field in self.fields.items():
            if name in cleaned_data:
                if isinstance(field, forms.MultipleChoiceField):
                    cleaned_data[name] = ','.join(cleaned_data[name])

                if cleaned_data[name] == '':
                    del cleaned_data[name]

        return cleaned_data
