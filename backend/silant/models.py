from django.db import models
from django.contrib.auth.models import User

class Reference(models.Model):
    """Справочники (модели двигателей, трансмиссий и т.п.)"""
    entity = models.CharField(max_length=100)  # тип справочника, например "двигатель"
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
        unique_together = ("entity", "name")  # внутри справочника не должно быть дублей
        ordering = ["entity", "name"]

    def __str__(self):
        return f"{self.entity} → {self.name}"

class Machine(models.Model):
    """Характеристики проданной машины"""
    serial_number = models.CharField("Зав. № машины", max_length=50, unique=True)
    model_technique = models.ForeignKey(
        Reference, on_delete=models.PROTECT, related_name="machines_model", verbose_name="Модель техники"
    )
    model_engine = models.ForeignKey(
        Reference, on_delete=models.PROTECT, related_name="machines_engine", verbose_name="Модель двигателя"
    )
    serial_engine = models.CharField("Зав. № двигателя", max_length=50, blank=True)
    model_transmission = models.ForeignKey(
        Reference, on_delete=models.PROTECT, related_name="machines_transmission", verbose_name="Модель трансмиссии"
    )
    serial_transmission = models.CharField("Зав. № трансмиссии", max_length=50, blank=True)
    model_drive_bridge = models.ForeignKey(
        Reference, on_delete=models.PROTECT, related_name="machines_drive", verbose_name="Модель ведущего моста"
    )
    serial_drive_bridge = models.CharField("Зав. № ведущего моста", max_length=50, blank=True)

    model_steer_bridge = models.ForeignKey(
        Reference, on_delete=models.PROTECT, related_name="machines_steer", verbose_name="Модель управляемого моста"
    )
    serial_steer_bridge = models.CharField("Зав. № управляемого моста", max_length=50, blank=True)
    contract_number = models.CharField("Договор поставки №, дата", max_length=100, blank=True)
    shipment_date = models.DateField("Дата отгрузки с завода")
    consignee = models.CharField("Грузополучатель (конечный потребитель)", max_length=255, blank=True)
    delivery_address = models.CharField("Адрес поставки (эксплуатации)", max_length=255, blank=True)
    equipment = models.TextField("Комплектация (доп. опции)", blank=True)
    client = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="client_machines", verbose_name="Клиент"
    )
    service_company = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="service_machines", verbose_name="Сервисная компания"
    )

    class Meta:
        ordering = ["-shipment_date"]

    def __str__(self):
        return f"{self.model_technique.name} SN:{self.serial_number}"



class Maintenance(models.Model):
    """
    Техническое обслуживание (история ТО по машинам)
    """
    kind = models.ForeignKey(
        Reference,
        on_delete=models.PROTECT,
        related_name="maintenance_kinds",
        verbose_name="Вид ТО",
        help_text="Справочник: Вид ТО",
    )
    performed_date = models.DateField(
        "Дата проведения ТО",
        db_index=True,
    )
    operating_hours = models.PositiveIntegerField(
        "Наработка, м/час",
        help_text="Моточасы на момент ТО",
        default=0,
    )
    work_order_number = models.CharField(
        "№ заказ-наряда",
        max_length=100,
        blank=True,
    )
    work_order_date = models.DateField(
        "Дата заказ-наряда",
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        Reference,
        on_delete=models.PROTECT,
        related_name="maintenance_organizations",
        verbose_name="Организация, проводившая ТО",
        help_text="Справочник: Организация ТО",
    )
    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="maintenances",
        verbose_name="Машина",
        db_index=True,
    )
    service_company = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="service_maintenances",
        verbose_name="Сервисная компания",
        db_index=True,
    )

    class Meta:
        verbose_name = "ТО"
        verbose_name_plural = "ТО"
        ordering = ["-performed_date", "-id"]
        indexes = [
            models.Index(fields=["performed_date"]),
            models.Index(fields=["machine", "performed_date"]),
            models.Index(fields=["service_company"]),
        ]

    def __str__(self):
        return f"{self.kind.name} — {self.machine.serial_number} — {self.performed_date:%Y-%m-%d}"


class Complaint(models.Model):
    """
    Рекламации (заявленные отказы и их устранение)
    """
    failure_date = models.DateField("Дата отказа", db_index=True)
    operating_hours = models.PositiveIntegerField("Наработка, м/час", default=0)
    failure_node = models.ForeignKey(
        Reference,
        on_delete=models.PROTECT,
        related_name="complaints_failure_node",
        verbose_name="Узел отказа",
        help_text="Справочник: Узел отказа",
    )
    failure_description = models.TextField("Описание отказа", blank=True)
    recovery_method = models.ForeignKey(
        Reference,
        on_delete=models.PROTECT,
        related_name="complaints_recovery_method",
        verbose_name="Способ восстановления",
        help_text="Справочник: Способ восстановления",
    )
    parts_used = models.TextField("Используемые запасные части", blank=True)
    recovery_date = models.DateField("Дата восстановления", null=True, blank=True)  
    downtime_days = models.PositiveIntegerField(
        "Время простоя техники (дни)",
        default=0,
        editable=False,
    )
    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name="Машина",
        db_index=True,
    )
    service_company = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="service_complaints",
        verbose_name="Сервисная компания",
        db_index=True,
    )

    class Meta:
        verbose_name = "Рекламация"
        verbose_name_plural = "Рекламации"
        ordering = ["-failure_date", "-id"]
        indexes = [
            models.Index(fields=["failure_date"]),
            models.Index(fields=["machine", "failure_date"]),
            models.Index(fields=["service_company"]),
        ]

    def clean(self):
        # валидация дат
        if self.recovery_date and self.recovery_date < self.failure_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("Дата восстановления не может быть раньше даты отказа.")

    def save(self, *args, **kwargs):
        # пересчёт простоя перед сохранением
        if self.recovery_date:
            self.downtime_days = (self.recovery_date - self.failure_date).days
            if self.downtime_days < 0:
                self.downtime_days = 0
        else:
            self.downtime_days = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.machine.serial_number} — {self.failure_node.name} — {self.failure_date:%Y-%m-%d}"
