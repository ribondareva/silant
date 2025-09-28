from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManager(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u and u.is_authenticated and (u.is_staff or u.is_superuser or u.groups.filter(name="manager").exists())

class CanWriteMaintenance(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS: return True
        u = request.user
        if not u.is_authenticated: return False
        if u.is_staff or u.is_superuser or u.groups.filter(name="manager").exists(): return True
        # service: может писать по своим; client: только по своим и только maintenance
        return u.groups.filter(name__in=["service","client"]).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: return True
        u = request.user
        if u.is_staff or u.is_superuser or u.groups.filter(name="manager").exists(): return True
        m = obj.machine if hasattr(obj, "machine") else obj
        if u.groups.filter(name="service").exists():
            return m.client_id == u.id or m.service_company_id == u.id
        if u.groups.filter(name="client").exists():
            return m.client_id == u.id or m.service_company_id == u.id
        return False

class CanWriteComplaint(CanWriteMaintenance):
    # клиент НЕ может создавать/менять рекламации: переопределяем
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS: return True
        u = request.user
        if not u.is_authenticated: return False
        if u.is_staff or u.is_superuser or u.groups.filter(name="manager").exists(): return True
        return u.groups.filter(name="service").exists()
