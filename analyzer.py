from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
import json

class ContractAnalyzer:
    def __init__(self, pdf_path: str):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.vectorstore = self._build_vectorstore(pdf_path)
        self.language = self._detect_language()

    def _build_vectorstore(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        embeddings = OpenAIEmbeddings()
        return FAISS.from_documents(chunks, embeddings)

    def _ask(self, question: str) -> str:
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5})
        )
        result = chain.invoke(question)["result"].strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return result.strip()

    def _detect_language(self) -> str:
        result = self._ask(
            "What language is this document written in? "
            "Reply with only the language name in English, e.g. 'Spanish', 'Catalan', 'French'."
        )
        return result.strip()

    def detect_red_flags(self) -> list:
        prompt = (
            f"You are a senior legal analyst. Reply exclusively in {self.language}.\n"
            "Thoroughly review this contract and identify all clauses that may be risky, "
            "abusive, ambiguous, or unfavorable to one party.\n\n"
            "Look specifically for:\n"
            "- Disproportionate penalties or liquidated damages\n"
            "- Automatic renewal or lock-in clauses\n"
            "- Excessive limitations of liability\n"
            "- Unilateral termination or modification rights\n"
            "- Hidden obligations or unclear responsibilities\n"
            "- Unfair payment terms or delay penalties\n"
            "- Intellectual property transfer clauses\n"
            "- Non-compete or exclusivity obligations\n"
            "- Governing law or jurisdiction risks\n"
            "- Force majeure clauses with unusual scope\n\n"
            "For each clause, provide:\n"
            "- A clear descriptive title\n"
            "- Risk level: high, medium, or low\n"
            "- A detailed explanation (2-4 sentences) of why it is risky\n"
            "- Industry benchmark: compare the clause to what is standard in the market, "
            "giving concrete numbers or norms when possible "
            "(e.g. 'Standard notice periods are 30-90 days; this clause requires 12 months')\n"
            "- The exact relevant fragment from the contract\n\n"
            'Return ONLY a JSON array: '
            '[{"titol": "clause name", "risc": "high/medium/low", '
            '"descripcio": "detailed explanation", '
            '"benchmark": "comparison with industry standard", '
            '"fragment": "exact text"}]'
        )
        result = self._ask(prompt)
        try:
            return json.loads(result)
        except:
            return []

    def risk_score(self) -> dict:
        prompt = (
            f"You are a senior legal analyst. Reply exclusively in {self.language}.\n"
            "Assess the overall risk level of this contract.\n\n"
            "Provide a risk score from 1 to 10 (1 = very safe, 10 = highly risky), "
            "a detailed justification (3-5 sentences) referencing specific clauses, "
            "and a recommendation: Accept, Negotiate, or Reject.\n\n"
            'Return ONLY a JSON object: '
            '{"puntuacio": <number>, "justificacio": "<text>", "recomanacio": "<Accept/Negotiate/Reject>"}'
        )
        result = self._ask(prompt)
        try:
            return json.loads(result)
        except:
            return {}

    def executive_summary(self) -> dict:
        prompt = (
            f"You are a senior legal analyst. Reply exclusively in {self.language}.\n"
            "Provide a thorough executive summary of this contract.\n\n"
            'Return ONLY a JSON object: '
            '{"tipus_contracte": "<type>", "parts_involucrades": ["<party1>", "<party2>"], '
            '"durada": "<duration or Not specified>", '
            '"punts_clau": ["<detailed point 1>", "<detailed point 2>", "<detailed point 3>", '
            '"<detailed point 4>", "<detailed point 5>"], '
            '"obligacions_principals": ["<obligation 1>", "<obligation 2>", '
            '"<obligation 3>", "<obligation 4>"]}'
        )
        result = self._ask(prompt)
        try:
            return json.loads(result)
        except:
            return {}

    def find_negotiable_clauses(self) -> list:
        prompt = (
            f"You are a senior contract lawyer. Reply exclusively in {self.language}.\n"
            "Even if this contract is generally balanced, identify the 3-5 clauses that "
            "could most benefit from negotiation to better protect both parties. "
            "Focus on clauses that are slightly one-sided, vague, or could be improved.\n\n"
            'Return ONLY a JSON array: '
            '[{"titol": "clause name", "risc": "low", '
            '"descripcio": "why this clause could be improved", '
            '"fragment": "relevant text from the contract"}]'
        )
        result = self._ask(prompt)
        try:
            return json.loads(result)
        except:
            return []

    def suggest_negotiations(self, flags: list) -> list:
        if not flags:
            return []
        flags_summary = json.dumps(
            [{"titol": f.get("titol"), "descripcio": f.get("descripcio"), "fragment": f.get("fragment")} for f in flags],
            ensure_ascii=False
        )
        prompt = (
            f"You are a senior contract lawyer. Reply exclusively in {self.language}.\n"
            "For each of the following risk clauses, suggest a fairer and more balanced reformulation "
            "that protects both parties. The suggestion should be practical and ready to use in a negotiation.\n\n"
            f"Clauses:\n{flags_summary}\n\n"
            'Return ONLY a JSON array in the same order as the input: '
            '[{"titol": "same title", "proposta": "suggested reformulation (2-4 sentences)"}]'
        )
        result = self._ask(prompt)
        try:
            return json.loads(result)
        except:
            return []

    def chat(self, question: str) -> str:
        prompt = (
            f"You are a senior legal analyst. Reply exclusively in {self.language}.\n"
            "Based strictly on the contract provided, answer the following question clearly and concisely.\n"
            "If the information is not in the contract, say so explicitly.\n\n"
            f"Question: {question}"
        )
        return self._ask(prompt)
