from django.contrib import admin

from .models import (
    Question,
    AssessmentAttempt,
    QuestionAttempt,
    AssessmentGenerationConfig,
)


admin.site.register(Question)
admin.site.register(QuestionAttempt)
admin.site.register(AssessmentAttempt)
admin.site.register(AssessmentGenerationConfig)
