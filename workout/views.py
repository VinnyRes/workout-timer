import os
import json
import datetime
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WorkoutLog, WorkoutDetail
from django.utils import timezone


def _load_program():
    """Load program.json and return (program_data, current_week_schedule)."""
    path = os.path.join(settings.BASE_DIR, 'data', 'program.json')
    with open(path, encoding='utf-8') as f:
        program = json.load(f)

    today = datetime.date.today()
    # Current ISO week number (1-52)
    iso_week = today.isocalendar()[1]
    # Map to program week 1-12 (cycling)
    program_week_num = ((iso_week - 1) % 12) + 1

    week_data = next(
        (w for w in program['weeks'] if w['week'] == program_week_num), None
    )

    # Find today's scheduled workout (day 1=Mon ... day 7=Sun)
    today_dow = today.isoweekday()  # 1=Monday … 7=Sunday
    today_day = None
    if week_data:
        for d in week_data['days']:
            if d['day'] == today_dow:
                today_day = d
                break

    return program, week_data, today_day, program_week_num


def index(request):
    file_path = os.path.join(settings.BASE_DIR, 'data', 'ovelser_v2.xlsx')
    df = pd.read_excel(file_path)

    df['Group'] = df['Group'].fillna('Default')
    df['Name'] = df['Name'].fillna('Default')

    workout_names = sorted(df['Name'].unique())
    selected_workout = request.GET.get('workout')
    selected_type = None
    selected_workout_type = None  # ✅ Initialize here
    full_sequence = []
    total_time = 0

    if selected_workout:
        df = df[df['Name'] == selected_workout]

        if not df.empty:
            selected_type = df['Type'].iloc[0]
            selected_workout_type = df['Workout_type'].iloc[0]

            if selected_workout_type == "Calisthenics":
                for group_name, group_df in df.groupby('Group'):
                    sets = int(group_df['Sets'].max())
                    for _ in range(sets):
                        for _, row in group_df.iterrows():
                            name = row['Exercise']
                            duration = int(row.get('Duration', 0))
                            rest = int(row.get('Rest', 0))

                            full_sequence.append({'exercise': name, 'duration': duration})
                            total_time += duration

                            if rest > 0:
                                full_sequence.append({'exercise': 'Rest', 'duration': rest})
                                total_time += rest
            else:
                # For Weights: just collect the structure; timer is not used
                for _, row in df.iterrows():
                    full_sequence.append({
                        'exercise': row['Exercise'],
                        'kilos': row.get('Kilos', ''),
                        'sets': row.get('Sets', ''),
                        'reps': row.get('Reps', ''),
                    })

    # Load training program
    program, week_data, today_day, program_week_num = _load_program()

    context = {
        'exercises': full_sequence,
        'total_time': total_time,
        'workout_names': workout_names,
        'selected_workout': selected_workout,
        'selected_workout_type': selected_workout_type,
        'selected_type': selected_type,
        'completed_logs': WorkoutLog.objects.all().order_by('-date_completed'),
        'program': program,
        'week_data': week_data,
        'today_day': today_day,
        'program_week_num': program_week_num,
    }

    return render(request, 'index.html', context)

def weights_log(request):
    logs = WorkoutLog.objects.filter(type="Weights").order_by('-date_completed')
    details = WorkoutDetail.objects.select_related('workout').filter(workout__in=logs)

    context = {
        'logs': logs,
        'details': details
    }
    return render(request, 'weights_log.html', context)

def save_workout_log(request):
    if request.method == "POST":
        workout_name = request.POST.get('name')
        workout_type = request.POST.get('type', '')
        duration = request.POST.get('duration', 0)

        if not workout_name:
            return JsonResponse({'status': 'error', 'message': 'Missing workout name'}, status=400)

        # Create the main workout log
        log = WorkoutLog.objects.create(name=workout_name, type=workout_type,duration=int(duration) if duration else 0, date_completed=timezone.now())

        # Only process details for "Weights"
        if workout_type == "Weights":
            exercises = request.POST.getlist("exercise[]")
            kilos = request.POST.getlist("kilos[]")
            reps = request.POST.getlist("reps[]")
            sets = request.POST.getlist("sets[]")

            for ex, kg, r, s in zip(exercises, kilos, reps, sets):
                try:
                    WorkoutDetail.objects.create(
                        workout=log,
                        exercise=ex,
                        kilos=int(kg),
                        reps=int(r),
                        sets=int(s)
                    )
                except (ValueError, TypeError) as e:
                    return JsonResponse({'status': 'error', 'message': f'Invalid data: {e}'}, status=400)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

def save_workout(request):
    if request.method == "POST":
        workout_name = request.POST.get('name')
        workout_type = request.POST.get('type', '')  # Optional

        if workout_name:
            WorkoutLog.objects.create(name=workout_name, type=workout_type)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# workout/views.py
import pandas as pd
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import WorkoutLog

def summary(request):
    logs = WorkoutLog.objects.all().order_by("date_completed")

    if not logs.exists():
        return render(request, "summary.html", {
            "chart_minutes": [], "chart_counts": [], "labels": [],
            "avg_2025_counts": 0, "avg_2025_minutes": 0,
            "weekly_2026_counts": [], "weekly_2026_minutes": [], "labels_2026": [],
            "completion_pct": 0, "completed_planned": 0, "total_planned": 0,
        })

    df = pd.DataFrame(list(logs.values("date_completed", "duration")))
    df["date_completed"] = pd.to_datetime(df["date_completed"])
    df["duration_minutes"] = df["duration"].apply(lambda d: d / 60 if d > 180 else d)
    df["week"] = df["date_completed"].dt.strftime("%G-%V")
    df["year"] = df["date_completed"].dt.year

    # ── All-time weekly (existing charts) ────────────────────────────────────
    weekly_minutes = df.groupby("week")["duration_minutes"].sum()
    weekly_counts  = df.groupby("week")["date_completed"].count()
    labels         = weekly_minutes.index.tolist()

    # ── 2025 averages ─────────────────────────────────────────────────────────
    df25 = df[df["year"] == 2025]
    if not df25.empty:
        avg_2025_counts  = round(df25.groupby("week")["date_completed"].count().mean(), 1)
        avg_2025_minutes = round(df25.groupby("week")["duration_minutes"].sum().mean(), 1)
    else:
        avg_2025_counts  = 0
        avg_2025_minutes = 0

    # ── 2026 per-week ─────────────────────────────────────────────────────────
    df26 = df[df["year"] == 2026]
    if not df26.empty:
        w26_counts  = df26.groupby("week")["date_completed"].count()
        w26_minutes = df26.groupby("week")["duration_minutes"].sum()
        labels_2026         = w26_counts.index.tolist()
        weekly_2026_counts  = w26_counts.tolist()
        weekly_2026_minutes = [round(v, 1) for v in w26_minutes.reindex(labels_2026, fill_value=0).tolist()]
    else:
        labels_2026         = []
        weekly_2026_counts  = []
        weekly_2026_minutes = []

    # ── Completion tracker ────────────────────────────────────────────────────
    # Program started week 1 of current year; count planned sessions (6/week)
    # from program start up to today, compare with actual logged sessions.
    import datetime, json as _json
    program_path = os.path.join(settings.BASE_DIR, 'data', 'program.json')
    with open(program_path, encoding='utf-8') as f:
        program = _json.load(f)

    today = datetime.date.today()
    # Program start date: stored in data/program_start.txt
    # If file doesn't exist, create it with today's date.
    start_file = os.path.join(settings.BASE_DIR, 'data', 'program_start.txt')
    if not os.path.exists(start_file):
        with open(start_file, 'w') as sf:
            sf.write(today.isoformat())
    with open(start_file) as sf:
        program_start = datetime.date.fromisoformat(sf.read().strip())

    days_elapsed = (today - program_start).days + 1  # inclusive
    if days_elapsed < 0:
        days_elapsed = 0

    # Count planned non-rest days up to today (cycling 12 weeks × 7 days)
    total_planned = 0
    completed_planned = 0
    for day_offset in range(days_elapsed):
        d = program_start + datetime.timedelta(days=day_offset)
        # Which program week (0-indexed cycling)
        week_idx = (day_offset // 7) % 12
        dow = d.isoweekday()  # 1=Mon…7=Sun
        week_data = program["weeks"][week_idx]
        day_data = next((x for x in week_data["days"] if x["day"] == dow), None)
        if day_data and day_data["workout"] is not None:
            total_planned += 1
            # Check if a workout was logged on this date
            logged = logs.filter(
                date_completed__date=d,
                type__in=["Calisthenics", "Full Body", "Core", "Butt", "Arms, core",
                           "Chest, back", "Core, back", "Butt, legs"]
            ).exists()
            if not logged:
                # Also accept any workout logged that day (type may be stored as focus)
                logged = logs.filter(date_completed__date=d).exists()
            if logged:
                completed_planned += 1

    completion_pct = round(100 * completed_planned / total_planned, 1) if total_planned else 0

    return render(request, "summary.html", {
        "labels":        labels,
        "chart_minutes": [round(v, 1) for v in weekly_minutes.tolist()],
        "chart_counts":  weekly_counts.tolist(),
        "avg_2025_counts":       avg_2025_counts,
        "avg_2025_minutes":      avg_2025_minutes,
        "labels_2026":           labels_2026,
        "weekly_2026_counts":    weekly_2026_counts,
        "weekly_2026_minutes":   weekly_2026_minutes,
        "completion_pct":        completion_pct,
        "completed_planned":     completed_planned,
        "total_planned":         total_planned,
        "program_start":         program_start.strftime("%d. %B %Y").lstrip("0"),
    })