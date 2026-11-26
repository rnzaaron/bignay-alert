from .models import ActivityLog


def log_activity(*, user, action, description, related_record_id=None):
    if not action or not action.strip():
        raise ValueError('action must not be empty')
    if not description or not description.strip():
        raise ValueError('description must not be empty')

    return ActivityLog.objects.create(
        user=user,
        action=action.strip(),
        description=description,
        related_record_id=(
            '' if related_record_id is None else str(related_record_id)
        ),
    )
