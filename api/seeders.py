from django.contrib.auth.models import Group


def generate_groups(force_reset=False):
    if force_reset:
        Group.objects.all().delete()

    group_dict = [
        {"name": "Student", "description": "User who can view and access course pages and the content of each pages."},
        {"name": "Teacher", "description": "User who can create course pages and granted the access to students to enroll the course."},
        {"name": "Officer", "description": "User who can manage the user account."},
    ]

    for group in group_dict:
        Group.objects.get_or_create(name=group.get("name"))