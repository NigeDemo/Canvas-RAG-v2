# 🤖 New Agent - Start Here (October 7, 2025)

Welcome! This is a Canvas RAG v2 system for architecture education. You're picking up where the previous session left off.

---

## 📋 Quick Context (Read This First!)

### What This Project Does
- **Purpose**: Student-facing RAG tool for Canvas LMS architecture course
- **Features**: Text + image content retrieval, module queries, vision AI integration
- **Tech Stack**: Python, FastAPI/Streamlit, OpenAI GPT-4, ChromaDB, Canvas API

### Current State
- ✅ **Module query fix implemented** (October 3) - uses PromptTemplate system
- ✅ **Repository cleaned** - 24 obsolete files removed
- 🔴 **Image retrieval BROKEN** - students can't access architectural drawings
- 🔴 **DO NOT PUSH TO GIT** - critical issues need resolution first

---

## 🎯 Your Mission: Fix & Test Before Push

### CRITICAL Issue (Priority #1)
Problem: Query "List all images from this canvas topic" returns no images and generic content. See details in the archived critical issue doc.
