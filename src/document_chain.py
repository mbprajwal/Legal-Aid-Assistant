# src/document_chain.py

import os
import json
from fpdf import FPDF
import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


class DocumentGeneratorChain:
    """
    Generates legal documents using:
    - Template JSON
    - User field inputs
    - Memory context
    - RAG legal context
    """

    def __init__(self, model_name="llama2", template_dir="src/templates"):
        self.llm = ChatOllama(model=model_name, temperature=0.2, max_tokens=700)
        self.template_dir = template_dir

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             """You are a formal Indian legal document drafting assistant.
Follow these rules:
- Produce a structured legal document.
- Use only factual information from template fields, memory, and legal context.
- Do NOT hallucinate details.
- Use placeholders where information is missing.
- Maintain correct legal formatting.
"""),
            ("system", "User memory:\n{memory}"),
            ("system", "Relevant legal context:\n{context}"),
            ("system", "Template title: {title}"),
            ("system", "Template instructions: {instructions}"),
            ("system", "Template fields filled by user:\n{fields}"),
            ("user", "Generate the complete legal document now.")
        ])

    # ------------------------------------------------------------
    # Load JSON template
    # ------------------------------------------------------------
    def load_template(self, template_name):
        path = os.path.join(self.template_dir, f"{template_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template '{template_name}' not found.")
        return json.load(open(path, "r", encoding="utf-8"))


    def generate(self, template_name, field_values, context):
        return self.generate_document(template_name, field_values, context)

    # ------------------------------------------------------------
    # Generate legal draft using LLM
    # ------------------------------------------------------------
    def generate_document(
        self,
        template_name: str,
        user_inputs: dict,
        memory_string: str,
        rag_context: str
    ):
        template = self.load_template(template_name)

        # Format fields text block
        fields_text = "\n".join(
            f"- {label}: {user_inputs.get(key, '[missing]')}"
            for key, label in template["fields"].items()
        )

        prompt = self.prompt_template.format(
            memory=memory_string or "None",
            context=rag_context or "None",
            title=template["title"],
            instructions=template["instructions"],
            fields=fields_text
        )

        response = self.llm.invoke(prompt)
        return response.content.strip()

    # ------------------------------------------------------------
    # Export to PDF
    # ------------------------------------------------------------

    def save_pdf(self, content: str, filename: str = None) -> str:
        """
        Save PDF inside a timestamped directory so files never overwrite.
        Auto-generates filenames if not provided.
        """

        # ---------- Create base directory ----------
        base_dir = "generated_documents"
        os.makedirs(base_dir, exist_ok=True)

        # ---------- Create unique folder per-generation ----------
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(base_dir, timestamp)
        os.makedirs(output_dir, exist_ok=True)

        # ---------- Generate unique filename ----------
        if filename is None:
            filename = f"document_{timestamp}.pdf"
        else:
            # add timestamp to avoid overwriting
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"

        save_path = os.path.join(output_dir, filename)

        # ---------- Write PDF ----------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in content.split("\n"):
            pdf.multi_cell(0, 8, line)

        pdf.output(save_path)

        return os.path.abspath(save_path)

