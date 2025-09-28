from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .roles import CLIENT_GROUP, SERVICE_GROUP, MANAGER_GROUP
from .models import Machine, Maintenance, Complaint, Reference

@transaction.atomic
def ensure_groups_and_perms(**kwargs):
    # группы
    client, _  = Group.objects.get_or_create(name=CLIENT_GROUP)
    service, _ = Group.objects.get_or_create(name=SERVICE_GROUP)
    manager, _ = Group.objects.get_or_create(name=MANAGER_GROUP)

    # контент-типы
    ct_machine     = ContentType.objects.get_for_model(Machine)
    ct_maint       = ContentType.objects.get_for_model(Maintenance)
    ct_complaint   = ContentType.objects.get_for_model(Complaint)
    ct_reference   = ContentType.objects.get_for_model(Reference)

    # стандартные права
    def perms(ct, *codes):  # "add", "change", "delete", "view"
        return Permission.objects.filter(content_type=ct, codename__in=[f"{c}_{ct.model}" for c in codes])

    # Менеджер: полный доступ ко всему + справочники редактируемы
    manager.permissions.set(
        list(perms(ct_machine,"add","change","delete","view")) +
        list(perms(ct_maint,"add","change","delete","view")) +
        list(perms(ct_complaint,"add","change","delete","view")) +
        list(perms(ct_reference,"add","change","delete","view"))
    )

    # Сервисная организация: читать свои машины, добавлять/редактировать ТО и Рекламации (свои)
    service.permissions.set(
        list(perms(ct_machine,"view")) +
        list(perms(ct_maint,"add","change","view")) +
        list(perms(ct_complaint,"add","change","view"))
    )

    # Клиент: читать свои машины, добавлять/редактировать ТО (свои), жалобы только читать
    client.permissions.set(
        list(perms(ct_machine,"view")) +
        list(perms(ct_maint,"add","change","view")) +
        list(perms(ct_complaint,"view"))
    )