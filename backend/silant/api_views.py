from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Machine, Maintenance, Complaint, Reference
from .serializers import (
    MachineSerializer, MachinePublicSerializer,
    MaintenanceSerializer, ComplaintSerializer, ReferenceSerializer
)
from .permissions import IsManager, CanWriteMaintenance, CanWriteComplaint
from .roles import CLIENT_GROUP, SERVICE_GROUP, MANAGER_GROUP


# ---- активная роль из заголовка ----
VALID_GROUPS = {CLIENT_GROUP, SERVICE_GROUP, MANAGER_GROUP}

def _active_from_header(request, user):
    """
    Читает X-Active-Role и валидирует, что пользователь состоит в этой группе.
    Возвращает 'manager' | 'service' | 'client' | None
    """
    role = (request.headers.get("X-Active-Role") or "").strip().lower()
    if role in VALID_GROUPS and user.groups.filter(name=role).exists():
        return role
    return None


# ---- профиль текущего пользователя ----
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    u = request.user
    return Response({
        "id": u.id,
        "username": u.username,
        "first_name": u.first_name,
        "groups": list(u.groups.values_list("name", flat=True)),
    })


# ---- ограничение queryset с учётом активной роли ----
def limited_qs_for(user, request, queryset, is_child=False):
    # анон на приватные списки не допущен
    if not user.is_authenticated:
        return queryset.none()

    # staff/superuser — полный доступ
    if user.is_staff or user.is_superuser:
        return queryset

    active = _active_from_header(request, user)

    # менеджер (выбран явно) — полный доступ
    if active == "manager":
        return queryset

    # роль не задана — старое поведение (OR по клиенту/сервису)
    if not active:
        if is_child:
            return queryset.filter(
                Q(machine__client=user) | Q(machine__service_company=user)
            )
        return queryset.filter(Q(client=user) | Q(service_company=user))

    # явная роль service/client
    if active == "service":
        return queryset.filter(machine__service_company=user) if is_child \
               else queryset.filter(service_company=user)

    if active == "client":
        return queryset.filter(machine__client=user) if is_child \
               else queryset.filter(client=user)

    # на всякий случай
    return queryset.none()


# ===== Машины =====
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.select_related(
        "model_technique", "model_engine", "model_transmission",
        "model_drive_bridge", "model_steer_bridge"
    ).all()
    serializer_class = MachineSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "model_technique": ["exact"],
        "model_engine": ["exact"],
        "model_transmission": ["exact"],
        "model_steer_bridge": ["exact"],
        "model_drive_bridge": ["exact"],
    }
    ordering = ("-shipment_date",)

    def get_queryset(self):
        return limited_qs_for(self.request.user, self.request, super().get_queryset())

    def get_permissions(self):
        # писать машины — только менеджер
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsManager()]


# ===== ТО =====
class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.select_related(
        "machine", "kind", "organization", "service_company"
    ).all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated, CanWriteMaintenance]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "kind": ["exact"],
        "machine__serial_number": ["icontains", "exact"],
        "service_company": ["exact"],
    }
    ordering = ("-performed_date",)

    def get_queryset(self):
        return limited_qs_for(self.request.user, self.request, super().get_queryset(), is_child=True)


# ===== Рекламации =====
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related(
        "machine", "failure_node", "recovery_method", "service_company"
    ).all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated, CanWriteComplaint]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "failure_node": ["exact"],
        "recovery_method": ["exact"],
        "service_company": ["exact"],
    }
    ordering = ("-failure_date",)

    def get_queryset(self):
        return limited_qs_for(self.request.user, self.request, super().get_queryset(), is_child=True)


# ===== Справочники =====
class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["entity", "name"]
    ordering = ("entity", "name")

    def get_permissions(self):
        # редактировать справочники может только менеджер
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsManager()]


# ===== Публичная точка: поиск по серийному номеру =====
serial_param = openapi.Parameter(
    name="serial",
    in_=openapi.IN_QUERY,
    description="Заводской номер машины (точное совпадение)",
    type=openapi.TYPE_STRING,
    required=True,
)

class PublicMachineBySerial(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[serial_param],
        responses={200: MachinePublicSerializer},
        operation_description="Публичный поиск по заводскому номеру. Возвращает поля 1–10."
    )
    def get(self, request):
        serial = (request.query_params.get("serial") or "").strip()
        if not serial:
            return Response({"detail": "serial query param is required"}, status=400)

        m = Machine.objects.select_related(
            "model_technique", "model_engine", "model_transmission",
            "model_drive_bridge", "model_steer_bridge"
        ).filter(serial_number=serial).first()
        if not m:
            return Response({"detail": "not_found"}, status=404)
        return Response(MachinePublicSerializer(m).data)
