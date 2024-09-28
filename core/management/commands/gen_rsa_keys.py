import os
import shutil
import subprocess

from django.conf import settings

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Generate RSA keys"

    def handle(self, *args, **options):
        # Define the directory to store the keys
        keys_dir = settings.BEATSIGHT_DATA_DIR
        private_key_file = os.path.join(keys_dir, "id_rsa")
        public_key_file = os.path.join(keys_dir, "id_rsa.pub")

        if os.path.exists(public_key_file):
            print('key pair already generated!')
            return

        # Generate the RSA key pair using ssh-keygen
        try:
            subprocess.check_call([
                'ssh-keygen', '-t', 'rsa', '-b', '2048', '-f', private_key_file, '-N', ''
            ])
            self.stdout.write(
                self.style.SUCCESS(f"RSA key pair generated: {private_key_file} and {public_key_file}")
            )
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Error generating RSA key pair: {e}"))
