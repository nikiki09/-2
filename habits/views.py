import json
from datetime import date

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from .models import Habit, HabitLog

from django.db.models import Exists, OuterRef


def habits_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    today = date.today()
    q = (request.GET.get("q") or "").strip()

    qs = Habit.objects.order_by("-id")
    if q:
        qs = qs.filter(name__icontains=q)

    qs = qs.annotate(
        done_today=Exists(
            HabitLog.objects.filter(habit_id=OuterRef("pk"), done_date=today)
        )
    )

    data = []
    for h in qs:
        data.append({
            "id": h.id,
            "name": h.name,
            "frequency": h.frequency,
            "is_active": h.is_active,
            "done_today": bool(h.done_today),
            "created_at": h.created_at.isoformat(),
        })

    return JsonResponse({"habits": data})


@csrf_exempt
def habits_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = (payload.get("name") or "").strip()
    frequency = (payload.get("frequency") or "daily").strip()

    if not name:
        return JsonResponse({"error": "name is required"}, status=400)

    if frequency not in ("daily", "weekly"):
        return JsonResponse({"error": "frequency must be daily or weekly"}, status=400)

    h = Habit.objects.create(name=name, frequency=frequency, is_active=True)
    return JsonResponse({
        "id": h.id,
        "name": h.name,
        "frequency": h.frequency,
        "is_active": h.is_active,
    }, status=201)


@csrf_exempt
def habit_done_today(request, habit_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        habit = Habit.objects.get(id=habit_id, is_active=True)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "habit not found"}, status=404)

    today = date.today()
    obj, created = HabitLog.objects.get_or_create(habit=habit, done_date=today)

    return JsonResponse({
        "habit_id": habit.id,
        "done_date": today.isoformat(),
        "created": created,
    })


@csrf_exempt
def habit_undone_today(request, habit_id: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        habit = Habit.objects.get(id=habit_id, is_active=True)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "habit not found"}, status=404)

    today = date.today()

    deleted_count, _ = HabitLog.objects.filter(habit=habit, done_date=today).delete()

    return JsonResponse({
        "habit_id": habit.id,
        "done_date": today.isoformat(),
        "deleted": deleted_count,
    })


def habit_stats(request, habit_id: int):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "habit not found"}, status=404)

    total_done = HabitLog.objects.filter(habit=habit).count()

    return JsonResponse({
        "habit_id": habit.id,
        "name": habit.name,
        "total_done": total_done,
    })


@csrf_exempt
def habit_delete(request, habit_id: int):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])

    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "habit not found"}, status=404)

    habit.delete()
    return JsonResponse({"deleted": True, "habit_id": habit_id})
