from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from .models import User

# Create a new user
async def create_user(db: AsyncSession, firstname: str, lastname: str, email: str, password: str):
    new_user = User(firstname=firstname, lastname=lastname, email=email, password=password)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        print(str(e))
    return new_user

# Get all users
async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

# Get a single user by ID
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise NoResultFound
    return user

# Update a user
async def update_user(db: AsyncSession, user_id: int, firstname: str | None, email: str | None):
    user = await get_user(db, user_id)  # Fetch user
    if firstname:
        user.firstname = firstname
    if email:
        user.email = email
    await db.commit()
    await db.refresh(user)
    return user

# Delete a user
async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
