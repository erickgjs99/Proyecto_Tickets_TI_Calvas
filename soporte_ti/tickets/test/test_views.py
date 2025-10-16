from django.test import TestCase
from django.contrib.auth.models import User
from tickets.forms import (
    TicketForm,
    CommentForm,
    TicketUpdateForm,
    UserRegistrationForm,
    UserEditForm
)
from tickets.models import Ticket


class TicketFormTest(TestCase):
    """Tests para el formulario de tickets"""
    
    def test_ticket_form_valid_data(self):
        """Verifica que el formulario es válido con datos correctos"""
        form = TicketForm(data={
            'title': 'Test Ticket',
            'description': 'Test Description',
            'category': 'software',
            'priority': 'medium'
        })
        self.assertTrue(form.is_valid())
    
    def test_ticket_form_missing_title(self):
        """Verifica que el formulario es inválido sin título"""
        form = TicketForm(data={
            'title': '',
            'description': 'Test Description',
            'category': 'software',
            'priority': 'medium'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_ticket_form_missing_description(self):
        """Verifica que el formulario es inválido sin descripción"""
        form = TicketForm(data={
            'title': 'Test Ticket',
            'description': '',
            'category': 'software',
            'priority': 'medium'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
    
    def test_ticket_form_widget_classes(self):
        """Verifica que los widgets tienen las clases CSS correctas"""
        form = TicketForm()
        self.assertIn('form-control', form.fields['title'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['description'].widget.attrs['class'])


class CommentFormTest(TestCase):
    """Tests para el formulario de comentarios"""
    
    def test_comment_form_valid_data(self):
        """Verifica que el formulario es válido con datos correctos"""
        form = CommentForm(data={'text': 'Test Comment'})
        self.assertTrue(form.is_valid())
    
    def test_comment_form_missing_text(self):
        """Verifica que el formulario es inválido sin texto"""
        form = CommentForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
    
    def test_comment_form_widget_attributes(self):
        """Verifica los atributos del widget"""
        form = CommentForm()
        self.assertEqual(form.fields['text'].widget.attrs['rows'], 3)
        self.assertIn('form-control', form.fields['text'].widget.attrs['class'])


class TicketUpdateFormTest(TestCase):
    """Tests para el formulario de actualización de tickets"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        self.ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
    
    def test_update_form_valid_data(self):
        """Verifica que el formulario es válido con datos correctos"""
        form = TicketUpdateForm(
            instance=self.ticket,
            data={
                'status': 'in_progress',
                'priority': 'high',
                'assigned_to': self.staff_user.id
            }
        )
        self.assertTrue(form.is_valid())
    
    def test_update_form_changes_status(self):
        """Verifica que el formulario puede cambiar el estado"""
        form = TicketUpdateForm(
            instance=self.ticket,
            data={
                'status': 'resolved',
                'priority': self.ticket.priority,
                'assigned_to': ''
            }
        )
        self.assertTrue(form.is_valid())
        updated_ticket = form.save()
        self.assertEqual(updated_ticket.status, 'resolved')
    
    def test_update_form_assigns_ticket(self):
        """Verifica que el formulario puede asignar tickets"""
        form = TicketUpdateForm(
            instance=self.ticket,
            data={
                'status': self.ticket.status,
                'priority': self.ticket.priority,
                'assigned_to': self.staff_user.id
            }
        )
        self.assertTrue(form.is_valid())
        updated_ticket = form.save()
        self.assertEqual(updated_ticket.assigned_to, self.staff_user)


class UserRegistrationFormTest(TestCase):
    """Tests para el formulario de registro de usuarios"""
    
    def test_registration_form_valid_data(self):
        """Verifica que el formulario es válido con datos correctos"""
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123',
            'cargo': 'Desarrollador',
            'departamento': 'TI',
            'telefono': '0999123456',
            'celular': '0998765432',
            'extension': '101',
            'is_staff': False
        })
        self.assertTrue(form.is_valid())
    
    def test_registration_form_password_mismatch(self):
        """Verifica que las contraseñas deben coincidir"""
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'differentpass123',
            'cargo': 'Desarrollador',
            'departamento': 'TI'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_registration_form_duplicate_username(self):
        """Verifica que no se pueden duplicar nombres de usuario"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        form = UserRegistrationForm(data={
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_registration_form_missing_required_fields(self):
        """Verifica que los campos obligatorios son requeridos"""
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': '',  # Campo obligatorio
            'first_name': '',  # Campo obligatorio
            'last_name': '',  # Campo obligatorio
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
    
    def test_registration_form_saves_user_with_profile(self):
        """Verifica que el formulario crea usuario y perfil correctamente"""
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'strongpass123',
            'password2': 'strongpass123',
            'cargo': 'Desarrollador',
            'departamento': 'TI',
            'telefono': '0999123456',
            'celular': '0998765432',
            'extension': '101',
            'is_staff': True
        })
        
        self.assertTrue(form.is_valid())
        user = form.save()
        
        # Verificar que el usuario se creó correctamente
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_staff)
        
        # Verificar que el perfil se creó con los datos correctos
        self.assertEqual(user.profile.cargo, 'Desarrollador')
        self.assertEqual(user.profile.departamento, 'TI')
        self.assertEqual(user.profile.telefono, '0999123456')
        self.assertEqual(user.profile.celular, '0998765432')
        self.assertEqual(user.profile.extension, '101')
    
    def test_registration_form_weak_password(self):
        """Verifica que se rechazan contraseñas débiles"""
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': '123',  # Contraseña muy corta
            'password2': '123'
        })
        self.assertFalse(form.is_valid())


class UserEditFormTest(TestCase):
    """Tests para el formulario de edición de usuarios"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.profile.cargo = 'Analista'
        self.user.profile.departamento = 'Desarrollo'
        self.user.profile.save()
    
    def test_edit_form_loads_existing_data(self):
        """Verifica que el formulario carga los datos existentes"""
        form = UserEditForm(instance=self.user)
        
        self.assertEqual(form.initial['username'], 'testuser')
        self.assertEqual(form.initial['email'], 'test@example.com')
        self.assertEqual(form.fields['cargo'].initial, 'Analista')
        self.assertEqual(form.fields['departamento'].initial, 'Desarrollo')
    
    def test_edit_form_updates_user_data(self):
        """Verifica que el formulario actualiza los datos del usuario"""
        form = UserEditForm(
            instance=self.user,
            data={
                'username': 'testuser',
                'email': 'newemail@example.com',
                'first_name': 'Updated',
                'last_name': 'Name',
                'cargo': 'Senior Developer',
                'departamento': 'Engineering',
                'telefono': '0999888777',
                'celular': '0998777666',
                'extension': '202',
                'is_staff': True,
                'is_active': True
            }
        )
        
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        
        # Verificar cambios en el usuario
        self.assertEqual(updated_user.email, 'newemail@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertTrue(updated_user.is_staff)
        
        # Verificar cambios en el perfil
        updated_user.refresh_from_db()
        self.assertEqual(updated_user.profile.cargo, 'Senior Developer')
        self.assertEqual(updated_user.profile.departamento, 'Engineering')
        self.assertEqual(updated_user.profile.telefono, '0999888777')
        self.assertEqual(updated_user.profile.celular, '0998777666')
        self.assertEqual(updated_user.profile.extension, '202')
    
    def test_edit_form_cannot_change_to_existing_username(self):
        """Verifica que no se puede cambiar a un username existente"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        form = UserEditForm(
            instance=self.user,
            data={
                'username': 'otheruser',  # Ya existe
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': False,
                'is_active': True
            }
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)