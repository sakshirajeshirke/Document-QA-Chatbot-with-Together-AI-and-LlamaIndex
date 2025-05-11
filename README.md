# Document-QA-Chatbot-with-Together-AI-and-LlamaIndex
---

````markdown
# 🤖 Document QA Chatbot with Together AI & LlamaIndex

A smart, multi-document Question Answering (QA) chatbot built with **Streamlit**, **Together AI**, and **LlamaIndex**. Upload your PDFs, DOCX, or TXT files and instantly ask questions in natural language. Ideal for insurance agents, legal professionals, students, and knowledge workers.

---

## 🚀 Features

✨ Ask questions directly from uploaded documents  
📚 Supports multi-document queries  
🧠 Uses Together AI’s powerful LLMs & Embeddings  
⚙️ LlamaIndex for flexible indexing (VectorStore, etc.)  
📊 Langfuse integration for observability  
🎨 Clean, responsive Streamlit UI  

---

## 🧠 Powered By

| Component         | Technology Used                                  |
|------------------|---------------------------------------------------|
| **Frontend**      | `Streamlit`                                       |
| **LLM**           | `Together AI` (Mistral, LLaMA, Qwen, etc.)        |
| **Embeddings**    | `togethercomputer/m2-bert-80M-8k-retrieval`       |
| **Indexing**      | `LlamaIndex` with `VectorStoreIndex`             |
| **Tracing**       | `Langfuse` for monitoring and logging             |
| **Supported Files**| `.pdf`, `.docx`, `.txt`                          |

---

## 📦 Installation

```bash
git clone https://github.com/your-username/Document-QA-Chatbot-with-Together-AI-and-LlamaIndex.git
cd Document-QA-Chatbot-with-Together-AI-and-LlamaIndex

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
````

---

## 🔐 Environment Setup

Create a `.env` file in the root directory and add the following:

```env
TOGETHER_API_KEY=your_together_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional
```

> ⚠️ **Note:** Don't commit your `.env` file. Add it to `.gitignore`!

---

## ▶️ How to Run

```bash
streamlit run lang.py
```

Open in your browser at `http://localhost:8501`.

---

## 🧪 Sample Use Cases

* 🔍 Extract specific info from insurance claim documents
* 📑 Compare multiple contracts or policies
* 🎓 Ask questions from research papers or study material
* 🧾 Search summaries in invoices and receipts

---

## 📸 Screenshots

# Upload & Ask                                                         
| ![upload](![chat1](https://github.com/user-attachments/assets/2ff4160d-d5be-4092-a6e1-54d26eb60b3b))
# Chat Interface 
| ![chat](https://via.placeholder.com/400x250?text=Ask+Questions) |
# langfuse 
| ![langfuse] (![chatbot2](https://github.com/user-attachments/assets/63f8ff7b-72db-4dbe-a4d4-40d0b8cf516c)) |
---

## 📁 Project Structure

```
├── lang.py               # Main Streamlit app
├── .env                 # API keys (excluded from repo)
├── requirements.txt     # Required Python packages
├── README.md            # Project info
```

---

## 📊 Langfuse Monitoring (Optional)

Track and trace your LLM responses using Langfuse.

* Get keys from [Langfuse Cloud](https://cloud.langfuse.com/)
* Easily trace LLM performance and prompt interactions

---

## 📌 Roadmap

* ✅ Multi-document support
* ✅ Together AI + Langfuse integration
* ⏳ PDF summarization
* ⏳ Qdrant/Pinecone support for persistent storage
* ⏳ Batch preprocessing

---

## 🛡 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

* [Together AI](https://www.together.ai/)
* [LlamaIndex](https://www.llamaindex.ai/)
* [Langfuse](https://www.langfuse.com/)
* [Streamlit](https://streamlit.io/)

---

Made with ❤️ for smart document understanding.

```
