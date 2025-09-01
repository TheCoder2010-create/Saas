from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import jwt
import bcrypt
import json
import pandas as pd
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="AI Model Training Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')

# AI Configuration
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user: User

class Dataset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_id: str
    file_type: str
    file_size: int
    data_preview: List[Dict[str, Any]]
    column_count: int
    row_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ModelTraining(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_id: str
    dataset_id: str
    status: str = "training"  # training, completed, failed
    model_type: str = "gemini-2.0-flash"
    custom_prompt: str
    training_data: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class DeployedModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_id: str
    training_id: str
    api_endpoint: str
    status: str = "active"  # active, inactive
    usage_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ModelTest(BaseModel):
    input_text: str

class ModelTestResponse(BaseModel):
    output: str
    confidence: float
    processing_time: float

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    payload = {"user_id": user_id, "exp": datetime.now(timezone.utc).timestamp() + 3600 * 24 * 7}  # 7 days
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = await db.users.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def process_uploaded_data(file_content: bytes, file_type: str) -> Dict[str, Any]:
    """Process uploaded file and return structured data"""
    try:
        if file_type.lower() == 'csv':
            df = pd.read_csv(io.BytesIO(file_content))
            data = df.to_dict('records')
            preview = data[:5]  # First 5 rows
            return {
                "data": data,
                "preview": preview,
                "column_count": len(df.columns),
                "row_count": len(df)
            }
        elif file_type.lower() == 'json':
            data = json.loads(file_content.decode('utf-8'))
            if isinstance(data, list):
                preview = data[:5]
                return {
                    "data": data,
                    "preview": preview,
                    "column_count": len(data[0].keys()) if data else 0,
                    "row_count": len(data)
                }
            else:
                return {
                    "data": [data],
                    "preview": [data],
                    "column_count": len(data.keys()),
                    "row_count": 1
                }
        elif file_type.lower() == 'txt':
            text_content = file_content.decode('utf-8')
            lines = text_content.split('\n')
            data = [{"text": line} for line in lines if line.strip()]
            preview = data[:5]
            return {
                "data": data,
                "preview": preview,
                "column_count": 1,
                "row_count": len(data)
            }
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

# Auth Routes
@api_router.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(email=user_data.email, name=user_data.name)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Generate token
    access_token = create_access_token(user.id)
    
    return AuthResponse(access_token=access_token, user=user)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    # Find user
    user_data = await db.users.find_one({"email": credentials.email})
    if not user_data or not verify_password(credentials.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_data)
    access_token = create_access_token(user.id)
    
    return AuthResponse(access_token=access_token, user=user)

# Dataset Routes
@api_router.post("/datasets/upload", response_model=Dataset)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ['csv', 'json', 'txt']
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type not supported. Allowed: {allowed_types}")
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Process data
    processed_data = process_uploaded_data(file_content, file_extension)
    
    # Create dataset record
    dataset = Dataset(
        name=name,
        user_id=current_user.id,
        file_type=file_extension,
        file_size=file_size,
        data_preview=processed_data["preview"],
        column_count=processed_data["column_count"],
        row_count=processed_data["row_count"]
    )
    
    dataset_dict = dataset.dict()
    dataset_dict["full_data"] = processed_data["data"]  # Store full data
    
    await db.datasets.insert_one(dataset_dict)
    
    return dataset

@api_router.get("/datasets", response_model=List[Dataset])
async def get_datasets(current_user: User = Depends(get_current_user)):
    datasets = await db.datasets.find({"user_id": current_user.id}).to_list(1000)
    return [Dataset(**{k: v for k, v in dataset.items() if k != "full_data"}) for dataset in datasets]

# Model Training Routes
@api_router.post("/models/train", response_model=ModelTraining)
async def train_model(
    dataset_id: str = Form(...),
    model_name: str = Form(...),
    custom_prompt: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Get dataset
    dataset_data = await db.datasets.find_one({"id": dataset_id, "user_id": current_user.id})
    if not dataset_data:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create training record
    training = ModelTraining(
        name=model_name,
        user_id=current_user.id,
        dataset_id=dataset_id,
        custom_prompt=custom_prompt,
        training_data=dataset_data["full_data"][:100]  # Limit to first 100 rows for demo
    )
    
    # Simulate training completion (in real app, this would be async)
    training.status = "completed"
    training.completed_at = datetime.now(timezone.utc)
    
    await db.model_trainings.insert_one(training.dict())
    
    return training

@api_router.get("/models", response_model=List[ModelTraining])
async def get_models(current_user: User = Depends(get_current_user)):
    models = await db.model_trainings.find({"user_id": current_user.id}).to_list(1000)
    return [ModelTraining(**model) for model in models]

# Model Testing Routes
@api_router.post("/models/{model_id}/test", response_model=ModelTestResponse)
async def test_model(
    model_id: str,
    test_data: ModelTest,
    current_user: User = Depends(get_current_user)
):
    # Get model
    model_data = await db.model_trainings.find_one({"id": model_id, "user_id": current_user.id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        start_time = datetime.now()
        
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=GOOGLE_API_KEY,
            session_id=f"test-{model_id}",
            system_message=model_data["custom_prompt"]
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create user message
        user_message = UserMessage(text=test_data.input_text)
        
        # Get response
        response = await chat.send_message(user_message)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ModelTestResponse(
            output=response,
            confidence=0.95,  # Simulated confidence score
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing model: {str(e)}")

# Model Deployment Routes
@api_router.post("/models/{model_id}/deploy", response_model=DeployedModel)
async def deploy_model(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    # Get model
    model_data = await db.model_trainings.find_one({"id": model_id, "user_id": current_user.id})
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Create deployment record
    deployment = DeployedModel(
        name=f"{model_data['name']}-api",
        user_id=current_user.id,
        training_id=model_id,
        api_endpoint=f"/models/{model_id}/predict"
    )
    
    await db.deployed_models.insert_one(deployment.dict())
    
    return deployment

@api_router.get("/models/deployed", response_model=List[DeployedModel])
async def get_deployed_models(current_user: User = Depends(get_current_user)):
    models = await db.deployed_models.find({"user_id": current_user.id}).to_list(1000)
    return [DeployedModel(**model) for model in models]

# API Prediction Route
@api_router.post("/models/{model_id}/predict")
async def predict(
    model_id: str,
    test_data: ModelTest,
    current_user: User = Depends(get_current_user)
):
    # Increment usage count
    await db.deployed_models.update_one(
        {"training_id": model_id, "user_id": current_user.id},
        {"$inc": {"usage_count": 1}}
    )
    
    # Use the same testing logic
    return await test_model(model_id, test_data, current_user)

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    datasets_count = await db.datasets.count_documents({"user_id": current_user.id})
    models_count = await db.model_trainings.count_documents({"user_id": current_user.id})
    deployed_count = await db.deployed_models.count_documents({"user_id": current_user.id})
    
    # Get total API usage
    deployed_models = await db.deployed_models.find({"user_id": current_user.id}).to_list(1000)
    total_usage = sum(model.get("usage_count", 0) for model in deployed_models)
    
    return {
        "datasets": datasets_count,
        "models": models_count,
        "deployed": deployed_count,
        "api_calls": total_usage
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()