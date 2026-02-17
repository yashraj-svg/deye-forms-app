"""
Fix profile photo paths in database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import UserProfile

# Get all profiles with profile photos
profiles = UserProfile.objects.exclude(profile_photo='')

print(f"Found {profiles.count()} profiles with photos")

for profile in profiles:
    old_path = str(profile.profile_photo)
    print(f"\nProfile: {profile.user.username}")
    print(f"Current path: {old_path}")
    
    # If the path doesn't start with 'profile_photos/', fix it
    if old_path and not old_path.startswith('profile_photos/'):
        # Extract just the filename
        filename = os.path.basename(old_path)
        new_path = f'profile_photos/{filename}'
        
        print(f"Updating to: {new_path}")
        profile.profile_photo = new_path
        profile.save()
        print("✅ Updated!")
    else:
        print("✅ Path is correct!")

print("\n✅ All profile photo paths fixed!")
