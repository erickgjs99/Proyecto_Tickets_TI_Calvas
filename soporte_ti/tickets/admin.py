from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ticket, Comment, UserProfile

# Inline para mostrar perfil en el admin de usuarios
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'

# Extender UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_cargo', 'get_departamento')
    
    def get_cargo(self, obj):
        return obj.profile.cargo if hasattr(obj, 'profile') else '-'
    get_cargo.short_description = 'Cargo'
    
    def get_departamento(self, obj):
        return obj.profile.departamento if hasattr(obj, 'profile') else '-'
    get_departamento.short_description = 'Departamento'

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cargo', 'departamento', 'telefono', 'extension', 'celular']
    search_fields = ['user__username', 'cargo', 'departamento']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'title', 'user', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['ticket_number', 'title', 'description', 'user__username']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username', 'ticket__ticket_number']