from django.contrib import admin
from .models import Machine, Maintenance, Complaint, Reference
from .acl import is_manager

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("entity", "name", "description")
    list_filter = ("entity",)
    search_fields = ("entity", "name")
    ordering = ("entity", "name")

    def has_view_permission(self, request, obj=None):  # всем можно читать
        return True

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return is_manager(request.user)

    def has_change_permission(self, request, obj=None):
        return is_manager(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_manager(request.user)

# ---- Инлайны для карточки Машины ----
class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 0
    fields = ("performed_date", "kind", "operating_hours",
              "work_order_number", "work_order_date",
              "organization", "service_company")
    autocomplete_fields = ("kind", "organization", "service_company")
    show_change_link = True

class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 0
    fields = ("failure_date", "failure_node", "recovery_method",
              "recovery_date", "downtime_days", "service_company")
    readonly_fields = ("downtime_days",)
    autocomplete_fields = ("failure_node", "recovery_method", "service_company")
    show_change_link = True


# ---- Машины ----
@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number", "model_technique", "model_engine",
        "shipment_date", "client", "service_company",
    )
    list_filter = (
        "model_technique", "model_engine", "model_transmission",
        "model_steer_bridge", "model_drive_bridge", "shipment_date",
    )
    search_fields = ("serial_number", "contract_number", "consignee", "delivery_address")
    date_hierarchy = "shipment_date"
    ordering = ("-shipment_date", "-id")
    list_select_related = (
        "model_technique", "model_engine", "model_transmission",
        "model_steer_bridge", "model_drive_bridge", "client", "service_company",
    )
    autocomplete_fields = (
        "model_technique", "model_engine", "model_transmission",
        "model_steer_bridge", "model_drive_bridge",
        "client", "service_company",
    )
    inlines = [MaintenanceInline, ComplaintInline]


# ---- ТО ----
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("performed_date", "machine", "kind", "operating_hours", "service_company")
    list_filter = ("performed_date", "kind", "service_company")
    search_fields = ("machine__serial_number", "work_order_number")
    date_hierarchy = "performed_date"
    ordering = ("-performed_date", "-id")
    list_select_related = ("machine", "kind", "organization", "service_company")
    autocomplete_fields = ("machine", "kind", "organization", "service_company")


# ---- Рекламации ----
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("failure_date", "machine", "failure_node", "recovery_method",
                    "recovery_date", "downtime_days", "service_company")
    list_filter = ("failure_date", "failure_node", "recovery_method", "service_company")
    search_fields = ("machine__serial_number", "failure_description", "parts_used")
    date_hierarchy = "failure_date"
    ordering = ("-failure_date", "-id")
    list_select_related = ("machine", "failure_node", "recovery_method", "service_company")
    readonly_fields = ("downtime_days",)
    autocomplete_fields = ("machine", "failure_node", "recovery_method", "service_company")


admin.site.site_header = "Силант — админка"
admin.site.site_title = "Силант"
admin.site.index_title = "Управление данными"

try:
    from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialToken)
except Exception:
    pass