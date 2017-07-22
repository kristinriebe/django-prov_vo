from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from provapp.models import Entity, RaveObsids


class ObservationIdForm(forms.Form):
    observation_id = forms.CharField(label='RAVE_OBS_ID',
                        max_length=1024,
                        help_text="e.g. 20030411_1507m23_001, 20121220_0752m38_089")    # An inline class to provide additional information on the form.
    #entity_list = Entity.objects.all()
    #observation_id = forms.ChoiceField(choices=[(x.id, x.label+" ("+x.type+")") for x in entity_list])

    detail_flag = forms.ChoiceField(
        label="Level of detail",
        choices=[('basic', 'basic'), ('detailed','detailed'), ('all', 'all')],
        widget=forms.RadioSelect(),
        help_text="basic: only entity-collections, detailed: exclude entity-collections, all: include entities and collections"
    )

    def clean_observation_id(self):
        desired_obs = self.cleaned_data['observation_id']
        queryset = RaveObsids.objects.filter(rave_obs_id=desired_obs)
        if not queryset.exists():
        #if desired_obs not in [e.label for e in self.entity_list]:
            raise ValidationError(
                _('Invalid value: %(value)s is not a valid RAVE_OBS_ID or it cannot be found.'),
                code='invalid',
                params={'value': desired_obs},
            )

        # always return the data!
        return desired_obs

class ProvDalForm(forms.Form):
    obj_id = forms.CharField(
        label='Entity or activity ID',
        max_length=1024,
        widget=forms.TextInput(attrs={'size':36}),
        help_text="Please enter the identifier for an entity (e.g. rave:20030411_1507m23_001 or rave:20121220_0752m38_089) or an activity (e.g. rave:act_irafReduction)",
    )

    step_flag = forms.ChoiceField(
        label="Step flag",
        choices=[('LAST', 'last'), ('ALL','all')],
        widget=forms.RadioSelect(),
        help_text="Specify if just one or all previous steps shall be retrieved",
        initial='ALL'
    )

    model = forms.ChoiceField(
        label="Data model",
        choices=[('IVOA','IVOA'), ('W3C', 'W3C')],
        widget=forms.RadioSelect(),
        help_text="Choose W3C for W3C Prov-DM compliant serialization",
        initial='IVOA'
    )

    format = forms.ChoiceField(
        label="Format",
        choices=[('PROV-N', 'PROV-N'), ('PROV-JSON','PROV-JSON'), ('GRAPH', 'Graphics')],
        widget=forms.RadioSelect(),
        help_text="Format of returned provenance record",
        initial='PROV-JSON'
    )
