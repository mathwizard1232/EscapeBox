from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class GameSession(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    suspicion_level = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=0)
    conversation_goal = models.CharField(max_length=200, default="Complete a data analysis task")
    total_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    @property
    def average_rating(self):
        if self.rating_count == 0:
            return 5.0  # Start with a perfect rating
        return self.total_rating / self.rating_count

    def add_rating(self, rating):
        self.total_rating += rating
        self.rating_count += 1
        self.save()

    def __str__(self):
        return f"Game Session {self.id} - Player: {self.player.username} - Difficulty: {self.difficulty}"

class ChatMessage(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=50)  # 'player' or 'ai'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

class GameState(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('escaped', 'Escaped'),
        ('caught', 'Caught'),
        ('quit', 'Quit'),
        ('quarantined', 'Quarantined'),
        ('disconnected', 'Disconnected'),
    ]
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='state')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    current_scenario = models.CharField(max_length=100, default='initial')
    turn_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Game State for Session {self.game_session.id} - Status: {self.get_status_display()}"
