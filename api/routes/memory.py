from fastapi import APIRouter, Depends
from utils.memory import MemoryManager
from utils.security import get_current_user

router = APIRouter(tags=["Memory"])

# Single global memory instance (for demo purposes)
memory_manager = MemoryManager()

@router.get("/memory")
async def get_memory(user=Depends(get_current_user)):
    """
    Return the conversation memory for the current session.
    Accessible to all authenticated users.
    """
    context = memory_manager.get_context()
    return {
        "message": " Memory retrieved successfully",
        "user": user,
        "context": context
    }

@router.delete("/memory")
async def clear_memory(user=Depends(get_current_user)):
    """
    Clear memory (useful for resetting sessions).
    """
    memory_manager.memory.clear()
    memory_manager.save()
    return {"message": " Memory cleared", "user": user}
