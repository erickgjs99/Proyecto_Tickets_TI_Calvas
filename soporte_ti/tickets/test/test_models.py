from django.test import TestCase
from django.contrib.auth.models import User
from tickets.models import Ticket, Comment, UserProfile
import time

class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_created_automatically(self):
        """Verifica que el perfil se crea automáticamente al crear un usuario"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str(self):
        """Verifica la representación en string del perfil"""
        expected = f'Perfil de {self.user.username}'
        self.assertEqual(str(self.user.profile), expected)
    
    def test_user_profile_fields(self):
        """Verifica que los campos del perfil funcionan correctamente"""
        profile = self.user.profile
        profile.cargo = 'Desarrollador'
        profile.departamento = 'TI'
        profile.telefono = '0999123456'
        profile.celular = '0998765432'
        profile.extension = '101'
        profile.save()
        
        # Recargar desde la base de datos
        profile.refresh_from_db()
        
        self.assertEqual(profile.cargo, 'Desarrollador')
        self.assertEqual(profile.departamento, 'TI')
        self.assertEqual(profile.telefono, '0999123456')
        self.assertEqual(profile.celular, '0998765432')
        self.assertEqual(profile.extension, '101')


class TicketModelTest(TestCase):
    """Tests para el modelo Ticket"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_ticket_creation(self):
        """Verifica la creación básica de un ticket"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description',
            category='software',
            priority='medium'
        )
        
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.title, 'Test Ticket')
        self.assertEqual(ticket.description, 'Test Description')
        self.assertEqual(ticket.category, 'software')
        self.assertEqual(ticket.priority, 'medium')
        self.assertEqual(ticket.status, 'open')  # Estado por defecto
    
    def test_ticket_number_generation(self):
        """Verifica que el número de ticket se genera automáticamente"""
        ticket1 = Ticket.objects.create(
            user=self.user,
            title='Ticket 1',
            description='Description 1'
        )
        ticket2 = Ticket.objects.create(
            user=self.user,
            title='Ticket 2',
            description='Description 2'
        )
        
        self.assertIsNotNone(ticket1.ticket_number)
        self.assertIsNotNone(ticket2.ticket_number)
        self.assertTrue(ticket1.ticket_number.startswith('TKT-'))
        self.assertTrue(ticket2.ticket_number.startswith('TKT-'))
        self.assertNotEqual(ticket1.ticket_number, ticket2.ticket_number)
    
    def test_ticket_number_uniqueness(self):
        """Verifica que los números de ticket son únicos"""
        ticket1 = Ticket.objects.create(
            user=self.user,
            title='Ticket 1',
            description='Description 1'
        )
        
        # Intentar crear otro ticket con el mismo número debería fallar
        with self.assertRaises(Exception):
            Ticket.objects.create(
                user=self.user,
                title='Ticket 2',
                description='Description 2',
                ticket_number=ticket1.ticket_number
            )
    
    def test_ticket_str(self):
        """Verifica la representación en string del ticket"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
        expected = f'{ticket.ticket_number} - Test Ticket'
        self.assertEqual(str(ticket), expected)
    
    def test_ticket_ordering(self):
        """Verifica que los tickets se ordenan por fecha de creación descendente"""
        ticket1 = Ticket.objects.create(
            user=self.user,
            title='Ticket 1',
            description='Description 1'
        )
        ticket2 = Ticket.objects.create(
            user=self.user,
            title='Ticket 2',
            description='Description 2'
        )
        
        tickets = Ticket.objects.all()
        self.assertEqual(tickets[0], ticket2)  # Más reciente primero
        self.assertEqual(tickets[1], ticket1)
    
    def test_ticket_assignment(self):
        """Verifica la asignación de tickets a staff"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description',
            assigned_to=self.staff_user
        )
        
        self.assertEqual(ticket.assigned_to, self.staff_user)
    
    def test_ticket_status_choices(self):
        """Verifica que solo se pueden usar estados válidos"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
        
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        for status in valid_statuses:
            ticket.status = status
            ticket.save()
            ticket.refresh_from_db()
            self.assertEqual(ticket.status, status)
    
    def test_ticket_priority_choices(self):
        """Verifica que solo se pueden usar prioridades válidas"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
        
        valid_priorities = ['low', 'medium', 'high', 'critical']
        for priority in valid_priorities:
            ticket.priority = priority
            ticket.save()
            ticket.refresh_from_db()
            self.assertEqual(ticket.priority, priority)
    
    def test_ticket_category_choices(self):
        """Verifica que solo se pueden usar categorías válidas"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
        
        valid_categories = ['hardware', 'software', 'network', 'account', 'other']
        for category in valid_categories:
            ticket.category = category
            ticket.save()
            ticket.refresh_from_db()
            self.assertEqual(ticket.category, category)
    
    def test_ticket_timestamps(self):
        """Verifica que las marcas de tiempo funcionan correctamente"""
        ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
        
        self.assertIsNotNone(ticket.created_at)
        self.assertIsNotNone(ticket.updated_at)
        
        original_created = ticket.created_at
        original_updated = ticket.updated_at
        
        # Actualizar el ticket
        ticket.status = 'in_progress'
        ticket.save()
        ticket.refresh_from_db()
        
        # created_at no debe cambiar, updated_at sí
        self.assertEqual(ticket.created_at, original_created)
        self.assertGreater(ticket.updated_at, original_updated)


class CommentModelTest(TestCase):
    """Tests para el modelo Comment"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.ticket = Ticket.objects.create(
            user=self.user,
            title='Test Ticket',
            description='Test Description'
        )
    
    def test_comment_creation(self):
        """Verifica la creación básica de un comentario"""
        comment = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Test Comment'
        )
        
        self.assertEqual(comment.ticket, self.ticket)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, 'Test Comment')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_str(self):
        """Verifica la representación en string del comentario"""
        comment = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Test Comment'
        )
        expected = f'Comentario de {self.user.username} en {self.ticket.ticket_number}'
        self.assertEqual(str(comment), expected)
    
    def test_comment_ordering(self):
        """Verifica que los comentarios se ordenan por fecha de creación ascendente"""
        comment1 = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='First Comment'
        )
        comment2 = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Second Comment'
        )
        
        comments = Comment.objects.all()
        self.assertEqual(comments[0], comment1)  # Más antiguo primero
        self.assertEqual(comments[1], comment2)
    
    def test_comment_relationship_with_ticket(self):
        """Verifica la relación entre comentarios y tickets"""
        comment1 = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Comment 1'
        )
        comment2 = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Comment 2'
        )
        
        # Verificar que el ticket tiene los comentarios
        self.assertEqual(self.ticket.comments.count(), 2)
        self.assertIn(comment1, self.ticket.comments.all())
        self.assertIn(comment2, self.ticket.comments.all())
    
    def test_comment_deletion_on_ticket_deletion(self):
        """Verifica que los comentarios se eliminan cuando se elimina el ticket"""
        comment = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='Test Comment'
        )
        
        comment_id = comment.id
        self.ticket.delete()
        
        # Verificar que el comentario ya no existe
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
        
        
def test_ticket_timestamps(self):
    """Verifica que las marcas de tiempo funcionan correctamente"""
    ticket = Ticket.objects.create(
        user=self.user,
        title='Test Ticket',
        description='Test Description'
    )
    
    self.assertIsNotNone(ticket.created_at)
    self.assertIsNotNone(ticket.updated_at)
    
    original_created = ticket.created_at
    original_updated = ticket.updated_at
    
    # Espera mínima para que updated_at cambie
    time.sleep(0.001)  # 1 milisegundo
    
    # Actualizar el ticket
    ticket.status = 'in_progress'
    ticket.save()
    ticket.refresh_from_db()
    
    # created_at no debe cambiar, updated_at sí
    self.assertEqual(ticket.created_at, original_created)
    self.assertGreater(ticket.updated_at, original_updated)