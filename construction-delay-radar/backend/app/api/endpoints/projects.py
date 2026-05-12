from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    return await project_service.create(project)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 100):
    return await project_service.list_all(skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    project = await project_service.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, update: ProjectUpdate):
    project = await project_service.update(project_id, update)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    success = await project_service.delete(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
