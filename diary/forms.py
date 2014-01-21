from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=200)
    agree = forms.BooleanField(required=True)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        agree = cleaned_data.get('agree')

        if not agree:
            msg = u"Please tick this box to agree with the terms and conditions and proceed with registration"
            self._errors["agree"] = self.error_class([msg])
        return cleaned_data
