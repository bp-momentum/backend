from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import (
    DoneExercises,
    Exercise,
    ExerciseInPlan,
    Trainer,
    TrainingSchedule,
    User,
)
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler, LeaderboardHandler, PlanHandler


PLAN_LENGTH = 50


class CreatePlanView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["name", "exercise"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        if not ErrorHandler.check_input_length(req_data["name"], PLAN_LENGTH):
            return ErrorHandler.length_wrong_response("Plan name")

        # check if user is allowed to request
        if not token["info"]["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "Not allowed to add or change trainig schedule",
                "data": {},
            }
            return Response(data)

        # checks if trainer exists
        if not Trainer.objects.filter(username=token["info"]["username"]).exists():
            data = {"success": False, "description": "no valid trainer", "data": {}}

            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=token["info"]["username"])

        # create plan and data
        plan = PlanHandler.create_plan(trainer, req_data["name"])
        if plan[0] == "invalid":
            # check if plan was created or changed
            if req_data.get("id") == None:
                return Response(plan[1])
            else:
                data = {
                    "success": False,
                    "description": "plan could not be changed",
                    "data": {"error": plan[1], "plan_id": req_data["id"]},
                }
                return Response(data)
        plan: TrainingSchedule = plan[1]

        list_of_exs_in_plan = req_data["exercise"]
        ex_in_plans = []
        for exs in list_of_exs_in_plan:
            # check if exercise is valid
            if not Exercise.objects.filter(id=int(exs["id"])).exists():
                # if exercise is invalid delete already created entries
                TrainingSchedule.objects.filter(id=plan.id).delete()
                for ex in ex_in_plans:
                    ExerciseInPlan.objects.filter(id=ex.id).delete()
                # check if plan was created or changed
                if req_data.get("id") == None:
                    data = {
                        "success": False,
                        "description": "no valid exercise",
                        "data": {"invalid_exercise": exs["id"]},
                    }
                else:
                    data = {
                        "success": False,
                        "description": "no valid exercise, plan was not changed",
                        "data": {
                            "invalid_exercise": exs["id"],
                            "plan_id": req_data["id"],
                        },
                    }

                return Response(data)

            res = PlanHandler.add_exercise_to_plan(
                plan,
                exs["date"],
                int(exs["sets"]),
                int(exs["repeats_per_set"]),
                int(exs["id"]),
            )
            # check if ExerciseInPlan entry could be created
            if res[0] == "invalid":
                # if new data could not be created, because it was invalid, delete already created entries
                TrainingSchedule.objects.filter(id=plan.id).delete()
                for ex in ex_in_plans:
                    ExerciseInPlan.objects.filter(id=ex.id).delete()
                # check if plan was created or changed
                if req_data.get("id") == None:
                    return Response(res[1])
                else:
                    data = {
                        "success": False,
                        "description": "plan could not be changed",
                        "data": {"error": res[1], "plan_id": req_data["id"]},
                    }
                    return Response(data)
            ex_in_plans.append(res[1])

        # check if plan was created or changed
        if req_data.get("id") == None:
            data = {
                "success": True,
                "description": "plan created",
                "data": {"plan_id": plan.id},
            }
        else:
            if not TrainingSchedule.objects.filter(
                id=int(req_data["id"]), visable=True
            ).exists():
                data = {
                    "success": False,
                    "description": "plan not accessable",
                    "data": {},
                }
                return Response(data)
            users = User.objects.filter(plan=req_data["id"])
            for user in users:
                PlanHandler.add_plan_to_user(user.username, plan.id)
            old_plan: TrainingSchedule = TrainingSchedule.objects.get(
                id=int(req_data["id"])
            )
            # check if a doneExercise relates to this plan
            needed = False
            for exip in ExerciseInPlan.objects.filter(plan=old_plan):
                if DoneExercises.objects.filter(exercise=exip).exists():
                    needed = True
                    break
            # if yes keep old plan and relate it to new one
            if needed:
                old_plan.visable = False
                old_plan.save(force_update=True)
            # else delete old plan
            else:
                TrainingSchedule.objects.filter(id=int(req_data["id"])).delete()
            data = {
                "success": True,
                "description": "plan was changed",
                "data": {"plan_id": plan.id},
            }

        return Response(data)


class AddPlanToUserView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["user"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check if user is allowed to request
        if not token["info"]["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "Not allowed to request list of exercises",
                "data": {},
            }
            return Response(data)

        res = PlanHandler.add_plan_to_user(
            username=req_data["user"], plan=req_data.get("plan")
        )

        # checks whether assigning was successful
        if res == "user_invalid":
            data = {"success": False, "description": "invalid user", "data": {}}
        elif res == "plan_invalid":
            data = {"success": False, "description": "plan does not exist", "data": {}}
        else:
            data = {"success": True, "description": "plan assigned to user", "data": {}}

        return Response(data)


class ShowPlanView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["plan"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # only trainers can request plan
        if not info["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "you are not allow to request all plans",
                "data": {},
            }
            return Response(data)

        # check if plan exists
        if not TrainingSchedule.objects.filter(
            id=int(req_data["plan"]), visable=True
        ).exists():
            data = {
                "success": False,
                "description": "Training schedule does not exist",
                "data": {},
            }
            return Response(data)

        # get exercises of this plan
        exs = PlanHandler.getListOfExercises(int(req_data["plan"]))
        plan: TrainingSchedule = TrainingSchedule.objects.get(id=int(req_data["plan"]))
        data = {
            "success": True,
            "description": "returned plan",
            "data": {"name": plan.name, "exercises": exs},
        }
        return Response(data)


class GetAllPlansView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # only trainers can request all plans
        if not info["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "you are not allow to request all plans",
                "data": {},
            }
            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=info["username"])
        # get all plans as list
        plans = TrainingSchedule.objects.filter(trainer=trainer, visable=True)
        plans_res = []
        # get all ids as list
        for plan in plans:
            plans_res.append({"id": plan.id, "name": plan.name})

        data = {
            "success": True,
            "description": "returning all plans",
            "data": {"plans": plans_res},
        }
        return Response(data)


class GetPlanOfUser(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # user gets own plan
        if info["account_type"] == "user":
            user: User = User.objects.get(username=info["username"])
            # check if user has plan assigned
            if user.plan == None:
                data = {
                    "success": True,
                    "description": "user has no plan assigned",
                    "data": {},
                }

                return Response(data)

            # get exercise in plan
            exs = PlanHandler.getListOfExercises(user.plan)
            data = {
                "success": True,
                "description": "returned plan of this account",
                "data": {"exercises": exs},
            }
            return Response(data)

        # trainers can request plan of users
        elif info["account_type"] == "trainer":
            # checking if it contains all arguments
            check = ErrorHandler.check_arguments(
                ["Session-Token"], request.headers, ["username"], request.data
            )
            if not check.get("valid"):
                data = {
                    "success": False,
                    "description": "Missing arguments",
                    "data": check.get("missing"),
                }
                return Response(data)
            req_data = dict(request.data)
            # check if user exists
            if not User.objects.filter(username=req_data["username"]).exists():
                data = {"success": False, "description": "unknown user", "data": {}}
                return Response(data)

            user: User = User.objects.get(username=req_data["username"])
            # check if user has plan assigned
            if user.plan == None:
                data = {
                    "success": False,
                    "description": "user has no plan assigned",
                    "data": {},
                }

                return Response(data)

            # get exercises in plan
            exs = PlanHandler.getListOfExercises(user.plan)
            data = {
                "success": True,
                "description": "returned plan of user",
                "data": {"exercises": exs},
            }
            return Response(data)

        else:
            data = {
                "success": False,
                "description": "no permission to request plan of user",
                "data": {},
            }
            return Response(data)


class DeletePlanView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["id"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # check if user is allowed to delete plans
        if not info["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "you are not allowed to delete plans",
                "data": {},
            }
            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=info["username"])
        # check if plan exists and belongs to trainer
        if not TrainingSchedule.objects.filter(
            id=int(req_data["id"]), trainer=trainer.id, visable=True
        ).exists():
            data = {
                "success": False,
                "description": "plan does not exist or does not belong to this trainer",
                "data": {},
            }
            return Response(data)

        users_affected = User.objects.filter(plan=req_data["id"])

        for u in users_affected:
            LeaderboardHandler.reset_leaderboard_entry(u.username)

        # delete plan/keep it, but unaccessable
        needed = False
        ts: TrainingSchedule = TrainingSchedule.objects.get(
            id=int(req_data["id"]), trainer=trainer.id
        )
        for exip in ExerciseInPlan.objects.filter(plan=ts):
            if DoneExercises.objects.filter(exercise=exip).exists():
                needed = True
                break
        if needed:
            for user in User.objects.filter(plan=ts):
                user.plan = None
                user.save(force_update=True)
            ts = TrainingSchedule.objects.get(
                id=int(req_data["id"]), trainer=trainer.id
            )
            ts.visable = False
            ts.save(force_update=True)
        else:
            TrainingSchedule.objects.filter(
                id=int(req_data["id"]), trainer=trainer.id
            ).delete()
        data = {"success": True, "description": "plan deleted", "data": {}}

        return Response(data)
