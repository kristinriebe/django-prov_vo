from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from prov_vo.models import Entity


class ProvDalForm(forms.Form):

    obj_id = forms.CharField(
        label='Entity or activity ID',
        max_length=1024,
        widget=forms.TextInput(attrs={'size':36}),
        help_text="Please enter the identifier for an entity or an activity",
    )

    depth = forms.ChoiceField(
        label="DEPTH",
        choices=[('1', '1'), ('ALL','all')],
        widget=forms.RadioSelect(),
        help_text="Specify if just one or all previous steps shall be retrieved",
        initial='ALL'
    )

    #forward = forms.ChoiceField(
    #    label="Forward",
    #    choices=[('1', '1'), ('ALL','all')],
    #    widget=forms.RadioSelect(),
    #    help_text="Specify if just one or all forward steps shall be retrieved",
    #    initial='ALL'
    #)

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

    # if there are additional form settings defined in settings,
    # overwrite/add corresponding options:
    if settings.PROV_VO_CONFIG['provdalform']:
        formsettings = settings.PROV_VO_CONFIG['provdalform']

        if 'obj_id.help_text' in formsettings:
            obj_id.help_text = formsettings['obj_id.help_text']
