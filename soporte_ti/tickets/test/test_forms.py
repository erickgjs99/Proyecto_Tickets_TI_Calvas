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
        