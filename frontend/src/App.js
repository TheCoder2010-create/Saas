import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mock user for demo without auth
const DEMO_USER = {
  id: 'demo-user-123',
  name: 'Demo User',
  email: 'demo@aiplatform.com'
};

// Components
const LoginForm = ({ onSwitchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await login(email, password);
    if (!success) {
      alert('Login failed. Please check your credentials.');
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Sign in to your AI training platform</p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              placeholder="your@email.com"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              placeholder="Your password"
            />
          </div>
          
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <p className="auth-switch">
          Don't have an account?{' '}
          <button onClick={onSwitchToRegister} className="auth-link">
            Sign up here
          </button>
        </p>
      </div>
    </div>
  );
};

const RegisterForm = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await register(email, password, name);
    if (!success) {
      alert('Registration failed. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-subtitle">Start training custom AI models today</p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="form-input"
              placeholder="Your full name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              placeholder="your@email.com"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              placeholder="Choose a strong password"
              minLength="6"
            />
          </div>
          
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        
        <p className="auth-switch">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="auth-link">
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState({ datasets: 0, models: 0, deployed: 0, api_calls: 0 });
  const [datasets, setDatasets] = useState([]);
  const [models, setModels] = useState([]);
  const [deployedModels, setDeployedModels] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, datasetsRes, modelsRes, deployedRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/datasets`),
        axios.get(`${API}/models`),
        axios.get(`${API}/models/deployed`)
      ]);
      
      setStats(statsRes.data);
      setDatasets(datasetsRes.data);
      setModels(modelsRes.data);
      setDeployedModels(deployedRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your AI workspace...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="dashboard-title">🤖 AI Model Trainer</h1>
            <p className="dashboard-subtitle">Welcome back, {user?.name}</p>
          </div>
          <div className="header-right">
            <button onClick={logout} className="logout-button">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'datasets' ? 'active' : ''}`}
          onClick={() => setActiveTab('datasets')}
        >
          📁 Datasets
        </button>
        <button 
          className={`nav-tab ${activeTab === 'models' ? 'active' : ''}`}
          onClick={() => setActiveTab('models')}
        >
          🧠 Models
        </button>
        <button 
          className={`nav-tab ${activeTab === 'deploy' ? 'active' : ''}`}
          onClick={() => setActiveTab('deploy')}
        >
          🚀 Deploy
        </button>
      </nav>

      <main className="dashboard-main">
        {activeTab === 'overview' && <OverviewTab stats={stats} />}
        {activeTab === 'datasets' && <DatasetsTab datasets={datasets} onRefresh={fetchDashboardData} />}
        {activeTab === 'models' && <ModelsTab models={models} datasets={datasets} onRefresh={fetchDashboardData} />}
        {activeTab === 'deploy' && <DeployTab deployedModels={deployedModels} models={models} onRefresh={fetchDashboardData} />}
      </main>
    </div>
  );
};

const OverviewTab = ({ stats }) => (
  <div className="overview-tab">
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-icon">📁</div>
        <div className="stat-content">
          <h3 className="stat-number">{stats.datasets}</h3>
          <p className="stat-label">Datasets</p>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon">🧠</div>
        <div className="stat-content">
          <h3 className="stat-number">{stats.models}</h3>
          <p className="stat-label">Trained Models</p>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon">🚀</div>
        <div className="stat-content">
          <h3 className="stat-number">{stats.deployed}</h3>
          <p className="stat-label">Deployed APIs</p>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <h3 className="stat-number">{stats.api_calls}</h3>
          <p className="stat-label">API Calls</p>
        </div>
      </div>
    </div>
    
    <div className="getting-started">
      <h2>🚀 Getting Started</h2>
      <div className="steps-grid">
        <div className="step-card">
          <div className="step-number">1</div>
          <h3>Upload Data</h3>
          <p>Upload your CSV, JSON, or TXT files to create datasets</p>
        </div>
        
        <div className="step-card">
          <div className="step-number">2</div>
          <h3>Train Model</h3>
          <p>Create custom AI models with your data and prompts</p>
        </div>
        
        <div className="step-card">
          <div className="step-number">3</div>
          <h3>Test & Deploy</h3>
          <p>Test your models and deploy them as APIs</p>
        </div>
      </div>
    </div>
  </div>
);

const DatasetsTab = ({ datasets, onRefresh }) => {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="datasets-tab">
      <div className="tab-header">
        <h2>📁 Your Datasets</h2>
        <button 
          className="primary-button"
          onClick={() => setShowUpload(true)}
        >
          + Upload Dataset
        </button>
      </div>
      
      {showUpload && (
        <DatasetUpload 
          onClose={() => setShowUpload(false)} 
          onSuccess={() => {
            setShowUpload(false);
            onRefresh();
          }} 
        />
      )}
      
      <div className="datasets-grid">
        {datasets.map(dataset => (
          <div key={dataset.id} className="dataset-card">
            <div className="dataset-header">
              <h3 className="dataset-name">{dataset.name}</h3>
              <span className="dataset-type">{dataset.file_type.toUpperCase()}</span>
            </div>
            
            <div className="dataset-stats">
              <div className="dataset-stat">
                <span className="stat-label">Rows:</span>
                <span className="stat-value">{dataset.row_count.toLocaleString()}</span>
              </div>
              <div className="dataset-stat">
                <span className="stat-label">Columns:</span>
                <span className="stat-value">{dataset.column_count}</span>
              </div>
              <div className="dataset-stat">
                <span className="stat-label">Size:</span>
                <span className="stat-value">{(dataset.file_size / 1024).toFixed(1)} KB</span>
              </div>
            </div>
            
            <div className="dataset-preview">
              <h4>Preview:</h4>
              <div className="preview-content">
                {dataset.data_preview.slice(0, 2).map((row, idx) => (
                  <div key={idx} className="preview-row">
                    {JSON.stringify(row).substring(0, 100)}...
                  </div>
                ))}
              </div>
            </div>
            
            <div className="dataset-date">
              Created: {new Date(dataset.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
        
        {datasets.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📁</div>
            <h3>No datasets yet</h3>
            <p>Upload your first dataset to start training AI models</p>
            <button 
              className="primary-button"
              onClick={() => setShowUpload(true)}
            >
              Upload Dataset
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const DatasetUpload = ({ onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    if (!name && selectedFile) {
      setName(selectedFile.name.split('.')[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileChange(droppedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !name) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', name);

      await axios.post(`${API}/datasets/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onSuccess();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>📁 Upload Dataset</h3>
          <button onClick={onClose} className="modal-close">×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label>Dataset Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter dataset name"
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <label>File Upload</label>
            <div 
              className={`file-drop-zone ${dragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
            >
              {file ? (
                <div className="file-selected">
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                  <button 
                    type="button" 
                    onClick={() => setFile(null)}
                    className="file-remove"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="file-drop-content">
                  <div className="drop-icon">📁</div>
                  <p>Drop your file here or click to browse</p>
                  <p className="drop-hint">Supports CSV, JSON, and TXT files (max 100MB)</p>
                </div>
              )}
              
              <input
                type="file"
                accept=".csv,.json,.txt"
                onChange={(e) => handleFileChange(e.target.files[0])}
                className="file-input-hidden"
              />
            </div>
          </div>
          
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="secondary-button">
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={!file || !name || uploading}
              className="primary-button"
            >
              {uploading ? 'Uploading...' : 'Upload Dataset'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ModelsTab = ({ models, datasets, onRefresh }) => {
  const [showTraining, setShowTraining] = useState(false);
  const [testingModel, setTestingModel] = useState(null);

  return (
    <div className="models-tab">
      <div className="tab-header">
        <h2>🧠 Your Models</h2>
        <button 
          className="primary-button"
          onClick={() => setShowTraining(true)}
          disabled={datasets.length === 0}
        >
          + Train New Model
        </button>
      </div>
      
      {datasets.length === 0 && (
        <div className="warning-banner">
          ⚠️ Upload a dataset first before training models
        </div>
      )}
      
      {showTraining && (
        <ModelTraining 
          datasets={datasets}
          onClose={() => setShowTraining(false)} 
          onSuccess={() => {
            setShowTraining(false);
            onRefresh();
          }} 
        />
      )}
      
      {testingModel && (
        <ModelTesting 
          model={testingModel}
          onClose={() => setTestingModel(null)}
        />
      )}
      
      <div className="models-grid">
        {models.map(model => (
          <div key={model.id} className="model-card">
            <div className="model-header">
              <h3 className="model-name">{model.name}</h3>
              <div className={`model-status ${model.status}`}>
                {model.status}
              </div>
            </div>
            
            <div className="model-details">
              <p><strong>Type:</strong> {model.model_type}</p>
              <p><strong>Created:</strong> {new Date(model.created_at).toLocaleDateString()}</p>
              {model.completed_at && (
                <p><strong>Completed:</strong> {new Date(model.completed_at).toLocaleDateString()}</p>
              )}
            </div>
            
            <div className="model-prompt">
              <h4>Custom Prompt:</h4>
              <p className="prompt-text">
                {model.custom_prompt.substring(0, 150)}
                {model.custom_prompt.length > 150 ? '...' : ''}
              </p>
            </div>
            
            {model.status === 'completed' && (
              <div className="model-actions">
                <button 
                  className="secondary-button"
                  onClick={() => setTestingModel(model)}
                >
                  🧪 Test Model
                </button>
              </div>
            )}
          </div>
        ))}
        
        {models.length === 0 && datasets.length > 0 && (
          <div className="empty-state">
            <div className="empty-icon">🧠</div>
            <h3>No models trained yet</h3>
            <p>Train your first AI model with your uploaded data</p>
            <button 
              className="primary-button"
              onClick={() => setShowTraining(true)}
            >
              Train Model
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const ModelTraining = ({ datasets, onClose, onSuccess }) => {
  const [selectedDataset, setSelectedDataset] = useState('');
  const [modelName, setModelName] = useState('');
  const [customPrompt, setCustomPrompt] = useState('You are a helpful AI assistant trained on custom data. Use the provided context to answer questions accurately and helpfully.');
  const [training, setTraining] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDataset || !modelName || !customPrompt) return;

    setTraining(true);
    try {
      const formData = new FormData();
      formData.append('dataset_id', selectedDataset);
      formData.append('model_name', modelName);
      formData.append('custom_prompt', customPrompt);

      await axios.post(`${API}/models/train`, formData);
      onSuccess();
    } catch (error) {
      console.error('Training failed:', error);
      alert('Training failed. Please try again.');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content large">
        <div className="modal-header">
          <h3>🧠 Train New Model</h3>
          <button onClick={onClose} className="modal-close">×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="training-form">
          <div className="form-group">
            <label>Model Name</label>
            <input
              type="text"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="Enter model name"
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Select Dataset</label>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="form-select"
              required
            >
              <option value="">Choose a dataset...</option>
              {datasets.map(dataset => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.row_count} rows)
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Custom System Prompt</label>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="Define how your AI model should behave..."
              className="form-textarea"
              rows="6"
              required
            />
            <div className="form-hint">
              This prompt will define your model's personality and behavior. Make it specific to your use case.
            </div>
          </div>
          
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="secondary-button">
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={!selectedDataset || !modelName || !customPrompt || training}
              className="primary-button"
            >
              {training ? 'Training Model...' : 'Train Model'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ModelTesting = ({ model, onClose }) => {
  const [inputText, setInputText] = useState('');
  const [output, setOutput] = useState('');
  const [testing, setTesting] = useState(false);
  const [testHistory, setTestHistory] = useState([]);

  const handleTest = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setTesting(true);
    try {
      const response = await axios.post(`${API}/models/${model.id}/test`, {
        input_text: inputText
      });

      const result = {
        input: inputText,
        output: response.data.output,
        confidence: response.data.confidence,
        processing_time: response.data.processing_time,
        timestamp: new Date()
      };

      setOutput(response.data.output);
      setTestHistory(prev => [result, ...prev]);
      setInputText('');
    } catch (error) {
      console.error('Testing failed:', error);
      alert('Testing failed. Please try again.');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content large">
        <div className="modal-header">
          <h3>🧪 Test Model: {model.name}</h3>
          <button onClick={onClose} className="modal-close">×</button>
        </div>
        
        <div className="testing-interface">
          <form onSubmit={handleTest} className="test-form">
            <div className="form-group">
              <label>Test Input</label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter your test message here..."
                className="form-textarea"
                rows="4"
                required
              />
            </div>
            
            <button 
              type="submit" 
              disabled={!inputText.trim() || testing}
              className="primary-button"
            >
              {testing ? 'Testing...' : 'Test Model'}
            </button>
          </form>
          
          {output && (
            <div className="test-output">
              <h4>Latest Output:</h4>
              <div className="output-content">
                {output}
              </div>
            </div>
          )}
          
          {testHistory.length > 0 && (
            <div className="test-history">
              <h4>Test History:</h4>
              {testHistory.map((test, idx) => (
                <div key={idx} className="test-record">
                  <div className="test-input">
                    <strong>Input:</strong> {test.input}
                  </div>
                  <div className="test-output-small">
                    <strong>Output:</strong> {test.output}
                  </div>
                  <div className="test-meta">
                    Confidence: {(test.confidence * 100).toFixed(1)}% | 
                    Time: {test.processing_time.toFixed(2)}s | 
                    {test.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const DeployTab = ({ deployedModels, models, onRefresh }) => {
  const [deploying, setDeploying] = useState(null);

  const handleDeploy = async (modelId) => {
    setDeploying(modelId);
    try {
      await axios.post(`${API}/models/${modelId}/deploy`);
      onRefresh();
    } catch (error) {
      console.error('Deployment failed:', error);
      alert('Deployment failed. Please try again.');
    } finally {
      setDeploying(null);
    }
  };

  const completedModels = models.filter(m => m.status === 'completed');
  const deployedModelIds = new Set(deployedModels.map(dm => dm.training_id));
  const availableForDeployment = completedModels.filter(m => !deployedModelIds.has(m.id));

  return (
    <div className="deploy-tab">
      <div className="tab-header">
        <h2>🚀 Deploy Models</h2>
      </div>
      
      {availableForDeployment.length > 0 && (
        <div className="deploy-section">
          <h3>Available for Deployment</h3>
          <div className="deploy-grid">
            {availableForDeployment.map(model => (
              <div key={model.id} className="deploy-card">
                <h4 className="deploy-model-name">{model.name}</h4>
                <p className="deploy-model-type">{model.model_type}</p>
                <div className="deploy-actions">
                  <button 
                    className="primary-button"
                    onClick={() => handleDeploy(model.id)}
                    disabled={deploying === model.id}
                  >
                    {deploying === model.id ? 'Deploying...' : 'Deploy API'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {deployedModels.length > 0 && (
        <div className="deployed-section">
          <h3>Deployed APIs</h3>
          <div className="deployed-grid">
            {deployedModels.map(deployed => {
              const model = models.find(m => m.id === deployed.training_id);
              return (
                <div key={deployed.id} className="deployed-card">
                  <div className="deployed-header">
                    <h4 className="deployed-name">{deployed.name}</h4>
                    <div className={`deployed-status ${deployed.status}`}>
                      {deployed.status}
                    </div>
                  </div>
                  
                  <div className="deployed-details">
                    <p><strong>Endpoint:</strong> {deployed.api_endpoint}</p>
                    <p><strong>Usage:</strong> {deployed.usage_count} calls</p>
                    <p><strong>Deployed:</strong> {new Date(deployed.created_at).toLocaleDateString()}</p>
                  </div>
                  
                  <div className="api-example">
                    <h5>API Usage Example:</h5>
                    <code className="api-code">
                      POST {BACKEND_URL}{deployed.api_endpoint}
                      <br />
                      {`{"input_text": "Your question here"}`}
                    </code>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {deployedModels.length === 0 && availableForDeployment.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🚀</div>
          <h3>No models ready for deployment</h3>
          <p>Train and complete models first to deploy them as APIs</p>
        </div>
      )}
    </div>
  );
};

const App = () => {
  const [showLogin, setShowLogin] = useState(true);

  return (
    <div className="App">
      <AuthProvider>
        <AppContent showLogin={showLogin} setShowLogin={setShowLogin} />
      </AuthProvider>
    </div>
  );
};

const AppContent = ({ showLogin, setShowLogin }) => {
  const { user } = useAuth();

  if (user) {
    return <Dashboard />;
  }

  return showLogin ? (
    <LoginForm onSwitchToRegister={() => setShowLogin(false)} />
  ) : (
    <RegisterForm onSwitchToLogin={() => setShowLogin(true)} />
  );
};

export default App;