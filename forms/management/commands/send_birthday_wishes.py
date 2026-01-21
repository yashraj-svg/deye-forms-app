from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from datetime import date
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send birthday wishes to users whose birthday is today'

    def handle(self, *args, **kwargs):
        today = date.today()
        
        # Find all users with birthday today
        users_with_birthday = User.objects.filter(
            profile__date_of_birth__month=today.month,
            profile__date_of_birth__day=today.day
        ).select_related('profile')

        if not users_with_birthday.exists():
            self.stdout.write(self.style.SUCCESS('No birthdays today.'))
            return

        sent_count = 0
        failed_count = 0

        for user in users_with_birthday:
            if not user.email:
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} has no email address. Skipping.')
                )
                failed_count += 1
                continue

            try:
                # Generate the gift URL (birthday greeting page)
                gift_url = f"{settings.SITE_URL}/birthday/{user.id}/"
                
                # Prepare email context
                context = {
                    'user': user,
                    'gift_url': gift_url,
                    'current_year': today.year,
                }

                # Render HTML email
                html_message = render_to_string('birthday/birthday_email.html', context)
                plain_message = strip_tags(html_message)

                # Send email
                send_mail(
                    subject=f'🎉 Happy Birthday {user.first_name}! 🎂',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                self.stdout.write(
                    self.style.SUCCESS(f'Birthday email sent to {user.username} ({user.email})')
                )
                sent_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send email to {user.username}: {str(e)}')
                )
                logger.error(f'Birthday email error for {user.username}: {str(e)}')
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {sent_count} emails sent successfully, {failed_count} failed.'
            )
        )
