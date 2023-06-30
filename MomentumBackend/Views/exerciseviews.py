import datetime
from django.http import JsonResponse
from django.utils.timezone import make_aware
from MomentumBackend.helper.utils import get_request_data, login_required_401, restrict_roles_403
from ..models import Account, Exercise, ExerciseExecution, ExerciseInPlan, PlayerExercisePreferences, SetStats
from ..helper.handlers import ErrorHandler


def get_exercise(request, exercise_id):
    exercise = Exercise.objects.filter(id=exercise_id).first()
    # check if requested exercise exists
    if exercise is None:
        return JsonResponse({
            "success": False,
            "description": "no exercise with this id exists",
            "data": {},
        })

    if request.user.is_authenticated:
        description = exercise.description.get(request.user.account.language)
    else:
        description = exercise.description.get("en")

    return JsonResponse({
        "success": True,
        "description": "Returned data",
        "data": {
            "title": exercise.title,
            "description": description,
            "video": exercise.video,
            "expectation": exercise.expectation,
        },
    })


@login_required_401
@restrict_roles_403([Account.PLAYER])
def get_exercise_preferences(request, exercise_id):
    exercise = Exercise.objects.filter(id=exercise_id).first()

    # check if requested exercise exists
    if exercise is None:
        return JsonResponse({
            "success": False,
            "description": "No exercise with this id exists",
            "data": {},
        })

    # check if user wants to get instructions
    personal_prefs = PlayerExercisePreferences.objects.filter(
        user=request.user, exercise=exercise
    ).first()

    # default values
    visible = personal_prefs.open_instruction_default if personal_prefs else True
    speed = personal_prefs.speed if personal_prefs else 10

    return JsonResponse({
        "success": True,
        "description": "Returned data",
        "data": {
            "visible": visible,
            "speed": speed,
        },
    })


@login_required_401
@restrict_roles_403([Account.PLAYER])
def set_exercise_preferences(request, exercise_id):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        {
            "visible": {
                "name": "visible",
                "required": False
            }, "speed": {
                "name": "speed",
                "required": False
            },
        },
        data
    )
    if not check.get("valid"):
        return check.get("response")

    exercise = Exercise.objects.filter(id=exercise_id).first()

    # check if requested exercise exists
    if exercise is None:
        return JsonResponse({
            "success": False,
            "description": "No exercise with this id exists",
            "data": {},
        })

    if "visible" in data:
        obj, _ = PlayerExercisePreferences.objects.get_or_create(
            user=request.user, exercise=exercise
        )
        obj.open_instruction_default = data["visible"]
        obj.save()

    if "speed" in data:
        obj, _ = PlayerExercisePreferences.objects.get_or_create(
            user=request.user, exercise=exercise
        )
        obj.speed = data["speed"]
        obj.save()

    obj = PlayerExercisePreferences.objects.get(
        user=request.user, exercise=exercise
    )

    return JsonResponse({
        "success": True,
        "description": "Changed preferences of instructions",
        "data": {
            "visible": obj.open_instruction_default,
            "speed": obj.speed,
        },
    })


@login_required_401
@restrict_roles_403([Account.TRAINER])
def get_all_exercises(request):
    # get all exercises as list
    exercises = Exercise.objects.all()
    exs_res = []
    # get all ids as list
    for ex in exercises:
        exs_res.append({"id": ex.id, "title": ex.title})

    return JsonResponse({
        "success": True,
        "description": "returning all exercises",
        "data": {"exercises": exs_res},
    })


@login_required_401
@restrict_roles_403([Account.PLAYER])
def get_done_exercises(request):
    if request.user.account.plan is None:
        return JsonResponse({
            "success": False,
            "description": "User has no plan assigned",
            "data": {},
        })

    # list of all done in this week
    maybedone = ExerciseExecution.objects.filter(
        user=request.user,
        date__gt=make_aware(datetime.datetime.now() -
                            datetime.timedelta(days=7))
    )

    done = []
    for d in maybedone:
        stats = SetStats.objects.filter(exercise=d)
        if stats.count() == d.exercise.sets:
            done.append(d)

    # list of all exercises to done
    all = ExerciseInPlan.objects.filter(plan=request.user.account.plan)
    out = []
    for a in all:
        done_found = False
        for d in done:
            if done_found:
                continue
            if a.id == d.exercise.id:
                out.append(
                    {
                        "exercise_plan_id": a.id,
                        "id": a.exercise.id,
                        "date": a.date,
                        "sets": a.sets,
                        "repeats_per_set": a.repeats_per_set,
                        "done": True,
                    }
                )
                done_found = True
                break
        if done_found:
            continue

        out.append(
            {
                "exercise_plan_id": a.id,
                "id": a.exercise.id,
                "date": a.date,
                "sets": a.sets,
                "repeats_per_set": a.repeats_per_set,
                "done": False,
            }
        )

    return JsonResponse({
        "success": True,
        "description": "Returned list of Exercises and if its done",
        "data": {"name": request.user.account.plan.name, "exercises": out},
    })


@login_required_401
@restrict_roles_403([Account.PLAYER])
def get_done_exercises_in_month(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["month", "year"], data
    )
    if not check.get("valid"):
        return check.get("response")

    if (data["month"] < 1) or (data["month"] > 12):
        return JsonResponse({"success": False, "description": "invalid month", "data": {}})

    maybedone = ExerciseExecution.objects.filter(
        user=request.user,
        date__range=(
            make_aware(datetime.datetime(
                data["year"], data["month"], 1, 0, 0, 0)),
            make_aware(datetime.datetime(
                data["year"], data["month"], 31, 23, 59, 59))
        )
    )

    done = []
    for d in maybedone:
        stats = SetStats.objects.filter(exercise=d)
        if stats.count() == d.exercise.sets:
            done.append(d)

    # list of all exercises to done
    all = ExerciseInPlan.objects.filter(plan=request.user.account.plan)
    out = []
    for a in all:
        done_found = False
        for d in done:
            if done_found:
                continue
            if a.id == d.exercise.id:
                out.append(
                    {
                        "exercise_plan_id": a.id,
                        "id": a.exercise.id,
                        "date": a.date,
                        "sets": a.sets,
                        "repeats_per_set": a.repeats_per_set,
                        "done": True,
                    }
                )
                done_found = True
                break
        if done_found:
            continue

        out.append(
            {
                "exercise_plan_id": a.id,
                "id": a.exercise.id,
                "date": a.date,
                "sets": a.sets,
                "repeats_per_set": a.repeats_per_set,
                "done": False,
            }
        )

    return JsonResponse({
        "success": True,
        "description": "Returning exercises done in this month",
        "data": {"done": out},
    })
