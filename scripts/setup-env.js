#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

async function checkPrerequisites() {
  console.log('🔍 Checking prerequisites...\n');
  
  const checks = [
    { name: 'Node.js', command: 'node --version' },
    { name: 'npm', command: 'npm --version' },
    { name: 'Python', command: 'python --version' },
    { name: 'pip', command: 'pip --version' },
    { name: 'Docker', command: 'docker --version' }
  ];
  
  for (const check of checks) {
    try {
      const { stdout } = await execAsync(check.command);
      console.log(`✅ ${check.name}: ${stdout.trim()}`);
    } catch (error) {
      console.log(`❌ ${check.name}: Not found or not accessible`);
    }
  }
}

async function createEnvFile() {
  const envPath = path.join(__dirname, '..', '.env');
  
  if (fs.existsSync(envPath)) {
    console.log('✅ .env file already exists');
    return;
  }
  
  const envContent = `# QualAI Environment Configuration
# Backend Configuration
OLLAMA_URL=http://ollama:11434
QDANT_URL=http://qdrant:6333
API_URL=http://localhost:8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=sqlite:///./qualai.db

# Development Configuration
DEBUG=true
LOG_LEVEL=INFO
`;
  
  try {
    fs.writeFileSync(envPath, envContent);
    console.log('✅ Created .env file with default configuration');
  } catch (error) {
    console.log('❌ Failed to create .env file:', error.message);
  }
}

async function createStartupScripts() {
  console.log('\n📝 Creating startup scripts...');
  
  // Windows batch file
  const windowsScript = `@echo off
echo Starting QualAI Project...
npm start
pause
`;
  
  // Unix/Linux shell script
  const unixScript = `#!/bin/bash
echo "Starting QualAI Project..."
npm start
`;
  
  try {
    fs.writeFileSync('start-qualai.bat', windowsScript);
    fs.writeFileSync('start-qualai.sh', unixScript);
    
    // Make Unix script executable
    if (process.platform !== 'win32') {
      fs.chmodSync('start-qualai.sh', '755');
    }
    
    console.log('✅ Created startup scripts:');
    console.log('   - start-qualai.bat (Windows)');
    console.log('   - start-qualai.sh (Unix/Linux)');
  } catch (error) {
    console.log('❌ Failed to create startup scripts:', error.message);
  }
}

async function main() {
  console.log('🚀 QualAI Project Setup\n');
  
  await checkPrerequisites();
  await createEnvFile();
  await createStartupScripts();
  
  console.log('\n🎉 Setup complete!');
  console.log('\n💡 Next steps:');
  console.log('   1. npm run install:all    - Install all dependencies');
  console.log('   2. npm start              - Start all services');
  console.log('   3. Open http://localhost:3000 in your browser');
  console.log('\n📚 Run "npm run help" for more information');
}

if (require.main === module) {
  main().catch(console.error);
}
