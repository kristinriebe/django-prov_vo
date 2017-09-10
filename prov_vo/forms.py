from django import forms
from django.conf import settings
from django.utils.translation import gettext as _
from prov_vo.models import Entity


class ProvDalForm(forms.Form):

    obj_id = forms.CharField(
        label='Identifier',
        max_length=1024,
        widget=forms.TextInput(attrs={'size':36}),
        help_text="Please enter the ID for an entity, activity or agent"
    )

    depth = forms.ChoiceField(
        label="Depth",
        choices=[('1', '1'), ('2', '2'), ('3','3'), ('4', '4'), ('5', '5'), ('0', '0'), ('ALL','all')],
        widget=forms.Select(),
        help_text="Specify number of relations to be tracked",
        initial='1'
    )
    direction = forms.ChoiceField(
        label="Direction",
        choices=[('BACK', 'back'), ('FORTH','forth')],
        widget=forms.RadioSelect(),
        help_text="Choose the tracking direction",
        initial='BACK'
    )

    model = forms.ChoiceField(
        label="Data model",
        choices=[('IVOA','IVOA'), ('W3C', 'W3C')],
        widget=forms.RadioSelect(),
        help_text="Choose W3C for W3C Prov-DM compliant serialization",
        initial='IVOA'
    )

    format = forms.ChoiceField(
        label="Response format",
        choices=[('PROV-N', 'PROV-N'), ('PROV-JSON','PROV-JSON'), ('GRAPH', 'Graphics')],
        widget=forms.RadioSelect(),
        help_text="Format of returned provenance record",
        initial='PROV-JSON'
    )

    members = forms.BooleanField(
        label="Members",
        widget=forms.CheckboxInput(),
        #choices=[('1', '1'), ('ALL','all')],
        help_text="Also find and track members of collections",
        initial=False,
        required=False
        #default=False
    )

    steps = forms.BooleanField(
        label="Activity steps",
        widget=forms.CheckboxInput(),
        help_text="Also find and track steps of activityFlows",
        initial=False,
        required=False
    )

    agent = forms.BooleanField(
        label="Agent",
        widget=forms.CheckboxInput(),
        help_text="Also find and track other entities and activities that the found agents are responsible for",
        initial=False,
        required=False
    )

    # if there are additional form settings defined in settings,
    # overwrite/add corresponding options:
    if settings.PROV_VO_CONFIG['provdalform']:
        formsettings = settings.PROV_VO_CONFIG['provdalform']

        if 'obj_id.help_text' in formsettings:
            obj_id.help_text = formsettings['obj_id.help_text']
