"""
Evaluate RAG Performance
Runs the generated testset against the QueryService and calculates metrics
using 'ragas'.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from datasets import Dataset

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag.engine.query_service import get_query_service
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy,
    context_recall,
)

# Load env variables
load_dotenv()


def run_evaluation(testset_path="testset.csv", output_path="evaluation_results.csv"):
    print("🚀 Starting RAG Evaluation...")

    # 1. Load Testset
    if not os.path.exists(testset_path):
        print(f"❌ Testset not found at {testset_path}")
        return

    df = pd.read_csv(testset_path)
    # Ragas 0.2 uses 'user_input' and 'reference'
    if "user_input" in df.columns:
        questions = df["user_input"].tolist()
        ground_truths = df["reference"].tolist()
    else:
        # Fallback for older versions
        questions = df["question"].tolist()
        ground_truths = df["ground_truth"].tolist()

    print(f"Loaded {len(questions)} test cases.")

    # 2. Run Queries against System
    qs = get_query_service()

    answers = []
    contexts = []

    print("running queries...")
    for i, q in enumerate(questions):
        print(f"   [{i + 1}/{len(questions)}] Query: {q[:50]}...")

        # Use our RAG system
        result = qs.query(q)

        answers.append(result.answer)

        # Extract context content list
        # Ragas expects: list[str]
        doc_contents = [s["content"] for s in result.sources]
        contexts.append(doc_contents)

    # 3. Prepare Dataset for Ragas
    data_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }
    dataset = Dataset.from_dict(data_dict)

    # 4. Evaluate
    print(
        "Evaluating metrics (Faithfulness, Answer Relevancy, Context Precision/Recall)..."
    )

    result = evaluate(
        dataset=dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
    )

    print("\n📊 Evaluation Results:")
    print(result)

    # 5. Save Results
    result_df = result.to_pandas()
    result_df.to_csv(output_path, index=False)
    print(f"✅ Detailed results saved to {output_path}")


if __name__ == "__main__":
    run_evaluation()
