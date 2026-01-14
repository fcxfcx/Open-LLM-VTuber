@echo off
REM ============================================
REM Open-LLM-VTuber 启动脚本 - 使用 CUDA 11.8
REM ============================================

REM 设置 CUDA 11.8 路径
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8
set CUDA_PATH_V11_8=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8

REM 设置 cuDNN 8.9 路径
set CUDNN_PATH=C:\Program Files\NVIDIA\CUDNN\v8.9

REM 保存原始的 PATH 环境变量
set ORIGINAL_PATH=%PATH%

REM 将 CUDA 11.8 和 cuDNN 8.9 的路径添加到 PATH 的最前面
REM 注意：顺序很重要，cuDNN 应该在 CUDA 之后
set PATH=%CUDA_PATH%\bin;%CUDNN_PATH%\bin;%PATH%
set PATH=%CUDA_PATH%\libnvvp;%PATH%

REM 设置其他可能需要的 CUDA 环境变量
set CUDA_HOME=%CUDA_PATH%
set CUDA_ROOT=%CUDA_PATH%

REM 显示当前使用的 CUDA 版本（用于确认）
echo ============================================
echo Use CUDA 11.8 and cuDNN 8.9 to start the project
echo ============================================
echo CUDA_PATH: %CUDA_PATH%
echo CUDNN_PATH: %CUDNN_PATH%
echo.

REM 验证 DLL 文件是否存在
if exist "%CUDA_PATH%\bin\cudart64_110.dll" (
    echo [OK] CUDA 11.8 DLL file exists
) else (
    echo [Warning] CUDA 11.8 DLL file not found
)

if exist "%CUDNN_PATH%\bin\cudnn64_8.dll" (
    echo [OK] cuDNN 8.9 DLL file exists
) else (
    echo [Warning] cuDNN 8.9 DLL file not found
)
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 运行服务器
echo Starting server...
echo.
uv run run_server.py %*

REM The environment variables will be automatically restored when the script ends (because they are set in a sub-process)