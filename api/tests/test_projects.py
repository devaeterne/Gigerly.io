import pytest
from app.models import Project, ProjectBudgetType, ProjectStatus


@pytest.mark.asyncio
async def test_list_projects_empty(client):
    response = await client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    response = await client.get("/projects/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_success(client, test_db, test_customer):
    project = Project(
        title="Test Project Title",
        description="This is a test project description that is definitely long enough to meet validation requirements.",
        customer_id=test_customer.id,
        budget_type=ProjectBudgetType.fixed,
        status=ProjectStatus.open,
        currency="USD",
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)

    response = await client.get(f"/projects/{project.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project.id
    assert data["title"] == project.title


@pytest.mark.asyncio
async def test_create_project_requires_auth(client):
    payload = {
        "title": "Unauthorized Project",
        "description": "This project should not be created due to missing auth and serves as a negative test case for authorization.",
        "budget_type": "fixed",
        "currency": "USD",
    }
    response = await client.post("/projects", json=payload)
    assert response.status_code == 401

