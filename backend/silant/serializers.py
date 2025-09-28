from rest_framework import serializers
from .models import Machine, Maintenance, Complaint, Reference

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ["id", "entity", "name", "description"]

class MachineSerializer(serializers.ModelSerializer):
    model_technique_name   = serializers.CharField(source="model_technique.name", read_only=True)
    model_engine_name      = serializers.CharField(source="model_engine.name", read_only=True)
    model_transmission_name= serializers.CharField(source="model_transmission.name", read_only=True)
    model_steer_bridge_name= serializers.CharField(source="model_steer_bridge.name", read_only=True)
    model_drive_bridge_name= serializers.CharField(source="model_drive_bridge.name", read_only=True)

    class Meta:
        model = Machine
        fields = [
            "id","serial_number",
            "model_technique","model_engine","model_transmission","model_steer_bridge","model_drive_bridge",
            "model_technique_name","model_engine_name","model_transmission_name","model_steer_bridge_name","model_drive_bridge_name",
            "serial_engine","serial_transmission","serial_drive_bridge","serial_steer_bridge",
            "contract_number","shipment_date","consignee","delivery_address","equipment",
            "client","service_company",
        ]

class MachinePublicSerializer(serializers.ModelSerializer):
    model_technique_name   = serializers.CharField(source="model_technique.name", read_only=True)
    model_engine_name      = serializers.CharField(source="model_engine.name", read_only=True)
    model_transmission_name= serializers.CharField(source="model_transmission.name", read_only=True)
    model_steer_bridge_name= serializers.CharField(source="model_steer_bridge.name", read_only=True)
    model_drive_bridge_name= serializers.CharField(source="model_drive_bridge.name", read_only=True)

    class Meta:
        model = Machine
        fields = [
            "serial_number",
            "model_technique_name","model_engine_name","serial_engine",
            "model_transmission_name","serial_transmission",
            "model_drive_bridge_name","serial_drive_bridge",
            "model_steer_bridge_name","serial_steer_bridge",
        ]

class MaintenanceSerializer(serializers.ModelSerializer):
    kind_name = serializers.CharField(source="kind.name", read_only=True)
    machine_serial = serializers.CharField(source="machine.serial_number", read_only=True)

    class Meta:
        model = Maintenance
        fields = [
            "id","machine","machine_serial","kind","kind_name","performed_date","operating_hours",
            "work_order_number","work_order_date","organization","service_company",
        ]

class ComplaintSerializer(serializers.ModelSerializer):
    failure_node_name = serializers.CharField(source="failure_node.name", read_only=True)
    recovery_method_name = serializers.CharField(source="recovery_method.name", read_only=True)
    machine_serial = serializers.CharField(source="machine.serial_number", read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id","machine","machine_serial","failure_date","operating_hours",
            "failure_node","failure_node_name","failure_description",
            "recovery_method","recovery_method_name","parts_used","recovery_date",
            "downtime_days","service_company",
        ]
