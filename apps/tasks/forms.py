from django import forms
from .models import Todo
from apps.users.models import User
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField


class LoginForm(forms.Form):
    username = forms.CharField(error_messages={'required': '用户名不能为空'})
    password = forms.CharField()
    remember = forms.BooleanField(required=False)


# TODO 数据不可为空
class TodoForm(forms.ModelForm):
    required_css_class = 'required'

    # (confused by Form & ModelForm https://stackoverflow.com/questions/2303268/djangos-forms-form-vs-forms-modelform)
    # maturity = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=(
    #     ('0%', '0%'),
    #     ('10%', '10%'),
    #     ('50%', '50%'),
    #     ('90%', '90%'),
    #     ('100%', '100%')
    # ))
    # real_work = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # sub_executor = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = Todo
        fields = ['maturity', 'real_work', 'sub_executor', 'evaluate_factor', 'complete_note', 'is_archived', 'quality_mark']
        widgets = {'complete_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                   # 'evaluate_factor': forms.NumberInput(attrs={'class': 'form-control'}),
                   }

    def __init__(self, *args, **kwargs):
        need_archive = kwargs.pop('need_archive', None)  # 捕获传入的need_archive参数(是否需要归档),给默认值，避免无法提交
        super(TodoForm, self).__init__(*args, **kwargs)
        # self.fields['sub_executor'].widget.attrs['class'] = 'form-control'
        fields = ['maturity', 'real_work', 'sub_executor', 'evaluate_factor', 'complete_note', 'is_archived']
        self.fields['sub_executor'].queryset = User.objects.filter(department=self.instance.main_executor.department)  # 按照承办人所属部门过滤协办人
        for i in fields:
            self.fields[i].widget.attrs['class'] = 'form-control'

        if need_archive:
            # print('需要归档但未存档')
            # 需要归档但未存档，成熟度最高90%
            self.fields['maturity'].choices = [('0%', '0%'), ('10%', '10%'), ('50%', '50%'), ('90%', '90%')]
        else:
            self.fields['maturity'].choices = [('0%', '0%'), ('10%', '10%'), ('50%', '50%'), ('90%', '90%'),
                                               ('100%', '100%')]

    def clean(self):
        # 利用clean方法，数据存储前检查是否已归档，若归档则将成熟度设置为100%
        if self.cleaned_data['is_archived']:
            self.cleaned_data['maturity'] = '100%'
        return self.cleaned_data


class FileFieldForm(forms.Form):
    # file_field = forms.FileField(label='multi', widget=forms.ClearableFileInput(attrs={'multiple': True}))
    attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*50)
    confidential_level = forms.CharField(widget=forms.Select(choices=(('内部', '内部'), ('非涉密', '非涉密'))))