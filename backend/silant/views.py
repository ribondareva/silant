from django.views.generic import (
    DetailView, CreateView, UpdateView, TemplateView, RedirectView
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django_filters.views import FilterView

from .models import Machine, Maintenance, Complaint
from .filters import MachineFilter, MaintenanceFilter, ComplaintFilter
from .acl import RoleQuerysetMixin, OwnerWriteRequiredMixin


# --- Домашний редирект: аноним -> public_lookup, авторизованный -> список машин
class HomeRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse_lazy("machine_list")
        return reverse_lazy("public_lookup")

# --- Публичный поиск (CBV). Показывает только поля 1–10 в шаблоне.
class PublicMachineLookupView(TemplateView):
    template_name = "silant/public_lookup.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        serial = self.request.GET.get("serial", "").strip()
        machine = None
        if serial:
            machine = (
                Machine.objects.select_related(
                    "model_technique",
                    "model_engine",
                    "model_transmission",
                    "model_drive_bridge",
                    "model_steer_bridge",
                )
                .filter(serial_number=serial)
                .first()
            )
        ctx.update({"serial": serial, "machine": machine})
        return ctx

# --- Машины
class MachineList(RoleQuerysetMixin, FilterView):
    model = Machine
    filterset_class = MachineFilter
    template_name = "silant/machine_list.html"
    paginate_by = 50
    filter_on = None

class MachineDetail(RoleQuerysetMixin, DetailView):
    model = Machine
    template_name = "silant/machine_detail.html"
    filter_on = None

# --- ТО
class MaintenanceList(RoleQuerysetMixin, FilterView):
    model = Maintenance
    filterset_class = MaintenanceFilter
    template_name = "silant/maintenance_list.html"
    paginate_by = 50

class MaintenanceCreate(OwnerWriteRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Maintenance
    fields = [
        "machine", "kind", "performed_date", "operating_hours",
        "work_order_number", "work_order_date", "organization", "service_company",
    ]
    permission_required = "silant.add_maintenance"
    model_kind = "maintenance"

    def get_success_url(self):
        return reverse_lazy("machine_detail", kwargs={"pk": self.object.machine_id})

class MaintenanceUpdate(OwnerWriteRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Maintenance
    fields = [
        "kind", "performed_date", "operating_hours",
        "work_order_number", "work_order_date", "organization", "service_company",
    ]
    permission_required = "silant.change_maintenance"
    model_kind = "maintenance"

    def get_success_url(self):
        return reverse_lazy("machine_detail", kwargs={"pk": self.object.machine_id})

# --- Рекламации
class ComplaintList(RoleQuerysetMixin, FilterView):
    model = Complaint
    filterset_class = ComplaintFilter
    template_name = "silant/complaint_list.html"
    paginate_by = 50

class ComplaintCreate(OwnerWriteRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Complaint
    fields = [
        "machine", "failure_date", "operating_hours",
        "failure_node", "failure_description",
        "recovery_method", "parts_used", "recovery_date",
        "service_company",
    ]
    permission_required = "silant.add_complaint"
    model_kind = "complaint"

    def get_success_url(self):
        return reverse_lazy("machine_detail", kwargs={"pk": self.object.machine_id})

class ComplaintUpdate(OwnerWriteRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Complaint
    fields = [
        "failure_date", "operating_hours",
        "failure_node", "failure_description",
        "recovery_method", "parts_used", "recovery_date",
        "service_company",
    ]
    permission_required = "silant.change_complaint"
    model_kind = "complaint"

    def get_success_url(self):
        return reverse_lazy("machine_detail", kwargs={"pk": self.object.machine_id})
