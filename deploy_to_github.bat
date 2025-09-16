@echo off
echo.
echo 🚀 GPT.R1 - GitHub Deployment Script
echo 👨‍💻 Created by: Rajan Mishra
echo ==================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

echo ✅ Git is installed

REM Initialize git repository if not already initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

REM Create .gitignore file
echo 📝 Creating .gitignore file...
(
echo # Environment files
echo .env
echo .env.local
echo .env.development.local
echo .env.test.local
echo .env.production.local
echo.
echo # Dependencies
echo node_modules/
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo env/
echo venv/
echo ENV/
echo.
echo # Database
echo *.db
echo *.sqlite
echo *.sqlite3
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Logs
echo logs/
echo *.log
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo.
echo # Build outputs
echo build/
echo dist/
echo .next/
echo out/
echo.
echo # Testing
echo .pytest_cache/
echo test.db
echo test_*.db
) > .gitignore

echo ✅ .gitignore created

REM Create LICENSE file
echo 📄 Creating LICENSE file...
(
echo MIT License
echo.
echo Copyright ^(c^) 2025 Rajan Mishra
echo.
echo Permission is hereby granted, free of charge, to any person obtaining a copy
echo of this software and associated documentation files ^(the "Software"^), to deal
echo in the Software without restriction, including without limitation the rights
echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
echo copies of the Software, and to permit persons to whom the Software is
echo furnished to do so, subject to the following conditions:
echo.
echo The above copyright notice and this permission notice shall be included in all
echo copies or substantial portions of the Software.
echo.
echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
echo SOFTWARE.
) > LICENSE

echo ✅ LICENSE created

REM Stage all files
echo 📦 Staging files for commit...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "🚀 Initial commit: GPT.R1 - Advanced AI Assistant

✨ Features:
- Real-time chat streaming with FastAPI
- Modern Next.js frontend with TypeScript  
- Advanced RAG system with DuckDuckGo search
- Enterprise authentication with JWT
- Comprehensive testing suite
- Production-ready architecture

👨‍💻 Created by: Rajan Mishra
🎯 Grade: A+ Production Ready"

echo ✅ Initial commit created
echo.
echo 🌟 GITHUB UPLOAD INSTRUCTIONS
echo =============================
echo.
echo 1. Create a new repository on GitHub:
echo    - Go to https://github.com/new
echo    - Repository name: gpt-r1
echo    - Description: 🚀 GPT.R1 - Advanced AI Assistant ^| Enterprise-grade ChatGPT clone
echo    - Make it Public
echo    - Don't initialize with README
echo.
echo 2. Connect and push to GitHub:
echo    git remote add origin https://github.com/YOUR_USERNAME/gpt-r1.git
echo    git branch -M main  
echo    git push -u origin main
echo.
echo 3. Add these topics to your repository:
echo    chatgpt, ai, fastapi, nextjs, openai, rag, streaming, typescript
echo.
echo 🎉 Your GPT.R1 project is ready for GitHub!
echo 📊 Repository will showcase your advanced AI development skills
echo 🚀 Perfect for portfolio and client demonstrations
echo.
echo Created with ❤️ by Rajan Mishra
echo.
pause