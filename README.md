# Microsoft IQ Solution Accelerator

A streamlined Azure AI Foundry solution for document-based question answering using knowledge bases and intelligent agents.

## 🚀 Infrastructure Deployed

This solution automatically deploys:

- **Azure AI Foundry Hub & Project** - Core AI platform for agent management
- **Azure AI Search** - Document indexing and semantic search capabilities  
- **Azure Storage Account** - Document storage with direct blob access for citations
- **Azure OpenAI Models** - GPT-4.1-mini for chat and text-embedding-3-small for search
- **Managed Identities** - Secure authentication between services

## 🤖 AI Agents Created

### Chat Agent
- **Purpose**: Document-based question answering and analysis
- **Knowledge Source**: Foundry IQ Knowledge Base with automatic query planning
- **Capabilities**: 
  - Policy and guideline lookups
  - Document search with semantic ranking
  - Direct source citations with blob storage links
  - Chart generation from retrieved data

## 📚 Knowledge Base Features

The knowledge base will be populated with your documents:
- Upload PDF documents to `src/foundry/data/documents/` folder
- Automatic page-aware chunking for precise citations
- Semantic search with vector embeddings
- Azure Blob Storage integration for direct document access

**Note**: The documents folder is currently empty. Add your PDF documents there and run the upload script to populate the knowledge base.

## 🎯 Sample Questions to Try

*After uploading your documents, try questions like these based on typical business content:*

### Document Discovery
- "What documents are available in the knowledge base?"
- "Show me the supplier onboarding process"
- "Find information about evaluation criteria or approval processes"

### Content Search
- "What are the qualification criteria for new suppliers?"
- "How long does the supplier evaluation process take?" 
- "What documentation is required for supplier approval?"
- "What are the trial order procedures mentioned?"

### Analysis Requests
- "Summarize the key steps in the supplier onboarding process"
- "What performance metrics are used for supplier monitoring?"
- "Compare the requirements between different procedures"

### Specific Details
- "What is the minimum reliability score required?"
- "How much volume can trial orders include?"
- "What training is provided to suppliers?"
- "What security standards are mentioned for data exchange?"

## 🔧 Getting Started

1. **Deploy**: Run `azd up` to deploy all infrastructure and create agents
2. **Add Documents**: Upload your PDF files to `src/foundry/data/documents/` folder
3. **Index Documents**: Run `python src/foundry/scripts/01_upload_to_search.py` (if not done during deployment)
4. **Access**: Open Azure AI Foundry Studio in the Azure portal
5. **Chat**: Navigate to the Playground and select your "ChatAgent"
6. **Ask Questions**: Start with document discovery questions to see what's available

## 💡 Tips for Best Results

- **Add Documents First**: Upload PDF documents to get meaningful responses
- **Be Specific**: Ask about policies, procedures, or specific document content
- **Use Context**: Reference document types or names you've uploaded
- **Request Citations**: The agent will provide direct links to source documents
- **Ask Follow-ups**: Build on previous answers for deeper analysis
- **Start Simple**: Begin with "What documents are available?" to understand your knowledge base

## 📁 Document Management

- **Upload Documents**: Add your PDF files to `src/foundry/data/documents/` folder
- **Run Upload Script**: Execute `python src/foundry/scripts/01_upload_to_search.py` after adding documents
- **Storage**: Documents are stored in Azure Blob Storage for reliable access
- **Citations**: Each response includes page numbers and direct document links
- **Updates**: Add new PDFs and re-run the upload script to update the knowledge base

---

**Next Steps**: Visit the [Azure AI Foundry playground](https://ai.azure.com) to start chatting with your knowledge-powered agent!