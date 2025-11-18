"""Scheduled export service."""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os

from src.domain.scheduled_export import ScheduledExport
from src.domain.scheduled_query import ScheduleStatus, ScheduleFrequency
from src.infrastructure.scheduled_export.repository import ScheduledExportRepository
from src.application.services.query_service import QueryService
from src.application.services.export_template_service import ExportTemplateService
from src.utils.cron_parser import CronParser
from src.utils.exporters.factory import ExporterFactory
from src.utils.webhooks import WebhookService, WebhookEvent


class ScheduledExportService:
    """Service for managing scheduled exports."""
    
    def __init__(
        self,
        repository: ScheduledExportRepository,
        query_service: QueryService,
        export_template_service: Optional[ExportTemplateService] = None,
        webhook_service: Optional[WebhookService] = None,
        export_storage_path: str = "/tmp/exports"
    ):
        self.repository = repository
        self.query_service = query_service
        self.export_template_service = export_template_service
        self.webhook_service = webhook_service
        self.export_storage_path = export_storage_path
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Ensure export directory exists
        os.makedirs(self.export_storage_path, exist_ok=True)
    
    async def create_scheduled_export(
        self,
        name: str,
        query: str,
        frequency: ScheduleFrequency,
        schedule: str,
        export_format: str,
        database_ids: Optional[List[str]] = None,
        export_template_id: Optional[str] = None,
        destination: Optional[str] = None,
        filename_pattern: Optional[str] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> ScheduledExport:
        """Create a new scheduled export."""
        now = datetime.utcnow()
        next_run = CronParser.calculate_next_run(frequency, schedule, None)
        
        # Generate default filename pattern if not provided
        if not filename_pattern:
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            filename_pattern = f"export_{timestamp}.{export_format}"
        
        scheduled_export = ScheduledExport(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            query=query,
            database_ids=database_ids,
            schedule=schedule,
            frequency=frequency,
            export_format=export_format,
            export_template_id=export_template_id,
            destination=destination,
            filename_pattern=filename_pattern,
            status=ScheduleStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            next_run_at=next_run,
            created_by=created_by
        )
        
        return await self.repository.save(scheduled_export)
    
    async def execute_export(self, export_id: str) -> Dict[str, Any]:
        """Execute a scheduled export."""
        scheduled_export = await self.repository.get_by_id(export_id)
        if not scheduled_export:
            raise ValueError(f"Scheduled export {export_id} not found")
        
        if scheduled_export.status != ScheduleStatus.ACTIVE:
            return {
                "status": "skipped",
                "reason": f"Export is {scheduled_export.status}"
            }
        
        try:
            # Execute query
            result = await self.query_service.execute_query(
                user_query=scheduled_export.query,
                database_ids=scheduled_export.database_ids
            )
            
            # Get data
            data = result.merged_data
            
            # Apply export template if specified
            if scheduled_export.export_template_id and self.export_template_service:
                template = await self.export_template_service.get_template(
                    scheduled_export.export_template_id
                )
                if template:
                    context = {
                        "export_id": export_id,
                        "query": scheduled_export.query,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    data, filename = self.export_template_service.apply_template(
                        template, data, context
                    )
                else:
                    filename = self._generate_filename(scheduled_export)
            else:
                filename = self._generate_filename(scheduled_export)
            
            # Create exporter
            exporter = ExporterFactory.create(scheduled_export.export_format)
            
            # Export to file
            file_data = await exporter.export(data)
            file_path = os.path.join(self.export_storage_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data.getvalue())
            
            # Update scheduled export
            now = datetime.utcnow()
            scheduled_export.last_run_at = now
            scheduled_export.run_count += 1
            scheduled_export.success_count += 1
            scheduled_export.next_run_at = CronParser.calculate_next_run(
                scheduled_export.frequency,
                scheduled_export.schedule,
                now
            )
            scheduled_export.last_export_path = file_path
            await self.repository.save(scheduled_export)
            
            # Send to destination if specified
            if scheduled_export.destination:
                await self._send_to_destination(
                    scheduled_export,
                    file_path,
                    filename
                )
            
            return {
                "status": "success",
                "file_path": file_path,
                "filename": filename,
                "total_rows": result.total_rows,
                "execution_time": result.execution_time
            }
        
        except Exception as e:
            # Update failure count
            scheduled_export.run_count += 1
            scheduled_export.failure_count += 1
            await self.repository.save(scheduled_export)
            
            # Notify on failure if configured
            if scheduled_export.notify_on_failure:
                await self._notify_failure(scheduled_export, str(e))
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _send_to_destination(
        self,
        scheduled_export: ScheduledExport,
        file_path: str,
        filename: str
    ) -> None:
        """Send export to destination (webhook, email, etc.)."""
        if scheduled_export.destination.startswith("http"):
            # Webhook destination
            if self.webhook_service:
                await self.webhook_service.trigger_webhook(
                    WebhookEvent.EXPORT_COMPLETED,
                    {
                        "export_id": scheduled_export.id,
                        "filename": filename,
                        "file_path": file_path,
                        "query": scheduled_export.query
                    }
                )
        # Email destination would be implemented here
        # Storage destination (S3, etc.) would be implemented here
    
    async def _notify_failure(
        self,
        scheduled_export: ScheduledExport,
        error: str
    ) -> None:
        """Notify about export failure."""
        if self.webhook_service:
            await self.webhook_service.trigger_webhook(
                WebhookEvent.QUERY_FAILED,
                {
                    "export_id": scheduled_export.id,
                    "name": scheduled_export.name,
                    "error": error
                }
            )
        # Email notification would be implemented here
    
    def _generate_filename(self, scheduled_export: ScheduledExport) -> str:
        """Generate filename from pattern."""
        if not scheduled_export.filename_pattern:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            return f"export_{timestamp}.{scheduled_export.export_format}"
        
        filename = scheduled_export.filename_pattern
        now = datetime.utcnow()
        
        # Replace placeholders
        filename = filename.replace("{date}", now.strftime("%Y%m%d"))
        filename = filename.replace("{datetime}", now.strftime("%Y%m%d_%H%M%S"))
        filename = filename.replace("{timestamp}", str(int(now.timestamp())))
        filename = filename.replace("{format}", scheduled_export.export_format)
        filename = filename.replace("{name}", scheduled_export.name.replace(" ", "_"))
        
        # Ensure extension matches format
        if not filename.endswith(f".{scheduled_export.export_format}"):
            filename = f"{filename}.{scheduled_export.export_format}"
        
        return filename
    
    async def start_scheduler(self, check_interval: int = 60):
        """Start the scheduler background task."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop(check_interval))
    
    async def stop_scheduler(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _scheduler_loop(self, check_interval: int):
        """Background task to check and execute due exports."""
        while self._running:
            try:
                due_exports = await self.repository.get_due_exports()
                
                for export in due_exports:
                    try:
                        await self.execute_export(export.id)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error executing export {export.id}: {e}")
                
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                await asyncio.sleep(check_interval)



