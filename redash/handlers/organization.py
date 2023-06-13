from flask_login import current_user, login_required

from redash import models
from redash.handlers.base import routes
from redash.handlers.base import json_response, org_scoped_rule
from redash.authentication import current_org


@routes.route(org_scoped_rule("/api/organization/status"), methods=["GET"])
@login_required
def organization_status(org_slug=None):
    counters = {
        "users": models.User.all(current_org).count(),
        "alerts": models.Alert.all(group_ids=current_user.group_ids).count(),
        "data_sources": models.DataSource.all(
            current_org, group_ids=current_user.group_ids
        ).count(),
        "queries": models.Query.all_queries(
            current_user.group_ids, current_user.id, include_drafts=True
        ).count(),
        "dashboards": models.Dashboard.query.filter(
            models.Dashboard.org == current_org, models.Dashboard.is_archived == False
        ).count(),
    }

    return json_response(dict(object_counters=counters))


# Immersa change to create an API endpoint to create an Org for a superadmin
from redash.handlers.base import BaseResource
from redash.models import Group, User
from redash.permissions import require_super_admin
from flask import request
from flask_restful import abort


class OrganizationResource(BaseResource):

    @require_super_admin
    def get(self, slug):
        org = models.Organization.get_by_slug(slug)
        self.record_event(
            {"action": "list", "object_id": "org", "object_type": "organization"}
        )

        if org is None:
            abort(404, message="No Org found")

        return org.to_dict()

    @require_super_admin
    def delete(self, slug):
        org = models.Organization.get_by_slug(slug)

        if org is not None:
            groups = models.Group.all(org)
            if groups is not None:
                for group in groups:
                    org_fk_constraints = [models.Query, models.QueryResult, models.DataSource, models.Event]
                    for org_fk_constraint in org_fk_constraints:
                        constraints = models.db.session.query(org_fk_constraint).filter(
                            org_fk_constraint.org == org)
                        for constraint in constraints:
                            models.db.session.delete(constraint)
                    members = models.Group.members(group.id)
                    for member in members:
                        user_fk_constraints = [models.Change]
                        for user_fk_constraint in user_fk_constraints:
                            constraints = models.db.session.query(user_fk_constraint).filter(user_fk_constraint.user == member)
                            for constraint in constraints:
                                models.db.session.delete(constraint)
                        models.db.session.delete(member)
                    models.db.session.delete(group)
            models.db.session.delete(org)
            models.db.session.commit()
        else:
            abort(404, message=f"Org '{slug}' not found")
        self.record_event(
            {"action": "delete", "object_id": f"{slug}", "object_type": "organization"}
        )
        return {"message": f"Org '{slug}' successfully deleted"}


class OrganizationListResource(BaseResource):

    @require_super_admin
    def get(self):
        orgs = models.db.session.query(models.Organization).all()
        self.record_event(
            {"action": "list", "object_id": "all", "object_type": "organization"}
        )
        return [org.to_dict() for org in orgs]

    @require_super_admin
    def post(self):
        org_name = request.json["org_name"]
        org_slug = request.json["org_slug"]
        org_settings = request.json["org_settings"]

        org = models.Organization.get_by_slug(org_slug)

        if org is not None:
            abort(409, message=f"Org '{org_slug}' already exists")
        org = models.Organization(name=org_name, slug=org_slug, settings=org_settings)

        admin_group = Group(
            name="admin",
            permissions=["admin"],
            org=org,
            type=Group.BUILTIN_GROUP,
        )
        default_group = Group(
            name="default",
            permissions=Group.DEFAULT_PERMISSIONS,
            org=org,
            type=Group.BUILTIN_GROUP,
        )

        models.db.session.add_all([org, admin_group, default_group])
        models.db.session.commit()
        admins = request.json["admins"]
        users = []
        for admin in admins:
            email = admin["email"]
            username = admin["username"]
            user = User(
                org=org,
                name=username,
                email=email,
                group_ids=[admin_group.id, default_group.id],
            )
            if "password" in admin:
                password = admin["password"]
                user.hash_password(password)
            users.append(user)
            models.db.session.add(user)

        models.db.session.commit()

        self.record_event(
            {"action": "create", "object_id": org.id, "object_type": "group"}
        )

        return {
            "org": org.to_dict(),
            "groups": {"default": default_group.to_dict(), "admin": admin_group.to_dict()},
            "users": [user.to_dict(True) for user in users]
        }

    @require_super_admin
    def patch(self):
        original_org_slug = request.json["original_org_slug"]
        org = models.Organization.get_by_slug(original_org_slug)
        if org is not None:
            if "org_name" in request.json:
                org.name = request.json["org_name"]
            if "org_slug" in request.json:
                org.slug = request.json["org_slug"]
            models.db.session.add(org)
            models.db.session.commit()
            self.record_event(
                {"action": "patch", "object_id": f"{original_org_slug} to {org.slug}/{org.name}",
                 "object_type": "organization"}
            )
        else:
            abort(404, message=f"Org '{original_org_slug}' not found")
        return [org.to_dict()]
