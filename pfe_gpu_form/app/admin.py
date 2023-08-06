from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SessionRequest, Etudiant
from .tasks import start_user_session


admin.site.register(Etudiant)

from django.contrib import admin
from celery.result import AsyncResult
from celery.worker.control import revoke 

class SessionRequestAdmin(admin.ModelAdmin):
    
    list_display = ('etudiant', 'session_choice', 'date_debut', 'date_fin', 'type', 'status')
    
    def save_model(self, request, obj, form, change):
        # If date_debut or date_fin is changed and a task id exists, then revoke the task
        if 'date_debut' in form.changed_data or 'date_fin' in form.changed_data:
            if obj.celery_task_id:
                revoke(task_id=obj.celery_task_id, terminate=True, state='REVOKED')  # Revoke the old task

                # Schedule a new task with the updated dates
                scheduled_start = obj.date_debut
                result = start_user_session.apply_async(args=[obj.etudiant.id, obj.id], eta=scheduled_start)
                obj.celery_task_id = result.id

        super().save_model(request, obj, form, change)

    # Admin action to revoke a scheduled task
    def cancel_scheduled_task(modeladmin, request, queryset):
        for obj in queryset:
            if obj.celery_task_id:
                revoke(obj.celery_task_id, terminate=True)
                obj.celery_task_id = ""
                obj.save()

    cancel_scheduled_task.short_description = "Cancel scheduled Celery tasks for selected sessions"

    actions = [cancel_scheduled_task]

admin.site.register(SessionRequest, SessionRequestAdmin)

