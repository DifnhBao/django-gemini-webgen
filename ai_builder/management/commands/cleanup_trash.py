from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ai_builder.models import GeneratedWebsite

class Command(BaseCommand):
    help = 'Xóa vĩnh viễn các website đã nằm trong thùng rác quá 7 ngày'

    def handle(self, *args, **kwargs):
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # Lọc ra các web ĐÃ XÓA MỀM (deleted_at có dữ liệu) và thời gian xóa CŨ HƠN 7 ngày
        old_records = GeneratedWebsite.objects.filter(
            deleted_at__isnull=False,
            deleted_at__lt=seven_days_ago
        )
        
        count = old_records.count()
        old_records.delete() 
        
        self.stdout.write(self.style.SUCCESS(f'Đã dọn dẹp vĩnh viễn {count} websites quá hạn.'))