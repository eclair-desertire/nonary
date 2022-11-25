from django.contrib.admin.widgets import FilteredSelectMultiple

from shop.models import Brand, Product
from django.forms import ModelForm, ModelMultipleChoiceField


class BrandForm(ModelForm):

    products = ModelMultipleChoiceField(queryset=Product.objects.all(), label='Товары',
                                        widget=FilteredSelectMultiple(verbose_name='Товары', is_stacked=False))

    class Meta:
        model = Brand
        fields = ('name', 'image', 'is_active', 'is_top', 'products')

    def __init__(self, *args, **kwargs):
        super(BrandForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['products'].initial = self.instance.products.all()

    def save_m2m(self):
        pass

    def save(self, *args, **kwargs):

        instance = super(BrandForm, self).save(commit=True)
        self.fields['products'].initial.update(brand=None)
        self.cleaned_data['products'].update(brand=instance)
        return instance
