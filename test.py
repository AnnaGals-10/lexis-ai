from dotenv import load_dotenv
load_dotenv()

from analyzer import ContractAnalyzer

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
analyzer = ContractAnalyzer(os.path.join(BASE_DIR, "contracts", "FECINDCAS.pdf"))

print("=== RESUM EXECUTIU ===")
print(analyzer.executive_summary())

print("\n=== RED FLAGS ===")
print(analyzer.detect_red_flags())

print("\n=== PUNTUACIÓ DE RISC ===")
print(analyzer.risk_score())
