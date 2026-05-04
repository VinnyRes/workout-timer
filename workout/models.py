
# Create your models here.
from django.db import models

class WorkoutLog(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    duration = models.IntegerField(default=0)
    date_completed = models.DateTimeField()
    

    def __str__(self):
        return f"{self.name} ({self.type}) on {self.date_completed.strftime('%Y-%m-%d')}"
    
class WorkoutDetail(models.Model):
    workout = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE, related_name='details')
    exercise = models.CharField(max_length=100)
    kilos = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    sets = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.exercise}: {self.sets} x {self.reps} @ {self.kilos}kg"