from django.urls import Resolver404, resolve
from django.utils import translation


class RussianAdminInterfaceMiddleware:
    admin_planner_views = {
        "planner:cabinet",
        "planner:image_list",
        "planner:image_upload",
        "planner:delete_image",
        "planner:lunch_participants",
        "planner:all_lunch_participants",
        "planner:delete_lunch_participant",
        "planner:archive",
        "planner:text",
        "planner:text_update",
        "planner:text_detail",
        "planner:post-create",
        "planner:post-edit",
        "planner:schedule_edit_lock",
        "planner:schedule_edit_unlock",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        is_russian_interface = (
            request.path_info.startswith("/admin/")
            or match.namespace == "users"
            or match.view_name in self.admin_planner_views
        )
        if is_russian_interface:
            with translation.override("ru"):
                return self.get_response(request)
        return self.get_response(request)
