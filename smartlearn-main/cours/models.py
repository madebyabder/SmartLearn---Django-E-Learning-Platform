from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Inscription(models.Model):
    cours = models.ForeignKey('Cours', on_delete=models.CASCADE)
    apprenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cours', 'apprenant')


class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.module.title} : {self.score}%"

class Category(models.TextChoices):
    SCIENCES = "sciences", "Sciences"
    LANGUAGES = "languages", "Languages"
    DEVWEB = "devweb", "Web Development"
    CYBERSECURITY = "cybersecurity", "Cybersecurity"
    MACHINE_LEARNING = "machine_learning", "Machine Learning"

class DifficultyLevel(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"

class Cours(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices)
    difficulty_level = models.CharField(max_length=20, choices=DifficultyLevel.choices, default=DifficultyLevel.BEGINNER)
    image = models.URLField(blank=True, null=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Module(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order_position = models.IntegerField()

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()  # reverse relation to Question model



class Question(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"Q: {self.text} (Module: {self.module.title})"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} [{'✔' if self.is_correct else '✘'}]"


class Contenu(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contenus')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.URLField(blank=True, null=True)

    @property
    def video_embed_url(self):
        """Convert YouTube URL to embed format."""
        if not self.video:
            return None
        if 'youtube.com/watch?v=' in self.video:
            video_id = self.video.split('watch?v=')[1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in self.video:
            video_id = self.video.split('youtu.be/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        return self.video

    def __str__(self):
        return self.title
