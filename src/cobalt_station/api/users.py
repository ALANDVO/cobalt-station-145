"""Users API router for Cobalt Station."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from cobalt_station.models.user import UserCreate, UserResponse, UserListResponse, UserUpdate, UserStatus
from cobalt_station.services.user_service import UserService


router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_service(request: Request) -> UserService:
    """Dependency to get the user service instance from app state."""
    return request.app.state.user_service


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    """Create a new user with isolated workspace."""
    user = service.create_user(user_create)
    return UserResponse.from_user(user)


@router.get("", response_model=UserListResponse)
async def list_users(service: UserService = Depends(get_user_service)) -> UserListResponse:
    """List all users."""
    users = service.list_users()
    return UserListResponse(
        users=[UserResponse.from_user(u) for u in users],
        total=len(users),
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)) -> UserResponse:
    """Get a user by ID."""
    try:
        user = service.get_user(user_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}")
    return UserResponse.from_user(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: str,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update a user's properties."""
    # Validate specialist_id refers to an existing agent
    if user_update.specialist_id is not None:
        agent_service = request.app.state.agent_service
        try:
            agent_service.get_agent(user_update.specialist_id)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Specialist agent not found: {user_update.specialist_id}",
            )
    try:
        user = service.update_user(
            user_id,
            name=user_update.name,
            specialist_id=user_update.specialist_id,
            workspace_path=user_update.workspace_path,
            status=user_update.status,
        )
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}")
    return UserResponse.from_user(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)) -> None:
    """Delete a user and its workspace."""
    try:
        service.delete_user(user_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}")
