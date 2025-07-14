# 📦 Environment Overview for Swift AI Trader

This project uses **two separate Python environments** to ensure compatibility across all dependencies, especially those that currently don't support Python 3.12.

---

## 🔁 Environment Summary

| Environment | Python Version | Purpose                                 | Directory         | Requirements File       |
|-------------|----------------|-----------------------------------------|-------------------|--------------------------|
| `env_main`  | 3.12.x         | FastAPI backend, DB, dev tools          | `env_main/`       | `requirements_main.txt` |
| `env_310`   | 3.10.x         | Supabase client, AI/ML, Quant finance   | `env_310/`        | `requirements_py310.txt` |

---

## ✅ Setup Instructions

### 1. Create Environments (only once)

#### ➤ Python 3.12 (Main Backend)
```bash
py -3.12 -m venv env_main
