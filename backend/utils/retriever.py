"""
Enterprise Industrial AI Copilot

Semantic Retriever

Used by

Notebook 06
Notebook 07
Streamlit
FastAPI
"""

import numpy as np
import pandas as pd
import faiss

from sentence_transformers import SentenceTransformer


class EnterpriseRetriever:

    def __init__(

        self,

        index_path,

        metadata_path,

        chunk_path,

        model_name="sentence-transformers/all-MiniLM-L6-v2"

    ):

        self.index = faiss.read_index(index_path)

        self.metadata = pd.read_parquet(metadata_path)

        self.chunks = pd.read_parquet(chunk_path)

        self.model = SentenceTransformer(model_name)

    def search(

        self,

        query,

        top_k=5

    ):

        query_embedding = self.model.encode(

            [query],

            normalize_embeddings=True,

            convert_to_numpy=True

        ).astype(np.float32)

        scores, indices = self.index.search(

            query_embedding,

            top_k

        )

        results = []

        for rank, (score, idx) in enumerate(

            zip(scores[0], indices[0]),

            start=1

        ):

            meta = self.metadata.iloc[idx]

            chunk = self.chunks[

                self.chunks["Chunk_ID"]

                == meta["Chunk_ID"]

            ].iloc[0]

            results.append({

                "Rank": rank,

                "Score": round(float(score),4),

                "Chunk_ID": meta["Chunk_ID"],

                "Document_ID": meta["Document_ID"],

                "File_Name": meta["File_Name"],

                "Page_Number": meta["Page_Number"],

                "Source": meta["Source"],

                "Chunk_Text": chunk["Chunk_Text"]

            })

        return pd.DataFrame(results)