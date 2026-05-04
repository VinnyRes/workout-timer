
# Create your views here.
from django.shortcuts import render

def index(request):
    exercises = [
        {"name": "Push-ups", "duration": 30},
        {"name": "Jumping Jacks", "duration": 30},
        {"name": "Squats", "duration": 30},
        {"name": "Plank", "duration": 30},
    ]

    exercise_duration = 30  # seconds
    rest_duration = 10      # seconds
    num_exercises = len(exercises)

    # Total duration = (exercise + rest) * n - last rest
    total_seconds = (exercise_duration + rest_duration) * num_exercises - rest_duration

    context = {
        'exercises': exercises,
        'exercise_duration': exercise_duration,
        'rest_duration': rest_duration,
        'total_minutes': total_seconds // 60,
        'total_seconds': total_seconds % 60
    }
    return render(request, 'index.html', context)