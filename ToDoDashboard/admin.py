from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from ToDoDashboard.models import Member, Dashboard, DashboardColumn, ToDoItem
from users.models import User


class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'created_at', 'updated_at', 'get_avatar')

    def get_avatar(self, record):
        if record.avatar:
            return mark_safe(f'<image src="{record.avatar.url}" width="75">')
        else:
            return '-'

    get_avatar.short_description = 'avatar'
    empty_value_display = 'unset'


class ColumnInline(admin.StackedInline):
    model = DashboardColumn

    extra = 1


class DashboardAdmin(admin.ModelAdmin):
    inlines = [ColumnInline, ]
    list_display = ('id', 'title', 'get_owner', 'is_public', 'created_at', 'updated_at')
    list_editable = ('is_public',)
    list_display_links = ('id', 'title')

    fields = (('title', 'is_public'), 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    # def get_list_display(self, request):
    #     ld = ['id', 'title', 'get_owner', 'is_public']
    #
    #     if request.user.is_superuser:
    #         ld += ['created_at', 'updated_at']
    #
    #     return ld

    def get_owner(self, record):
        return record.owner.user.username

    get_owner.short_description = 'owner'


class ToDoInline(admin.TabularInline):
    model = ToDoItem

    show_change_link = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        else:
            return 5


class DashboardColumnAdmin(admin.ModelAdmin):
    inlines = [ToDoInline, ]
    list_display = ('title', 'dashboard', 'created_at', 'updated_at')

    fields = ('title', 'dashboard', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class ToDoFilter(admin.SimpleListFilter):
    title = 'Time'
    parameter_name = 'time_estimate_hours'

    def lookups(self, request, model_admin):
        return (
            ('easy', 'Easy'),
            ('average', 'Average'),
            ('hard', 'Hard')
        )

    def queryset(self, request, queryset):
        if self.value() == 'easy':
            return queryset.filter(time_estimate_hours__lt=2)
        if self.value() == 'average':
            return queryset.filter(time_estimate_hours__gte=2, time_estimate_hours__lt=8)
        if self.value() == 'hard':
            return queryset.filter(time_estimate_hours__gte=8)


class ToDoItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'label', 'comment', 'due_date', 'time_estimate_hours')
    list_editable = ('label', 'time_estimate_hours')

    search_fields = ('description', 'comment')
    list_filter = ('label', ToDoFilter)

    sortable_by = ('label', 'due_date', 'time_estimate_hours')
    ordering = ('due_date', 'time_estimate_hours')

    fieldsets = (
        ('Main', {'fields': ('description', 'comment', 'label')}),
        ('Dates and Times', {'fields': (('start_date', 'due_date'), 'time_estimate_hours'),
                             'description': 'Dates and Times',
                             'classes': ('collapse',)})
    )

    actions_on_bottom = True

    def add_1_hour_to_estimated_time(self, request, queryset):
        for rec in queryset:
            rec.time_estimate_hours += 1
            rec.save()

        self.message_user(request, 'Done')

    add_1_hour_to_estimated_time.short_description = 'Add 1 hour to estimated time'
    actions = (add_1_hour_to_estimated_time, )


admin.site.register(User, UserAdmin)

admin.site.register(Member, MemberAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(DashboardColumn, DashboardColumnAdmin)
admin.site.register(ToDoItem, ToDoItemAdmin)

admin.site.site_header = 'Admin Panel'
admin.site.site_title = 'Site Admin'
admin.site.index_title = 'Administration'
