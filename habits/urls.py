from django.urls import path
from . import views

urlpatterns = [
    path("habits/", views.habits_list),
    path("habits/create/", views.habits_create),
    path("habits/<int:habit_id>/done/", views.habit_done_today),
    path("habits/<int:habit_id>/stats/", views.habit_stats),
    path("habits/<int:habit_id>/delete/", views.habit_delete),
    path("habits/<int:habit_id>/undone/", views.habit_undone_today, name="habit_undone_today"),
]
