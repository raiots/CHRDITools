import logging
from datetime import datetime, timedelta
import re

from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.http import JsonResponse
from django.utils.html import format_html
from django import forms
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from . import models
from apps.users.models import TaskProperty, User
from .resources import TodoResources, TaskResources


class TodoInline(admin.StackedInline):

    # 在Inline中同样筛选仅本部门的承办人、协办人
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'related_task':
            kwargs["queryset"] = models.Task.objects.filter(department=request.user.department)
        elif db_field.name == 'main_executor':
            kwargs["queryset"] = User.objects.filter(department=request.user.department)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'sub_executor':
            kwargs["queryset"] = User.objects.filter(department=request.user.department)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    model = models.Todo
    extra = 0
    show_change_link = True
    # classes = ['collapse']


# TODO 选择年度任务时排序 https://www.codenong.com/40740869/

class AttachmentInline(admin.TabularInline):
    model = models.Attachment
    extra = 0
    classes = ['expand']
    readonly_fields = ['upload_time']
    fields = ['attachment', 'confidential_level', 'upload_time']

    def file_name(self, obj):
        return obj.file.name

    def file_size(self, obj):
        return obj.file.size

    def file_type(self, obj):
        return obj.file.content_type

    def file_url(self, obj):
        return format_html('<a href="{}">{}</a>', obj.file.url, obj.file.name)

    file_url.short_description = '附件'
    file_url.allow_tags = True
    file_url.admin_order_field = 'file'


class TaskAdmin(ImportExportModelAdmin):
    resource_class = TaskResources

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "related_task":
    #         ori_path = request.path
    #         f_id = re.sub("\D", "", ori_path)
    #         try:
    #             kwargs["queryset"] = models.Task.objects.get(id=f_id).related_task
    #             return super().formfield_for_manytomany(db_field, request, **kwargs)
    #         except:
    #             pass
    #             # kwargs["queryset"] = models.Task.objects.get(id=2).related_task

    # 所属单位默认为访问用户的部门
    def get_changeform_initial_data(self, request):
        return {'department': request.user.department}

    # 年度任务编辑界面仅显示本部门的任务属性
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'task_property':
            kwargs["queryset"] = TaskProperty.objects.filter(own_department=request.user.department)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # 仅显示当前部门的年度任务，除非为超管
    def get_queryset(self, request):
        qs = super(TaskAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(department=request.user.department)

    def save_model(self, request, obj, form, change):
        mvDict = dict(request.POST)
        # 解决当工作包协办人数均为0时报错
        # print(len(mvDict['related_task-0-sub_executor']))
        try:
            obj.related_task__sub_executor_count = int(len(mvDict['related_task-0-sub_executor']))
        except:
            obj.related_task__sub_executor_count = 0

        super().save_model(request, obj, form, change)

    list_display = (
        'task_property', 'task_id', 'task_topic', 'task_origin', 'aim_value', 'deadline', 'duty_group', 'principal',
        'leader', 'task_note',
    )

    fieldsets = (
        (None, {
            'fields': (
                ('task_property', 'task_id', 'task_topic', 'task_origin', 'aim_value', 'deadline', 'duty_group',
                 'principal', 'leader'),
                'task_note', 'department'),
        }),
    )
    inlines = [TodoInline]
    raw_id_fields = ("principal", "leader",)
    list_display_links = ('task_topic',)

    # autocomplete_fields = ('related_task',)
    # search_fields = ('related_task',)

    # 导入导出功能限制
    def get_export_formats(self):  # 该方法是限制格式为XLS
        formats = (
            base_formats.XLS,
        )
        return [f for f in formats if f().can_export()]

    def has_import_permission(self, request):  # 这是隐藏导入按钮，如果隐藏其他按钮也可以这样操作，
        if request.user.is_superuser:
            return True
        else:
            return False


class PeriodTodoCheck(forms.ModelForm):
    YEAR_CHOICES = []
    for r in range(datetime.now().year, (datetime.now().year + 3)):
        YEAR_CHOICES.append((r, r))
    is_period_todo = forms.BooleanField(label='使用此模板创建周期任务', required=False, initial=False,
                                        help_text="<a href='/static/docs/guide/task_admin.html#%E5%A4%8D%E5%88%B6%E5%B7%A5%E4%BD%9C%E5%8C%85%E5%88%B0%E6%8C%87%E5%AE%9A%E5%B9%B4%E5%BA%A6'>如果您对此选项不熟悉，请点此以查看文档</a>")
    period_type = forms.ChoiceField(label='周期类型',
                                    choices=[('weekly', '每周'), ('monthly', '每月'), ('quarterly', '每季度'),
                                             ('yearly', '复制到该年')], required=False)
    action_year = forms.ChoiceField(label='执行年份', choices=YEAR_CHOICES, required=False, initial=YEAR_CHOICES[0][0])


class TodoAdmin(ImportExportModelAdmin):
    resource_class = TodoResources
    form = PeriodTodoCheck

    # 工作包页面仅显示所属本部门的年度任务、承办人、协办人
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'related_task':
            kwargs["queryset"] = models.Task.objects.filter(department=request.user.department)
        elif db_field.name == 'main_executor':
            kwargs["queryset"] = User.objects.filter(department=request.user.department)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'sub_executor':
            kwargs["queryset"] = User.objects.filter(department=request.user.department)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # 仅显示当前部门的工作包，除非为超管
    def get_queryset(self, request):
        qs = super(TodoAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(related_task__department=request.user.department)

    fieldsets = [
        (None, {
            'fields': [
                'related_task', 'todo_topic', 'todo_note', 'need_archive', 'deadline', 'duty_group', 'main_executor',
                'sub_executor',
                'sub_executor_count', 'predict_work', 'evaluate_factor', 'real_work'
            ],
            'description': ''
        }),

        ('周期任务', {
            'fields': ['is_period_todo', 'period_type', 'action_year'],
        }),
    ]
    list_display = (
        'todo_topic',
        'deadline',
        'todo_note',
        'task_id',
        'task_origin',
        'lined_task',
        # 'duty_department',
        'duty_group',
        'main_executor',
        'list_sub_executor',
        'predict_work',
        'evaluate_factor',
        'maturity',
        'real_work',
        'complete_note',
        'quality_mark',
    )
    list_editable = ['quality_mark']
    list_filter = ('deadline',)
    list_display_links = ('todo_topic', 'deadline',)
    date_hierarchy = 'deadline'
    list_per_page = 70  # 目的是取消自动分页，好像有bug
    # raw_id_fields = ("sub_executor",)
    search_fields = ('todo_topic',)
    ordering = ('related_task',)
    inlines = [AttachmentInline]

    def approval_state(self, obj):
        return format_html('<span style="color:{};">{}</span>', 'green', obj.approval)

    def task_id(self, obj):
        return obj.task_id

    task_id.admin_order_field = 'related_task__task_id'
    task_id.short_description = '任务编号'

    def task_origin(self, obj):
        return obj.task_origin

    task_origin.short_description = '任务来源'

    def duty_department(self, obj):
        return obj.duty_group

    duty_department.short_description = '责任部门'

    def lined_task(self, obj):
        return obj.related_task

    lined_task.short_description = '任务名称'

    # 导入导出功能限制
    def get_export_formats(self):  # 该方法是限制格式为XLS
        formats = (
            base_formats.XLS,
        )
        return [f for f in formats if f().can_export()]

    def has_import_permission(self, request):  # 这是隐藏导入按钮，如果隐藏其他按钮也可以这样操作，
        if request.user.is_superuser:
            return True
        else:
            return False

    # 对工作包页面选择其所属的年度任务中，对年度任务进行筛选。条件为：年度任务的完成时间不早于今年或年度任务中有工作包的完成时间晚于今年
    def get_form(self, request, obj=None, **kwargs):
        form = super(TodoAdmin, self).get_form(request, obj, **kwargs)
        query = models.Task.objects.filter(
            department=request.user.department, deadline__year__gte=datetime.now().strftime('%Y')).order_by('task_id') \
                | models.Task.objects.filter(
            department=request.user.department, related_task__deadline__year__gte=datetime.now().strftime('%Y')) \
                    .order_by('task_id')
        form.base_fields['related_task'].queryset = query.distinct()
        return form

    def save_model(self, request, obj, form, change):
        obj.pub_user = request.user
        super().save_model(request, obj, form, change)

        # 若选中了周期任务，则批量创建任务
        if 'is_period_todo' in form.cleaned_data and form.cleaned_data['is_period_todo'] is True:
            if form.cleaned_data['period_type'] == 'weekly':
                current_deadline = obj.deadline + timedelta(days=7)
                while current_deadline.year == int(form.cleaned_data['action_year']):
                    new_todo = obj
                    new_todo.pk = None
                    new_todo.deadline = current_deadline
                    new_todo.save()
                    current_deadline = current_deadline + timedelta(days=7)

            elif form.cleaned_data['period_type'] == 'monthly':
                current_deadline = obj.deadline + relativedelta(months=1)
                while current_deadline.year == int(form.cleaned_data['action_year']):
                    new_todo = obj
                    new_todo.pk = None
                    new_todo.deadline = current_deadline
                    new_todo.save()
                    current_deadline = current_deadline + relativedelta(months=1)

            elif form.cleaned_data['period_type'] == 'quarterly':
                current_deadline = obj.deadline + relativedelta(months=3)
                while current_deadline.year == int(form.cleaned_data['action_year']):
                    # print("current_deadline: ", current_deadline)
                    new_todo = obj
                    new_todo.pk = None
                    new_todo.deadline = current_deadline
                    new_todo.save()
                    current_deadline = current_deadline + relativedelta(months=3)

            elif form.cleaned_data['period_type'] == 'yearly':
                # 用于将工作包复制到指定年份
                if form.cleaned_data['action_year'] != form.cleaned_data['deadline'].year:
                    # create another using selected year
                    new_todo = obj
                    new_todo.pk = None  # 重置主键以此复制对象
                    current_deadline = new_todo.deadline
                    new_todo.deadline = datetime(int(form.cleaned_data['action_year']), current_deadline.month,
                                                 current_deadline.day)
                    new_todo.save()
            else:
                logging.warning("period_type is not correct")


        else:
            pass

    # def save_model(self, request, obj, form, change):
    #     # 这一行代码写了一个晚上呜呜！ 解决了当保存时，无法从未保存的数据中获取协办人数的问题！
    #     mvDict = dict(request.POST)
    # dicts = request.POST
    # print(dicts)
    # for key, values in dicts:
    #     print(key, values)
    # obj.user = request.user

    # obj.sub_executor_count = int(len(mvDict['sub_executor']))
    # super().save_model(request, obj, form, change)

    # 增加批量操作按钮
    actions = ['bulk_action']

    def bulk_action(self, request, queryset):
        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    # 显示的文本，与django admin一致
    bulk_action.short_description = '批量操作'
    # icon，参考element-ui icon与https://fontawesome.com
    bulk_action.icon = 'el-icon-files'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    bulk_action.type = 'warning'

    # 给按钮追加自定义的颜色
    bulk_action.style = 'color:white;'

    # 指定为弹出层，这个参数最关键
    bulk_action.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '弹出层输入框',
        # 提示信息
        'tips': '这个弹出对话框是需要在admin中进行定义，数据新增编辑等功能，需要自己来实现。',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '名称',
            # 为空校验，默认为False
            'require': True
        }, {
            'type': 'select',
            'key': 'type',
            'label': '类型',
            'width': '200px',
            # size对应elementui的size，取值为：medium / small / mini
            'size': 'small',
            # value字段可以指定默认值
            'value': '0',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }]
        }, {
            'type': 'number',
            'key': 'money',
            'label': '金额',
            # 设置默认值
            'value': 1000
        }, {
            'type': 'date',
            'key': 'date',
            'label': '日期',
        }, {
            'type': 'datetime',
            'key': 'datetime',
            'label': '时间',
        }, {
            'type': 'rate',
            'key': 'star',
            'label': '评价等级'
        }, {
            'type': 'color',
            'key': 'color',
            'label': '颜色'
        }, {
            'type': 'slider',
            'key': 'slider',
            'label': '滑块'
        }, {
            'type': 'switch',
            'key': 'switch',
            'label': 'switch开关'
        }, {
            'type': 'input_number',
            'key': 'input_number',
            'label': 'input number'
        }, {
            'type': 'checkbox',
            'key': 'checkbox',
            # 必须指定默认值
            'value': [],
            'label': '复选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }, {
            'type': 'radio',
            'key': 'radio',
            'label': '单选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }]
    }


admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.Todo, TodoAdmin)
