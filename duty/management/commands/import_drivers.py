import csv
from django.core.management.base import BaseCommand
from duty.models import DriverImportLog

class Command(BaseCommand):
    help = 'Import drivers and staff IDs from CSV file'

    def handle(self, *args, **kwargs):
        # Correct path for Ubuntu/Linux
        csvfile_path ='/home/toobler/Sarun_project/Sarun_project/Drivers_Master/Driver_Staff_ data.csv'

        try:
            with open(csvfile_path, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    driver_name = row.get('name', '').strip()
                    staff_id = row.get('staff_id', '').strip()

                    # Validate the data
                    if driver_name and staff_id and staff_id != '-':
                        DriverImportLog.objects.create(
                            driver_name=driver_name,
                            staff_id=staff_id
                        )
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipping invalid row: {row}'))

            self.stdout.write(self.style.SUCCESS('Successfully imported drivers and staff IDs'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csvfile_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
