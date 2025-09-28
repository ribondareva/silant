import django_filters as f
from django.contrib.auth.models import User
from .models import Machine, Maintenance, Complaint, Reference
from .roles import SERVICE_GROUP

def ref_qs(entity: str):
    return Reference.objects.filter(entity=entity)

class MachineFilter(f.FilterSet):
    model_technique   = f.ModelChoiceFilter(label="Модель техники",      queryset=ref_qs("Модель техники"))
    model_engine      = f.ModelChoiceFilter(label="Модель двигателя",     queryset=ref_qs("Модель двигателя"))
    model_transmission= f.ModelChoiceFilter(label="Модель трансмиссии",   queryset=ref_qs("Модель трансмиссии"))
    model_steer_bridge= f.ModelChoiceFilter(label="Модель управляемого моста", queryset=ref_qs("Модель управляемого моста"))
    model_drive_bridge= f.ModelChoiceFilter(label="Модель ведущего моста",    queryset=ref_qs("Модель ведущего моста"))

    class Meta:
        model = Machine
        fields = ["model_technique","model_engine","model_transmission","model_steer_bridge","model_drive_bridge"]

class MaintenanceFilter(f.FilterSet):
    kind            = f.ModelChoiceFilter(label="Вид ТО", queryset=ref_qs("Вид ТО"))
    machine__serial_number = f.CharFilter(label="Зав. № машины", lookup_expr="icontains")
    service_company = f.ModelChoiceFilter(
        label="Сервисная компания",
        queryset=User.objects.filter(groups__name=SERVICE_GROUP).distinct()
    )

    class Meta:
        model = Maintenance
        fields = ["kind","machine__serial_number","service_company"]

class ComplaintFilter(f.FilterSet):
    failure_node    = f.ModelChoiceFilter(label="Узел отказа", queryset=ref_qs("Узел отказа"))
    recovery_method = f.ModelChoiceFilter(label="Способ восстановления", queryset=ref_qs("Способ восстановления"))
    service_company = f.ModelChoiceFilter(
        label="Сервисная компания",
        queryset=User.objects.filter(groups__name=SERVICE_GROUP).distinct()
    )

    class Meta:
        model = Complaint
        fields = ["failure_node","recovery_method","service_company"]
