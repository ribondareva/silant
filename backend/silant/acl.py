from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .roles import CLIENT_GROUP, SERVICE_GROUP, MANAGER_GROUP

def is_in(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

def is_manager(user): return is_in(user, MANAGER_GROUP) or user.is_staff or user.is_superuser
def is_client(user):  return is_in(user, CLIENT_GROUP)
def is_service(user): return is_in(user, SERVICE_GROUP)

class RoleQuerysetMixin(LoginRequiredMixin):
    """
    Ограничивает queryset:
      - менеджеру: все;
      - остальным: только машины/объекты, привязанные к пользователю.
    Предполагает наличие FK: obj.machine.client / obj.machine.service_company.
    Для Machine — поля client / service_company.
    """
    filter_on = "machine"

    def get_base_filter(self):
        user = self.request.user
        if is_manager(user):
            return Q()  # без ограничений
        if self.filter_on is None:
            # это Machine
            return Q(client=user) | Q(service_company=user)
        # это дочерние сущности
        return Q(**{f"{self.filter_on}__client": user}) | Q(**{f"{self.filter_on}__service_company": user})

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(self.get_base_filter()).distinct()

class OwnerWriteRequiredMixin:
    """
    Для операций create/update:
      - менеджер может всё;
      - сервис может создавать/менять ТО и Рекламации по "своим" машинам;
      - клиент может создавать/менять только ТО по "своим" машинам.
    """
    model_kind = "maintenance"

    def _is_allowed_for_user(self, obj_or_machine, user):
        from .models import Machine
        machine = obj_or_machine if isinstance(obj_or_machine, Machine) else obj_or_machine.machine
        if is_manager(user):
            return True
        if is_service(user):
            return machine.service_company_id == user.id or machine.client_id == user.id
        if is_client(user):
            return self.model_kind == "maintenance" and (machine.client_id == user.id or machine.service_company_id == user.id)
        return False

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        obj = form.instance
        if not getattr(obj, "machine_id", None) and "machine" in self.kwargs:
            obj.machine_id = self.kwargs["machine"]
        if not self._is_allowed_for_user(obj, user):
            raise PermissionDenied("Недостаточно прав для изменения объекта.")
        return super().form_valid(form)