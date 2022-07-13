from rest_framework.permissions import BasePermission


class ActionViewPermission(BasePermission):
    """
    Allows group to access based on allowed action(s)

    usage:

        class ExampleViewSet(GenericViewSet):
            permission_classes = (ActionViewPermission,)
            list_rules = [
                [["Group 1", "Group 2"], ["list", "retrieve", "destroy"]],
                [["Group 1"], ["create", "update", "update", "send"]],
            ]
    """

    def has_permission(self, request, view):
        rules = view.list_rules
        user = request.user
        action = view.action

        # set unauthorized
        if not user and not user.is_authenticated:
            return False

        user_groups = list(user.groups.values_list("name", flat=True))
        for group in user_groups:
            user_in_group = False
            allowed_action = []
            for rule in rules:
                user_in_group = group in rule[0]

                if user_in_group and action in (allowed_action + rule[1]):
                    return True
        return False
