from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .roles import CLIENT_GROUP, SERVICE_GROUP, MANAGER_GROUP
from .models import Machine, Maintenance, Complaint, Reference


@transaction.atomic
def ensure_groups_and_perms(**kwargs):
    client, _  = Group.objects.get_or_create(name=CLIENT_GROUP)
    service, _ = Group.objects.get_or_create(name=SERVICE_GROUP)
    manager, _ = Group.objects.get_or_create(name=MANAGER_GROUP)

    ct_machine   = ContentType.objects.get_for_model(Machine)
    ct_maint     = ContentType.objects.get_for_model(Maintenance)
    ct_complaint = ContentType.objects.get_for_model(Complaint)
    ct_reference = ContentType.objects.get_for_model(Reference)

    def perms(ct, *codes):
        return Permission.objects.filter(
            content_type=ct,
            codename__in=[f"{c}_{ct.model}" for c in codes],
        )

    manager.permissions.set(
        list(perms(ct_machine,"add","change","delete","view")) +
        list(perms(ct_maint,"add","change","delete","view")) +
        list(perms(ct_complaint,"add","change","delete","view")) +
        list(perms(ct_reference,"add","change","delete","view"))
    )
    service.permissions.set(
        list(perms(ct_machine,"view")) +
        list(perms(ct_maint,"add","change","view")) +
        list(perms(ct_complaint,"add","change","view"))
    )
    client.permissions.set(
        list(perms(ct_machine,"view")) +
        list(perms(ct_maint,"add","change","view")) +
        list(perms(ct_complaint,"view"))
    )


@receiver(post_migrate, dispatch_uid="silant_ensure_groups_and_perms")
def _ensure_groups_and_perms_receiver(**kwargs):
    ensure_groups_and_perms(**kwargs)
