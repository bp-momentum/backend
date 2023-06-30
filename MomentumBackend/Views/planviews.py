from ..models import (
    Account,
    Exercise,
    ExerciseExecution,
    ExerciseInPlan,
    TrainingSchedule,
)
from django.http import JsonResponse
from django.contrib.auth.models import User
from MomentumBackend.helper.utils import get_request_data, login_required_401, restrict_roles_403
from ..helper.handlers import ErrorHandler

PLAN_LENGTH = 50


@login_required_401
@restrict_roles_403([Account.TRAINER])
def save_plan(request):
    data = get_request_data(request)
    # INPUT VALIDATION
    check = ErrorHandler.check_arguments(
        ["name", "exercise"], data
    )
    if not check.get("valid"):
        return check.get("response")

    if len(data["name"]) > PLAN_LENGTH:
        return JsonResponse({
            "success": False,
            "description": "Name is too long",
            "data": {},
        })

    for exs in data["exercise"]:
        # check if exercise is valid
        if not Exercise.objects.filter(id=int(exs["id"])).exists():
            return JsonResponse({
                "success": False,
                "description": "Invalid exercise id, no changes were committed",
                "data": {},
            })

    # COMMIT CHANGES

    # TODO(urgent): a new plan needs to always be created

    plan = TrainingSchedule.objects.create(
        trainer=request.user,
        name=data["name"],
    )
    plan.save()

    for exs in data["exercise"]:
        exercise = Exercise.objects.filter(id=int(exs["id"])).first()
        ex_in_plan = ExerciseInPlan.objects.create(
            date=exs["date"],
            sets=int(exs["sets"]),
            repeats_per_set=int(exs["repeats_per_set"]),
            exercise=exercise,
            plan=plan,
        )
        ex_in_plan.save()

    # check if plan was created or changed
    if data.get("id") == None:
        return JsonResponse({
            "success": True,
            "description": "plan created",
            "data": {"plan_id": plan.id},
        })
    else:
        if not TrainingSchedule.objects.filter(
            id=int(data["id"]), visible=True
        ).exists():
            return JsonResponse({
                "success": False,
                "description": "plan not accessable",
                "data": {},
            })
        users = Account.objects.filter(plan=data["id"])
        for user in users:
            user.plan = plan
            user.save()
        old_plan: TrainingSchedule = TrainingSchedule.objects.get(
            id=int(data["id"])
        )
        # check if a doneExercise relates to this plan
        needed = False
        for exip in ExerciseInPlan.objects.filter(plan=old_plan):
            if ExerciseExecution.objects.filter(exercise=exip).exists():
                needed = True
                break
        # if yes keep old plan and relate it to new one
        if needed:
            old_plan.visible = False
            old_plan.save(force_update=True)
        # else delete old plan
        else:
            TrainingSchedule.objects.filter(id=int(data["id"])).delete()
        return JsonResponse({
            "success": True,
            "description": "plan was changed",
            "data": {"plan_id": plan.id},
        })


@login_required_401
@restrict_roles_403([Account.TRAINER])
def add_plan_to_user(request):
    data = get_request_data(request)
    check = ErrorHandler.check_arguments(
        ["user", "plan"], data
    )
    if not check.get("valid"):
        return check.get("response")

    user = User.objects.filter(username=data["user"]).first()
    if user is None:
        return JsonResponse({
            "success": False,
            "description": "User does not exist.",
            "data": {},
        })

    plan = TrainingSchedule.objects.filter(
        id=int(data["plan"])).first()
    if plan is None:
        return JsonResponse({
            "success": False,
            "description": "Plan does not exist.",
            "data": {},
        })

    user.account.plan = plan
    user.account.save()

    return JsonResponse({"success": True, "description": "plan assigned to user", "data": {}})


@login_required_401
@restrict_roles_403([Account.TRAINER])
def get_plan(_, plan_id):
    plan = TrainingSchedule.objects.filter(
        id=plan_id, visible=True
    ).first()
    # check if plan exists
    if plan is None:
        return JsonResponse({
            "success": False,
            "description": "Training schedule does not exist",
            "data": {},
        })

    exs = []
    plan_data = ExerciseInPlan.objects.filter(plan=plan)
    for ex in plan_data:
        ex_id = ex.exercise.id
        sets = ex.sets
        rps = ex.repeats_per_set
        date = ex.date
        exs.append(
            {
                "exercise_plan_id": ex.id,
                "id": ex_id,
                "sets": sets,
                "repeats_per_set": rps,
                "date": date,
            }
        )

    return JsonResponse({
        "success": True,
        "description": "returned plan",
        "data": {"name": plan.name, "exercises": exs},
    })


@login_required_401
@restrict_roles_403([Account.TRAINER])
def get_all_plans(request):
    # get all plans as list
    plans = TrainingSchedule.objects.filter(trainer=request.user, visible=True)
    plans_res = []
    # get all ids as list
    for plan in plans:
        plans_res.append({"id": plan.id, "name": plan.name})

    return JsonResponse({
        "success": True,
        "description": "returning all plans",
        "data": {"plans": plans_res},
    })


@login_required_401
@restrict_roles_403([Account.TRAINER, Account.PLAYER])
def get_plan_of_user(request):
    data = get_request_data(request)
    # user gets own plan
    if request.user.account.role == "player":
        user = request.user
    else:
        check = ErrorHandler.check_arguments(
            ["username"], data
        )
        if not check.get("valid"):
            return check.get("response")
        user = User.objects.filter(username=data["username"]).first()
        if user is None:
            return JsonResponse({
                "success": False,
                "description": "User does not exist.",
                "data": {},
            })

    # check if user has plan assigned
    if user.account.plan == None:
        return JsonResponse({
            "success": False,
            "description": "User has no plan assigned.",
            "data": {},
        })

    exs = []
    plan_data = ExerciseInPlan.objects.filter(plan=user.account.plan)
    for ex in plan_data:
        ex_id = ex.exercise.id
        sets = ex.sets
        rps = ex.repeats_per_set
        date = ex.date
        exs.append(
            {
                "exercise_plan_id": ex.id,
                "id": ex_id,
                "sets": sets,
                "repeats_per_set": rps,
                "date": date,
            }
        )
    return JsonResponse({
        "success": True,
        "description": "returned plan of user",
        "data": {"exercises": exs},
    })


@login_required_401
@restrict_roles_403([Account.TRAINER])
def delete_plan(request, plan_id):
    plan = TrainingSchedule.objects.filter(
        id=plan_id, trainer=request.user, visible=True
    ).first()
    # check if plan exists and belongs to trainer
    if plan is None:
        return JsonResponse({
            "success": False,
            "description": "Training schedule does not exist or does not belong to trainer",
            "data": {},
        })

    # delete plan/keep it, but unaccessable
    needed = False
    for exip in ExerciseInPlan.objects.filter(plan=plan):
        if ExerciseExecution.objects.filter(exercise=exip).exists():
            needed = True
            break

    if needed:
        for user in User.objects.filter(plan=plan):
            user.plan = None
            user.save()
        plan.visible = False
        plan.save()
    else:
        plan.delete()

    return JsonResponse({"success": True, "description": "plan deleted", "data": {}})
