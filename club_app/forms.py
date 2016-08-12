from django.forms.models import BaseInlineFormSet
from django_jinja_knockout.widgets import ForeignKeyGridWidget
from django_jinja_knockout.forms import (
    BootstrapModelForm, FormWithInlineFormsets, set_knockout_template, ko_inlineformset_factory
)
from .models import Profile, Manufacturer, Club, Equipment, Member


class ProfileForm(BootstrapModelForm):

    class Meta:
        model = Profile
        fields = '__all__'


class ManufacturerForm(BootstrapModelForm):

    class Meta:
        model = Manufacturer
        fields = '__all__'


class ClubForm(BootstrapModelForm):

    class Meta:
        model = Club
        fields = '__all__'


class EquipmentForm(BootstrapModelForm):

    class Meta:
        model = Equipment
        fields = '__all__'
        widgets = {
            'manufacturer': ForeignKeyGridWidget(grid_options={
                'pageRoute': 'manufacturer_fk_widget_grid',
            })
        }


class MemberForm(BootstrapModelForm):

    class Meta:
        model = Member
        fields = '__all__'
        widgets = {
            'profile': ForeignKeyGridWidget(grid_options={
                'pageRoute': 'profile_fk_widget_grid',
                'dialogOptions': {'size': 'size-wide'},
            })
        }

    def clean(self):
        super().clean()
        role = self.cleaned_data.get('role')
        club = self.cleaned_data.get('club')
        if role != Member.ROLE_MEMBER and Member.objects.filter(club=club, role=role).exists():
            self.add_error('role', 'Non-member roles should be unique')

ClubEquipmentFormSet = ko_inlineformset_factory(
    Club, Equipment, form=EquipmentForm, extra=0, min_num=1, max_num=3, can_delete=True
)


class ClubMemberFormSetCls(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            return
        roles = []
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                # Do not validate deleted forms.
                continue
            # Warning! May be None, thus dict.get() is used.
            role = form.cleaned_data.get('role')
            if role != Member.ROLE_MEMBER:
                if role in roles:
                    form.add_error('role', 'Non-member roles should be unique')
                    # raise forms.ValidationError(msg)
                else:
                    roles.append(role)

ClubMemberFormSet = ko_inlineformset_factory(
    Club, Member, form=MemberForm, formset=ClubMemberFormSetCls, extra=0, min_num=0, max_num=10, can_delete=True
)


class ClubFormWithInlineFormsets(FormWithInlineFormsets):

    FormClass = ClubForm
    FormsetClasses = [ClubEquipmentFormSet, ClubMemberFormSet]
