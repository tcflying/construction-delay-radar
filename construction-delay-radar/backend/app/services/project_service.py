from typing import List, Optional, Dict
from datetime import datetime
import uuid

from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    def __init__(self):
        self._projects: Dict[str, dict] = {}

    async def create(self, project: ProjectCreate) -> ProjectResponse:
        pid = f"proj_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        data = {
            "id": pid,
            "name": project.name,
            "location": project.location,
            "start_date": project.start_date.isoformat(),
            "duration_days": project.duration_days,
            "description": project.description,
            "status": "planning",
            "progress_percent": 0,
            "risk_level": "LOW",
            "created_at": now,
            "updated_at": now,
        }
        self._projects[pid] = data
        return ProjectResponse(**data)

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        projects = list(self._projects.values())[skip : skip + limit]
        return [ProjectResponse(**p) for p in projects]

    async def get_by_id(self, project_id: str) -> Optional[ProjectResponse]:
        project = self._projects.get(project_id)
        return ProjectResponse(**project) if project else None

    async def update(self, project_id: str, update: ProjectUpdate) -> Optional[ProjectResponse]:
        if project_id not in self._projects:
            return None
        project = self._projects[project_id]
        update_data = update.model_dump(exclude_unset=True)
        project.update(update_data)
        project["updated_at"] = datetime.utcnow().isoformat()
        self._projects[project_id] = project
        return ProjectResponse(**project)

    async def delete(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False
