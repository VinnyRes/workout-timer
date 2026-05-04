import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WorkoutLog, WorkoutDetail
from django.utils import timezone

def index(request):
    file_path = os.path.join(settings.BASE_DIR, 'data', 'ovelser.xlsx')
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

    context = {
        'exercises': full_sequence,
        'total_time': total_time,
        'workout_names': workout_names,
        'selected_workout': selected_workout,
        'selected_workout_type': selected_workout_type,  # ✅ Now always defined
        'selected_type': selected_type,
        'completed_logs': WorkoutLog.objects.all().order_by('-date_completed'),
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
            "chart_minutes": [],
            "chart_counts": [],
            "labels": []
        })

    import pandas as pd

    # Convert queryset to DataFrame
    df = pd.DataFrame(list(logs.values("date_completed", "duration")))

    # Convert to datetime
    df["date_completed"] = pd.to_datetime(df["date_completed"])

    # ✅ Normalize duration:
    # If duration is > 180 → assume it's seconds and convert
    df["duration_minutes"] = df["duration"].apply(
        lambda d: d / 60 if d > 180 else d
    )

    # Add a "week" column (year-week)
    df["week"] = df["date_completed"].dt.strftime("%G-%V")

    # Group by week
    weekly_minutes = df.groupby("week")["duration_minutes"].sum()
    weekly_counts = df.groupby("week")["date_completed"].count()

    labels = weekly_minutes.index.tolist()
    chart_minutes = weekly_minutes.tolist()
    chart_counts = weekly_counts.tolist()

    return render(request, "summary.html", {
        "labels": labels,
        "chart_minutes": chart_minutes,
        "chart_counts": chart_counts,
    })