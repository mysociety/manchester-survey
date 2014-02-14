import string
from django import forms

class SurveyForm(forms.Form):
    email = forms.CharField(required=False)
    permission = forms.CharField(required=True)

    def __init__(self, fields, *args, **kwargs):
        super(SurveyForm, self).__init__(fields, *args, **kwargs)
        a_to_z = zip(list(string.ascii_lowercase), list(string.ascii_lowercase))
        field_list_15 = [ (field, field) for field in ( '15browsed', '15registered', '15joined', '15attended', '15promote', '15other', "15don't know")]
        field_list_16 = [ (field, field) for field in ('16browsed', '16registered', '16joined', '16attended', '16promote', '16other', "16 don't know") ]
        field_list_17 = [ (field, field) for field in (
            'party_information', 'party_joined', 'party_attended', 'party_voluntary', 'union_information', 'union_joined', 'union_attended', 'union_voluntary',
            'local_information', 'local_joined', 'local_attended', 'local_voluntary', 'ngo_information', 'ngo_joined', 'ngo_attended', 'ngo_voluntary',
            'religious_information', 'religious_joined', 'religious_attended', 'religious_voluntary', 'hobby_information', 'hobby_joined', 'hobby_attended',
            'hobby_voluntary', 'health_information', 'health_joined', 'health_attended', 'health_voluntary', 'other_information', 'other_joined', 'other_attended',
            'other_voluntary'
        )]
        field_list_28 = [ ( field, field) for field in ('blog', 'purchase', 'logged on', 'commented', 'multimedia', 'emailed', 'blog comment', '28 none')]
        for i in fields:
            if i == 'csrfmiddlewaretoken':
                continue
            val = fields.getlist(i)
            if len(val) > 1:
                self.fields[i] = forms.MultipleChoiceField(choices=a_to_z)
            else:
                self.fields[i] = forms.CharField(required=False)

        self.fields['15'] = forms.MultipleChoiceField(choices=field_list_15, required=False)
        self.fields['16'] = forms.MultipleChoiceField(choices=field_list_16, required=False)
        self.fields['17'] = forms.MultipleChoiceField(choices=field_list_17, required=False)
        self.fields['28'] = forms.MultipleChoiceField(choices=field_list_28, required=False)
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
