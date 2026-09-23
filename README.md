# ⚖️ المساعد القانوني الذكي (RAG)

مساعد قانوني بالعربي بيجاوب عن أسئلة المستخدم **استنادًا للنصوص الرسمية لثلاثة قوانين مصرية فقط**، مع ذكر اسم القانون ورقم المادة في كل إجابة. المشروع مبني بتقنية **RAG (Retrieval-Augmented Generation)** وبيشتغل بالكامل على جهازك عن طريق Ollama، من غير أي API خارجي.

> مشروع التخرج - ITI

---

## القوانين المتاحة

| القانون | الرقم |
|---|---|
| قانون حماية البيانات الشخصية | 151 لسنة 2020 |
| قانون حماية المستهلك | 181 لسنة 2018 |
| قانون العمل | 14 لسنة 2025 |

## إزاي بيشتغل

```
سؤال المستخدم
      │
      ▼
 Streamlit (frontend)  ──HTTP──▶  FastAPI (backend)
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                  Retrieval                   Generation
            BAAI/bge-m3 + ChromaDB        Ollama (qwen2.5:7b)
            أقرب 4 مواد للسؤال            بيجاوب من المواد دي بس
                          └────────────┬────────────┘
                                       ▼
                              الإجابة + المصادر
```

1. **الاسترجاع:** السؤال بيتحوّل لـ embedding بموديل `BAAI/bge-m3`، وبيتدوّر على أقرب `top_k` مقاطع في ChromaDB (بمقياس cosine).
2. **التوليد:** المقاطع دي بتتبعت لموديل `qwen2.5:7b` على Ollama مع تعليمات صارمة: يجاوب من النصوص المرفقة بس، ويذكر القانون والمادة، ومايخترعش أي معلومة.
3. **العرض:** الإجابة بتظهر في واجهة Streamlit ومعاها المصادر.

## التقنيات المستخدمة

| الطبقة | التقنية |
|---|---|
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit |
| Embeddings | `BAAI/bge-m3` (sentence-transformers) |
| Vector store | ChromaDB |
| LLM | Ollama - `qwen2.5:7b` |
| الاختبارات | pytest, httpx |

## هيكل المشروع

```
.
├── Data/
│   ├── consumer_protection_181_2018.txt      # النصوص الخام للقوانين
│   ├── labor_law_raw_wikitext.txt
│   ├── personal_data_151_2020.txt
│   └── processed/                            # المواد بعد التنظيف والتقسيم + نتائج التقييم
├── backend/
│   ├── app/
│   │   ├── main.py                           # نقطة تشغيل FastAPI
│   │   ├── api/routes/query.py               # endpoints
│   │   ├── core/config.py                    # الإعدادات
│   │   ├── schemas/query.py                  # شكل الطلب والرد
│   │   └── services/                         # retrieval.py + generation.py
│   ├── data/
│   │   ├── vector_store/                     # قاعدة ChromaDB جاهزة (473 مقطع)
│   │   └── rag_config.json
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app.py                                # واجهة Streamlit
│   ├── api_client.py                         # الاتصال بالـ backend
│   ├── requirements.txt
│   └── .env.example
└── Project.ipynb                             # بناء الـ corpus والـ embeddings والتقييم
```

## المتطلبات

- **Python 3.10** أو أحدث
- **[Ollama](https://ollama.com/download)** متسطّب وشغّال
- الموديل بتاع التوليد:

```powershell
ollama pull qwen2.5:7b
```

> أول تشغيل للـ backend هينزّل موديل `BAAI/bge-m3` من HuggingFace (حجمه أكتر من 2 جيجا)، فلازم يكون فيه إنترنت المرة الأولى بس.

## التشغيل

الـ vector store **جاهز ومرفوع مع المشروع**، فمش محتاج تعيد بناء الـ embeddings. الأوامر دي لـ Windows PowerShell.

### 1) الـ Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

الـ API هيشتغل على `http://localhost:8000`، والـ docs التفاعلية على `http://localhost:8000/docs`.

### 2) الـ Frontend

افتح terminal جديد:

```powershell
cd frontend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

الواجهة هتفتح على `http://localhost:8501`.

> تأكد إن Ollama شغّال والـ backend شغّال قبل ما تسأل. الشريط الجانبي في الواجهة بيوريك حالة الاتصال بالخادم.

## الإعدادات

بتتظبط من ملف `.env` (انسخه من `.env.example`).

**Backend** (`backend/.env`):

| المتغير | القيمة الافتراضية | الوصف |
|---|---|---|
| `VECTOR_STORE_PATH` | `data/vector_store` | مسار قاعدة ChromaDB |
| `COLLECTION_NAME` | `laws` | اسم الـ collection |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | موديل الـ embeddings |
| `OLLAMA_MODEL` | `qwen2.5:7b` | موديل التوليد |
| `TOP_K` | `4` | عدد المقاطع المسترجعة لكل سؤال |

**Frontend** (`frontend/.env`):

| المتغير | القيمة الافتراضية | الوصف |
|---|---|---|
| `API_BASE_URL` | `http://localhost:8000` | عنوان الـ backend |

## الـ API

### `GET /health`

```json
{ "status": "ok" }
```

### `POST /query`

الطلب:

```json
{ "question": "هل أقدر أرجّع السلعة وأسترد فلوسي؟" }
```

الرد:

```json
{
  "answer": "...",
  "sources": ["قانون حماية المستهلك 181 لسنة 2018 - المادة 17"]
}
```

## بيانات المشروع

- **المصادر:** النصوص الخام للقوانين (ملفات txt، وويكي مصدر، وPDF لقانون العمل).
- **المعالجة:** استخراج المواد بالـ regex، ومقارنة نص ويكي مصدر بنص الـ PDF في قانون العمل واختيار الأدق، وتصحيح الأرقام المقلوبة في الـ PDF.
- **التقسيم (Chunking):** حسب بنية المواد والبنود بحد أقصى 1200 حرف، بدون overlap. الناتج **473 مقطع**.
- كل الخطوات موجودة ومتوثّقة في [`Project.ipynb`](Project.ipynb).

## التقييم

اتعمل تقييم يدوي على **20 سؤال** (17 سؤال ليهم مادة محددة، و3 أسئلة برّه النطاق أو من غير مادة محددة):

| المقياس | النتيجة |
|---|---|
| Hit@4 (للأسئلة ذات المادة المحددة) | **1.0** |
| متوسط زمن الاستجابة | **10.2 ثانية** |

النتايج التفصيلية في `Data/processed/evaluation_results.csv`.

## تشغيل الاختبارات

```powershell
cd backend
pytest
```

## تنبيه

إجابات المساعد **للاستئناس فقط** وليست بديلًا عن استشارة قانونية رسمية.
