"""
Módulo: views.py
Aplicación: tickets

Descripción:
------------
Contiene las vistas del sistema de gestión de tickets TI.
Incluye paneles para usuarios y administradores, operaciones CRUD sobre tickets,
manejo de comentarios y generación de reportes PDF.

Autor: Ing. Erick Jaramillo
Fecha: Octubre 2025
"""

from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import Ticket, Comment
from .forms import TicketForm, CommentForm, TicketUpdateForm
from .pdf_generator import TicketPDFGenerator




# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------
def is_staff(user):
    """
    Verifica si el usuario tiene permisos administrativos.

    Args:
        user (User): Objeto de usuario autenticado.

    Returns:
        bool: True si es staff o superusuario, False en caso contrario.
    """
    return user.is_staff or user.is_superuser


# -----------------------------------------------------------------------------
# VISTAS PARA USUARIOS REGULARES
# -----------------------------------------------------------------------------
@login_required
def user_dashboard(request):
    """
    Vista principal del usuario.
    Muestra todos los tickets creados por el usuario autenticado
    junto con estadísticas básicas por estado.
    """
    tickets = Ticket.objects.filter(user=request.user)

    context = {
        'tickets': tickets,
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status='open').count(),
        'in_progress_tickets': tickets.filter(status='in_progress').count(),
    }
    return render(request, 'tickets/user_dashboard.html', context)


@login_required
def create_ticket(request):
    """
    Permite a un usuario crear un nuevo ticket de soporte.
    Asocia automáticamente el ticket con el usuario autenticado.
    """
    form = TicketForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        messages.success(request, f'Ticket {ticket.ticket_number} creado exitosamente.')
        return redirect('user_dashboard')

    return render(request, 'tickets/create_ticket.html', {'form': form})


@login_required
def ticket_detail(request, ticket_id):
    """
    Muestra los detalles de un ticket y permite agregar comentarios.

    Args:
        ticket_id (int): ID del ticket solicitado.

    Seguridad:
        Solo el dueño del ticket o personal autorizado puede acceder.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verificación de permisos
    if not (request.user.is_staff or ticket.user == request.user):
        messages.error(request, 'No tienes permiso para ver este ticket.')
        return redirect('user_dashboard')

    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.user = request.user
        comment.save()
        messages.success(request, 'Comentario agregado exitosamente.')
        return redirect('ticket_detail', ticket_id=ticket.id)

    context = {
        'ticket': ticket,
        'form': form,
        'comments': ticket.comments.select_related('user').all(),
    }
    return render(request, 'tickets/ticket_detail.html', context)


# -----------------------------------------------------------------------------
# VISTAS ADMINISTRATIVAS
# -----------------------------------------------------------------------------
@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    """
    Panel de administración.
    Permite a los usuarios con permisos de staff ver y filtrar todos los tickets.

    Funcionalidades:
        - Filtro por estado, prioridad, categoría, mes y año.
        - Búsqueda por número de ticket, título o nombre de usuario.
        - Estadísticas globales del sistema.
    """
    tickets = Ticket.objects.select_related('user', 'assigned_to').all()

    # --- Filtros dinámicos (GET) ---
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    priority = request.GET.get('priority', '').strip()
    category = request.GET.get('category', '').strip()
    month = request.GET.get('month', '').strip()
    year = request.GET.get('year', '').strip()
    user = request.GET.get('user', '').strip()
    assign = request.GET.get('assigned_to', '').strip()
    assigned_to_id = request.GET.get('assigned_to', '').strip() 
    # --- Filtro de búsqueda ---
    if search:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search) |
            Q(title__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(assigned_to__username__icontains=search) |  
            Q(assigned_to__first_name__icontains=search) |  
            Q(assigned_to__last_name__icontains=search)  
        )

    # --- Filtros específicos ---
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if category:
        tickets = tickets.filter(category=category)
    if assign:
        tickets = tickets.filter(assing=assign)
        
# Nuevo: Filtro por 'assigned_to' (usando el ID del usuario)
    if assigned_to_id:
        # Si el valor es 'unassigned', filtra por assigned_to=None
        if assigned_to_id == 'unassigned':
            tickets = tickets.filter(assigned_to__isnull=True)
        else:
            try:
                tickets = tickets.filter(assigned_to_id=int(assigned_to_id))
            except ValueError:
                # Manejar el caso de un ID no válido, si es necesario.
                pass 
        
    

    # --- Filtros temporales ---
    if month and year:
        tickets = tickets.filter(created_at__year=int(year), created_at__month=int(month))
    elif month:
        tickets = tickets.filter(created_at__year=datetime.now().year, created_at__month=int(month))
    elif year:
        tickets = tickets.filter(created_at__year=int(year))

    # --- Estadísticas globales ---
    stats = {
        'total_tickets': Ticket.objects.count(),
        'open_tickets': Ticket.objects.filter(status='open').count(),
        'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
        'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
        'closed_tickets': Ticket.objects.filter(status='closed').count(),
        'unassigned_tickets': Ticket.objects.filter(assigned_to__isnull=True).count(),
    }

    # --- Datos auxiliares (años y meses) ---
    years = [date.year for date in Ticket.objects.dates('created_at', 'year', order='DESC')]
    months = [
        {'value': i, 'name': name}
        for i, name in enumerate([
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ], start=1)
    ]
    
    assignable_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by('first_name')


    context = {
        'tickets': tickets,
        'stats': stats,
        'search': search,
        'status_filter': status,
        'priority_filter': priority,
        'category_filter': category,
        'assigned_to_filter': assigned_to_id, 
        'month_filter': month,
        'year_filter': year,
        'years': years,
        'months': months,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'category_choices': Ticket.CATEGORY_CHOICES,
        'current_year': datetime.now().year,
    }
    return render(request, 'tickets/admin_dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def update_ticket(request, ticket_id):
    """
    Permite al personal autorizado actualizar la información de un ticket existente.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    form = TicketUpdateForm(request.POST or None, instance=ticket)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Ticket {ticket.ticket_number} actualizado exitosamente.')
        return redirect('admin_dashboard')

    return render(request, 'tickets/update_ticket.html', {'form': form, 'ticket': ticket})


@login_required
@user_passes_test(is_staff)
def delete_ticket(request, ticket_id):
    """
    Permite eliminar un ticket de manera permanente.
    Requiere confirmación vía POST.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        ticket_number = ticket.ticket_number
        ticket.delete()
        messages.success(request, f'Ticket {ticket_number} eliminado exitosamente.')
        return redirect('admin_dashboard')

    return render(request, 'tickets/delete_ticket.html', {'ticket': ticket})


# -----------------------------------------------------------------------------
# REPORTES Y EXPORTACIÓN
# -----------------------------------------------------------------------------
@login_required
def generate_ticket_pdf(request, ticket_id):
    """
    Genera un reporte PDF del ticket solicitado.

    Args:
        ticket_id (int): ID del ticket a exportar.

    Permisos:
        Solo el dueño del ticket o el personal de soporte puede generarlo.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verificación de permisos
    if not (request.user.is_staff or ticket.user == request.user):
        messages.error(request, 'No tienes permiso para generar el PDF de este ticket.')
        return redirect('user_dashboard')

    # Generación del PDF
    pdf_generator = TicketPDFGenerator(ticket)
    pdf = pdf_generator.generate_pdf()

    # Respuesta HTTP con nombre dinámico
    filename = f'Ticket_{ticket.ticket_number}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
# === GESTIÓN DE USUARIOS ===

@login_required
@user_passes_test(is_staff)
def user_list(request):
    """Lista de usuarios del sistema"""
    users = User.objects.all().order_by('username')
    
    # Filtro de búsqueda
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'users': users,
        'search': search,
    }
    return render(request, 'tickets/user_list.html', context)


@login_required
@user_passes_test(is_staff)
def user_create(request):
    """Crear nuevo usuario"""
    from .forms import UserRegistrationForm
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'tickets/user_form.html', context)


@login_required
@user_passes_test(is_staff)
def user_edit(request, user_id):
    """Editar usuario existente"""
    from .forms import UserEditForm
    
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user_obj.username} actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_obj)
    
    context = {
        'form': form,
        'user_obj': user_obj,
        'action': 'Editar',
    }
    return render(request, 'tickets/user_form.html', context)


@login_required
@user_passes_test(is_staff)
def user_delete(request, user_id):
    """Eliminar usuario"""
    user_obj = get_object_or_404(User, id=user_id)
    
    # No permitir eliminar al propio usuario
    if user_obj == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('user_list')
    
    # No permitir eliminar superusuarios
    if user_obj.is_superuser:
        messages.error(request, 'No puedes eliminar un superusuario.')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('user_list')
    
    context = {
        'user_obj': user_obj,
    }
    return render(request, 'tickets/user_delete.html', context)

@login_required
@user_passes_test(is_staff)
def user_list(request):
    """Lista de usuarios del sistema"""
    users = User.objects.all().order_by('username')
    
    # Filtro de búsqueda
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Calcular estadísticas
    staff_count = users.filter(is_staff=True).count()
    active_count = users.filter(is_active=True).count()
    
    context = {
        'users': users,
        'search': search,
        'staff_count': staff_count,
        'active_count': active_count,
    }
    return render(request, 'tickets/user_list.html', context)
