@echo off
echo 🚀 启动回译训练系统...

cd /d %~dp0

echo 📥 正在同步最新数据...
git pull

echo 🌐 启动 Web 界面...
call .venv\Scripts\activate
streamlit run app.py

echo 📤 正在提交数据...
git add translation_train.db
git commit -m "auto update %date% %time%"
git push

echo ✅ 完成
pause