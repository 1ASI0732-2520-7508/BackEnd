from rest_framework import serializers
from auditlog.models import LogEntry

class LogEntrySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "timestamp",
            "actor",
            "content_type",
            "object_id",
            "object_repr",
            "action",
            "action_display",
            "changes",
            "remote_addr",
        ]
