from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from api.constants import USER_INACTIVITY_EXPIRY_INTERVAL

User = get_user_model()

class Command(BaseCommand):
    help = 'Removes users who have been inactive for longer than the expiry period'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which users would be deleted without actually deleting them',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        # Calculate the cutoff date
        cutoff_date = timezone.now() - USER_INACTIVITY_EXPIRY_INTERVAL
        
        # Find inactive users
        inactive_users = User.objects.filter(
            last_modified__lt=cutoff_date,
            is_superuser=False,  # Don't delete superusers
            is_staff=False,       # Don't delete staff users
        )
        
        user_count = inactive_users.count()
        
        if user_count == 0:
            self.stdout.write(self.style.SUCCESS('No inactive users found.'))
            return
            
        # Always show all users that would be deleted for full transparency
        self.stdout.write(f'\nFound {user_count} inactive user(s) (last modified before {cutoff_date}):')
        for user in inactive_users.order_by('last_modified'):
            self.stdout.write(f'  - {user.username} (last modified: {user.last_modified})')
            
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDry run complete. {user_count} user(s) would be deleted.'))
            self.stdout.write(self.style.WARNING('No actual changes were made. Use --force to perform the actual deletion.'))
            return
            
        # Ask for confirmation if not forced
        if not force:
            confirm = input(f'\nAre you sure you want to delete these {user_count} user(s)? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return
        
        # Perform the deletion
        with transaction.atomic():
            deleted_count, _ = inactive_users.delete()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} inactive user(s).'))
