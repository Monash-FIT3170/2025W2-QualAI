#!/usr/bin/env node

const http = require('http');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

const services = [
  { name: 'Landing Page', port: 3000, url: 'http://localhost:3000' },
  { name: 'React Frontend', port: 5173, url: 'http://localhost:5173' },
  { name: 'FastAPI Backend', port: 8000, url: 'http://localhost:8000' },
  { name: 'Qdrant Database', port: 6333, url: 'http://localhost:6333' }
];

async function checkService(service) {
  return new Promise((resolve) => {
    const req = http.get(service.url, (res) => {
      resolve({ ...service, status: '🟢 Running', code: res.statusCode });
    });
    
    req.on('error', () => {
      resolve({ ...service, status: '🔴 Not Running', code: 'N/A' });
    });
    
    req.setTimeout(3000, () => {
      req.destroy();
      resolve({ ...service, status: '🟡 Timeout', code: 'N/A' });
    });
  });
}

async function checkDockerStatus() {
  try {
    const { stdout } = await execAsync('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"');
    return stdout.trim();
  } catch (error) {
    return 'Docker not running or not installed';
  }
}

async function main() {
  console.log('🔍 QualAI Project Status Check\n');
  
  // Check all services
  const results = await Promise.all(services.map(checkService));
  
  console.log('📊 Service Status:');
  console.log('==================');
  results.forEach(service => {
    console.log(`${service.status} ${service.name} (Port ${service.port})`);
  });
  
  console.log('\n🐳 Docker Containers:');
  console.log('=====================');
  const dockerStatus = await checkDockerStatus();
  console.log(dockerStatus);
  
  console.log('\n💡 Quick Actions:');
  console.log('==================');
  console.log('npm start          - Start all services');
  console.log('npm run dev:docker - Start with Docker');
  console.log('npm run help       - Show all commands');
}
